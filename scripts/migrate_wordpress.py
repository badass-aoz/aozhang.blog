#!/usr/bin/env python3
"""Clean WordPress.com -> Hugo PaperMod migration script for aozhang.blog."""

from __future__ import annotations

import argparse
import concurrent.futures
import html
import io
import json
import re
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
from markdownify import MarkdownConverter
from PIL import Image, ImageOps
import yaml

SITE_HOST = "aozlife.wordpress.com"
API_BASE = f"https://public-api.wordpress.com/rest/v1.1/sites/{SITE_HOST}"
REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = REPO_ROOT / "migration_cache"
CONTENT_DIR = REPO_ROOT / "content"
POSTS_DIR = CONTENT_DIR / "posts"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )
}


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_or_fetch_all(refresh: bool = False) -> tuple[list[dict], list[dict], list[dict]]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    posts_cache = CACHE_DIR / "posts.json"
    pages_cache = CACHE_DIR / "pages.json"
    comments_cache = CACHE_DIR / "comments.json"

    if not refresh and posts_cache.exists() and pages_cache.exists() and comments_cache.exists():
        return (
            json.loads(posts_cache.read_text("utf-8")),
            json.loads(pages_cache.read_text("utf-8")),
            json.loads(comments_cache.read_text("utf-8")),
        )

    print("Fetching posts from WordPress.com REST API...")
    posts: list[dict] = []
    offset = 0
    while True:
        data = fetch_json(f"{API_BASE}/posts/?number=100&offset={offset}")
        batch = data.get("posts", [])
        if not batch:
            break
        posts.extend(batch)
        found = int(data.get("found", len(posts)))
        print(f"  fetched {len(posts)} / {found} posts")
        if len(posts) >= found:
            break
        offset += len(batch)

    print("Fetching pages & comments...")
    pages_data = fetch_json(f"{API_BASE}/posts/?type=page&number=50")
    pages = pages_data.get("posts", [])

    comments: list[dict] = []
    c_offset = 0
    while True:
        cdata = fetch_json(f"{API_BASE}/comments/?number=100&offset={c_offset}")
        cbatch = cdata.get("comments", [])
        if not cbatch:
            break
        comments.extend(cbatch)
        cfound = int(cdata.get("found", len(comments)))
        if len(comments) >= cfound:
            break
        c_offset += len(cbatch)

    posts_cache.write_text(json.dumps(posts, ensure_ascii=False, indent=2), "utf-8")
    pages_cache.write_text(json.dumps(pages, ensure_ascii=False, indent=2), "utf-8")
    comments_cache.write_text(json.dumps(comments, ensure_ascii=False, indent=2), "utf-8")
    return posts, pages, comments


def candidate_image_urls(src: str) -> list[str]:
    """Return ordered download candidates (full-res WP first, then exact URL)."""
    src = html.unescape(src).strip()
    if src.startswith("//"):
        src = "https:" + src
    candidates: list[str] = []

    parsed = urllib.parse.urlparse(src)
    host = parsed.netloc.lower()
    if any(h in host for h in ("wordpress.com", "wp.com", "aozhang.blog")):
        qs = urllib.parse.parse_qs(parsed.query)
        for drop in ("w", "h", "resize", "fit", "ssl"):
            qs.pop(drop, None)
        clean_query = urllib.parse.urlencode(qs, doseq=True)
        stripped = urllib.parse.urlunparse(parsed._replace(scheme="https", query=clean_query))
        candidates.append(stripped)
        if "aozhang.blog" in host:
            wp_alt = urllib.parse.urlunparse(
                parsed._replace(scheme="https", netloc=SITE_HOST, query=clean_query)
            )
            candidates.append(wp_alt)

    if src not in candidates:
        candidates.append(src)
    return candidates


def download_and_convert_image(src: str, dest_base: Path) -> tuple[str | None, str | None]:
    """Download image URL and convert to EXIF-corrected WebP (max width 1600px).

    Returns (filename_written, error_msg).
    """
    last_err = None
    raw_bytes = None
    for url in candidate_image_urls(src):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=25) as resp:
                raw_bytes = resp.read()
            if raw_bytes:
                break
        except Exception as exc:  # noqa: BLE001
            last_err = f"{url}: {exc}"

    if not raw_bytes:
        return None, last_err or "empty response"

    try:
        with Image.open(io.BytesIO(raw_bytes)) as im:
            if getattr(im, "is_animated", False) and im.format == "GIF":
                out_name = f"{dest_base.name}.gif"
                (dest_base.parent / out_name).write_bytes(raw_bytes)
                return out_name, None

            im = ImageOps.exif_transpose(im)
            im.thumbnail((1280, 1280), Image.Resampling.LANCZOS)

            if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
                im = im.convert("RGBA")
            elif im.mode != "RGB":
                im = im.convert("RGB")

            out_name = f"{dest_base.name}.webp"
            im.save(dest_base.parent / out_name, format="WEBP", quality=75, method=6)
            return out_name, None
    except Exception as exc:  # noqa: BLE001
        return None, f"PIL decode error ({src}): {exc}"


class BlogMarkdownConverter(MarkdownConverter):
    def convert_pre(self, el: Tag, text: str, parent_tags: set[str]) -> str:
        # Preserve already-tokenized blocks untouched
        if text.strip().startswith("@@TOKEN_"):
            return f"\n\n{text.strip()}\n\n"
        return super().convert_pre(el, text, parent_tags)


def extract_youtube_id(src: str) -> str | None:
    m = re.search(r"(?:youtube\.com/embed/|youtu\.be/|youtube\.com/watch\?v=)([A-Za-z0-9_-]{11})", src)
    return m.group(1) if m else None


def safe_shortcode_attr(val: str) -> str:
    cleaned = re.sub(r"\s+", " ", val).strip()
    return cleaned.replace('"', "&quot;")


def convert_html_body(
    raw_html: str,
    bundle_dir: Path | None,
    img_jobs: list[tuple[str, Path, list[dict]]],
) -> tuple[str, list[dict]]:
    """Convert WordPress HTML into clean Hugo Markdown + queued image records."""
    soup = BeautifulSoup(raw_html or "", "html.parser")

    # Strip WordPress sharing / flair widgets
    for sel in ("div.sharedaddy", "div#jp-post-flair", "div.jp-relatedposts"):
        for node in soup.select(sel):
            node.decompose()

    tokens: dict[str, str] = {}
    token_counter = 0

    def next_token(replacement: str) -> str:
        nonlocal token_counter
        token_counter += 1
        tok = f"@@HUGOTOKEN{token_counter}@@"
        tokens[tok] = replacement
        return tok

    # 1. Handle <pre> code blocks (SyntaxHighlighter brush classes or <pre><code>)
    for pre in soup.find_all("pre"):
        classes = " ".join(pre.get("class", []))
        lang = ""
        m = re.search(r"brush:\s*([A-Za-z0-9_+#-]+)", classes)
        if m:
            lang = m.group(1).lower()
        else:
            code_child = pre.find("code")
            if code_child:
                c_cls = " ".join(code_child.get("class", []))
                m2 = re.search(r"(?:language|lang)-([A-Za-z0-9_+#-]+)", c_cls)
                if m2:
                    lang = m2.group(1).lower()
        code_text = pre.get_text().strip("\r\n")
        fence = "````" if "```" in code_text else "```"
        tok = next_token(f"\n\n{fence}{lang}\n{code_text}\n{fence}\n\n")
        pre.replace_with(NavigableString(tok))

    # 2. Handle <iframe> embeds (YouTube -> shortcode, VideoPress/others -> clean iframe)
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src", "")
        yt_id = extract_youtube_id(src)
        if yt_id:
            tok = next_token(f"\n\n{{{{< youtube {yt_id} >}}}}\n\n")
        else:
            clean_src = html.unescape(src)
            title = html.escape(iframe.get("title", "Embedded video"), quote=True)
            tok = next_token(
                f'\n\n<div class="embed-container"><iframe src="{clean_src}" '
                f'title="{title}" loading="lazy" allowfullscreen '
                f'style="width:100%;aspect-ratio:16/9;border:0;"></iframe></div>\n\n'
            )
        # Replace enclosing embed figure/div if this iframe was its sole media content
        parent_fig = iframe.find_parent("figure", class_=re.compile(r"wp-block-embed"))
        if parent_fig:
            parent_fig.replace_with(NavigableString(tok))
        else:
            iframe.replace_with(NavigableString(tok))

    # 3. Unwrap outer gallery <figure class="wp-block-gallery"> so inner figures process individually
    for gallery in soup.find_all("figure", class_=re.compile(r"wp-block-gallery")):
        gallery.unwrap()

    # 4. Handle leaf <figure> containing <img> and standalone <img> tags
    post_images: list[dict] = []

    def queue_image(src: str, alt: str, caption: str) -> str:
        idx = len(post_images) + 1
        base_stem = f"img-{idx:02d}"
        tok_id = f"@@IMGTOKEN{len(tokens) + 1}@@"
        rec = {
            "token": tok_id,
            "src": src,
            "alt": alt.strip(),
            "caption": caption.strip(),
            "filename": None,
            "error": None,
        }
        post_images.append(rec)
        tokens[tok_id] = ""  # resolved after downloads complete
        if bundle_dir is not None:
            img_jobs.append((src, bundle_dir / base_stem, [rec]))
        return tok_id

    for fig in soup.find_all("figure"):
        if fig.find("figure"):
            continue
        img = fig.find("img")
        if not img or not img.get("src"):
            continue
        cap_el = fig.find("figcaption")
        caption = cap_el.get_text(" ", strip=True) if cap_el else ""
        alt = img.get("alt", "") or caption
        tok = queue_image(img["src"], alt, caption)
        fig.replace_with(NavigableString(f"\n\n{tok}\n\n"))

    for img in soup.find_all("img"):
        src = img.get("src")
        if not src:
            img.decompose()
            continue
        alt = img.get("alt", "")
        tok = queue_image(src, alt, "")
        img.replace_with(NavigableString(f"\n\n{tok}\n\n"))

    # Remove empty <p> tags
    for p_tag in soup.find_all("p"):
        if not p_tag.get_text(strip=True) and not p_tag.find():
            p_tag.decompose()

    md = BlogMarkdownConverter(heading_style="ATX", bullets="-", escape_asterisks=False, escape_underscores=False).convert_soup(soup)
    # Restore non-image tokens immediately; image tokens are kept in md for post-download substitution
    for tok, rep in tokens.items():
        if not tok.startswith("@@IMGTOKEN"):
            md = md.replace(tok, rep)

    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    return md, post_images


def detect_lang(title: str, md_text: str) -> str:
    zh_chars = len(re.findall(r"[\u4e00-\u9fff]", title + md_text))
    en_words = len(re.findall(r"\b[A-Za-z]{2,}\b", title + md_text))
    return "zh" if zh_chars > en_words else "en"


def sanitize_slug(raw_slug: str, post_id: int) -> str:
    decoded = urllib.parse.unquote(raw_slug or "").strip()
    decoded = decoded.replace("/", "-").replace("\\", "-").strip("-")
    return decoded or f"post-{post_id}"


def render_image_markdown(rec: dict) -> str:
    if rec["filename"]:
        fn = rec["filename"]
        if rec["caption"]:
            cap = safe_shortcode_attr(rec["caption"])
            return f'{{{{< figure src="{fn}" caption="{cap}" align="center" >}}}}'
        alt = rec["alt"].replace("[", "").replace("]", "").replace("\n", " ").strip()
        return f"![{alt}]({fn})"
    # Fallback to original external URL if download failed
    alt = (rec["alt"] or rec["caption"]).replace("[", "").replace("]", "").replace("\n", " ").strip()
    return f"![{alt}]({rec['src']})"


def write_markdown_with_frontmatter(path: Path, fm: dict, body: str) -> None:
    yaml_str = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, default_flow_style=False).strip()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{yaml_str}\n---\n\n{body.lstrip()}", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Re-fetch WP API ignoring migration_cache")
    args = parser.parse_args()

    posts, pages, comments = load_or_fetch_all(refresh=args.refresh)
    print(f"Loaded {len(posts)} posts, {len(pages)} pages, {len(comments)} comments.")

    # Clean content/posts and content/contact.md while keeping archives.md and search.md
    if POSTS_DIR.exists():
        shutil.rmtree(POSTS_DIR)
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    contact_path = CONTENT_DIR / "contact.md"
    if contact_path.exists():
        contact_path.unlink()

    staging_dir = CACHE_DIR / "staging_bundles"
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    prepared_posts: list[dict] = []
    # Deduplicate downloads by exact candidate key (url -> bytes/converted cache inside a temp dir per unique src)
    download_tasks: list[tuple[str, Path, dict]] = []

    for p in posts:
        pid = p["ID"]
        title = html.unescape(p.get("title") or "").strip()
        date_str = p.get("date", "")
        yyyy, mm, dd = date_str[:4], date_str[5:7], date_str[8:10]
        date_prefix = f"{yyyy}-{mm}-{dd}"
        slug = sanitize_slug(p.get("slug", ""), pid)

        bundle_tmp = staging_dir / f"{date_prefix}-{slug}"
        bundle_tmp.mkdir(parents=True, exist_ok=True)

        img_jobs: list[tuple[str, Path, list[dict]]] = []
        body_md, post_images = convert_html_body(p.get("content", ""), bundle_tmp, img_jobs)
        for src, dest_base, recs in img_jobs:
            download_tasks.append((src, dest_base, recs[0]))

        cats = [html.unescape(c) for c in (p.get("categories") or {}).keys()]
        tags = [html.unescape(t) for t in (p.get("tags") or {}).keys()]
        lang = detect_lang(title, body_md)

        fm = {
            "title": title,
            "date": date_str,
            "slug": slug,
            "aliases": [f"/{yyyy}/{mm}/{dd}/{slug}/"],
            "categories": cats,
            "tags": tags,
            "lang": lang,
            "draft": False,
            "comments": True,
            "wp_id": pid,
        }
        prepared_posts.append(
            {
                "pid": pid,
                "date_prefix": date_prefix,
                "slug": slug,
                "fm": fm,
                "body_md": body_md,
                "images": post_images,
                "tmp_dir": bundle_tmp,
            }
        )

    print(f"Downloading & converting {len(download_tasks)} post images to WebP...")
    t0 = time.time()
    failed_imgs: list[tuple[str, str]] = []

    def _worker(task: tuple[str, Path, dict]) -> None:
        src, dest_base, rec = task
        fn, err = download_and_convert_image(src, dest_base)
        rec["filename"] = fn
        rec["error"] = err

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(_worker, download_tasks))

    ok_imgs = 0
    for _, _, rec in download_tasks:
        if rec["filename"]:
            ok_imgs += 1
        else:
            failed_imgs.append((rec["src"], rec["error"] or "unknown"))

    print(f"Image conversion done in {time.time() - t0:.1f}s: {ok_imgs} OK, {len(failed_imgs)} failed.")
    for src, err in failed_imgs[:20]:
        print(f"  FAILED IMG: {src} -> {err}")

    # Materialize posts (leaf bundle if >=1 local image, single .md otherwise)
    total_img_bytes = 0
    pid_to_permalink: dict[int, str] = {}
    bundle_count = 0
    single_count = 0

    for item in prepared_posts:
        pid_to_permalink[item["pid"]] = f"/posts/{item['slug']}/"
        body = item["body_md"]
        local_imgs = [r for r in item["images"] if r["filename"]]
        for rec in item["images"]:
            body = body.replace(rec["token"], render_image_markdown(rec))
        body = re.sub(r"\n{3,}", "\n\n", body).strip() + "\n"

        stem = f"{item['date_prefix']}-{item['slug']}"
        if local_imgs:
            bundle_count += 1
            out_dir = POSTS_DIR / stem
            out_dir.mkdir(parents=True, exist_ok=True)
            for rec in local_imgs:
                src_file = item["tmp_dir"] / rec["filename"]
                dst_file = out_dir / rec["filename"]
                shutil.copy2(src_file, dst_file)
                total_img_bytes += dst_file.stat().st_size
            write_markdown_with_frontmatter(out_dir / "index.md", item["fm"], body)
        else:
            single_count += 1
            write_markdown_with_frontmatter(POSTS_DIR / f"{stem}.md", item["fm"], body)

    # Migrate Contact page (and any other WP pages)
    pages_written = 0
    for pg in pages:
        pg_slug = sanitize_slug(pg.get("slug", ""), pg["ID"])
        pg_title = html.unescape(pg.get("title") or "").strip()
        pg_body, _ = convert_html_body(pg.get("content", ""), None, [])
        pg_fm = {
            "title": pg_title,
            "date": pg.get("date", ""),
            "url": f"/{pg_slug}/",
            "comments": False,
            "ShowReadingTime": False,
            "ShowWordCount": False,
            "ShowToc": False,
        }
        write_markdown_with_frontmatter(CONTENT_DIR / f"{pg_slug}.md", pg_fm, pg_body)
        pages_written += 1

    # Export historical WP comments to Waline JSON import format (kept in gitignored migration_cache)
    waline_comments = []
    for idx, c in enumerate(comments, start=1):
        post_id = (c.get("post") or {}).get("ID")
        url_path = pid_to_permalink.get(post_id)
        if not url_path:
            continue
        author = c.get("author") or {}
        raw_txt = c.get("raw_content") or BeautifulSoup(c.get("content") or "", "html.parser").get_text("\n", strip=True)
        waline_comments.append(
            {
                "objectId": f"wp-comment-{c.get('ID', idx)}",
                "comment": raw_txt.strip(),
                "insertedAt": c.get("date", ""),
                "createdAt": c.get("date", ""),
                "updatedAt": c.get("date", ""),
                "nick": html.unescape(author.get("name") or "Anonymous"),
                "mail": author.get("email") or "",
                "link": author.get("URL") or "",
                "url": url_path,
                "status": "approved",
                "type": "comment",
                "pid": None,
                "rid": None,
                "ua": "",
                "ip": "",
            }
        )

    waline_export = {
        "type": "waline",
        "version": 1,
        "time": int(time.time() * 1000),
        "tables": ["Comment"],
        "data": {
            "Comment": waline_comments,
        },
    }
    (CACHE_DIR / "waline-import.json").write_text(
        json.dumps(waline_export, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    shutil.rmtree(staging_dir, ignore_errors=True)

    print("\n=== MIGRATION SUMMARY ===")
    print(f"Posts written: {len(prepared_posts)} ({bundle_count} bundles w/ images, {single_count} markdown files)")
    print(f"Pages written: {pages_written}")
    print(f"Local images:  {ok_imgs} converted ({total_img_bytes / (1024 * 1024):.2f} MB total)")
    print(f"Failed images: {len(failed_imgs)}")
    print(f"Waline export: {len(waline_comments)} comments -> {CACHE_DIR / 'waline-import.json'}")


if __name__ == "__main__":
    main()

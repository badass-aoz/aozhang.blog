# 野文 · Follow the Skyline (`aozhang.blog`)

Personal bilingual (Chinese & English) blog built with **Hugo** (`v0.170.1` extended) + **PaperMod**, **Waline** comments, and **Cloudflare Pages**.

## Local Development

```bash
hugo server -D
```

Production build check:

```bash
hugo --gc --minify
```

## Deploy to Cloudflare Pages (Free, Zero Ads)

1. In **Cloudflare Dashboard → Workers & Pages → Create → Pages → Connect to Git**, select `badass-aoz/aozhang.blog` (`main` branch).
2. Configure build settings:
   - **Framework preset**: Hugo
   - **Build command**: `hugo --gc --minify`
   - **Build output directory**: `public`
   - **Environment variables**: `HUGO_VERSION` = `0.170.1`
3. Attach custom domains `aozhang.blog` and `www.aozhang.blog` under **Custom domains**.

## Domain Transfer (`aozhang.blog`)

`aozhang.blog` is currently registered at Automattic / WordPress.com. To eliminate WordPress hosting fees:
1. Add `aozhang.blog` as a site on Cloudflare (Free plan) and verify DNS records point to Cloudflare Pages.
2. Unlock `aozhang.blog` in WordPress.com Domains and obtain the EPP/authorization transfer code.
3. Transfer the domain to **Cloudflare Registrar** (at-cost wholesale `.blog` renewal, ~$20.20/yr).

## Waline Comments Setup (No-Login Guest + Anti-Spam)

`layouts/_partials/comments.html` automatically enables Waline v3 once `params.waline.serverURL` in `hugo.toml` is non-empty.

1. Create a free PostgreSQL database on **Neon** (or **Supabase**).
2. Deploy Waline Server to **Vercel** (1-click deploy from `walinejs/waline`) using the Postgres `DATABASE_URL` and environment variables from Waline's guide (`PG_HOST`, `PG_DB`, `PG_USER`, `PG_PASSWORD`, `PG_PORT`).
3. Create a free **Cloudflare Turnstile** widget for `aozhang.blog` and set `TURNSTILE_KEY` / `TURNSTILE_SECRET` (optional `AKISMET_KEY` or `COMMENT_AUDIT=true` for pre-moderation).
4. Update `hugo.toml`:
   ```toml
   [params.waline]
     serverURL = 'https://comments.aozhang.blog' # or your *.vercel.app URL
     turnstileKey = 'your-turnstile-site-key'
   ```
5. Register the admin account at `<serverURL>/ui/register` and import historical WordPress comments from `migration_cache/waline-import.json` (stored locally, gitignored) via the Waline Admin **Import** button.

---
title: The Demise of a Unicorn
date: '2025-03-08T23:11:47-08:00'
slug: the-demise-of-a-unicorn
aliases:
- /2025/03/08/the-demise-of-a-unicorn/
categories:
- Occupation | 营营
tags:
- business
- entrepreneurship
- leadership
- startups
- technology
lang: en
draft: false
comments: true
wp_id: 2083
---

It’s heartbreaking to see a successful company falling apart as fast as Lacework (shortened to LW in this article).

In this blog, I’ll analyze the demise from the following aspects:

- Reasons for the downfall
- Early warning signs (aka “what could have told me as a new hire that this would be an issue”)
- What I could have done to stop the downfall
- If the answer is no, what were early signals of a downfall

Note, *The Information* has an excellent report on Lacework’s fire sale. Unfortunately, it’s behind a hefty subscription wall.

I will shamelessly take all the unfair advantage of doing a retrospective. Even though something may appear apparent at this moment, it can be unfair to blame anyone involved in the decision-making back then. As for myself, despite having a senior role in the company, I was also busier worrying about launching a new product feature than any strategic decision for the company. After all, the intention of this post is to meditate over failures so we can build a brighter future.

I will also admit that I was not in the high-level decision-making loop for the company, so I can only speak from my perspective. If at any moment I make incorrect assumptions or was blissfully ignorant of the constraints in the decision-making process, I apologize.

With those disclaimers out of the way, let’s investigate.

## The History

Lacework was founded in 2015 by Sanjay Kalra and Vikram Kapoor. The company’s early years saw steady development of its cloud security platform under their leadership, with the platform officially launching in 2017.

A significant leadership change occurred in February 2019 when Dan Hubbard, previously the company’s Chief Product Officer, took over as CEO. Under Hubbard’s leadership, the company secured a Series C funding round of $525 million in January 2021.

In July 2021, Jay Parikh, former Facebook VP of Engineering, joined as Co-CEO alongside Dan Hubbard. This was followed by a massive Series D funding round of $1.3 billion in November 2021, valuing the company at $8.3 billion.

The leadership structure changed again in February 2022 when Jay Parikh became the sole CEO, with Dan Hubbard transitioning to an advisory role. Under Parikh’s leadership, the company continued its expansion while bringing in several former Meta (Facebook) executives to key positions through 2022 and early 2023.

## The Story

I quit Meta to join Lacework in July 2023. From an outsider’s perspective, this seemed like a very promising company in a hot market. It had a solid financial runway and had the strong prospect of an IPO. I also had a few ex-Meta colleagues there and I’d love to work with those colleagues again in a new setting.

This was my first *startup* experience. Yes, some semantic snobs will dismiss this since Lacework was founded 7 years ago and already had 800 employees, rather than those typical “4 college drop-outs sleeping in the garage and working 24/7 to launch new features” that people tend to see in movies.

In May 2024, rumors began floating around about a potential acquisition of Lacework for $200M. Given Lacework [raised $1.3B with a valuation at $8.3B in late 2021](https://www.lacework.com/press-release/lacework-closes-seriesd-funding-round), this came as a heavy blow to the company’s prospects. It was made worse by the fact that the acquirer was Lacework’s main competitor, Wiz. The acquisition eventually fell through due to “due diligence” issues. As would naturally happen, more companies followed suit given how cheaply the company was selling (200M for a company with ARR around 90M seemed like a steal), and after weeks of internal unrest, things were finalized. Fortinet acquired us for $200M-$230M. Layoffs and reorganization ensued.

It’s not pretty. Not pretty at all.

How did we get here? Here are my theories and analyses of other perspectives.

## The Numbers

Lacework was valued at $8.3B USD in 2021 during its series D funding. In 2023, its ARR (annual recurring revenue) was approaching $100M, which was a shrinkage from its 2022 ARR. Meanwhile, the company had gone through a few rounds of layoffs starting from early 2023. The total number of employees went from around 900 in early 2023 to less than 600 pre-acquisition. The engineering department had fewer than 200 people.

Since I don’t have internal valuation figures, I’ll use public numbers to make rough calculations. Given that 2023 and 2024 were tough years for everyone in tech, and Lacework’s close to $90M ARR was a result of shrinkage from the previous year, let’s use $100M as the rough estimate for Lacework in 2021. We’re looking at an 80x multiplier, which is a decent number for a SaaS company in 2021. However, I believe the expectation was for the ARR to grow steadily over the years, but Lacework’s growth stagnated in 2023 and 2024. Why?

## External Factors of Growth Stagnation

There are both external and internal factors. The biggest external factor was the macroeconomic environment, when the U.S. was in a stagflation state. This had several implications:

- Small-Medium Businesses (SMBs) had less chance of survival than enterprises
- Security, as a traditional cost center, is usually the first to be cut during cost-reduction efforts

Lacework positioned itself to target SMBs initially (by its definition, SMBs are businesses with fewer than 1,000 employees, whereas enterprises are larger). In 2023, many of Lacework’s customers churned because those companies themselves were culled in the economic downturn. In contrast, Lacework’s competitor Wiz started by targeting enterprises and fared better as a result. Lacework tried to turn the tide by becoming enterprise-ready and competed head-to-head with Wiz to secure contracts with major Wall Street firms. Lacework did manage to get a Fortune 500 company to use its product. Unfortunately, these initiatives ultimately failed. I believe there are several reasons, but it boils down to real user value, which I’ll discuss later.

Security *is* a cost center. As a security professional, I advocate for security being an enabler for better product experience. However, growing more pessimistic over the year, I’m agreeing that businesses often cut security costs first when things are going badly. After all, security typically costs money without generating revenue, and when you’re struggling to meet basic needs, security becomes a lower priority. This is the tragedy of the industry.

With these observations combined, here’s my perspective: Security vendors for SMB startups operate in a risky space. When a business is just starting, they need to prove their value first. If there’s no value, there’s little security risk because most attackers won’t bother. Meanwhile, SMBs are less stable than enterprises, so when they’re struggling financially, security spending is often cut first.

## Value, Vision, Strategy, and Prioritization

Before analyzing internal factors of the growth stagnation, let me share an anecdote: I enjoy chatting with folks in the sales department, and one day I spoke with a director in a field bridging sales and engineering. After pleasantries, he opened our login portal and pulled up Chrome’s developer console.

Fourteen distinct JavaScript errors appeared.

Then he stared at me, “Why?”

To my deepest shame, I didn’t have an answer beyond, “I didn’t work on those pieces.”

Seriously? What’s wrong with me? What’s wrong with the company?

I challenge you to set aside your mundane work and ask yourself two questions:

- What is the **value** your product/service should provide?
- Does it actually provide it?

I was guilty of not asking those questions often enough, and I think most of us at Lacework weren’t either. As another anecdote, I once talked with engineering leaders within the security department (I was a software engineer and didn’t directly use our products except for testing purposes) about their feedback on our products. They couldn’t provide any because some of the landing pages took more than 30 seconds to load.

If we can’t properly use our own product, why would we expect others to?

Underlying the end value we provide, I believe there was a lack of consistent vision for the company. Lacework’s stated vision was to be *the* security company for the cloud. I was once inspired by this vision, but later found myself questioning it.

What did this vision actually mean? How would we achieve it?

We didn’t have good answers for these questions. As a result, we didn’t properly prioritize projects. Once I read a company-wide priorities document and found around 55 projects that were considered priorities. Note that these were only priorities for the engineering departments.

## Infrastructure Thrived While Frontend Suffered

This issue relates to the previous point about misplaced priorities. We paid too much attention to infrastructure while neglecting the basics of frontend development. There were places in the frontend with numbers that simply didn’t match up. Of course, engineers could always find explanations for these discrepancies, but each instance eroded customer trust.

The frontend issues weren’t limited to inconsistent numbers. Basic performance problems, confusing navigation, and error-prone interfaces plagued the user experience. While infrastructure teams were building sophisticated systems that could scale to theoretical limits far beyond our actual customer needs, users struggled with the fundamentals of actually using our product.

## “Big-Corp Syndrome”

This is a common sentiment shared by LW employees who weren’t previously Meta employees (aka “Metamates”). To put it simply, people thought that Metamates approached problems in a Meta-centric way. The complaints generally fell into these categories:

- All the big corporate bureaucracies with none of the startup agility
- Too much talking and planning with too little coding and shipping
- Expert knowledge in Meta infrastructure but poor familiarity with industry standards
  - For example, K8S + AWS + 3rd party configuration management, etc., as opposed to Meta’s proprietary containerization solutions
- Over-fixation on scaling systems that didn’t need to scale yet
- Focus on inflated titles and compensation rather than willingness to do the necessary work
- Experience in running large teams at big companies versus the skills needed in a startup environment

While I agree that many of these points hold true to some extent, I dislike when the argument inevitably degrades into an “us versus them” comparison. I am not in a leadership role at LW (though interestingly, despite being an individual contributor at LW and an engineering manager at Meta, I felt I had more leverage at LW), so while there could be some bias, I’ll try to maintain objectivity.

I agree that Meta executives tend to emphasize scaling concerns (given this infrastructure, how do we support more users/QPS/etc.), so LW ended up investing heavily in building infrastructure (data systems in particular). This approach was somewhat ironic, given that LW started by targeting SMBs. When 99% of the customer base consisted of SMBs, it didn’t make sense to spin up numerous side projects for the data system optimized for enterprise-scale throughput.

## Being in the Right Market

I don’t think we were in the wrong market—just look at Wiz’s success in the same space.

The question is whether our product execution matched market needs. In Facebook’s early days, users were willing to overlook UX issues because the core value proposition was so compelling. But in the security space, especially for tools aimed at technical users, UX is crucial.

User experience is one of the hardest parts of security products. As noted in [this analysis of Wiz Code](https://pulse.latio.tech/p/what-do-i-think-about-wiz-code), security tools need to prioritize UX to gain adoption. Getting a product into a good place initially is often better than iterating and shipping incomplete features.

## Half-Baked Products

“Let’s ship A. Quick, work on B now!”

Lacework became skilled at shipping half-baked products. While this is a common approach in startups, I think we got the priorities wrong. In my experience, engineering work is usually generated from three sources:

1. What prospective customers want: “If we don’t ship this, we won’t get a chance to talk with this customer”
2. What existing customers complain about: “Your pipeline is broken. Fix your product or I’ll take my business elsewhere”
3. What engineering/product managers think we need: While many of these ideas come from #1 and #2, engineers and product managers often proactively identify features they believe are important

The prioritization challenge is determining which should come first.

I believe #2 should take highest priority. Existing customers are who a company makes money from. Their requests should come first.

Category #3 represents the classic Steve Jobs approach: “People don’t know what they want until you show it to them.” While this philosophy is controversial, it wasn’t a significant issue for Lacework.

Instead, #1 caused the biggest problems. “Implement feature X or customer A will walk away,” a sales person would say. What followed in the engineering organization was often chaos and reprioritization. I’ve seen people abandon their current tasks to pursue the new shiny object.

This differs from my experience at Meta, which took the opposite extreme. People planned their work at the beginning of a cycle and rigidly stuck to it. Team members were reluctant to help with new projects that emerged, fearing it would disrupt their plans and affect their performance reviews.

Neither approach is ideal. There are two better ways to handle this:

1. Empower engineers to make judgment calls and push back on sales: “I’m sorry, but I’m busy shipping this product. Can we discuss that new feature for the prospective customer later?”
2. Build a process that helps engineers with prioritization, such as simple heuristics or having product managers filter requests

Another reason for our half-baked products was our constant rush. We were eager to capture the next big opportunity without letting things settle. Why were we in such a hurry? Why couldn’t we slow down and ensure quality before moving to the next project?

While this approach might seem inappropriate for a startup, for a company with eroding customer trust, slowing down becomes essential.

## Prioritization Challenges

Remember the 50+ project list that’s company-level priorities?

I believe we could have done better.

I’ve seen mismatched prioritization in large corporations, where a small project (taking 1-2 weeks) sits alongside a massive project (taking 6 months) on the same priority list. I saw the same issue at Lacework. The most effective way to prioritize should be to identify what the business needs and what engineering needs, then align these priorities. It doesn’t help when projects are proposed by individual engineers without a central vision guiding the company’s efforts.

## The Enterprise Pivot

Why did we move upmarket so quickly, from SMBs to suddenly targeting Fortune 500 enterprise customers? I understand this might have been necessary—Lacework couldn’t make enough money from non-churning SMBs, so it needed to find other revenue sources—but should we have instead doubled down on our SMB expertise?

I got the sense that sales expended significant energy competing against Wiz among Wall Street buyers, and we ultimately lost these battles. In retrospect, I’d argue it might have been more cost-effective to strengthen our position in the SMB market and gradually move upmarket.

Shouldn’t we first learn how to walk before we run?

Additional observations:

1. **Cost model**: There were complaints that we lacked a unified cost model for customers. Customers didn’t have a clear understanding of our pricing structure.
2. **The actual value**: How many people were using Lacework internally? Was our own security engineering team using it? Did we find value in our own product? I divide security offerings into two main categories, and unfortunately, I don’t think Lacework excelled at either:
   - Tools that discover security vulnerabilities: whether memory corruption, CVEs, or misconfigurations in your infrastructure. These should accurately identify security issues so developers can fix them.
   - Tools for compliance: these help meet regulatory requirements. They should run quickly, be accurate, and give definitive answers about whether you can check compliance boxes.

## Lessons for New Hires

I’ve spoken with colleagues, including those higher in the reporting chain, about issues like:

- Murky and shrinking ARR
- The need for backend engineers to understand products, regardless of whether they’re directly working on product features

I’ll also be honest that I followed the herd, as former Meta employees flocked to this company, especially during the rounds of layoffs happening at Meta.

The layoffs at Lacework in early 2023 were described as “preemptive,” so they didn’t raise too much concern from me initially. In retrospect, this was an early warning sign.

Recently, it turned out a Meta colleague of mine interviewed with LW a few years ago, but decided to back off because they believed LW wasn’t willing to invest in security research. I asked how they were able to tell, they said with a wise smirk:

“You ask a lot of questions during interviews.”

## Conclusion

The story of Lacework’s downfall contains valuable lessons for both employees and companies. What began as an $8.3 billion unicorn ended as a $200 million acquisition—a stark reminder that even well-funded companies can falter without proper execution and focus.

For those considering joining startups, especially those experiencing rapid growth and leadership changes, look beyond the funding numbers and valuation. Examine the product’s actual value to customers, internal usage of the product, and whether the company’s vision translates into coherent execution.

For companies scaling quickly, remember that infrastructure scalability means little if the core product experience doesn’t delight users. Sometimes slowing down to get the fundamentals right is more valuable than racing to the next feature or market segment.

I also wrote a short satirical verse in Chinese:

> 树倒猢狲散，我亦乐摆烂。
>
> 前路阻而长，不妨听我言。
>
> 产品偏后端，前端不能看；
>
> 坐标既中小，妄想几百万；
>
> 疫情复加息，客户死大半；
>
> 急功近利赶，未完先上线。
>
> ARR凄惨，IPO扯淡，
>
> Wiz起波澜，后有Fortinet。
>
> 昔日独角兽，今为人笑谈。
>
> 莫作冯唐叹，莞尔听猫眠。

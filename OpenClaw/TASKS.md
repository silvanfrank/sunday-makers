# 🦞 OpenClaw Tasks

> **Scheduling:** `Schedule a task to [ACTION] on a [FREQUENCY] basis and update me via Telegram.`

---

## Brand Context

**Identity:** The Honest Engineer — we build systems, not sell dreams.

**Mission:** Help people reach financial goals by providing good advice and uncovering the bad.

**The Villain:** The Financial Industrial Complex (Complexity, Opacity, Activity).

**The Campbell Test:** Everything must be **Simple, Cheap, Safe, Easy**.

**Voice:**
- Mistake-First (identify the trap before the solution)
- Radical Simplicity (Grade 5 reading level)
- Punch Up (attack the industry, protect the user)
- Counter-Intuitive Truths (data that *is* right > stories that *feel* right)

**3 Modes:**
| Mode | Vibe | Use When | Emotion |
|------|------|----------|---------|
| **Liberator** | Aggressive, Blunt | Ads, Social, "Punching Up" | Righteous Anger |
| **Sage** | Calm, Historical | Newsletter, Education | Fear of Loss |
| **Fixer** | Functional, Defensive | Product, Onboarding | Safety/Relief |

---

## Contents

**Core**
- [Brand Context](#brand-context)
- [Active Cron Jobs](#active-cron-jobs)

**Content**
- [Discovery](#discovery) — Reddit, YouTube, Affiliate gaps
- [Ideation](#ideation) — New charts, products, features
- [Drafting](#drafting) — Lessons, articles, research
- [Review](#review) — Voice check, hooks

**Marketing**
- [YouTube](#youtube) — Scripts, welcome video
- [Meetups](#meetups) — Invites, checklist
- [Newsletter](#newsletter) — Quarterly brief, sections
- [Launches](#launches) — Product announcements
- [Email](#email) — Flow review

**Business**
- [Partners](#partners) — Outreach, tracking, stuck apps
- [Hiring](#hiring) — Messages, trial evaluation

**Operations**
- [Freelancers](#freelancer-management) — Summaries, action items
- [Proofreading](#proofreading) — Emails, newsletters
- [Dev Ops](#dev-ops) — PRs, deployments
- [Reports](#reports) — Weekly, competitors, backlog

**Technical**
- [Agents](#agents) — Improvements
- [Site Maintenance](#site-maintenance) — Sitemap, speed, data

---

## Active Cron Jobs

| Task | Schedule | Cron ID |
|------|----------|---------|
| Weekly Link Audit | Mon 09:00 UTC | `0b203ff7-ce82-4afb-8147-7ddae784baf9` |

```
Perform a full link audit of https://www.longtermtrends.com/ using the sitemap. Report broken links (404s, 500s). Ignore 403s from Investopedia/FRED. If all clear, say 'All clear'.
```

---

## Content

### Discovery

**Reddit Scout**
```
Scan top 20 posts from r/Bogleheads, r/personalfinance, r/investing, r/financialindependence (past week, >10 comments). Classify as Trap/Question/Trend. Skip "rate my portfolio". Return: Date | Topic | Type | Hook | URL
```

**YouTube Outliers**
```
Find 5 YouTube videos (last 3 months) about "wealth preservation" or "financial independence" with outlier view counts. For each: 1) Hype narrative 2) Contrarian truth 3) Blog title idea ("The Problem with X")
```

**Affiliate Gaps**
```
Review high-traffic pages (Bitcoin vs Gold, S&P 500 Returns). Identify content gaps for affiliate products. Return: Traffic Source | The Trap | Product Category | Article Idea
```

### Ideation

**New Chart Ideas**
```
Based on our existing charts (ratios, comparisons, macro indicators), suggest 5 new chart ideas.

Existing categories:
- Asset ratios: Dow/Gold, Bitcoin/Gold, Copper/Gold, Gold/Oil, Gold/Silver, Stocks/Commodities
- Comparisons: Stocks vs Bonds, Growth vs Value, Large vs Small, US vs World
- Crypto: BTC/Gold, BTC/Nasdaq, BTC/M2, ETH/BTC
- Macro: Yield Curve, Credit Spreads, M2 vs Inflation, Real Rates

Suggest: New ratios, comparisons, or indicators that would resonate with our "Survival" audience. For each: Name | Data Sources | Why It Matters | The Trap It Exposes
```

**New Product/Feature Ideas**
```
Based on our existing products (FIRE Agent, Investment Co-Pilot, Weekly Macro Report, Macro Compass), suggest 3 new product or feature ideas.

Criteria (Campbell Test):
- Simple: Easy to understand
- Cheap: Low/no cost to user
- Safe: Prevents mistakes
- Easy: Minimal decisions

For each: Name | Problem It Solves | The Trap It Prevents | MVP Scope
```

**Ratio Gap Analysis**
```
What asset ratios or comparisons are we missing? Look at what competitors track (TradingView, MacroMicro, Koyfin) vs our charts.

Suggest gaps in:
1. Commodities (ex: Lumber/Copper, Natural Gas/Oil)
2. Currencies (ex: DXY vs Gold, EUR/USD long-term)
3. Bonds (ex: TIPS vs Nominals, Corp vs Govt)
4. Alt data (ex: Shipping indices, Credit card data)

Return: Ratio | Data Source | Why Relevant | Priority
```

**Community Feature Ideas**
```
What features would make our community stickier? 

Current: Discord, Meetups, Comments, Macro Report, FIRE Agent, Co-Pilot.

Suggest features that:
1. Increase retention (keep members coming back)
2. Create network effects (members help each other)
3. Align with "Honest Engineer" brand (systems, not gurus)

For each: Feature | User Problem | How It Works | Effort (S/M/L)
```

### Drafting

**Lesson Draft** *(Mode: Sage)*
```
Write 80% lesson on: "[TOPIC]"
Structure: Hook (trap) → Pivot (industry lie) → Proof (Buffett/Bogle quote) → System
Voice: Sage mode — calm, historical, teaching. Grade 5 reading. Punch up.
Campbell Test: Solution must be Simple, Cheap, Safe, Easy.
Output: Title, 3 Takeaways, Hook, Trap, Truth, System, References
```

**Affiliate Article** *(Mode: Liberator → Fixer)*
```
Write affiliate article for: [PRODUCT]
Trap: [TRAP]
Arc:
1) Liberator hook: Emotional, expose the industry trap
2) Pivot: "But there's a boring solution..."
3) Fixer pitch: "We recommend this because it won't blow up, not because they pay the most."
Campbell Test: Product must be Simple, Cheap, Safe, Easy.
Voice: Deadpan, no hype, clear CTA.
```

**User Profile**
```
Analyze visitor to: [PAGE URL]
1. Who are they?
2. Fears/Problems/Goals?
3. What triggered this search?
4. What trap will they fall into?
5. Solution (Simple, Cheap, Safe, Easy)?
```

**Research Dossier**
```
Research: "[TOPIC]"
1. Who is this for? Fear? Aspiration?
2. The Trap (industry lie)?
3. Authority quote (Buffett/Bogle/Munger) with source URL
4. Contrarian data point
```

### Review

**Brand Voice Check**
```
Review draft:
[PASTE DRAFT]

Check against "Honest Engineer" voice:
1. Grade 5-6 reading level?
2. Forbidden words (utilize, synergy, in order to)?
3. Mistake-First structure (trap before solution)?
4. Punches Up (attacks industry, not user)?
5. Starts with punch, not context/fluff?
6. Campbell Test: Is the solution Simple, Cheap, Safe, Easy?

Return: Pass/Fail + specific fixes.
```

**Hook Generator**
```
Write 5 hooks for: "[TOPIC]"
Each: Target emotion (LOL/WTF/OMG/WOW/fear), 2 sentences max, pass "First Two Sentences Test".
```

---

## Marketing

### YouTube

**Video Script** *(Mode: [LIBERATOR/SAGE/FIXER])*
```
Write script for: "[TOPIC]"
Mode: [Choose: Liberator (aggressive) / Sage (educational) / Fixer (onboarding)]
Format: A-Roll (speaking) / B-Roll (visuals)
Structure: Hook (0-30s, state the trap) → Pivot → Reveal → CTA
Voice: Humble, anti-hype. Engineer, not guru.
```

**Welcome Video** *(Mode: Fixer)*
```
Write 2-min welcome script for new signups.
Arc: "You chose Data > Hype" → "But data alone isn't enough" → "You need a System" → "Join as Member"
Voice: Fixer mode — functional, reassuring, Safety/Relief emotion.
```

### Meetups

**Invite Draft**
```
Draft meetup invite for: "[TOPIC]" on [DATE]
Style: Morgan Housel. Start with contrarian insight → Problem → "In our next free meetup..." → Bullet details → Logistics.
```

**Pre-Flight Checklist**
```
Run meetup checklist: Zoom link? Subscribers imported? Dates correct? Test email sent? Text-to-speech proofread?
```

### Launches

**Launch Package**
```
Create launch materials for: "[PRODUCT]"
Value Prop: [DESCRIBE]

Drafts needed:
1. Internal Email (anti-hype, value-focused)
2. Hacker News (technical, humble)
3. Reddit r/Bogleheads (value-first, feedback request)
4. Product Hunt (tagline + maker comment)
5. LinkedIn (professional summary)
```

### Email

**Flow Review**
```
Review email flow for: [SEGMENT]
Goal: Unify Chart Value + Community Marketing in Brevo.
Suggest: 1) Trigger 2) 24h delayed welcome 3) Non-annoying upsell
```

### Newsletter

**Quarterly Brief Outline** *(Mode: Sage)*
```
Create outline for the Quarterly Chart Brief (Q[X] [YEAR]).

Standard sections:
1. Global Diversification (US vs World, Sectors, Growth/Value)
2. Valuations (PE, CAPE, Buffett Indicator, Concentration)
3. Sentiment (Fear & Greed, VIX, Credit Spreads)
4. Crypto (BTC, ETH, ETH/BTC ratio)
5. Gold & Commodities
6. Thematic (what's hot: Defense, AI, Energy?)
7. Macro (Fed, rates, tariffs, trade)
8. Debt & Fiscal (CBO projections, deficits)
9. Inequality & Consumer (wealth gap, delinquencies)
10. Housing (affordability, mortgage rates)
11. Geopolitics (China, Europe)
12. "What I Am Reading" (book/podcast recommendation)
13. Community Update

For each section: Key chart(s) | Main insight | The Trap/Counter-Intuitive Truth
```

**Section Draft** *(Mode: Sage)*
```
Write newsletter section on: "[TOPIC]"
Charts to reference: [LIST CHARTS]

Structure:
- Lead with the insight, not context
- Reference 2-3 specific charts with data points
- Include one authority quote (Damodaran, Dalio, Bernstein, etc.)
- End with the counter-intuitive truth

Voice: Sage mode — calm, historical, teaching. Data-first.
```

**Chart Selection**
```
For the Q[X] [YEAR] newsletter, suggest which charts to highlight.

Criteria:
1. Moved significantly (breakout, breakdown, or reversal)
2. Tells a "Counter-Intuitive Truth" story
3. Timely (relates to current news/events)

Return: Chart Name | Current Value | Change | Why It Matters Now
```

**"What I'm Reading" Suggestion**
```
Suggest 3 books or podcasts for the "What I Am Reading" section.

Criteria:
- Aligns with "Honest Engineer" brand (systems, survival, anti-hype)
- Recent or evergreen
- Ideally by an authority we cite (Damodaran, Housel, Bernstein, Bogle, Dalio)

For each: Title | Author | One-sentence pitch | Link
```

**Newsletter Proofread**
```
Proofread this newsletter draft:
[PASTE DRAFT]

Check:
1. Data points accurate? (compare to current chart values)
2. Charts linked correctly?
3. No .net references (use .com)?
4. Reading level appropriate? (Sage mode, not academic)
5. Flows logically section-to-section?
6. CTA at end (donate, subscribe, community)?

Return: Issues found + fixes.
```

---

## Business

### Partners

**Cold Outreach**
```
Draft affiliate outreach to: [COMPANY]
Context: 100k+ visitors, Tier 1 geo, research-oriented audience.
Ask: 1) CPA rates 2) Funding conditions 3) Tiered structures
Tone: Professional, data-backed.
```

**Onboarding Status**
```
Compile partner onboarding status:
| Partner | Status | Next Action | Owner | Notes |
Known partners: eToro, CMC Markets, Axi, XTB, TradingView, Revolut, IBKR, Binance, Trade Republic, Trading212
```

**Partner Email Scan**
```
Check partner emails for: 1) New campaigns we can use 2) Follow-up requests 3) Deadlines approaching
Flag anything urgent.
```

**Stuck Applications**
```
Which partner applications are stuck? Check impact.com status for: Pepperstone, Revolut, Robinhood, Trade Republic.
Suggest: Alternative contact methods or direct email outreach.
```

### Hiring

**Outreach Message**
```
Write hiring message for: [Discord/Email/YouTube/Upwork]
Points: 100k visitors, content too academic, pivoting to solutions, 50% rev share option, want "Honest Engineer" ethos.
```

**Trial Evaluation**
```
Evaluate submission:
[PASTE]
Score 1-10 on: User profile, Trap identification, Solution alignment, Writing voice.
```

---

## Technical

### Agents

**Improvement Task**
```
Suggest next task for: [AGENT NAME]
Categories: 1) Robustness 2) Latency 3) Conversational capability
Output: Task description for developer.
```

### Site Maintenance

**Sitemap Check**
```
Validate sitemap.xml: Correct domain (www)? Duplicates? All 200s?
```

**Speed Audit**
```
Check speed on top 5 pages. Flag anything >5s.
```

**Data Sources**
```
Check external data sources (FRED, Yahoo Finance). Report errors or empty data.
```

---

## Reports

**Weekly Summary**
```
Weekly summary: Top 5 pages, new community activity, trending topics to cover.
```

**Competitor Watch**
```
Check AWealthOfCommonSense, MorganHousel, OfDollarsAndData for new content. What did we miss?
```

**Page Comparison**
```
Compare our [PAGE] to top 5 competitors. Analyze:
1. Content structure
2. Visual/graphic quality
3. Affiliate integration
4. "Further reading" suggestions
5. What are we missing?

Return: Competitor | Strength | Our Gap | Priority
```

**SEO Keyword Check**
```
For topic: "[TOPIC]"
Find: 1) Head keywords (high volume) 2) Long-tail keywords (high intent) 3) Questions people ask
Suggest: Title and H2 structure optimized for these keywords.
```

**Backlog Review**
```
Review content backlog. Prioritize by: 1) Traffic alignment 2) Affiliate potential 3) Trap coverage. Return top 3.
```

---

## Freelancer Management

**Weekly Summary Request**
```
Ask [NAME] for their weekly summary. Format:
- What did you complete this week?
- What's in progress?
- What's blocked / needs my input?
- Action items for me?
```

**Compile Action Items**
```
Extract action items from this conversation:
[PASTE CONVERSATION]
Return: Who | Action | Deadline | Status
```

**Bharti Content Check**
```
Review Bharti's draft for: "[ARTICLE TITLE]"
Check: 1) Mistake-first structure? 2) Leads into "how to buy correctly"? 3) Grade 5 reading level? 4) No fluff intro?
```

---

## Proofreading

**Outreach Email Check**
```
Proofread this outreach email:
[PASTE EMAIL]
Check:
1. Company name spelled correctly?
2. Using .com (not .net)?
3. "LongtermTrends" (not "LogTerm Trends")?
4. Stats accurate? (100k+ visitors, 17% MoM, Tier 1 geo)
5. Tone: Professional, data-backed, direct?
```

**Newsletter Pre-Send**
```
Review newsletter before sending:
[PASTE DRAFT]
Check: 1) Dates correct? 2) Zoom link placeholder filled? 3) No .net references? 4) Subject line punchy? 5) Text-to-speech proofread?
```

---

## Dev Ops

**PR Status Check**
```
Check open PRs on longtermtrends2. Report:
- PR # | Title | Status | Merge conflicts? | Stale?
Flag anything >7 days old or with conflicts.
```

**Deployment Confirmation**
```
Confirm deployment status for: [FEATURE]
Checklist: 1) Merged to main? 2) Deployed to staging? 3) Tested? 4) Deployed to prod? 5) .env changes needed?
```

**Trello Card Update**
```
Based on this conversation, update the Trello card:
[PASTE CONVERSATION]
Extract: What changed? What's the new status? Any new action items?
```

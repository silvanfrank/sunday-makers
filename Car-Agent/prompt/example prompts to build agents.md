Prompt 1: Upwork Scraper

Build an end-to-end pipeline that scrapes Upwork jobs matching AI/automation keywords, generates personalized cover letters and proposals using Gemini 3 Pro, creates Google Docs for each proposal, and outputs everything to a Google Sheet with one-click apply links.

## Architecture

Follow the 3-layer DOE pattern:
1. **Directive** (`directives/upwork_scrape_apply.md`): SOP documenting inputs, execution tools, output format, edge cases, learnings
2. **Execution scripts** (`execution/`): Deterministic Python scripts that do the actual work
3. **Orchestration**: You read directives, call scripts, handle errors, update directives with learnings

## Pipeline Components

### 1. Upwork Scraper (`execution/upwork_apify_scraper.py`)

Use the `upwork-vibe~upwork-job-scraper` Apify actor (free tier, $0/event).

**Key constraints discovered:**
- Free tier only supports `limit`, `fromDate`, `toDate` filters
- All other filtering (budget, experience, verified payment, client spend) must be post-scrape
- Job URL format: `https://www.upwork.com/jobs/~{id}`
- Apply URL format: `https://www.upwork.com/nx/proposals/job/~{id}/apply/`

**CLI interface:**
```bash
python execution/upwork_apify_scraper.py \
  --limit 50 --days 1 --verified-payment \
  --min-spent 1000 --experience intermediate,expert \
  -o .tmp/upwork_jobs.json
```

### 2. Proposal Generator (`execution/upwork_proposal_generator.py`)

**LLM Strategy:**
- Use Gemini 3 Pro (`gemini-3-pro-preview`)
- Parallelize LLM calls with `ThreadPoolExecutor` (default 5 workers)

**Google Docs Strategy:**
- Serialize Doc creation with `threading.Semaphore(1)` - parallel creates cause SSL errors
- Retry with exponential backoff (1.5s, 3s, 6s, 12s) on failures
- Fall back to embedding proposal text in sheet if Doc creation fails after retries

**Cover Letter Format (must stay above the fold, ~35 words):**
```
Hi. I work with [2-4 word paraphrase] daily & just built a [2-5 word thing]. Free walkthrough: [DOC_LINK]
```

**Proposal Format (first-person, conversational, ~300 words):**
```
Hey [name if available].

I spent ~15 minutes putting this together for you. In short, it's how I would create your [2-4 word paraphrase] end to end.

I've worked with $MM companies like Anthropic (yes—that Anthropic) and I have a lot of experience designing/building similar workflows.

Here's a step-by-step, along with my reasoning at every point:

My proposed approach

[4-6 numbered steps with WHY for each, mention specific tools: n8n, Claude API, Zapier, Make, etc.]

What you'll get

[2-3 concrete deliverables]

Timeline

[Realistic estimate, conversational]
```

**CLI interface:**
```bash
python execution/upwork_proposal_generator.py \
  --input .tmp/upwork_jobs.json \
  --workers 5 \
  -o .tmp/upwork_proposals.json
```
- Omit `--sheet-id` to auto-create new Google Sheet
- Use `--sheet-id ID` to append to existing sheet

### 3. Google Sheet Output

Columns: Title, URL, Budget, Experience, Skills, Category, Client Country, Client Spent, Client Hires, Connects, Apply Link, Cover Letter, Proposal Doc

## Technical Requirements

**Dependencies:**
- `google-genai` - Gemini 3 API
- `google-auth`, `google-auth-oauthlib`, `google-api-python-client` - Google APIs
- `requests` - Apify API calls
- `python-dotenv` - Environment variables

**Environment:**
- `GEMINI_API_KEY` in `.env`
- `APIFY_API_TOKEN` in `.env`
- `token.json` with Google OAuth credentials (scopes: spreadsheets, drive, documents)
- `credentials.json` for OAuth flow

**Google OAuth Scopes:**
```python
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents'
]
```

## Autonomous Building Loop

**CRITICAL: Build, test, iterate independently until done.**

1. **Build first version** of each script with basic functionality
2. **Test immediately** with real data (small batch: 5-10 jobs)
3. **Observe failures** - API errors, rate limits, format issues
4. **Fix and enhance** - add retry logic, parallelization, fallbacks
5. **Test again** - verify fixes work
6. **Update directive** with learnings (edge cases, timing, constraints)
7. **Repeat** until pipeline runs end-to-end without intervention

**Error handling patterns discovered:**
- Apify: Poll status every 3s, timeout after 5 min
- Gemini: Parallelize with ThreadPoolExecutor, reduce workers if rate limited
- Google Docs: Serialize with semaphore + exponential backoff retry
- Always have fallback (embed proposal in sheet if Doc fails)

**Performance benchmarks:**
- 10 jobs with 5 workers: ~2 min (vs ~20 min sequential)
- Gemini 3 Pro: 5-10s per call
- Google Doc creation: 2-5s each (serialized)

## Deliverables

1. `directives/upwork_scrape_apply.md` - Complete SOP
2. `execution/upwork_apify_scraper.py` - Scraper with post-filtering
3. `execution/upwork_proposal_generator.py` - Parallel proposal generator
4. Working Google Sheet with proposals and one-click apply links

## Success Criteria

- Pipeline runs end-to-end without manual intervention
- All Google Docs created successfully (retry handles transient failures)
- Cover letters are under 35 words and include Doc links
- Proposals follow the conversational first-person format
- Sheet has all columns populated
- Directive documents all edge cases and learnings



Prompt 2: Google Maps Scraper

# Prompt: Build Google Maps Lead Generation Pipeline

Use this prompt to have an AI build the complete GMaps lead scraping + contact enrichment pipeline from scratch.

---

## The Prompt

```
Build me an end-to-end Google Maps lead generation pipeline with the following specifications:

## Goal
Scrape businesses from Google Maps, enrich each with deep contact extraction from their websites, and save to a Google Sheet that grows over time.

## Architecture Requirements

### Layer 1: Google Maps Scraping
- Use Apify's `compass/crawler-google-places` actor (I have APIFY_API_TOKEN in .env)
- Accept dynamic search queries (e.g., "plumbers in Austin TX")
- Accept a --limit parameter for number of results
- Return structured business data: name, address, phone, website, rating, reviews, place_id, google_maps_url

### Layer 2: Website Contact Extraction
For each business with a website:
1. HTTP fetch the main page (use httpx, not requests)
2. Convert HTML to markdown (use html2text library)
3. Find and fetch up to 5 additional pages matching contact patterns:
   - Priority order: /contact, /about, /team, /contact-us, /about-us, /our-team, /staff, /people, /meet-the-team, /leadership, /management, /founders, /who-we-are, /company, /meet-us, /our-story, /the-team, /employees, /directory, /locations, /offices
4. Search DuckDuckGo for `"{business name}" owner email contact` and include snippets + first relevant result page
5. Combine all content and send to Gemini 3 Pro for structured extraction

### Layer 3: Extraction Schema
Have the model extract this JSON structure:
```json
{
  "emails": ["all email addresses found"],
  "phone_numbers": ["all phone numbers found"],
  "addresses": ["physical addresses found"],
  "social_media": {
    "facebook": "url or null",
    "twitter": "url or null",
    "linkedin": "url or null",
    "instagram": "url or null",
    "youtube": "url or null",
    "tiktok": "url or null"
  },
  "owner_info": {
    "name": "owner/founder name",
    "title": "their position",
    "email": "direct email if found",
    "phone": "direct phone if found",
    "linkedin": "personal linkedin"
  },
  "team_members": [{"name", "title", "email", "phone", "linkedin"}],
  "business_hours": "operating hours",
  "additional_contacts": ["other contact methods like WhatsApp, Calendly, etc."]
}
```

### Layer 4: Google Sheets Integration
- Use gspread with OAuth credentials (credentials.json exists)
- Create sheet with headers on first run, or append to existing sheet via --sheet-url
- Implement deduplication using lead_id (MD5 hash of name|address)
- Track metadata: scraped_at, search_query, pages_scraped, search_enriched, enrichment_status

## Technical Requirements

### Error Handling
- ~10-15% of sites return 403/503 - handle gracefully, still save lead with GMaps data
- Facebook URLs always return 400 - skip them in web search results
- Some sites have broken DNS - catch and mark as error
- The model sometimes returns dicts instead of strings for fields like business_hours - use a stringify_value() helper

### Performance
- Use ThreadPoolExecutor for parallel website enrichment (default 3 workers)
- Limit contact pages to 5 max per site
- Truncate content to 1M chars before sending to Gemini
- DuckDuckGo HTML search (html.duckduckgo.com/html/) is free and doesn't block

### Output Schema (36 columns)
lead_id, scraped_at, search_query, business_name, category, address, city, state, zip_code, country, phone, website, google_maps_url, place_id, rating, review_count, price_level, emails, additional_phones, business_hours, facebook, twitter, linkedin, instagram, youtube, tiktok, owner_name, owner_title, owner_email, owner_phone, owner_linkedin, team_contacts, additional_contact_methods, pages_scraped, search_enriched, enrichment_status

## File Structure
Create these files:
- `execution/scrape_google_maps.py` - Standalone GMaps scraper
- `execution/extract_website_contacts.py` - Standalone website contact extractor
- `execution/gmaps_lead_pipeline.py` - Main orchestration script
- `directives/gmaps_lead_generation.md` - Documentation

## CLI Interface
```bash
# Basic usage
python3 execution/gmaps_lead_pipeline.py --search "plumbers in Austin TX" --limit 10

# Append to existing sheet
python3 execution/gmaps_lead_pipeline.py --search "roofers in Austin TX" --limit 50 \
  --sheet-url "https://docs.google.com/spreadsheets/d/..."
```

## Autonomous Building Loop

IMPORTANT: Build this iteratively with real testing:

1. Build the Google Maps scraper first, test with --limit 3
2. Build the website contact extractor, test on a single URL
3. Build the orchestration pipeline, test end-to-end with --limit 5
4. Fix any bugs that appear (there will be edge cases)
5. Run a full test with --limit 10 to verify everything works
6. Update the directive with learnings

Do NOT just write code and stop. Actually run it, observe errors, fix them, and iterate until you have a working pipeline that successfully:
- Scrapes businesses from Google Maps
- Enriches them with website + search data
- Extracts structured contacts via Claude
- Saves to Google Sheet with deduplication

Test with the same search query multiple times to verify deduplication works.

## Cost Targets
- Apify: ~$0.01-0.02 per business
- Gemini 3 Pro: (Check pricing)
- Everything else: Free
- Total: ~$0.015-0.025 per lead

## Success Criteria
The pipeline is complete when:
1. `python3 execution/gmaps_lead_pipeline.py --search "test query" --limit 10` runs without errors
2. 10 leads appear in the Google Sheet with populated contact fields
3. Running the same command again shows "No new leads to add (all duplicates)"
4. The directive documents all learnings and edge cases discovered

Now build it.
```

---

## Notes for Users

This prompt encodes all the learnings from building the pipeline:
- The 22 contact page URL patterns (priority ordered)
- DuckDuckGo HTML as free search fallback
- The stringify_value() helper for Claude's inconsistent output
- 403/503 error rates and handling
- Deduplication via MD5 hash
- Parallel enrichment with ThreadPoolExecutor
- The exact output schema that works with Google Sheets

The "autonomous building loop" instruction is critical - it forces the model to actually test and iterate rather than just writing code and stopping.



Prompt 3: Instantly Campaign Writer

# Prompt: Instantly Campaign Creator Workflow

Use this prompt to recreate the Instantly campaign creation workflow from scratch.

---

## The Prompt

Build a complete workflow that creates cold email campaigns in Instantly based on a client description and offers.

### Requirements

**Inputs:**
- Client name and description
- Target audience
- Social proof/credentials
- 3 offers (or auto-generate if not provided)

**Output:**
- 3 campaigns in Instantly (one per offer)
- Each campaign: 3 email steps
- First step: 2 A/B variants (meaningfully different approaches)
- Steps 2-3: 1 variant each (follow-up and breakup)

**Email structure (per the examples in `.tmp/instantly_campaign_examples/campaigns.md`):**
- Personalization hook (use `{{icebreaker}}` or custom opener)
- Social proof (credentials, results, experience)
- Offer (clear value prop, low barrier)
- Soft CTA

**Available variables:** `{{firstName}}`, `{{lastName}}`, `{{email}}`, `{{companyName}}`, `{{casualCompanyName}}`, `{{icebreaker}}`, `{{sendingAccountFirstName}}`

### Technical Constraints (Critical - Learned from API)

1. **Instantly API v2** - Use `POST https://api.instantly.ai/api/v2/campaigns` with Bearer token auth
2. **HTML formatting required** - Instantly strips ALL plain text outside HTML tags. Must wrap paragraphs in `<p>` tags, use `<br>` for line breaks within paragraphs
3. **Schedule requires `name` field** - Each schedule object needs a `name` property
4. **Timezone enum is restrictive** - Use `America/Chicago` (not `America/New_York` - it fails)
5. **Sequences array** - Only first element is used, add all steps to that one sequence
6. **Step type** - Must be `"email"` always

### Autonomous Building Loop

**You must build → test → iterate independently until complete. Do not stop at the first error.**

1. **Research first**: Check existing code in `execution/` and examples in `.tmp/`. Look up Instantly API v2 docs if needed.

2. **Create directive**: Write `directives/instantly_create_campaigns.md` with:
   - Clear inputs/outputs
   - Step-by-step process
   - Environment requirements
   - Example usage
   - Edge cases

3. **Create execution script**: Write `execution/instantly_create_campaigns.py` that:
   - Uses Gemini 3 Pro to generate campaigns from examples
   - Converts plain text to HTML (wrap paragraphs in `<p>` tags)
   - Creates campaigns via Instantly API v2
   - Handles errors gracefully
   - Supports `--dry_run` flag for testing

4. **Test with dry run**: Run with `--dry_run` first to verify generation works

5. **Test live creation**: Run without dry run, verify campaigns appear in Instantly

6. **Self-anneal on errors**: When something breaks:
   - Read the error message carefully
   - Fix the script
   - Test again
   - Update directive with learning
   - Continue until fully working

7. **Verify end-to-end**: Check that created campaigns in Instantly have:
   - Correct email bodies (not empty, not stripped)
   - Proper formatting (line breaks render correctly)
   - All 3 steps with correct variants

### Expected API Payload Structure

```json
{
  "name": "ClientName | Offer 1 - Description",
  "sequences": [{
    "steps": [
      {
        "type": "email",
        "delay": 0,
        "variants": [
          {"subject": "...", "body": "<p>...</p><p>...</p>"},
          {"subject": "...", "body": "<p>...</p><p>...</p>"}
        ]
      },
      {
        "type": "email",
        "delay": 3,
        "variants": [{"subject": "Re: ...", "body": "<p>...</p>"}]
      },
      {
        "type": "email",
        "delay": 4,
        "variants": [{"subject": "Re: ...", "body": "<p>...</p>"}]
      }
    ]
  }],
  "campaign_schedule": {
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "schedules": [{
      "name": "Weekday Schedule",
      "days": {"monday": true, "tuesday": true, "wednesday": true, "thursday": true, "friday": true},
      "timing": {"from": "09:00", "to": "17:00"},
      "timezone": "America/Chicago"
    }]
  },
  "email_gap": 10,
  "daily_limit": 50,
  "stop_on_reply": true,
  "stop_on_auto_reply": true,
  "link_tracking": true,
  "open_tracking": true
}
```

### Environment

Requires in `.env`:
```
INSTANTLY_API_KEY=your_api_v2_key
GEMINI_API_KEY=your_gemini_key
```

### Success Criteria

The workflow is complete when:
1. `--dry_run` generates 3 valid campaigns with proper HTML formatting
2. Live run creates 3 campaigns in Instantly
3. Campaigns display correctly in Instantly UI (text visible, line breaks work)
4. Directive documents all learnings and edge cases
5. Script handles missing API key gracefully (exits early, doesn't waste tokens)

**Do not notify me until all success criteria are met. Build, test, and iterate autonomously.**



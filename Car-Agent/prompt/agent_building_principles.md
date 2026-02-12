# The "Boring" Agent Building Principles

Based on the instructions for building the Upwork Scraper, Google Maps Scraper, Instantly Campaign Writer, YouTube Automation, and Investment Co-Pilot, here are the core principles for building reliable agentic workflows.

## 1. The DOE Architecture (Directive, Orchestration, Execution)
**The Core Philosophy:** LLMs are probabilistic; business logic must be deterministic.
*   **The Math:** If an LLM is 90% accurate per step, a 5-step process has only a 59% success rate ($0.90^5$).
*   **The Solution:** Push complexity into deterministic Python code. Use the LLM only for *routing* (Orchestration) and *reasoning* (Directive interpretation), not for the heavy lifting.

### The Layers
*   **Layer 1: Directive (The SOP):** Natural language instructions (Markdown) defining goal, inputs, tools, and edge cases. This is the distinct "brain" or instruction manual.
*   **Layer 2: Orchestration (The Agent):** The AI that reads the SOP and decides *what* to do. It routes inputs to the correct scripts.
*   **Layer 3: Execution (The Hands):** Deterministic Python scripts that do the actual work (API calls, scraping, file I/O). These are reliable, testable, and fast.

## 2. The Autonomous Building Loop
Do not try to build the whole system at once. Follow this strict cycle:
1.  **Check for Tools:** Before coding, check `execution/`. Re-use existing scripts if possible.
2.  **Build First Version:** Write the basic script for a single component.
3.  **Test Immediately:** Run with a small batch of real data (e.g., limit 5) or `--dry_run`.
4.  **Observe Failures:** Identify API errors, rate limits, or format issues.
5.  **Fix & Enhance:** Add retry logic, parallelization, or fallbacks.
6.  **Test Again:** Verify the fix.
7.  **Update Directive:** Document the edge case/learning in the SOP so the agent "remembers" next time.
8.  **Repeat:** Iterate until end-to-end success.

## 3. State Management Strategy
Separation of ephemeral processing and persistent value.
*   **Intermediates (.tmp/):** All temp files (dossiers, scraped JSON) live here. Never committed, always regenerated. Mounted via Docker volumes for persistence if needed.
*   **Deliverables (Cloud):** Final outputs go immediately to the Cloud (Google Sheets, Docs, Drive) where the user lives.
*   **Secrets:** Centralized in `.env`, injected at runtime. Never hardcoded.
    *   **Google Service Accounts:** Use a standardized `credentials.json` file (referenced via `GOOGLE_APPLICATION_CREDENTIALS`) for server-to-server auth.
        ```json
        {
          "type": "...",
          "project_id": "...",
          "private_key": "...",
          "client_email": "...",
          "token_uri": "..."
        }
        ```

## 4. Self-Annealing & Error Handling
Expect failure and build systems that heal themselves.
*   **Robust Retries:** Use exponential backoff for API calls.
*   **Graceful Fallbacks:** If a high-level tool fails (e.g., Doc creation), fall back to a simpler method (embed text in Sheet).
*   **Rate Limit Awareness:** Use `ThreadPoolExecutor` but throttle workers if limits are hit.
*   **Constraint Discovery:** Hardcode constraints discovered during testing (e.g., "Instantly API requires HTML tags") into the Directive.

## 5. Success Criteria Definition
Define exactly what "Done" looks like before starting.
*   "Pipeline runs end-to-end without manual intervention."
*   "API endpoints return 200 OK and trigger background tasks."
*   "Directive documents all learnings."

**Example Implementation:**
See the [Investment Co-Pilot](../Investment-Co-Pilot/README.md) for a reference implementation of these principles in action.

---

## Appendix: Optional Hosting (VPS)
Agens can run locally on your laptop or exist as 24/7 services. Hosting is **optional** but recommended for stable, ongoing tasks.

### If you choose to host:
1.  **Containerization:** Use `Dockerfile` to lock in system dependencies (e.g., `ffmpeg`, `fastapi`) so it runs the same on the server as it does locally.
2.  **Service Wrapper:** Wrap CLI scripts with `FastAPI`/`Uvicorn` to expose them as endpoints (e.g., `POST /run/simple-edit`).
3.  **Deployment:** Deploy via Docker Compose on a VPS (using tools like Coolify) with Traefik for secure HTTPS routing.
4.  **Observability:**
    *   **Health Checks:** `curl -f http://localhost:8000/health` so the server knows if the agent is alive.
    *   **Hooks:** Use Sound (local) or Slack Webhooks (cloud) to notify completion. Don't stare at a loading bar.

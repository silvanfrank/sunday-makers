# Agent Technical Improvement Roadmap

This document outlines the plan to unify, optimize, and modernize the **Investment Co-Pilot** and **FIRE Agent**. These changes can be implemented iteratively.

## Phase 1: Robustness & Unification (High Priority)
**Goal:** Ensure both agents share the best error-handling logic to minimize failures.

### 1. Unified Error Handling Strategy
*   **Context:** Currently, `FIRE-Agent` has retries (good for network blips), while `Investment Co-Pilot` has fallback logic for malformed JSON (good for LLM stupidity).
*   **Plan:**
    1.  **Extract Retry Logic:** Create a shared utility or apply the `FIRE` retry loop (3 attempts) to `Investment Co-Pilot`'s `send_message` method.
    2.  **Extract Fallback Logic:** Port the `_handle_malformed_function_call` method from `Investment-Co-Pilot/orchestrator.py` to `FIRE-Agent/orchestrator.py` to handle cases where the LLM fails to call the tool properly.
    3.  **Standardize Logging:** Ensure both agents log to `logs/` with consistent structure for easier debugging.

### 2. Dependency Cleanup
*   **Context:** `Investment Co-Pilot` uses `numpy`/`pandas` which are heavy. `FIRE-Agent` is pure Python.
*   **Plan:**
    1.  **Audit Co-Pilot Usage:** Check if `numpy`/`pandas` are strictly necessary in `financial_utils.py`.
    2.  **Remove if possible:** If usage is trivial (e.g., just calculating a mean), replace with standard `math`/`statistics` libs to reduce container size and cold-start time.

---

## Phase 2: Latency Optimization (High Impact)
**Goal:** Reduce the "Time to Result" for the user.

### 1. Implement "Optimistic Execution"
*   **Context:** Currently, agents ask "Is this correct?" before running calculations. This adds a full round-trip delay (~10-20s).
*   **Plan:**
    1.  **Update Prompt Directives:** Modify `orchestrator_directive.md` and `create_fire_plan.md`.
    2.  **New Rule:** Instruct the LLM: *"IF the user's message contains ALL required inputs, PROCEED IMMEDIATELY to calling the tool. DO NOT ask for confirmation."*
    3.  **UI Feedback:** Ensure the final output repeats the inputs used so the user can verify them post-facto (e.g., "Based on Age: 30, Income: $100k...").

### 2. Enable Response Streaming
*   **Context:** Users stare at a blank screen while the LLM generates the text explanation.
*   **Plan:**
    1.  **Backend:** Switch `google-genai` calls to `stream=True`.
    2.  **API Layer:** Update `api.py` to return `StreamingResponse` (FastAPI).
    3.  **Frontend (Chatbox JS):** Update `n8n-brandable-chatbox.js` (or equivalent) to use the Fetch API with `ReadableStream` to render text chunks as they arrive.
    4.  **Templates:** Update `investment-co-pilot.html` and `fire-agent.html` to ensure the chat initialization handles the new streaming parameter/endpoint correctly.

---

## Phase 3: Conversational Capabilities (User Experience)
**Goal:** Enable natural follow-up conversations without re-triggering the full report.

### 1. Enable Post-Generation Follow-up
*   **Context:** Currently, if a user says "Thanks" or "I agree" after a report is generated, the agent often gets confused or re-generates the entire report because it thinks it's still in the "Creation" loop.
*   **Plan:**
    1.  **Orchestrator Update:** Modify `_process_response` to inject a "system note" into the history after a tool successfully runs: *"[SYSTEM: The report has been generated. The user may now ask questions about it. Do NOT generate the report again unless the user explicitly asks to change inputs.]"*
    2.  **Directive Update:** Add a specific "Post-Report Phase" to the system instructions, teaching the agent how to answer questions about the specific report it just created (e.g., "What if I retire 2 years earlier?").
    3.  **State Management:** Ensure the `history` passed to the LLM includes the Tool Output so the LLM can "see" the report it just made.

### 2. Bengen's Optimal Portfolio Integration
*   **Context:** Users need guidance on asset allocation based on proven withdrawal rate studies (Bengen).
*   **Plan:**
    1.  **Frontend Update:** Add charts from Bengen (showing optimal equity allocation vs. withdrawal rates) to `fire-agent.html` landing page to educate users before they start.
    2.  **Advisory Capability:** Update `create_fire_plan.md` directive to give the chatbot knowledge of Bengen's findings (e.g., "50-75% equity is historically optimal for 30-year horizons").
    3.  **Tool Update:** Allow the agent to suggest an optimal portfolio allocation in the "Investment Strategy" section of the report, referencing Bengen's data.

---

## Phase 4: Modernization & Scaling
**Goal:** Handle more concurrent users efficiently.

### 1. Async Refactoring
*   **Context:** `orchestrator.send_message` is synchronous. This blocks the server thread while waiting for Google's API (1-5s).
*   **Plan:**
    1.  **Verify SDK Support:** Confirm `google-genai` supports `await client.chats.send_message_async` (or equivalent).
    2.  **Refactor Orchestrator:** Change methods to `async def` and use `await`.
    3.  **Refactor API:** Change `def chat_endpoint` to `async def chat_endpoint`.
    4.  **Benefit:** Allows a single container to handle hundreds of concurrent chat requests without blocking threads.

### 2. Shared Library (Long Term)
*   **Context:** `api.py` and `orchestrator.py` are 90% identical.
*   **Plan:**
    1.  Create a `longtermtrends-agent-core` package (or local `shared/` folder).
    2.  Move `Orchestrator`, `RateLimiter`, and `Logging` logic there.
    3.  Agents become lightweight configurations on top of this core.

---

## Phase 5: Self-Improvement (The "Analyst Agent")
**Goal:** Automate the feedback loop by analyzing user conversations to identify bottlenecks, confusion points, and success rates.

### 1. Transcript Analysis Pipeline
*   **Context:** We store conversation transcripts in `transcripts.jsonl` (downloadable via `scp`). Manually reviewing them is time-consuming.
*   **Plan:**
    1.  **New Agent:** Create a standalone script/agent (local or server-side) that parses the `.jsonl` logs.
    2.  **Analysis Logic:**
        *   **Success Rate:** Did the conversation end with a completed report?
        *   **User Confusion:** Identify turns where the user had to repeat themselves or clarify inputs.
        *   **Sentiment:** Did the user express frustration?
    3.  **Output:** A weekly summary report (markdown) highlighting:
        *   Common user questions not covered by the prompt.
        *   Frequent "malformed function call" errors.
        *   Suggestions for prompting improvements.

## Implementation Checklist

- [ ] **Phase 1**
    - [ ] Port `_handle_malformed_function_call` to FIRE Agent
    - [ ] Add Retry Loop to Investment Co-Pilot
- [ ] **Phase 2**
    - [ ] Update Directives for Optimistic Execution
    - [ ] Implement Streaming (Backend + Frontend)
- [x] **Phase 3** ✅ (Completed Jan 2026)
    - [x] Update Directives for Post-Report Q&A
    - [x] Update Orchestrator to handle "Task Complete" state
    - [ ] Add Bengen Charts to Landing Page (Deferred)
    - [x] Update Directive with Bengen's Portfolio Logic
- [ ] **Phase 4**
    - [ ] Prototype `async` support on one agent
    - [ ] Roll out to both
- [ ] **Phase 5**
    - [ ] Build Parser/Analyzer Script
    - [ ] Define Metrics (Success/Confusion)
    - [ ] Automate Weekly Report Generation

# FIRE Agent (Retire Early)

An autonomous AI agent that helps people plan their path to **Financial Independence, Retire Early (FIRE)**.

Built using the **DOE Framework** (Directive, Orchestration, Execution) and based on Bill Bengen's updated research (creator of the 4% Rule, now 4.7%).

---

## Core Objective

Democratize FIRE planning by providing:
- Accurate, evidence-based calculations
- Personalized FIRE roadmaps
- Multiple scenario analysis (conservative, standard, optimistic)
- CoastFIRE detection

---

## The Philosophy: Bengen's Updated Research

This agent implements the latest findings from Bill Bengen (2024):

1. **New Safe Withdrawal Rate: 4.7%** (up from 4.0%)
   - Based on better diversification (Large Cap + Small Cap Value)
   - Safe for 30-year retirements

2. **Early Retirement Adjustment: 4.1%**
   - For 50+ year horizons (retiring in your 30s-40s)
   - More conservative to handle longer timeframes

3. **Asset Allocation Requirements:**
   - Recommended **65% Equities** for most retirees (range: 50-75%)
   - 5% Cash buffer for bear markets
   - U-shaped glide path: reduce to ~45-50% early in retirement, increase to 65%+ over time

4. **Key Insight:**
   - **Inflation is more dangerous than bear markets**
   - High inflation (1968) was worse than the Great Depression (1929) for retirees

---

## Quick Start

### 1. Local Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your GEMINI_API_KEY to .env
```

### 2. Run Automated Tests

```bash
python3 tests/run_tests.py
```

You should see:
```
✅ All Tests Passed
```

### 3. Run Interactive Mode (CLI)

```bash
python -m execution.interactive_chat
```

This starts a conversation with the FIRE Coach in your terminal.

### 4. Run API Server

```bash
python -m execution.api
```

The API will be available at `http://localhost:8000`.

API Docs: `http://localhost:8000/docs`

---

## Project Structure

```text
FIRE-Agent/
├── directives/
│   └── create_fire_plan.md     # System instructions ("The Brain")
├── execution/
│   ├── api.py                  # FastAPI server
│   ├── orchestrator.py         # Gemini orchestration
│   ├── financial_calculators.py # Core math (deterministic)
│   ├── generate_fire_roadmap.py # Markdown generator
│   ├── data_mapper.py          # Data wiring layer
│   └── interactive_chat.py     # CLI interface
├── resources/
│   └── PROPOSED_ROADMAP_OUTPUT.md # Example roadmap output
├── tests/
│   ├── run_tests.py            # Test runner
│   ├── test_calculators.py     # Unit tests (Math)
│   ├── test_integration.py     # Integration tests (Wiring)
│   └── test_roadmap_content.py # Content tests (Output)
├── logs/
│   └── transcripts.jsonl       # Conversation logs
├── .tmp/                       # Temporary files
├── requirements.txt            # Python dependencies
├── test_cases.md               # 43 test scenarios
├── .env.example                # Environment template
└── README.md                   # This file
```

---

## Functionalities & Requirements Breakdown

### Core Scripts

| Functionality | Script | Libraries Used | API Keys |
| :--- | :--- | :--- | :--- |
| **Orchestration (Chat)** | `orchestrator.py` | `google-genai` | `GEMINI_API_KEY` |
| **API Server** | `api.py` | `fastapi`, `uvicorn`, `pydantic` | None |
| **CLI Interface** | `interactive_chat.py` | `python-dotenv` | `GEMINI_API_KEY` |
| **FIRE Calculations** | `financial_calculators.py` | None (Pure Python) | None |
| **Roadmap Generation** | `generate_fire_roadmap.py` | None (Markdown) | None |

### Dependencies (`requirements.txt`)

| Category | Package | Purpose |
| :--- | :--- | :--- |
| **AI/LLM** | `google-genai` | Gemini API SDK (manual function calling) |
| **Environment** | `python-dotenv` | Load `.env` file |
| **API Server** | `fastapi`, `uvicorn`, `pydantic` | REST API + validation |
| **Testing** | `requests` | HTTP testing |

---

## Step-by-Step Workflow

```
User Message → API/CLI → Orchestrator → LLM (Gemini) → Tools → Response
                                              ↓
                              (Manual intercept for generate_fire_roadmap)
```

### The Flow:

1. **Trigger:** User sends a message via `api.py` (web) or `interactive_chat.py` (CLI).

2. **Orchestration (The Brain):**
   - `orchestrator.py` creates a Gemini session with **System Instruction** from `create_fire_plan.md`.
   - It registers two tools (but handles them **manually**):
     - `calculate_fire_projections` — Returns FIRE numbers, scenarios, CoastFIRE status
     - `generate_fire_roadmap` — Generates the detailed Markdown roadmap

3. **Discovery Phase (LLM drives):**
   - The agent asks questions to gather inputs:
     - **Identity:** Age
     - **Current Finances:** Investments (liquid assets), Home Equity, Annual Income (after taxes), Annual Expenses
     - **Future Income:** Expected Inheritance (amount and age)
  

4. **Validation:**
   - Agent summarizes all inputs
   - User confirms ("Yes, that's correct")

5. **Calculation (Deterministic):**
   - LLM calls `calculate_fire_projections`
   - Function returns: FIRE numbers, years to FIRE, CoastFIRE status, Power Move analysis

6. **Roadmap Generation (Manual Intercept):**
   - LLM calls `generate_fire_roadmap`
   - **Orchestrator intercepts** and returns the Markdown **verbatim** (bypasses LLM)
   - Ensures formulas and transparency sections are preserved exactly

7. **Delivery:**
   - Agent outputs the full FIRE Roadmap document
   - Includes disclaimer and assumptions

---

## Logging

Both the CLI and API log all interactions to `logs/transcripts.jsonl` using a shared `logging_utils.py` module:

> [!IMPORTANT]
> **Persistent Volume Required:** In Docker/Coolify deployments, logs are stored inside the container and will be lost on restart. Configure a persistent volume mount for `/app/logs` in Coolify (Storages tab) to preserve logs across deployments.
>
> **Download Logs:** With persistent volume configured, download directly from host:
> ```bash
> scp -i ~/.ssh/id_rsa root@SERVER_IP:/var/lib/docker/volumes/fire-agent-logs/_data/transcripts.jsonl ~/Downloads/transcripts.jsonl
> ```

| Field | Description |
|-------|-------------|
| `metadata` | User info (`user_name`, `user_email`, `user_id`) — appears first |
| `timestamp` | ISO-8601 timestamp |
| `sessionId` | Unique session identifier |
| `role` | `user` or `model` |
| `message` | The message content |

**Format:** Per-message logging (each user input and model response logged separately with individual timestamps).

> [!NOTE]
> **Upcoming Refactor:** See [resources/api_cli_alignment_plan.md](./resources/api_cli_alignment_plan.md) for planned architectural changes to align this agent with the Investment Co-Pilot's stateless pattern.

## How It Works (DOE Architecture)

### 1. Directive (The SOP)
`directives/create_fire_plan.md` - Natural language instructions defining:
- The FIRE Coach persona
- Discovery process (what questions to ask)
- When to call which tools
- Edge cases and tough love scenarios

### 2. Orchestration (The Router)
`execution/orchestrator.py` - Gemini LLM (using modern `google-genai` SDK) that:
- Reads the directive
- Conducts the conversation
- Detects when to call calculation tools
- **MANUAL Function Calling:** Executes Python functions directly, with special handling for `generate_fire_roadmap`

**Key Feature:** Uses **manual function calling** for verbatim output control. When the `generate_fire_roadmap` tool is called, the orchestrator **bypasses the LLM's interpretation** and returns the raw Markdown directly to the user. This ensures the roadmap is displayed exactly as generated, including all formulas and transparency sections.

### 3. Execution (The Hands)
**Deterministic Python scripts:**
- `financial_calculators.py` - Pure math (FIRE numbers, time to FIRE, CoastFIRE)
- `generate_fire_roadmap.py` - Markdown report generator (displayed verbatim)

---

## API Usage

### Chat Endpoint

```bash
POST /chat
```

**Request:**
```json
{
  "session_id": "user-123",
  "message": "I want to retire early"
}
```

**Response:**
```json
{
  "session_id": "user-123",
  "response": "Great! Let's build your FIRE roadmap. First, how old are you?",
  "timestamp": "2026-01-09T15:30:00"
}
```

### Other Endpoints

- `GET /` - Health check
- `GET /health` - Detailed status
- `GET /sessions` - List active sessions
- `DELETE /session/{session_id}` - Clear session

---

## Example Conversation Flow

```
Agent: "Great! Let's build your FIRE roadmap. First, how old are you?"
User: "32"

Agent: "How much do you currently have invested? (Do NOT include your home, car, or emergency fund.)"
User: "$150,000"

Agent: "Do you own a home? If so, what is your approximate home equity?
        (Equity = Home Value minus Mortgage Balance. Example: $500k home with $200k mortgage = $300k equity.)"
User: "I own a $400k home with $250k mortgage, so $150k equity"

Agent: "What's your annual income after taxes?"
User: "$90,000"

Agent: "And what are your annual expenses?"
User: "$45,000"

Agent: "Do you have a target retirement age, or should I calculate ASAP?"
User: "ASAP"

Agent: [Summarizes inputs, notes that home equity is 'locked' and not in primary calculation]
User: "Yes, that's correct"

Agent: [Generates full FIRE Roadmap showing retirement at age 44]
```

**Note on Home Equity:**
The agent explicitly asks about home equity but does NOT include it in the primary FIRE calculation. This prevents the "House Rich, Cash Poor" trap where users think they can retire because they own a valuable home but have no liquid assets. If the user has significant home equity, the agent can offer a secondary "Downsizing Scenario".

---

## Key Features

1. **Multiple Scenarios:**
   - Bengen Standard (4.7%)
   - Early Retirement (4.1%)
   - Conservative (4.0%)



3. **Sensitivity Analysis:**
   - Your "Years to FIRE" depends on growth rates you won't know in advance. Here's how the timeline shifts:

| Growth Assumption | Years to FIRE | Retirement Age |
| :--- | :--- | :--- |
| 5% Real Return | 15 years | 47 |
| 7% Real Return | 12 years | 44 |
| 9% Real Return | 10 years | 42 |

   - *Note: 4.7% is the Withdrawal Rate (target), not the Growth Rate (speed).*
   - Labeled as **"Years to FIRE"** in the roadmap for clarity.

4. **CoastFIRE Detection:**
   - Automatically checks if you can stop saving
   - Handles edge case: "Already at retirement age" → shows NOT APPLICABLE

5. **Power Move Analysis:**
   - Shows impact of cutting $500/month
   - Gracefully handles edge cases where cutting doesn't help

6. **Home Equity Handling:**
   - Explicitly asks about home equity during discovery
   - Excludes from FIRE calculation (illiquid asset)
   - Shows downsizing strategies in roadmap

7. **Feedback & Analytics:**
   - **Feedback:** "Report Issue" link in chat UI
   - **Analytics:** Integration with Google Tag Manager (`chat_initiated`, `chat_response_received`)

8. **Inheritance Support:**
   - Accepts `inheritance_amount` and `inheritance_age` parameters
   - One-time lump sum added to portfolio at specified age
   - Accelerates FIRE timeline when inheritance expected

9. **Compound Growth Breakdown:**
    - "Where the money comes from" section shows:
      - Principal (Start + Saved)
      - Compound Growth (The power of 7% returns!)
    - Explains how savings + growth reaches FIRE target

10. **Forever Fund:**
    - Renamed from "Perpetual Pot" for clarity
    - Forever Fund = covers expenses gap forever

11. **Conversational Capabilities (Post-Report Q&A):**
    - After generating a roadmap, the agent enters "Analyst Mode"
    - Answers follow-up questions without regenerating the report
    - Agent has full context of the generated roadmap
    - Only re-runs calculations if user explicitly changes inputs

---

## Testing

### Automated Testing Framework

The agent uses a **3-Layer Testing Pyramid** with **45 automated tests**:

| Layer | Component | Focus | Tests |
|-------|-----------|-------|-------|
| **1. Unit** | `test_calculators.py` | Pure Math | 29 |
| **2. Content** | `test_roadmap_content.py` | Final Output | 15 |
| **3. Integration** | `test_integration.py` | Wiring/Mapping | 1 |

Run the full suite:

```bash
python3 tests/run_tests.py
```

Expected output: `Ran 45 tests in 0.004s OK`

### Quick Automated Test (All Scenarios)

Run all key test cases with assertions:

```bash
cd FIRE-Agent
python -c "
from execution.financial_calculators import calculate_fire_projections

# Test 1: Standard FIRE
result = calculate_fire_projections(35, 100000, 80000, 40000)
assert result['status'] == 'success' and result['savings_rate'] == 50.0
print('✅ Test 1: Standard FIRE')

# Test 4: CoastFIRE
result = calculate_fire_projections(30, 200000, 80000, 40000, target_retirement_age=65)
assert result['coast_fire']['coast_fire'] == True
print('✅ Test 4: CoastFIRE')

# Test 12: Already at FIRE
result = calculate_fire_projections(50, 2000000, 160000, 80000)
assert result['scenarios']['bengen_standard']['years_to_fire_7pct'] == 0
print('✅ Test 12: Already at FIRE')

# Test 15: Zero Income (Decumulation)
result = calculate_fire_projections(55, 500000, 0, 80000)
assert result['status'] == 'decumulation'
print('✅ Test 15: Zero Income (Decumulation)')

# Test 17: House Rich, Cash Poor
result = calculate_fire_projections(50, 50000, 40000, 60000)
assert result['status'] == 'decumulation'
print('✅ Test 17: House Rich, Cash Poor')

# Test 22: Power Move
result = calculate_fire_projections(40, 250000, 200000, 130000)
assert result['power_move']['new_fire_number'] < result['scenarios']['bengen_standard']['fire_number']
print('✅ Test 22: Power Move')

print('\n🎉 All quick tests passed!')
"
```

### Comprehensive Test Scenarios

See `test_cases.md` for **50 documented test scenarios** including:

| Category | Test Cases | Automated |
|----------|------------|----------|
| **Core FIRE** | Standard, LeanFIRE, FatFIRE, Already at FIRE | ✅ |
| **CoastFIRE** | Detection, Age 65 Baseline, Not Yet | ✅ |
| **Decumulation** | Zero Income, Negative Savings, Escape Velocity | ✅ |
| **Inheritance** | Accelerates, Past, Late, Instant FIRE | ✅ |
| **Edge Cases** | Age 18, Age 75, Zero Expenses, High Savings | ✅ |
| **Output Quality** | Verbatim Roadmap, Naming, Sections | ✅ |

**45 automated test functions** covering **30 of 50 documented test cases** (as of 2026-01-24).

---

## Deployment (Optional)

### Docker

```bash
# Build image
docker build -t fire-agent .

# Run container
docker run -p 8000:8000 --env-file .env fire-agent
```

### Environment Variables

Required:
- `GEMINI_API_KEY` - Your Google AI API key

Optional:
- `PORT` - Server port (default: 8000)

---

## Research Foundation

This agent is built on:

1. **Bill Bengen's Research (1994-2024)**
   - Original 4% Rule paper
   - "A Richer Retirement" (2024 book)
   - Updated withdrawal rates with better diversification

2. **Key Papers:**
   - Kitces & Pfau: U-shaped equity glide paths
   - Trinity Study: Safe withdrawal rates
   - Historical market data (1926-present)

---

## Limitations & Disclaimers

⚠️ **This is NOT financial advice.**

The agent:
- Uses historical data (past ≠ future)
- Ignores taxes (simplification)
- Assumes constant expenses (unrealistic)

**Always consult a licensed financial advisor before making investment decisions.**

---

## Technical Architecture

### Modern SDK Implementation (Manual Function Calling)

This agent uses the **modern `google-genai` SDK** (not the older `google-generativeai`), with a **custom manual function calling** approach:

- ✅ **Manual Function Calling** - We handle tool execution ourselves for fine-grained control
- ✅ **Verbatim Output** - The `generate_fire_roadmap` result bypasses LLM interpretation entirely
- ✅ **Transparency Preserved** - Formulas and math sections are displayed exactly as coded
- ✅ **Native Python Types** - No MapComposite handling needed with modern SDK
- ⚠️ **Different from Investment Co-Pilot** - Co-Pilot uses automatic function calling; FIRE Agent uses manual

### Memory & Context Management

The system uses a **stateless architecture with in-memory persistence**:

1.  **API Layer (`api.py`)**: Maintains a global `sessions` dictionary mapping `session_id` to `FIREOrchestrator` instances.
2.  **SDK Layer (`orchestrator.py`)**: Uses the Google GenAI SDK's `ChatSession` object (`self.chat`), which automatically manages the conversation history list.
3.  **Context Preservation**: With each `send_message()` call, the SDK sends the accumulated history to the model, allowing Gemini to "remember" previous inputs (like age or expenses).
4.  **Limitation**: Memory is ephemeral. Restarting the API server clears the `sessions` dictionary, resetting all active conversations.

### Function Calling Flow

```python
# Tools are registered, but automatic calling is DISABLED
automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)

# When LLM requests a tool:
# 1. We detect the function_call in the response
# 2. Execute the function ourselves
# 3. For `generate_fire_roadmap`: Return result DIRECTLY (bypass LLM)
# 4. For other tools: Send result back to LLM for interpretation
```

**Why Manual?**
With automatic function calling, the LLM would "interpret" the roadmap and rewrite it in its own words, losing the carefully crafted transparency sections (like "The Math Behind This"). Manual control ensures the user sees the exact output.

### Metadata Flow (Important Limitation)

```
Frontend → API (extracts metadata) → FIREOrchestrator → send_message() → generate_fire_roadmap()
              ↓                            ↓
         metadata logged              metadata NOT passed to tools
```

**The Trade-off:**
- With **manual function calling**, the orchestrator intercepts tool execution.
- The API logs `user_name`, `user_email`, etc. from the frontend metadata.
- However, this metadata is **not propagated** to the roadmap generator (by design, for privacy in output).
- Contrast with Investment Co-Pilot, which uses **automatic function calling** where the LLM can include metadata in tool parameters.

**Result:** The generated Roadmap is anonymous. User metadata exists only in logs.

**Key Dependencies:**
- `google-genai` - Modern Google AI SDK
- `fastapi` - Web API framework
- `pydantic` - Data validation
- `python-dotenv` - Environment management

---

## Credits

- **Bill Bengen** - Creator of the 4% Rule and updated research
- **Google Gemini 2.0** - AI orchestration
- **Built with** - Python, FastAPI, Google GenAI SDK

---

### Recent Updates (January 2026)
Added **12 new test cases** (TC47-TC58) covering:
- **Complex Decumulation:** Inheritance scenarios during drawdown.
- **Past Inheritance:** Fix for double-counting bug.
- **Accumulation Edge Cases:** High expenses, late inheritance, and instant-FIRE triggers.

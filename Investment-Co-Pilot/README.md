# Investment Co-Pilot (Agent)

An autonomous AI agent that generates personalized **Investment Policy Statements (IPS)** based on academic principles.

Built using the **DOE Framework** (Directive, Orchestration, Execution) and implementing the **Simple. Cheap. Safe. Easy.** philosophy from John Y. Campbell's book *"Fixed"*.

> **⚠️ DISCLAIMER:** This tool is for educational purposes only. It does **NOT** provide legal, tax, or personalized financial investment advice.

---

## Core Objective

Democratize high-quality, evidence-based financial education by providing:
- Personalized Investment Policy Statements (IPS)
- Portfolio models based on Lifecycle Investing theory
- Rule-based safety checks (Debt, Liquidity, Housing)
- Free of conflicts of interest

---

## The Philosophy: Simple, Cheap, Safe, Easy

This agent enforces design principles aimed at empowering investors:

| Principle | Meaning |
|-----------|---------|
| **Simple** | Standardized, modular products (broad Index Funds) for easy comparison |
| **Cheap** | Minimize costs — high fees are the biggest predictor of underperformance |
| **Safe** | "Self-driving" safety features; risky products quarantined (e.g., "Fun Bucket") |
| **Easy** | Minimal maintenance; works on autopilot once set up |

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

### 2. Run API Server

```bash
python -m execution.api
```

The API will be available at `http://localhost:8000`.

API Docs: `http://localhost:8000/docs`

### 3. Run Interactive Mode (CLI)

```bash
python -m execution.interactive_chat
```

This starts a conversation with the Investment Co-Pilot directly in your terminal (connects directly to the orchestrator, no API needed).

### 4. Run with Docker

```bash
# Ensure your .env file is present
docker compose up --build
```

The API will be available at `http://localhost:8001` (port 8001 avoids conflict with Django).

---

## Project Structure

```text
Investment Co-Pilot/
├── directives/
│   ├── orchestrator_directive.md # System instructions ("The Brain")
│   ├── create_ips.md             # IPS generation rules
│   └── check_rebalancing.md      # Rebalancing rules (planned)
├── execution/
│   ├── api.py               # FastAPI server
│   ├── orchestrator.py      # Gemini orchestration
│   ├── financial_utils.py   # Core financial logic (deterministic)
│   ├── generate_ips.py      # Markdown generator
│   ├── data_mapper.py       # Input wiring logic
│   └── interactive_chat.py  # CLI interface
├── tests/
│   ├── run_tests.py              # Custom test runner
│   ├── test_allocation.py        # Core logic tests
│   ├── test_edge_cases.py        # Boundary & priority tests
│   ├── test_integration.py       # Data wiring tests
│   ├── test_ips_content.py       # Output text verification
│   ├── test_cases.md             # 19 Manual test scenarios
│   ├── test_architecture.md      # Test strategy documentation
│   ├── test_coverage_analysis.md # Variable analysis
│   ├── test_implementation.md    # Summary of tests
│   ├── input_output_pipeline.md  # Data flow documentation
│   └── validation_report_2.md    # Bug fix history
├── resources/
│   └── resilience_improvements.md # Bug fixes and improvements
├── logs/
│   └── transcripts.jsonl    # Conversation logs
├── .tmp/                    # Intermediate files
├── Dockerfile               # Container definition
├── docker-compose.yml       # Deployment config
├── DEPLOY_COOLIFY.md        # Deployment guide
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

### Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | This file - project overview, setup, features |
| `tests/test_cases.md` | 17 test scenarios with manual test commands |
| `tests/input_output_pipeline.md` | Complete data flow from user input to IPS output |
| `tests/test_allocation.py` | 12 automated pytest tests |
| `tests/test_architecture.md` | Recommendations for automated testing (pytest) |
| `tests/test_coverage_analysis.md` | Variable impact analysis and coverage matrix |
| `tests/test_implementation.md` | Summary of test implementation |
| `tests/validation_report_*.md` | Validation reports with bug fixes |
| `resources/resilience_improvements.md` | Bug fixes and code improvements |
| `DEPLOY_COOLIFY.md` | Production deployment instructions |


---

## Functionalities & Requirements Breakdown

### Core Scripts

| Functionality | Script | Libraries Used | API Keys |
| :--- | :--- | :--- | :--- |
| **Orchestration (Chat)** | `orchestrator.py` | `google-genai` | `GEMINI_API_KEY` |
| **API Server** | `api.py` | `fastapi`, `uvicorn`, `pydantic` | None |
| **CLI Interface** | `interactive_chat.py` | `python-dotenv` | `GEMINI_API_KEY` |
| **Financial Logic** | `financial_utils.py` | None (Pure Python) | None |
| **Data Wiring** | `data_mapper.py` | None (Pure Python) | None |
| **IPS Generation** | `generate_ips.py` | None (Markdown) | None |
| **Allocation CLI** | `calculate_allocation.py` | `argparse`, `json` | None |
| **Rebalancing Check** | `check_rebalancing.py` | `argparse`, `json` | None |

### Dependencies (`requirements.txt`)

| Category | Package | Purpose |
| :--- | :--- | :--- |
| **AI/LLM** | `google-genai` | Gemini API SDK (function calling) |
| **Environment** | `python-dotenv` | Load `.env` file |
| **API Server** | `fastapi`, `uvicorn`, `pydantic` | REST API + validation |
| **Data** | `pandas`, `numpy` | Data manipulation (for rebalancing) |
| **Testing** | `pytest`, `requests` | Unit tests + HTTP testing |

---

## Step-by-Step Workflow

```
User Message → API/CLI → Orchestrator → LLM (Gemini) → Tools → Response
```

### The Flow:

1. **Trigger:** User sends a message via `api.py` (web) or `interactive_chat.py` (CLI).

2. **Orchestration (The Brain):**
   - `orchestrator.py` creates a Gemini session with the **System Instruction** from `orchestrator_directive.md`.
   - It registers two tools for the LLM to call:
     - `calculate_holistic_allocation` — Returns equity/bonds/fun percentages
     - `generate_ips_markdown` — Generates the formal IPS document

3. **Discovery Phase (LLM drives):**
   - The agent asks questions to gather inputs:
     - **Identity:** Age, Region (US/EU)
     - **Goals:** Liquidity, Longevity, or Legacy
     - **Wealth Context:** Home ownership, Debt status, Job stability
     - **Risk Tolerance:** Aggressive or Conservative?
     - **Fun Bucket:** Speculation allocation (0-10%)
     - **ESG Preference:** Sustainable funds?

4. **Safety Checks (Deterministic):**
   - When LLM calls `calculate_holistic_allocation`, the function applies:
     - **Debt Rule:** High-interest debt → Stop investing
     - **Liquidity Rule:** < 3 months savings → Build cash first
     - **Housing Rule:** Homeowners → Reduce equity by 10%
   - Returns allocation percentages

5. **Proposal:**
   - The agent presents the calculated strategy to the user
   - Waits for confirmation ("Yes, generate the IPS")

6. **Execution (Document Generation):**
   - When user confirms, LLM calls `generate_ips_markdown`
   - Returns the formal Markdown IPS document

7. **Delivery:**
   - Agent outputs the full IPS document
   - Appends the Legal Disclaimer

---

## Key Features

1. **Lifecycle Investing V2:**
   - Human Capital theory (younger = more equity)
   - Age-based glide path with three phases:
     - Under 50: Maximum growth
     - 50-64: Transition phase
     - 65+: Retirement floor (minimum 50% equity for 4.7% rule)

2. **Rule-Based Safety Checks:**
   - **Debt Rule:** High-interest debt → Stop investing (guaranteed return on payoff)
   - **Liquidity Rule:** < 3 months savings → Build cash buffer first
   - **Housing Rule:** Homeowners → Reduce equity by 10% (home is a bond-like asset)

3. **Investment Universe:**
   | Asset Class | US Domiciled | EU Domiciled |
   |-------------|--------------|--------------|
   | **Equity** | VT | VWCE |
   | **ESG Equity** | ESGV (65%) + VSGX (35%) | V3AA |
   | **Bonds** | LQD | LQDA or IEAA |
   | **Gold** | GLD | SGLD |
   | **Bitcoin** | IBIT | BTCE |

4. **Goal-Based Strategies:**
   - **LIQUIDITY:** Short-term focus (< 5 years) — 20% equity, 80% bonds
   - **LONGEVITY:** Standard lifecycle allocation
   - **LEGACY:** 90% equity minimum (time horizon is recipient's life)

5. **Fun Bucket (Speculation):**
   - User-controlled allocation (0-100%)
   - Quarantined from core portfolio
   - Clear risk warnings at 10%+ allocation

6. **IPS Document:**
   - Formal Investment Policy Statement
   - Rebalancing rules (5% drift threshold)
   - Panic Protocol (what to do in crashes)

7. **Income Stability Warnings:**
   - Self-employed / volatile income → 12x savings target (vs 6x standard)
   - No pension → extended runway warning

8. **Feedback & Analytics:**
   - "Report Issue" link in chat UI
   - Google Tag Manager integration (`chat_initiated`, `chat_response_received`)

9. **Conversational Capabilities (Post-Report Q&A):**
   - After generating an IPS, the agent enters "Analyst Mode"
   - Answers follow-up questions without regenerating the report
   - Agent has full context of the generated IPS
   - Only re-runs calculations if user explicitly changes inputs

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
  "message": "I want to create an investment plan"
}
```

**Response:**
```json
{
  "session_id": "user-123",
  "response": "Hello! I'm your Investment Co-Pilot. To get started, how old are you?",
  "timestamp": "2026-01-09T15:30:00"
}
```

### Other Endpoints

- `GET /` - Health check
- `GET /health` - Detailed status
- `GET /sessions` - List active sessions
- `DELETE /session/{session_id}` - Clear session

---

## Logging

Both the CLI and API log all interactions to `logs/transcripts.jsonl` using a shared `logging_utils.py` module:

> [!IMPORTANT]
> **Persistent Volume Required:** In Docker/Coolify deployments, logs are stored inside the container and will be lost on restart. Configure a persistent volume mount for `/app/logs` in Coolify (Storages tab) to preserve logs across deployments.
>
> **Download Logs:** With persistent volume configured, download directly from host:
> ```bash
> scp -i ~/.ssh/id_rsa root@SERVER_IP:/var/lib/docker/volumes/investment-copilot-logs/_data/transcripts.jsonl ~/Downloads/transcripts.jsonl
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
> **Upcoming Refactor:** See [resources/api_cli_alignment_plan.md](./resources/api_cli_alignment_plan.md) for planned architectural improvements.

---

## Testing

### Automated Tests
The agent uses a robust **3-Layer Testing Pyramid** powered by Python's standard `unittest` framework:

**Run the full suite:**
```bash
python3 tests/run_tests.py
```

**What is tested?**
*   **Unit Layer (`test_allocation.py`, `test_edge_cases.py`):** Core logic, Rules (Debt, Liquidity), and Boundaries.
*   **Integration Layer (`test_integration.py`):** Wiring and data mapping.
*   **Content Layer (`test_ips_content.py`):** Output Verification (English checks).

### Manual Test Scenarios
For a deep dive into the 19 distinct user personas and edge cases, refer to the detailed test documentation:

👉 **[View Test Cases](./tests/test_cases.md)**

This document includes:
*   **Persona behaviors** (e.g., "The Entrepreneur", "The Legacy Investor")
*   **Philosophy checks** (Why the agent decides what it decides)
*   **Copy/Paste commands** to verify specific scenarios manually

## How It Works (DOE Architecture)

### 1. Directive (The SOP)
`directives/orchestrator_directive.md` - Natural language instructions defining:
- The Co-Pilot persona
- Discovery process (what questions to ask)
- When to call which tools
- Financial rules (Debt, Liquidity, Housing)

### 2. Orchestration (The Router)
`execution/orchestrator.py` - Gemini LLM (using modern `google-genai` SDK) that:
- Reads the directive
- Conducts the conversation
- Uses **automatic function calling** for tool execution
- Routes to deterministic Python scripts

### 3. Execution (The Hands)
**Deterministic Python scripts:**
- `financial_utils.py` - Pure math (allocation calculations, rules)
- `generate_ips.py` - Markdown IPS generator

---

## Deployment (Coolify/VPS)

This agent is production-ready and designed to run on **Coolify**.

### Architecture
- **Service:** Single Docker container running FastAPI
- **State:** Mostly stateless (requires `sessionId` in payload)
- **Security:**
  - Strict CORS policy (whitelists `longtermtrends.net`)
  - SSL enforcement via Coolify/Traefik proxy

### How to Deploy
See [DEPLOY_COOLIFY.md](DEPLOY_COOLIFY.md) for detailed instructions.

---

## Technical Architecture

### Manual Function Calling

This agent uses **manual function calling** via the `google-genai` SDK:

```python
# Tools are registered, but automatic calling is DISABLED
automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)

# The orchestrator:
# 1. Detects when LLM wants to call a tool
# 2. Executes the Python function manually
# 3. For `generate_ips_markdown`: Returns result DIRECTLY (verbatim)
# 4. Injects the full IPS into context for follow-up Q&A
```

### Comparison with FIRE Agent

| Feature | Investment Co-Pilot | FIRE Agent |
|---------|---------------------|------------|
| **Function Calling** | Manual | Manual |
| **Post-Report Q&A** | ✅ Full report context | ✅ Full roadmap context |
| **Output Style** | Exact Markdown preserved | Exact Markdown preserved |
| **Primary Output** | Investment Policy Statement | FIRE Roadmap |

---

## Research Foundation

This agent is built on:

1. **John Y. Campbell's "Fixed" (2024)**
   - Simple, Cheap, Safe, Easy principles
   - Consumer protection in finance

2. **Lifecycle Investing Theory**
   - Human Capital considerations
   - Age-based asset allocation

3. **Academic Research:**
   - Bengen's withdrawal rates
   - Trinity Study
   - Modern Portfolio Theory

---

## Limitations & Disclaimers

⚠️ **This is NOT financial advice.**

The agent:
- Uses academic principles (not personalized recommendations)
- Ignores taxes (simplification)
- Assumes US or EU domicile only
- Does not account for individual circumstances

**Always consult a licensed financial advisor before making investment decisions.**

---

## Credits

- **John Y. Campbell** - "Fixed" philosophy
- **Google Gemini 2.0** - AI orchestration
- **Built with** - Python, FastAPI, Google GenAI SDK

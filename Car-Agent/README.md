
# Car Agent (Affordability Analyzer)

An autonomous AI agent that helps people determine how much car they can realistically afford based on the **10% Rule** and **Total Cost of Ownership (TCO)**.

Built using the **DOE Framework** (Directive, Orchestrator, Execution) and powered by **Google Gemini**.

## 🚀 Features
- **10% Rule Analysis:** Checks if transport costs are < 10% of **net income**.
- **TCO Calculator:** Estimates specific costs for Budget, Luxury, and Supercars.
- **Opportunity Cost:** Calculates investment growth lost by spending on a car.
- **Verbatim Reporting:** Generates a deterministic Markdown report (no LLM hallucinations).
- **Persistent Memory:** Saves conversation history to `logs/transcripts.jsonl`.

## 🛠️ Setup & Usage

### Prerequisites
- Python 3.10+
- Gemini API Key

### Installation

1. **Clone & Setup Env:**
   ```bash
   cd Car-Agent
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

### Running the Agent

**Interactive CLI Mode:**
```bash
python -m execution.interactive_chat
```

**API Server (FastAPI):**
```bash
python -m execution.api
# Server runs at http://0.0.0.0:8000
```

## 📂 Deployment (Coolify)

See [DEPLOY_COOLIFY.md](DEPLOY_COOLIFY.md) for detailed deployment instructions.

## 🏗️ Architecture

```
Car-Agent/
├── derivatives/          # System Instructions (SOPs)
│   └── calculate_car_affordability.md
├── execution/           # Core Logic
│   ├── api.py           # FastAPI Server
│   ├── car_calculators.py # Deterministic Math
│   ├── generate_car_report.py # Markdown Generator
│   ├── interactive_chat.py # CLI Interface
│   └── orchestrator.py  # Gemini Client & Tool Chaining
├── tests/               # Unit Tests
│   └── test_calculators.py
└── logs/                # Conversation Transcripts
```

## 🧠 Philosophy

This agent implements key principles from responsible car ownership:

1. **The 10% Rule:**
   - Transportation costs should be **< 10% of net income** (after taxes)
   - Includes: payment, insurance, fuel, maintenance
   - We use net income for a safer, more conservative estimate

2. **Total Cost of Ownership (TCO):**
   | Cost Category | What It Includes |
   |---------------|------------------|
   | Depreciation  | Value lost over time (biggest cost) |
   | Financing     | Interest paid on loan |
   | Insurance     | Monthly premiums |
   | Fuel          | Gas/Electric costs |
   | Maintenance   | Repairs, tires, oil changes |
   | Taxes & Fees  | Registration, sales tax |

3. **Opportunity Cost:**
   - Money spent on depreciation cannot compound in the market.
   - We calculate what that money *could have earned* if invested at 7%.

## Example Conversation Flow

```
Agent: "What is your annual net income (after taxes)?"
User: "$80,000"

Agent: "What are your total annual expenses?"
User: "$60,000"

Agent: "How much do you currently have invested? (Optional)"
User: "$150,000"

Agent: "What type of car are you considering?"
User: "Budget"

[Agent runs calculations and displays Markdown report]
```

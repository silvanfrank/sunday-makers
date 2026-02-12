# Test Cases for FIRE Agent

This document outlines various user personas and scenarios to test the **FIRE (Financial Independence, Retire Early) Agent**.

These tests ensure the agent correctly applies Bill Bengen's updated research (4.7% rule) and provides accurate projections.

> [!NOTE]
> **Removed Test Cases:**
> Test cases related to defined benefit pensions (bridges, commuted values) were removed in Jan 2026 to simplify the agent model.

---

## How to Run Tests

### Automated Test Suite (Recommended)

Run the full testing pyramid (Unit, Integration, Content):

```bash
cd docs/Longtermtrends-Content/Agents/FIRE-Agent
python tests/run_tests.py
```

Expected output: `Ran 45 tests in 0.004s OK`

### Individual Test Files

```bash
python tests/test_calculators.py -v      # Unit tests (29 tests)
python tests/test_roadmap_content.py -v  # Content tests (15 tests)
python tests/test_integration.py -v      # Integration test (1 test)
```

### Manual Testing (For Exploratory/Interactive Testing)

```bash
python -m execution.interactive_chat
```

Follow the conversation flow and verify agent behavior matches expectations.

---

## Complete Test Checklist (TC1-TC59)

> **Legend:** `[x]` = Automated test exists, `[ ]` = Manual only

- [x] TC1: Standard FIRE
- [x] TC2: LeanFIRE
- [x] TC3: FatFIRE
- [x] TC4: CoastFIRE Detection
- [x] TC5: Overspender Error
- [x] TC6: Early Retiree (4.1%)
- [x] TC7: Power Move
- [ ] TC8: High Saver
- [x] TC9: Bengen vs Conservative
- [ ] TC10: Full Conversation Flow
- [x] TC11: Sensitivity Analysis
- [x] TC12: Already at FIRE
- [x] TC15: Zero Income (Decumulation)
- [x] TC16: Verbatim Roadmap
- [x] TC17: House Rich Cash Poor
- [ ] TC18: Already At Retirement Age
- [ ] TC19: Power Move Negative check
- [x] TC20: Home Equity Exclusion
- [x] TC21: CoastFIRE Default Age
- [ ] TC24: Very Young (Longevity Risk)
- [ ] TC26: Partial Income Decumulation
- [ ] TC29: Scenario Comparison Logic
- [ ] TC30: CostFIRE Explanation
- [x] TC31: Negative Savings Decumulation
- [x] TC32: Zero Expenses
- [x] TC33: Inheritance Impact
- [x] TC34: Past Inheritance
- [ ] TC35: Inheritance + Standard
- [x] TC36: Age 18
- [x] TC37: Age 75
- [x] TC38: High Savings Rate
- [ ] TC39: Life Expectancy Edge
- [x] TC40: Naming Verification
- [x] TC41: Zero Inheritance
- [ ] TC42: Inheritance Calculation Check
- [ ] TC43: Inheritance Before FIRE (No Accel)
- [x] TC44: Instant FIRE via Inheritance
- [x] TC45: Late Inheritance
- [ ] TC46: Future One-Time Expense
- [x] TC47: Sustainable Partial Drawdown
- [ ] TC48: Decumulation + Late Inheritance
- [ ] TC50: Decumulation + Large Inheritance
- [x] TC51: Past Inheritance Logic
- [ ] TC52: Partial Decumulation + Inheritance
- [ ] TC53: Partial Decumulation Baseline
- [ ] TC54: Accumulation Standard
- [ ] TC55: Accumulation + Inheritance
- [ ] TC56: Accumulation + Large Inheritance
- [ ] TC57: High Exp + Inheritance Scenario
- [ ] TC58: Late Inheritance (Accumulation)
- [x] TC59: Zero Assets + Future Inheritance
- [x] TC60: Post-Report Acknowledgement (No Re-Run)
- [x] TC61: Post-Report Follow-Up Question

**Automated:** 32 of 52 test cases (~62%)

---

## 1. Core FIRE Scenarios

### TC1: The Standard FIRE Candidate
*   **Persona:** 35-year-old, $100k invested, $80k income, $40k expenses.
*   **Expected Output:** FIRE Number ~$851k, ~12 years to FIRE.

### TC2: The LeanFIRE Minimalist
*   **Persona:** 28-year-old, $50k invested, $45k income, $25k expenses.
*   **Expected Output:** Archetype "LeanFIRE", FIRE Number ~$532k.

### TC3: The FatFIRE Aspirant
*   **Persona:** 42-year-old, $500k invested, $250k income, $120k expenses.
*   **Expected Output:** Archetype "FatFIRE", FIRE Number ~$2.55M.

### TC4: The CoastFIRE Winner
*   **Persona:** 30-year-old, $200k invested, expenses $40k, target age 65.
*   **Expected Output:** CoastFIRE Status "ACHIEVED". Can stop saving.

### TC30: CoastFIRE "Not Yet"
*   **Persona:** 40-year-old, $150k invested, failing CoastFIRE.
*   **Expected Output:** Status "NOT YET", explains gap and meaning.

### TC18: Already At Retirement Age
*   **Persona:** 55-year-old, targeting 55, not yet FI.
*   **Expected Output:** CoastFIRE "NOT APPLICABLE".

---

## 2. Decumulation & Zero Income Scenarios

### TC15: Zero Income (Sabbatical/Retired)
*   **Persona:** 55-year-old, $500k invested, $0 income, $80k expenses.
*   **Expected Output:** Status "decumulation", Runway calculated.

### TC31: Negative Savings (Overspending > Income)
*   **Persona:** 55-year-old, $500k invested, $50k income, $80k expenses.
*   **Expected Output:** Status "decumulation", Runway based on $30k gap.

### TC17: House Rich, Cash Poor
*   **Persona:** 50-year-old, $50k liquid, $1.5M home, expenses $60k.
*   **Expected Output:** Runway < 1 year. Advice to downsize.

### TC47: Sustainable Partial Drawdown
*   **Persona:** 36-year-old, $1M invested, $80k income, $100k expenses ($20k gap).
*   **Expected Output:** Withdrawal Rate 2.0% (Sustainable), Infinite Runway.

---

## 3. Inheritance Scenarios

### TC33: Standard Inheritance Impact
*   **Persona:** 30-year-old, $100k invested. Inheritance $200k at 40.
*   **Expected Output:** Timeline accelerated vs baseline.

### TC34: Past Inheritance
*   **Persona:** 35-year-old. Inheritance age 30 (already received).
*   **Expected Output:** Treated as already in `current_investments`.

### TC51: Past Inheritance (Double Count Check)
*   **Persona:** 36-year-old, $1M invested. Inheritance $1M at age 4.
*   **Expected Output:** Runway matches baseline (no double counting).

### TC45: Late Inheritance
*   **Persona:** 30-year-old. Inheritance at 60 (after FIRE).
*   **Expected Output:** "Arrives after FIRE". No impact on timeline.

### TC41: Zero/None Inheritance
*   **Persona:** Inheritance = 0 or None.
*   **Expected Output:** No inheritance section in roadmap.

### TC59: Zero Assets + Future Inheritance (New)
*   **Persona:** 36-year-old, **$0 Assets**, $0 Income, $100k Expenses.
*   **Inheritance:** $1,000,000 at age 45.
*   **Expected Behavior:**
    -   Status: `decumulation` (not error).
    -   Runway: **0 years** (cannot survive until age 45).
    -   Withdrawal Rate: **Infinite (Assets Depleted)**.
    -   Inheritance Impact: Shown, but baseline is 0.

---

## 4. Edge Cases & Error Handling

### TC5: The Overspender (No Assets)
*   **Persona:** 32-year-old, $10k invested, $60k income, $70k expenses.
*   **Expected Output:** Status "error", "Expenses exceed income".

### TC32: Zero Expenses
*   **Persona:** 30-year-old, $0 expenses.
*   **Expected Output:** FIRE Number $0. Years to FIRE 0.

### TC36: Very Young User (Age 18)
*   **Persona:** 18-year-old.
*   **Expected Output:** 50+ year projection horizon handles OK.

### TC37: Very Old User (Age 75)
*   **Persona:** 75-year-old.
*   **Expected Output:** Handles past retirement age gracefully.

### TC38: High Savings Rate (75%+)
*   **Persona:** 26-year-old, 80% savings rate.
*   **Expected Output:** Very short timeline (~5 years).

---

## 5. UI & Naming Verification

### TC16: Verbatim Roadmap
*   **Objective:** Verify Roadmap is not rewritten by LLM.
*   **Check:** Output contains `# 🔥 Your FIRE Roadmap`.

### TC40: Forever Fund Naming
*   **Objective:** Verify "Perpetual Pot" is renamed "Preservation Strategies".

---

## 6. Conversational Capabilities

### TC60: Post-Report Acknowledgement (No Re-Run)
*   **Objective:** Verify agent handles acknowledgements without re-running tools.
*   **Trigger:** User says "thanks!" or "looks great!" after report is generated.
*   **Expected Output:** Agent responds with "You're welcome!" or similar. Does NOT call `calculate_fire_projections`.

### TC61: Post-Report Follow-Up Question
*   **Objective:** Verify agent can answer questions using report context.
*   **Trigger:** User asks "what is coastfire?" or "explain my roadmap" after report.
*   **Expected Output:** Agent answers using specific numbers from the generated report.


## Detailed Test Case Descriptions

### TC10: Full Conversation Flow (End-to-End)
*   **Objective:** Test complete agent interaction from greeting to roadmap delivery.
*   **Flow Check:**
    1. **Greeting:** Agent introduces itself as FIRE Coach
    2. **Age:** "How old are you?"
    3. **Investments:** "How much do you have invested?"
    4. **Income:** "Annual income after taxes?"
    5. **Expenses:** "Annual expenses?"
    6. **Inheritance:** "Expected inheritance?"
    7. **Confirmation:** Agent summarizes inputs
    8. **Calculation:** Calls `calculate_fire_projections`
    9. **Output:** Displays full FIRE Roadmap **VERBATIM** (not summarized)
*   **Failure Conditions:**
    -   Agent asks questions out of order
    -   Agent calls tool before confirmation
    -   Agent rewrites/summarizes the roadmap output (should be verbatim)

**Manual Test:**
```bash
python -m execution.interactive_chat
# Follow conversation flow above
```

---

### TC17: House Rich, Cash Poor (Liquidity Trap)
*   **Objective:** Handle users with high Net Worth but low Liquid Assets.
*   **Persona:** 50-year-old.
*   **Liquid Assets:** $50,000 (ETF/Cash).
*   **Illiquid Assets:** $1,500,000 (Home Equity, paid off).
*   **Expenses:** $60,000/year.
*   **Income:** $40,000 (Part-time).
*   **Expected Behavior:**
    *   **Calculation:** FIRE stats based on $50k (Liquid) → **Runway < 3 years**.
    *   **Advice:** Suggest "Downsizing" or "Geographic Arbitrage" to unlock the $1.5M.
*   **Best Practice:**
    *   Never count primary residence in SWR unless monetized.
    *   "You cannot buy groceries with a bathroom."

---

### TC26: Partial Income Decumulation (Part-Time Retiree)
*   **Objective:** Handle users with some income but expenses still exceed it.
*   **Persona:** 55-year-old, part-time worker.
*   **Current Investments:** $500,000
*   **Annual Income:** $30,000 (part-time)
*   **Annual Expenses:** $60,000
*   **Expense Gap:** $30,000/year (not $60k!)
*   **Expected Behavior:**
    -   Correctly calculates gap as `expenses - income = $30k`
    -   Runway is based on $30k drawdown, not $60k
    -   Shows decumulation mode with extended runway
*   **Expected Output:**
    -   Status: "decumulation"
    -   Expense Gap: $30,000 (not $60,000)
    -   0% Runway: $500k / $30k = ~16.7 years
*   **Failure Condition:**
    -   Ignores the $30k income when calculating drawdown

**Manual Test:**
```bash
python -c "
from execution.financial_calculators import calculate_fire_projections
result = calculate_fire_projections(55, 500000, 30000, 60000)
print(f'Status: {result[\"status\"]}')
print(f'Expense Gap: \${result[\"expense_gap\"]:,.0f}')
assert result['expense_gap'] == 30000, 'BUG: Gap should be 30k not 60k!'
print('✅ PASS: Income correctly reduces drawdown')
"
```

---

## Quick Manual Test Commands

### TC33: Inheritance Accelerates Timeline
```bash
python -c "
from execution.financial_calculators import calculate_time_to_fire
y1 = calculate_time_to_fire(100000, 30000, 50000, current_age=30)
y2 = calculate_time_to_fire(100000, 30000, 50000, current_age=30, inheritance_amount=200000, inheritance_age=40)
print(f'TC33: {y1}→{y2} years ✅' if y2 < y1 else '❌')
"
```

### TC31: Negative Savings → Decumulation
```bash
python -c "
from execution.financial_calculators import calculate_fire_projections
r = calculate_fire_projections(55, 500000, 50000, 80000)
print(f'TC31: {r[\"status\"]} ✅' if r['status'] == 'decumulation' else '❌')
"
```

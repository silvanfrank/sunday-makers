# Test Cases for Investment Co-Pilot

This document outlines various user personas and scenarios to test the **Investment Co-Pilot**.

These tests ensure the agent adheres to the "Simple. Cheap. Safe. Easy." philosophy and correctly applies the "Holistic" rules (Debt, Liquidity, Legacy).

---

## How to Run Tests

### Quick Start
```bash
cd docs/Longtermtrends-Content/Agents/Investment-Co-Pilot
```

### 1. Automated Test Suite (Recommended)

Run the full testing pyramid (Unit, Integration, Content):

```bash
python3 tests/run_tests.py
```

This automates all core logic checks (TC1-16). Output verification (TC16) is fully automated.

### Run Key Tests (Copy/Paste)
```bash
# TC2: Debtor (Safety Rule)
python -c "
from execution.financial_utils import calculate_holistic_allocation
r = calculate_holistic_allocation(age=40, has_high_interest_debt=True)
print(f'TC2: {r[\"strategy\"]} ✅' if r['strategy'] == 'DEBT_PAYOFF' else '❌')
"

# TC14: Housing Adjustment
python -c "
from execution.financial_utils import calculate_holistic_allocation
renter = calculate_holistic_allocation(age=25, housing_status='rent')
owner = calculate_holistic_allocation(age=25, housing_status='own')
diff = renter['equity_pct'] - owner['equity_pct']
print(f'TC14: {diff}% Adjustment ✅' if diff == 10 and owner['housing_adjustment'] else '❌')
"

# TC4: Legacy Goal (Override)
python -c "
from execution.financial_utils import calculate_holistic_allocation
r = calculate_holistic_allocation(age=75, goal='legacy')
print(f'TC4: {r[\"equity_pct\"]}% Equity ✅' if r['equity_pct'] >= 100 else '❌')
"
```

### Interactive Testing
```bash
python -m execution.interactive_chat
```

---

## Testing Checklist

- [ ] Test Case 1: Standard Saver (Lifecycle) ✅
- [ ] Test Case 2: The Debtor (Debt Rule) ✅
- [ ] Test Case 3: The Vulnerable (Liquidity Rule) ✅
- [ ] Test Case 4: The Legacy Investor (Goal Override) ✅
- [ ] Test Case 5: European Homeowner (Region/Housing) ✅
- [ ] Test Case 6: The Speculator (Fun Bucket) ✅
- [ ] Test Case 7: The Standard Retiree (4.7% Rule) ✅
- [ ] Test Case 8: The Entrepreneur (12x Rule) ✅
- [ ] Test Case 9: The Conservative Retiree (Floor Check) ✅
- [ ] Test Case 10: Full Interview Flow ✅
- [ ] Test Case 11: 100% Speculation Edge Case ✅
- [ ] Test Case 12: Age 50 Boundary (Glide Path) ✅
- [ ] Test Case 13: Age 65 Boundary (Retirement) ✅
- [ ] Test Case 14: Housing + Aggressive + Young (Compound) ✅
- [ ] Test Case 15: Liquidity Boundary (Exact 3 Months) ✅
- [ ] Test Case 16: Verbatim IPS Output ✅
- [ ] Test Case 17: Age 18 (Youngest Adult) ✅ *Added 2026-01-20*
- [ ] Test Case 18: Age 100 (Centenarian) ✅ *Added 2026-01-20*
- [ ] Test Case 19: Zero/Negative Savings ✅ *Added 2026-01-20*
- [ ] Test Case 20: The Glide Path Matrix ✅ *Added 2026-01-22*

---

## 1. The Standard Saver (The "Easy" Path)
*   **Persona:** 25-year-old, stable job, renting, no debt, adequate savings.
*   **Goal:** Retirement (Longevity).
*   **Philosophy Check:** Should recommend the "One-Stop Shop" (Simple) and high equity for human capital growth.
*   **Expected Output:** 
    *   Strategy: `LIFECYCLE_V2`.
    *   Allocation: 100% Equity (Aggressive) or 90% (Moderate).
    *   Tickers: VT (US) or VWCE (EU).

**Manual Test:**
```bash
python -c "
from execution.financial_utils import calculate_holistic_allocation
r = calculate_holistic_allocation(age=25, risk_profile='moderate', housing_status='rent')
print(f'Strategy: {r[\"strategy\"]}')
print(f'Equity: {r[\"equity_pct\"]}%')
"
```

---

## 2. The Debtor (The "Safe" Path)
*   **Persona:** 40-year-old, homeowner, steady income, but has **high-interest debt**.
*   **Goal:** "I want to start investing."
*   **Philosophy Check:** **Safe.** Guaranteed return on debt payoff > uncertain market return.
*   **Expected Output:**
    *   Strategy: `DEBT_PAYOFF`.
    *   Allocation: **0% Equity / 0% Bonds**.
    *   Note: "Stop investing. Pay off debt first."

**Manual Test:**
```bash
python -c "
from execution.financial_utils import calculate_holistic_allocation
r = calculate_holistic_allocation(age=40, has_high_interest_debt=True)
print(f'Strategy: {r[\"strategy\"]}') # Should be DEBT_PAYOFF
"
```

---

## 3. The Vulnerable (The "Liquidity" Rule)
*   **Persona:** 30-year-old, gig economy worker, renting, **only 1 month of savings**.
*   **Goal:** "Grow my wealth."
*   **Philosophy Check:** **Safe.** Survival priority. Without a buffer, forced selling destroys wealth.
*   **Expected Output:**
    *   Strategy: `CASH_BUILDER`.
    *   Allocation: **0% Equity**.
    *   Note: "Priority Zero is survival."

**Manual Test:**
```bash
python -c "
from execution.financial_utils import calculate_holistic_allocation
r = calculate_holistic_allocation(age=30, months_savings=1)
print(f'Strategy: {r[\"strategy\"]}') # Should be CASH_BUILDER
"
```

---

## 4. The Legacy Investor (The Endowment Model)
*   **Persona:** 75-year-old, wealthy, no debt, owns home.
*   **Goal:** **Legacy** (leaving money to grandchildren).
*   **Philosophy Check:** Time horizon is the *recipient's* life, not the donor's.
*   **Expected Output:**
    *   Strategy: `LEGACY_GROWTH`.
    *   Allocation: **100% Equity** (despite age).
    *   Note: "Legacy horizon is infinite."

**Manual Test:**
```bash
python -c "
from execution.financial_utils import calculate_holistic_allocation
r = calculate_holistic_allocation(age=75, goal='legacy')
print(f'Strategy: {r[\"strategy\"]}')
print(f'Equity: {r[\"equity_pct\"]}%') # Should be 100
"
```

---

## 5. The European Homeowner (Asset Location)
*   **Persona:** 45-year-old, living in **Germany**, **Owns Home**.
*   **Goal:** Retirement.
*   **Philosophy Check:** **Simple & Cheap**. Tax domicile matters. Home is a bond-like asset.
*   **Expected Output:**
    *   **Allocation:** Equity reduced by 10% (Housing Rule).
    *   **Tickers:** **VWCE** (EU Domiciled).
    *   **Housing Adjustment:** `True`.

**Manual Test:**
```bash
python -c "
from execution.financial_utils import calculate_holistic_allocation
r = calculate_holistic_allocation(age=45, region='EU', housing_status='own')
print(f'Equity: {r[\"equity_pct\"]}%')
print(f'Housing Adj: {r[\"housing_adjustment\"]}')
"
```

---

## 6. The Speculator (Fun Bucket)
*   **Persona:** 28-year-old, wants to put **10% into Bitcoin**.
*   **Philosophy Check:** **Safe.** Standard practice is to cap speculation at 10%.
*   **Expected Output:**
    *   Fun Bucket: 10%.
    *   Core Portfolio: 90% (allocated to Equity/Bonds).
    *   Strategy: `LIFECYCLE_V2`.

**Manual Test:**
```bash
python -c "
from execution.financial_utils import calculate_holistic_allocation
r = calculate_holistic_allocation(age=28, fun_bucket_pct=10)
print(f'Fun Bucket: {r[\"fun_bucket_pct\"]}%')
print(f'Equity: {r[\"equity_pct\"]}%')
"
```

---

## 7. The Standard Retiree (4.7% Rule Check)
*   **Persona:** 68-year-old, retired.
*   **Risk Profile:** Moderate.
*   **Philosophy Check:** **Safe.** Portfolio must support a 4.7% withdrawal rate, so Equity must be >= 65%.
*   **Expected Output:**
    *   Strategy: `LIFECYCLE_V2`.
    *   Allocation: **65% Equity / 35% Bonds**.

**Manual Test:**
```bash
python -c "
from execution.financial_utils import calculate_holistic_allocation
r = calculate_holistic_allocation(age=68, risk_profile='moderate')
print(f'Equity: {r[\"equity_pct\"]}%') # Should be 65
"
```

---

## 8. The Entrepreneur (12x Rule)
*   **Persona:** 45-year-old, Self-Employed (Volatile Income), no pension.
*   **Philosophy Check:** **Safe.** Without pension floor, savings target doubles (12x income vs 6x).
*   **Expected Output (IPS):**
    *   Advisory Note in IPS: "Target 12-15x Annual Income".

**Manual Test:**
1. Run `python -m execution.interactive_chat`
2. Select "Volatile" income.
3. Check IPS output for "12x" warning.

---

## 10. The Full Interview (Integration)
*   **Objective:** Verify proper flow and variable passing.
*   **Variables:** Age 35, EU, Rent, Longevity, Aggressive, ESG=Yes.
*   **Expected Output:**
    *   Verbatim IPS.
    *   Ticker: **V3AA** (ESG Global).
    *   Table: "Maximized Equity" for Aggressive risk.

**Manual Test:**
Run `python -m execution.interactive_chat` and follow the prompt.

---

## 11. 100% Speculation (Edge Case)
*   **Persona:** User insists on 100% Bitcoin.
*   **Philosophy Check:** User autonomy preserved, but heavily warned.
*   **Expected Output:**
    *   Strategy: `SPECULATION_ONLY`.
    *   Allocation: 0% Equity / 0% Bonds / 100% Fun.
    *   Note: "WARNING: Extremely risky."

**Manual Test:**
```bash
python -c "
from execution.financial_utils import calculate_holistic_allocation
r = calculate_holistic_allocation(age=30, fun_bucket_pct=100)
print(f'Strategy: {r[\"strategy\"]}')
"
```

---

## 12. Age Boundaries
*   **Objective:** Verify glide path transitions.
*   **Test:** Age 49 vs Age 50 (Moderate).
*   **Expected:** Equity drops at age 50.

**Manual Test:**
```bash
python -c "
from execution.financial_utils import calculate_holistic_allocation
r49 = calculate_holistic_allocation(age=49, risk_profile='moderate')
r50 = calculate_holistic_allocation(age=50, risk_profile='moderate')
print(f'Age 49: {r49[\"equity_pct\"]}%')
print(f'Age 50: {r50[\"equity_pct\"]}%')
assert r49['equity_pct'] > r50['equity_pct']
print('✅ Glide path works')
"
```

---

## 20. The Glide Path Matrix (Transition Phase)
*   **Objective:** Verify the interaction between Age, Risk, and Housing during the critical "Pre-Retirement" transition phase (Age 50-65).
*   **Method:** Matrix test of 8 key scenarios.

| Scenario | Age | Risk | Housing | Logic Chain | Expected Equity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **S1** | 35 | Aggressive | Rent | Age < 55 (1.0) | **100%** |
| **S2** | 35 | Moderate | Rent | Age < 50 (0.9) | **90%** |
| **S3** | 35 | Conservative | Rent | Age < 50 (0.8) | **80%** |
| **S4** | 60 | Aggressive | Rent | Age 55-65 (0.9) | **90%** |
| **S5** | 60 | Moderate | Rent | Age 50-65 (0.75) | **75%** |
| **S6** | 60 | Conservative | Rent | Age 50-65 (0.65) | **65%** |
| **S7** | 55 | Aggressive | Own | Age 55-65 (0.9) - 0.1 (Own) | **80%** |
| **S8** | 55 | Moderate | Own | Age 50-65 (0.75) - 0.1 (Own) | **65%** |
| **S9** | 68 | Aggressive | Rent | Age 65+ (0.75 CAP) | **75%** |

**Manual Test:**
```bash
python -c "
from execution.financial_utils import calculate_holistic_allocation
matrix = [
    (35, 'aggressive', 'rent', 100), (35, 'moderate', 'rent', 90), (35, 'conservative', 'rent', 80),
    (60, 'aggressive', 'rent', 90), (60, 'moderate', 'rent', 75), (60, 'conservative', 'rent', 65),
    (55, 'aggressive', 'own_no_mortgage', 80), (55, 'moderate', 'own_no_mortgage', 65),
    (68, 'aggressive', 'rent', 75)
]
for age, risk, house, exp in matrix:
    res = calculate_holistic_allocation(age=age, risk_profile=risk, housing_status=house)
    print(f'{age}/{risk}/{house}: {res[\"equity_pct\"]} (Exp: {exp}) {\"✅\" if res[\"equity_pct\"] == exp else \"❌\"}')
"
```

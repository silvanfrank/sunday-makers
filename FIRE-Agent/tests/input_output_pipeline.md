# FIRE Agent: Input-to-Output Pipeline

**Last Updated:** January 24, 2026

This document describes the complete data flow from user input to roadmap output.

---

## 1. Input Collection (Discovery Phase)

### Questions Asked by Agent

| Group | Question | Variable | Type | Default |
|-------|----------|----------|------|---------|
| **1. Identity** | "How old are you?" | `current_age` | int | Required |
| **2. Finances** | "How much invested?" | `current_investments` | float | Required |
| **2. Finances** | "Home equity?" | `home_equity` | float | 0 |
| **2. Finances** | "Annual income after taxes?" | `annual_income` | float | Required |
| **2. Finances** | "Annual expenses?" | `annual_expenses` | float | Required |

| **3. Future Income** | "Expected inheritance?" | `inheritance_amount` | float | 0 |
| **3. Future Income** | "...at what age?" | `inheritance_age` | int | 65 |
### Derived Variables (Calculated, Not Asked)

| Variable | Formula | Purpose |
|----------|---------|---------|
| `annual_savings` | `annual_income - annual_expenses` | Yearly contribution to portfolio |
| `savings_rate` | `annual_savings / annual_income × 100` | Percentage of income saved |
| `target_retirement_age` | Always `None` (ASAP mode) | System calculates earliest retirement |

---

## 2. Processing Pipeline

```
User Inputs
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│              calculate_fire_projections()                    │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Step 1: Derive Variables                                │ │
│  │   annual_savings = income - expenses                    │ │
│  │   savings_rate = savings / income                       │ │
│  │   archetype = classify(expenses)                        │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          │                                   │
│                          ▼                                   │
│  │ Step 2: Calculate FIRE Numbers                          │ │
│  │   pure_fire = expenses / 0.047                          │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Step 3: Calculate Years to FIRE                         │ │
│  │   Year-by-year simulation with:                         │ │
│  │   - Compound growth (7%)                                │ │
│  │   - Annual savings additions                            │ │
│  │   - Inheritance injection (if applicable)               │ │
│  │   - Dynamic target (bridge changes each year)           │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Step 4: Calculate Variants                              │ │
│  │   - scenarios{}                                         │ │
│  │   - coast_fire{} (can you stop saving?)                 │ │
│  │   - power_move{} (impact of 10% expense cut)            │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                    Result Dictionary
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              data_mapper.build_roadmap_context()             │
│   Wraps dictionary into arguments (e.g. { "data": struct })  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                     Tool Arguments
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              generate_fire_roadmap()                         │
│                                                              │
│    Transforms dict → Markdown with conditional sections      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                    Markdown Roadmap
```

---

## 3. Output Variables (Result Dictionary)

### Core Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | str | "success", "error", or "decumulation" |
| `current_age` | int | User's age |
| `current_investments` | float | Starting portfolio |
| `annual_expenses` | float | Yearly spending |
| `annual_savings` | float | Yearly savings (can be negative) |
| `savings_rate` | float | Percentage (0-100) |
| `archetype` | str | "LeanFIRE", "Standard", or "FatFIRE" |

### Scenario Objects

#### `scenarios{}` (FIRE Scenarios)

| Key | Contains |
|-----|----------|
| `bengen_standard` | 4.7% SWR: `fire_number`, `years_to_fire_7pct`, `years_to_fire_5pct`, `years_to_fire_9pct` |
| `conservative` | 4.0% SWR: Same fields |
| `early_retirement` | 4.2% SWR: Same fields |

### Other Objects

| Object | Purpose | Key Fields |
|--------|---------|------------|
| `coast_fire{}` | Can stop saving? | `coast_fire` (bool), `fire_number_needed`, `future_value_at_retirement`, `surplus_or_gap` |
| `power_move{}` | 10% expense cut impact | `expense_reduction`, `new_fire_number`, `years_saved` |

---

## 4. Roadmap Sections (Conditional Logic)

### Sections That Always Appear

| Section | Content |
|---------|---------|
| **📍 Baseline FIRE Target** | Primary FIRE number, years, retirement age |
| **📐 How We Calculated This** | Formula breakdown, compound growth |
| **📊 Sensitivity Analysis** | 5%, 7%, 9% growth scenarios |
| **⚖️ Strategy Comparison** | Preservation strategies (Bengen, Early, Conservative) |
| **📉 Expense Reduction** | Power Move (10% cut impact) |
| **📝 Assumptions** | What we assumed, what we ignored |

### Conditional Sections

| Section | Condition | Content |
|---------|-----------|---------|

| **🎁 Inheritance Impact** | `inheritance_amount > 0` | Timeline comparison with/without inheritance |
| **🏠 About Home Equity** | `home_equity > 0` | Displays equity amount and strategies |
| **🏖️ CoastFIRE** | Always, but content varies | ACHIEVED / NOT YET / NOT APPLICABLE |

---

## 5. Roadmap Variants

### Status-Based Variants

| Status | Roadmap Type | Key Differences |
|--------|--------------|-----------------|
| `success` | Full Roadmap | Complete analysis with all sections |
| `error` | Error Page | Shows error message, no calculations |
| `decumulation` | Runway Analysis | Shows years until money runs out, no "Years to FIRE" |

### CoastFIRE Variants

| State | Display |
|-------|---------|
| **ACHIEVED** | Celebration message, full explanation |
| **NOT YET** | Gap amount, perspective note, explanation |
| **NOT APPLICABLE** | User already at/past retirement age |



### Inheritance Variants

| Scenario | Display |
|----------|---------|
| No inheritance | No inheritance section |
| Inheritance before FIRE (accelerates) | Timeline comparison, years saved, "🎉 accelerates retirement" |
| Inheritance before FIRE (no acceleration) | "arrives before FIRE but doesn't change timeline (extra cushion)" |
| Inheritance after FIRE | "arrives after FIRE (extra cushion)" |

---

## 6. Key Formulas

### FIRE Number
```
FIRE Number = Annual Expenses ÷ Safe Withdrawal Rate

Bengen Standard:   expenses / 0.047
Conservative:      expenses / 0.040
Early Retirement:  expenses / 0.042
```



### Years to FIRE
```
Year-by-year simulation:
1. Start with current_investments
2. Each year: portfolio = portfolio × 1.07 + annual_savings
3. If inheritance_age reached: portfolio += inheritance_amount
4. Stop when portfolio >= target
```

### CoastFIRE Check
```
Future Value = Current Investments × (1.07)^(years to retire)
CoastFIRE = (Future Value >= FIRE Number needed)
```

---

## 7. Error States

| Condition | Status | Message |
|-----------|--------|---------|
| `expenses > income` AND `investments > 0` | `decumulation` | Runway analysis mode |
| `expenses > income` AND `investments ≈ 0` | `error` | "Cannot calculate" |
| `expenses = 0` | `success` | FIRE Number = 0 (already FIRE) |
| `age > target_retirement` | `decumulation` | Runway analysis |

---

## 8. Quick Reference

### Input → Output Mapping

| Input | Affects |
|-------|---------|
| `current_age` | Years to FIRE, CoastFIRE, retirement age |
| `current_investments` | Years to FIRE, CoastFIRE |
| `annual_income` | Savings rate, years to FIRE |
| `annual_expenses` | FIRE number, all scenarios |

| `inheritance_amount` | Years to FIRE acceleration |
| `inheritance_age` | When boost is applied |
| `home_equity` | Display only (excluded from calcs) |

---

## 9. Decumulation Roadmap Structure (New Jan 2026)

When `status` is `decumulation` (expenses > income), the roadmap structure changes significantly:

### Decumulation Sections
| Section | Content |
|---------|---------|
| **Title** | "Your Decumulation Roadmap" |
| **Executive Summary** | FI Status Check (Failed/Success), Gap Analysis, Safe Withdrawal Limit |
| **Your Situation** | Current drawdown rate, total gap |
| **Portfolio Runway** | Years until exhaustion at 0%, 5%, 7%, 9% growth |
| **Inheritance Impact** | Comparison of runway *with* and *without* inheritance |
| **CoastFIRE Status** | check if current assets can coat to traditional retirement |
| **Strategy Comparison** | Decumulation rates (Standard 4.7%, Safe 4.2%, Ultra-Conservative 4.0%) |
| **Reducing Expenses** | Scenario: Impact of 10% expense cut on runway |

### Key Differences
- **No "Years to FIRE"**: Replaced by "Portfolio Runway" (Years until broke).
- **Inheritance Logic**: Checks if inheritance extends runway or makes it "Indefinite".
- **Strategy Table**: Shows "Safe Withdrawal Amount" ($) instead of "FIRE Number Needed".

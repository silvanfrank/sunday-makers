# Investment Co-Pilot: Input-to-Output Pipeline

**Last Updated:** January 2026

This document describes the complete data flow from user input to IPS document output.

---

## 1. Input Collection (Discovery Phase)

### Questions Asked by Agent

| Group | Question | Variable | Type | Default |
|-------|----------|----------|------|---------|
| **1. Identity** | "How old are you?" | `age` | int | Required |
| **1. Identity** | "Region (US or EU)?" | `region` | str | Required |
| **2. Goals** | "What is your primary goal?" | `goal` | LIQUIDITY/LONGEVITY/LEGACY | LONGEVITY |
| **3. Wealth Context** | "Do you own or rent?" | `housing_status` | OWN/RENT | RENT |
| **3. Wealth Context** | "Do you have high-interest debt?" | `has_debt` | bool | false |
| **3. Wealth Context** | "Months of savings buffer?" | `savings_months` | int | 6 |
| **3. Wealth Context** | "Is your income stable?" | `income_stability` | STABLE/VOLATILE | STABLE |
| **3. Wealth Context** | "Do you have a pension?" | `has_pension` | bool | true |
| **4. Risk Profile** | "Risk tolerance?" | `risk_profile` | AGGRESSIVE/MODERATE/CONSERVATIVE | MODERATE |
| **5. Preferences** | "What % for speculation?" | `fun_bucket_pct` | int (0-100) | 0 |
| **5. Preferences** | "Prefer ESG funds?" | `esg_preference` | bool | false |

### Derived Variables (Calculated, Not Asked)

| Variable | Formula | Purpose |
|----------|---------|---------|
| `strategy` | Rule-based (debt/liquidity/goal check) | Determines allocation approach |
| `equity_pct` | Lifecycle formula with adjustments | Core equity allocation |
| `bonds_pct` | 100 - equity_pct - fun_bucket_pct | Bond allocation |

---

## 2. Processing Pipeline

```
User Inputs
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│          calculate_holistic_allocation()                     │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Step 1: Safety Checks                                   │ │
│  │   if has_debt → DEBT_PAYOFF (0% equity)                 │ │
│  │   if savings_months < 3 → CASH_BUILDER (0% equity)      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Step 2: Determine Strategy                              │ │
│  │   goal = LEGACY → LEGACY_GROWTH (high equity)           │ │
│  │   fun_bucket = 100 → SPECULATION_ONLY                   │ │
│  │   else → LIFECYCLE_V2                                   │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Step 3: Calculate Base Equity (Lifecycle)               │ │
│  │   Age < 50: Aggressive=100%, Moderate=90%, Cons=80%     │ │
│  │   Age 50-64: Aggressive=90%, Moderate=75%, Cons=65%     │ │
│  │   Age 65+: Aggressive=80%, Moderate=65%, Cons=50%       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Step 4: Apply Adjustments                               │ │
│  │   if housing_status = OWN → equity -= 10%               │ │
│  │   if goal = LEGACY → equity = max(equity, 90%)          │ │
│  │   equity -= fun_bucket_pct                              │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                    Allocation Object
                           │
                           ▼
                            ▼
                     Allocation Object
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│          execution/data_mapper.py (Wiring)                   │
│                                                             │
│    Unpacks Allocation + User Context → IPS Generator Args   │
│    (Fixes "Logic vs Presentation" gap)                      │
│    Tested by: `test_integration.py`                         │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
                   IPS Context Dict
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              generate_ips_markdown()                         │
│                                                             │
│    Transforms Context → Formal IPS Document                  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                    Markdown IPS
```

---

## 3. Output Variables (Result Object)

### Allocation Object

| Field | Type | Description |
|-------|------|-------------|
| `strategy` | str | LIFECYCLE_V2, DEBT_PAYOFF, CASH_BUILDER, LEGACY_GROWTH, SPECULATION_ONLY |
| `equity_pct` | int | Percentage in equities (0-100) |
| `bonds_pct` | int | Percentage in bonds (0-100) |
| `fun_bucket_pct` | int | Percentage in speculation (0-100) |
| `housing_adjustment` | bool | Whether housing rule was applied |
| `notes` | list[str] | Warnings and advisories |

### ETF Recommendations (Region-based)

| Region | Equity | Bonds | ESG Equity |
|--------|--------|-------|------------|
| US | VT | LQD | ESGV (65%) + VSGX (35%) |
| EU | VWCE | LQDA or IEAA | V3AA |

*Note: Fun Bucket options include GLD/SGLD (Gold) and IBIT/BTCE (Bitcoin).*

---

## 4. IPS Document Sections

### Sections That Always Appear

| Section | Content |
|---------|---------|
| **Header** | User profile summary |
| **Investment Objective** | Goal and time horizon |
| **Asset Allocation** | Equity/Bonds/Fun breakdown |
| **Implementation** | Specific ETF recommendations |
| **Rebalancing Rules** | When and how to rebalance |
| **Panic Protocol** | Instructions for market downturns |
| **Legal Disclaimer** | Standard disclaimer |

### Conditional Sections

| Section | Condition | Content |
|---------|-----------|---------|
| **Debt Warning** | `has_debt = true` | "Stop investing. Pay off debt first." |
| **Liquidity Warning** | `savings_months < 3` | "Build 3 months buffer first." |
| **12x Savings Rule** | `income_stability = VOLATILE` | "Target 12-15x annual income for retirement" |
| **Housing Note** | `housing_status = OWN` | "Home is a bond-like asset" |
| **Fun Bucket Warning** | `fun_bucket_pct > 10` | Risk acknowledgment |

---

## 5. Strategy Variants

| Strategy | Trigger | Allocation |
|----------|---------|------------|
| `DEBT_PAYOFF` | `has_debt = true` | 0% / 0% / 0% |
| `CASH_BUILDER` | `savings_months < 3` | 0% / 0% / 0% |
| `LIQUIDITY_FOCUS` | `goal = LIQUIDITY` | 20% equity / 80% bonds |
| `LIFECYCLE_V2` | Default | Age-based glide path |
| `LEGACY_GROWTH` | `goal = LEGACY` | 90% equity minimum |
| `SPECULATION_ONLY` | `fun_bucket_pct = 100` | 0% / 0% / 100% |

---


## 6. Key Rules

### Debt Rule
```
if has_debt:
    return DEBT_PAYOFF
    advisory = "Guaranteed return on debt payoff > uncertain market return"
```

### Liquidity Rule
```
if savings_months < 3:
    return CASH_BUILDER
    advisory = "Without buffer, forced selling destroys wealth"
```

### Housing Rule
```
if housing_status == OWN:
    equity_pct -= 10
    advisory = "Home is a bond-like asset, reducing equity exposure"
```

### Lifecycle Glide Path
```
Age < 50:   Aggressive=100%, Moderate=90%, Conservative=80%
Age 50-64:  Aggressive=90%, Moderate=75%, Conservative=65%
Age 65+:    Aggressive=80%, Moderate=65%, Conservative=50%
```

---

## 7. Error States

| Condition | Handling |
|-----------|----------|
| `age < 18` | Require guardian consent note |
| `age > 100` | Cap at 100 for calculation |
| `fun_bucket_pct > 100` | Cap at 100 |
| Missing required inputs | Agent re-asks question |

---

## 8. Quick Reference

### Input → Output Mapping

| Input | Affects |
|-------|---------|
| `age` | Base equity allocation (lifecycle) |
| `region` | ETF recommendations |
| `goal` | Strategy selection (LEGACY override) |
| `housing_status` | -10% equity if OWN |
| `has_debt` | DEBT_PAYOFF strategy |
| `savings_months` | CASH_BUILDER if < 3 |
| `income_stability` | 12x savings warning |
| `risk_profile` | Equity within age band |
| `fun_bucket_pct` | Speculation allocation |
| `esg_preference` | ESG ETF recommendations |

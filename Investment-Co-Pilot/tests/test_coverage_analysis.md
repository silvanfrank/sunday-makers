# Test Case Coverage Analysis

**Date:** January 15, 2026  
**Total Test Cases:** 16

This document analyzes the Investment Co-Pilot's input variables, their edge cases, and test coverage requirements.

---

## 1. Input Variables & Their Impact

| Variable | Type | Impact on Output | Edge Cases |
|----------|------|------------------|------------|
| `age` | int | Base equity allocation (lifecycle glide path) | < 18, exactly 50, exactly 65, > 100 |
| `region` | str | ETF recommendations (US vs EU) | Invalid region |
| `goal` | enum | Strategy override (LEGACY = high equity) | LIQUIDITY, LONGEVITY, LEGACY |
| `housing_status` | enum | -10% equity if OWN | OWN, RENT |
| `has_debt` | bool | DEBT_PAYOFF strategy (0% equity) | true, false |
| `savings_months` | int | CASH_BUILDER if < 3 | 0, 1, 2, exactly 3, > 3 |
| `income_stability` | enum | 12x savings warning | STABLE, VOLATILE |
| `has_pension` | bool | Affects retirement advice | true, false |
| `risk_profile` | enum | Equity within age band | AGGRESSIVE, MODERATE, CONSERVATIVE |
| `fun_bucket_pct` | int | Speculation allocation | 0, 10, 50, 100 |
| `esg_preference` | bool | ESG ETF recommendations | true, false |

---

## 2. Current Test Coverage (31 Tests)

We have moved from manual validations to a full automated suite.

### ✅ Automated Coverage Matrix

| Category | Tests | Status | File |
|----------|-------|--------|------|
| **1. Logic (Unit)** | 19 tests | ✅ | `test_allocation.py`, `test_edge_cases.py` |
| Standard paths | TC1, TC10 | ✅ | |
| Safety rules | TC2, TC3, TC19 (Priority) | ✅ | |
| Goal overrides | TC4 (Legacy), TC22 (Liquidity) | ✅ | |
| Region handling | TC5 (EU/US) | ✅ | |
| Age boundaries | TC12 (50), TC13 (65), TC18 (18), TC23 (100) | ✅ | |
| Compound rules | TC14 (Housing+Aggressive) | ✅ | |
| **2. Wiring (Integration)** | 5 tests | ✅ | `test_integration.py` |
| Data Mapping | TC24-28 (Goal/Context Mapping) | ✅ | |
| **3. Output (E2E)** | 7 tests | ✅ | `test_ips_content.py` |
| Text Verification | TC29-35 (Exact phrasing checks) | ✅ | |

---

## 3. Test Case Summary by Feature

### Safety Rules
- Debt Rule: Stop investing if high-interest debt
- Liquidity Rule: Build 3-month buffer first
- **Priority Test:** Verified that Debt Rule > Liquidity Rule (TC19)

### Lifecycle Allocation
- Age-based glide path (Verified at ages 18, 25, 49, 50, 64, 65, 75, 100)
- Risk profile bands (Aggressive > Moderate > Conservative)

### Goal-Based Overrides
- LEGACY: High equity regardless of age
- LIQUIDITY: High bonds regardless of risk profile
- **Display Logic:** Verified that selecting Legacy correctly displays "Legacy" in IPS table (TC24)

### Integration & Wiring
- **Data Mapper:** Verified that `goal="legacy"` string becomes `{'longevity': 'Legacy'}` dict.
- **Wealth Context:** Verified that nested context objects are preserved.

---

## 4. Variable Interaction Matrix

Some edge cases only emerge from *combinations* of variables:

| Combination | Expected Behavior | Test Case | Status |
|-------------|-------------------|-----------|--------|
| `has_debt = true` + any age | DEBT_PAYOFF (0% equity) | TC2 | ✅ |
| `savings_months < 3` + any goal | CASH_BUILDER (0% equity) | TC3 | ✅ |
| `goal = LEGACY` + age 75 | LEGACY_GROWTH (90% equity) | TC4 | ✅ |
| `housing = OWN` + aggressive + young | 90% equity (100% - 10%) | TC14 | ✅ |
| `fun_bucket = 100` | SPECULATION_ONLY | TC11 | ✅ |
| `income_stability = VOLATILE` + no pension | 12x savings warning | TC8 | ✅ |
| `savings_months = 3` exactly | LIFECYCLE_V2 (NOT CASH_BUILDER) | TC15 | ✅ |
| `age = 18` (Youngest Adult) | 100% Equity | TC18 | ✅ |
| `age = 100` (Centenarian) | Legacy/Floor | TC23 | ✅ |

---

## 5. Recently Implemented

We have successfully implemented the "Missing Test Cases" from the previous audit:

- ✅ **TC17 ESG Protocol:** Verified via `test_ips_content.py`
- ✅ **TC18 Very Young:** Verified via `test_edge_cases.py`
- ✅ **TC19 Rule Priority:** Verified via `test_edge_cases.py`
- ✅ **TC20 Integration:** Verified via `test_integration.py`

---

## 6. Strategy Decision Tree

```
                     ┌─────────────────┐
                     │   has_debt?     │
                     └────────┬────────┘
                              │
                     ┌────────┴────────┐
                     ▼                 ▼
                   YES               NO
                     │                 │
              ┌──────┴──────┐   ┌──────┴──────┐
              │ DEBT_PAYOFF │   │ savings < 3? │
              │ (0% equity) │   └──────┬───────┘
              └─────────────┘          │
                              ┌────────┴────────┐
                              ▼                 ▼
                            YES               NO
                              │                 │
                       ┌──────┴──────┐   ┌──────┴──────┐
                       │ CASH_BUILDER│   │ fun = 100%? │
                       │ (0% equity) │   └──────┬──────┘
                       └─────────────┘          │
                                       ┌────────┴────────┐
                                       ▼                 ▼
                                     YES               NO
                                       │                 │
                                ┌──────┴──────┐   ┌──────┴──────┐
                                │ SPECULATION │   │ goal=LEGACY?│
                                │ (100% fun)  │   └──────┬──────┘
                                └─────────────┘          │
                                              ┌──────────┴──────────┐
                                              ▼                     ▼
                                            YES                   NO
                                              │                     │
                                       ┌──────┴──────┐       ┌──────┴──────┐
                                       │ LEGACY_GROWTH│      │ LIFECYCLE_V2│
                                       │ (90% equity) │      │ (age-based) │
                                       └──────────────┘      └─────────────┘
```

---

## 7. Summary

| Metric | Count |
|--------|-------|
| Total Automated Tests | 31 |
| Unit Tests (Logic) | 19 |
| Integration Tests (Wiring) | 5 |
| E2E Tests (Content) | 7 |
| Manual Personas | 19 |

**Coverage Status:** 🟢 Excellent. All core logic, wiring, and edge cases are covered by an automated run.

**Next Steps:**
- Add CI/CD pipeline configuration (e.g. GitHub Actions) to run `python3 tests/run_tests.py` on every PR.

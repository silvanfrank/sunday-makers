# Test Case Architecture & Recommendations

**Date:** January 15, 2026

---

## 1. Current Test Case Structure

### How Tests Work (Hybrid Approach)

The testing strategy is a **Hybrid Model** combining:
1.  **Automated Unit/Integration Tests:** 29 tests running in a custom runner (`tests/run_tests.py`).
2.  **Manual Verification:** 19 detailed personas in `test_cases.md` for human review.

```
┌─────────────────────────────────────────────────────────┐
│                    test_cases.md                         │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ TC1: Persona │  │ TC2: Persona │  │ TC16: Persona│   │
│  │ • Objective  │  │ • Objective  │  │ • Objective  │   │
│  │ • Inputs     │  │ • Inputs     │  │ • Inputs     │   │
│  │ • Expected   │  │ • Expected   │  │ • Expected   │   │
│  │ • Failure    │  │ • Failure    │  │ • Failure    │   │
│  │ • Manual Test│  │ • Manual Test│  │ • Manual Test│   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
              Copy/paste into terminal
                          │
                          ▼
              Visual inspection of output
```

### Current Workflow

1. Developer opens `test_cases.md`
2. Finds relevant test case
3. Copies the `python3 execution/calculate_allocation.py ...` command
4. Pastes into terminal
5. Reads output
6. Manually verifies ✅ or ❌

### 2. Implemented Architecture (The "Solid" Plan)

We have moved from purely manual testing to a **3-Layer Automated Suite**:

| Layer | File | Responsibility |
|-------|------|----------------|
| **1. Logic (Unit)** | `test_allocation.py` <br> `test_edge_cases.py` | Verifies math, rules (Debt/Housing), and boundaries. |
| **2. Wiring (Integration)** | `test_integration.py` | Verifies `data_mapper.py` correctly translates Agent inputs -> Generator inputs. |
| **3. Output (E2E)** | `test_ips_content.py` | Verifies the final Markdown contains correct English phrases (e.g. "High Equity"). |

All tests run via a single command:
```bash
python3 tests/run_tests.py
```

### Cons of Current Approach
- **No automation:** Must run each test manually
- **No regression detection:** Easy to miss when changes break things
- **No CI/CD integration:** Can't run on commit/deploy
- **Verbose:** Same setup code repeated across tests
- **No coverage metrics:** Don't know what % of code is tested

---

### Implemented Architecture (The 3-Layer Pyramid)

As of January 2026, we have fully implemented the **3-Layer Testing Pyramid**:

| Layer | Focus | File |
|-------|-------|------|
| **1. Unit** | Pure Logic & Rules | `test_allocation.py`, `test_edge_cases.py` |
| **2. Integration** | Wiring & Mapping | `test_integration.py` |
| **3. Content** | Final Output Quality | `test_ips_content.py` |

### Infrastructure

- **Runner:** `tests/run_tests.py` using standard `unittest` discovery.
- **Framework:** `unittest.TestCase` inheritance for all tests.

### How to Run

```bash
python3 tests/run_tests.py
```

### Future Roadmap

1. **Coverage Reporting:** Add `coverage.py` to measure effectiveness.
2. **CI/CD Integration:** Add to GitHub Actions.


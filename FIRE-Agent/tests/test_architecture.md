# Test Case Architecture & Recommendations

**Date:** January 24, 2026

---

## 1. Current Test Architecture

### The 3-Layer Testing Pyramid

```
                    ┌─────────────────┐
                    │   Integration   │ ← 1 test (Wiring)
                    └────────┬────────┘
               ┌─────────────┴─────────────┐
               │      Content Tests        │ ← 15 tests (Output)
               └─────────────┬─────────────┘
          ┌──────────────────┴──────────────────┐
          │            Unit Tests               │ ← 29 tests (Math)
          └─────────────────────────────────────┘
```

### Layer Details

| Layer | Focus | File | Tests |
|-------|-------|------|-------|
| **1. Unit** | Pure Math Logic | `test_calculators.py` | 29 |
| **2. Content** | Final Output Quality | `test_roadmap_content.py` | 15 |
| **3. Integration** | Wiring & Data Flows | `test_integration.py` | 1 |
| **Total** | | | **45** |

---

## 2. Test File Structure

```
tests/
├── run_tests.py              # Main test runner (discovers all tests)
├── test_calculators.py       # Unit tests for financial_calculators.py
├── test_roadmap_content.py   # Content tests for generate_fire_roadmap.py
├── test_integration.py       # Integration tests for data_mapper.py
├── test_cases.md             # Documentation of all test scenarios
├── test_coverage_analysis.md # Coverage analysis and metrics
├── test_architecture.md      # This file
└── input_output_pipeline.md  # Data flow documentation
```

---

## 3. How to Run Tests

### Full Suite
```bash
cd docs/Longtermtrends-Content/Agents/FIRE-Agent
python tests/run_tests.py
```

### Individual Test Files
```bash
python tests/test_calculators.py -v      # Unit tests
python tests/test_roadmap_content.py -v  # Content tests
python tests/test_integration.py -v      # Integration tests
```

### Single Test
```bash
python -m unittest tests.test_calculators.TestFinancialCalculators.test_tc1_standard_fire
```

---

## 4. Test Naming Convention

Tests follow the pattern: `test_tc{N}_{description}` where `N` is the test case number.

Examples:
- `test_tc1_standard_fire` → TC1: Standard FIRE Candidate
- `test_tc15_zero_income_decumulation` → TC15: Zero Income
- `test_tc41_no_inheritance_section_when_zero` → TC41: Inheritance = 0

Legacy tests (from before TC mapping) use descriptive names:
- `test_savings_rate`
- `test_fire_number`
- `test_coast_fire`

---

## 5. Coverage Summary

| Category | Documented | Automated | Coverage |
|----------|------------|-----------|----------|
| Core FIRE | 6 | 6 | 100% |
| Decumulation | 4 | 4 | 100% |
| Inheritance | 7 | 7 | 100% |
| Edge Cases | 5 | 5 | 100% |
| UI/Content | 3 | 3 | 100% |
| **Total** | **50** | **45** | **90%** |

---

## 6. Adding New Tests

### Step 1: Document in `test_cases.md`
Add a new TC entry with persona, inputs, and expected output.

### Step 2: Implement in Appropriate File
- **Math logic** → `test_calculators.py`
- **Output content** → `test_roadmap_content.py`
- **Data flow** → `test_integration.py`

### Step 3: Follow Naming Convention
```python
def test_tc99_new_scenario(self):
    """TC99: Description of new scenario."""
    result = calculate_fire_projections(...)
    self.assertEqual(result["expected_field"], expected_value)
```

### Step 4: Run and Verify
```bash
python tests/run_tests.py
```

---

## 7. Future Roadmap

1. **CI/CD Integration:** Add GitHub Actions workflow
2. **Coverage Reporting:** Integrate `coverage.py`
3. **Performance Tests:** Add benchmarks for calculation speed
4. **Fuzz Testing:** Random input generation for edge case discovery

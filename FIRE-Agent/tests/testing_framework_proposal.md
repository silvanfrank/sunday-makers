# FIRE Agent Testing Framework Proposal

## Executive Summary
The FIRE Agent currently relies on manual testing and basic unit tests for calculators (`test_calculators.py`). To match the robustness of the Investment Co-Pilot, we propose implementing a **3-Layer Automated Testing Framework**.

This framework ensures that not only is the math correct, but the "wiring" between the AI's inputs and the final report is accurate, and the generated content (English text and tables) meets user expectations.

---

## 1. The 3-Layer Architecture

We recommended adopting the same "Pyramid" structure used successfully in the Investment Co-Pilot:

### Layer 1: Logic (Unit Tests)
*   **Focus:** Pure mathematical correctness.
*   **Current Status:** Partially implemented (`test_calculators.py`).
*   **Action:** Keep and expand. Ensure all financial formulas (Time to FIRE, Coast FIRE logic) are covered.

### Layer 2: Wiring (Integration Tests)
*   **Focus:** Bridging the gap between the LLM and the Tools.
*   **Problem:** Currently, `orchestrator.py` contains inline logic that transforms user input (e.g., "I want to retire ASAP") into tool arguments. This is hard to test.
*   **Solution:** Extract this transformation logic into a new pure module: `execution/data_mapper.py`.
*   **Test:** Create `tests/test_integration.py` to verify that specific user inputs correctly map to the expected tool parameters.

### Layer 3: Output (End-to-End Tests)
*   **Focus:** The user-facing result.
*   **Test:** Create `tests/test_roadmap_content.py`. This runs the actual generation script (`generate_fire_roadmap.py`) with fixed inputs and asserts that specific phrases, tables, or warnings appear in the final Markdown string.
*   **Example:** Verify that if "Coast FIRE" is possible, the Output explicitly says "You have reached Coast FIRE status".

---

## 2. Implementation Steps

### Phase 1: Infrastructure
1.  **Create Custom Test Runner:**
    *   Copy `run_tests.py` from the Investment Co-Pilot to `docs/Longtermtrends-Content/Agents/FIRE-Agent/tests/`.
    *   This allows running all tests with a single command: `python3 tests/run_tests.py`.

### Phase 2: Refactoring (The "Solid" Foundation)
2.  **Create `execution/data_mapper.py`:**
    *   Move the logic that builds the roadmap arguments from `orchestrator.py` into functions like `build_roadmap_context()`.
    *   This makes the logic deterministic and testable without running the full LLM chat.

3.  **Update `execution/orchestrator.py`:**
    *   Import and use the new data mapper functions.
    *   This cleans up the orchestrator code significantly.

### Phase 3: Test Creation
4.  **Create `tests/test_integration.py`:**
    *   Test cases for `build_roadmap_context`:
        *   Input: "Target Age 50" -> Output: `target_age=50`.
        *   Input: "ASAP" -> Output: `marketing_mode="aggressive"`, `target_age=None` (or calculated value).

5.  **Create `tests/test_roadmap_content.py`:**
    *   Test cases for `generate_fire_roadmap`:
        *   **Standard Path:** Verify headers like "## Financial Independence Roadmap".
        *   **Edge Case (Coast FIRE):** Inject data where Coast FIRE is true, verify the specific congratulations text appears.
        *   **Edge Case (Impossible):** Inject data where expenses > income, verify the warning section appears.

---

## 3. Comparison: Before vs. After

| Feature | Current State | Proposed State |
| :--- | :--- | :--- |
| **Math Verification** | ✅ `test_calculators.py` | ✅ `test_calculators.py` |
| **Logic/Wiring Check** | ❌ Manual only | ✅ `test_integration.py` |
| **Output Text Check** | ❌ Visual check | ✅ `test_roadmap_content.py` |
| **Test Running** | Manual `python file.py` | Automated `python run_tests.py` |

## 4. Why This Matters
This framework allows you to refactor the complex FIRE Roadmap generation code with confidence. If you break the logic for "Coast FIRE" detection or the mapping of "ASAP" goals, the test suite will catch it immediately—before the user sees it.

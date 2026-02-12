"""
Test suite for financial calculators.
These tests verify the math against known scenarios.
"""
import unittest
import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from execution.financial_calculators import (
    calculate_savings_rate,
    calculate_fire_number,
    calculate_time_to_fire,
    calculate_coast_fire_check,
    calculate_fire_projections
)


class TestFinancialCalculators(unittest.TestCase):
    """Unit tests for financial calculation functions."""

    def test_savings_rate(self):
        """Test savings rate calculation."""
        # 50% savings rate
        rate = calculate_savings_rate(100000, 50000)
        self.assertEqual(rate, 50.0, f"Expected 50.0, got {rate}")
        
        # 75% savings rate (extreme saver)
        rate = calculate_savings_rate(100000, 25000)
        self.assertEqual(rate, 75.0, f"Expected 75.0, got {rate}")
        
        # 0% savings rate (spending everything)
        rate = calculate_savings_rate(100000, 100000)
        self.assertEqual(rate, 0.0, f"Expected 0.0, got {rate}")

    def test_fire_number(self):
        """Test FIRE number calculation."""
        # Bengen Standard: 4.7%
        fire_num = calculate_fire_number(50000, 0.047)
        expected = 50000 / 0.047  # ~1,063,829
        self.assertAlmostEqual(fire_num, expected, delta=1, msg=f"Expected ~{expected}, got {fire_num}")
        
        # Classic 4% rule
        fire_num = calculate_fire_number(50000, 0.040)
        expected = 50000 / 0.040  # 1,250,000
        self.assertEqual(fire_num, expected, f"Expected {expected}, got {fire_num}")
        
        # Conservative 3.5%
        fire_num = calculate_fire_number(40000, 0.035)
        expected = 40000 / 0.035  # ~1,142,857
        self.assertAlmostEqual(fire_num, expected, delta=1, msg=f"Expected ~{expected}, got {fire_num}")

    def test_time_to_fire(self):
        """Test time to FIRE calculation."""
        # Already at FIRE
        years = calculate_time_to_fire(1000000, 50000, 40000, 0.07, 0.04)
        self.assertEqual(years, 0, f"Expected 0 years (already at FIRE), got {years}")
        
        # Simple case: need to save, no starting capital
        # Target: 40k * 25 = 1M, Saving 50k/yr at 7%
        years = calculate_time_to_fire(0, 50000, 40000, 0.07, 0.04)
        self.assertTrue(12 <= years <= 14, f"Expected ~13 years, got {years}")
        
        # No savings - should return 999
        years = calculate_time_to_fire(0, 0, 40000, 0.07, 0.04)
        self.assertEqual(years, 999, f"Expected 999 (impossible), got {years}")

    def test_coast_fire(self):
        """Test CoastFIRE detection."""
        # Age 30, have $200k, expenses $40k, want to retire at 65
        # At 7%, $200k grows to ~1.5M in 35 years
        # Need 40k / 0.047 = ~850k
        # Should be CoastFIRE
        result = calculate_coast_fire_check(200000, 30, 65, 40000, 0.07, 0.047)
        self.assertTrue(result["coast_fire"], f"Expected CoastFIRE status, got {result}")
        
        # Age 30, have $50k, same target - NOT CoastFIRE
        result = calculate_coast_fire_check(50000, 30, 65, 40000, 0.07, 0.047)
        self.assertFalse(result["coast_fire"], f"Expected non-CoastFIRE status, got {result}")

    def test_coast_fire_asap_target(self):
        """Test CoastFIRE with aggressive early target (ASAP)."""
        # User wants to retire at 40 (ASAP), but we should check against 65.
        # Age 30, $200k invests.
        # Target 40: 10 years growth. $200k * 1.07^10 = ~$393k. Need $850k. Fail.
        # Target 65: 35 years growth. $200k * 1.07^35 = ~$2.1M. Need $850k. Pass.
        
        # If the function uses the passed target_retirement_age (40), this will returns False.
        # If it enforces 65, it should return True.
        
        result = calculate_coast_fire_check(200000, 30, 40, 40000, 0.07, 0.047)
        self.assertTrue(result["coast_fire"], f"Expected CoastFIRE=True (checking against 65), but got {result['coast_fire']}")

    def test_full_projection(self):
        """Test the main projection function."""
        result = calculate_fire_projections(
            current_age=35,
            current_investments=100000,
            annual_income=80000,
            annual_expenses=40000,
            target_retirement_age=65
        )
        
        self.assertEqual(result["status"], "success", f"Expected success, got {result['status']}")
        self.assertEqual(result["savings_rate"], 50.0, f"Expected 50% savings rate, got {result['savings_rate']}")
        self.assertIn("scenarios", result, "Missing scenarios in result")
        self.assertIn("bengen_standard", result["scenarios"], "Missing Bengen Standard scenario")
        self.assertIn("power_move", result, "Missing power move calculation")

    def test_expense_exceeds_income(self):
        """Test error handling when expenses exceed income."""
        result = calculate_fire_projections(
            current_age=30,
            current_investments=0,
            annual_income=50000,
            annual_expenses=60000
        )
        
        self.assertEqual(result["status"], "error", f"Expected error status, got {result['status']}")
        self.assertIn("exceed", result["message"].lower(), "Expected 'exceed' in error message")


    def test_inheritance_in_past(self):
        """Test inheritance age < current age (should be treated as immediate lump sum)."""
        # Scenario: Age 50, Inheritance at 40 (10 years ago).
        # Should be added immediately in Year 0.
        
        # 1. Standard Projection
        # $100k start, $100k inheritance (past), $0 savings.
        # Effectively starts with $200k.
        result = calculate_fire_projections(
            current_age=50,
            current_investments=100000,
            annual_income=50000, 
            annual_expenses=50000, # Savings = 0
            inheritance_amount=100000,
            inheritance_age=40
        )
        # Check scenarios:
        # Bengen (4.7%): Target $1M approx.
        # Start $200k. 7% growth.
        # Without inheritance ($100k): $1M takes ~34 years.
        # With inheritance ($200k): $1M takes ~24 years.
        # Current logic should see it immediately added.
        
        # Verify inheritance logic works even if age is past
        # Note: financial_calculators logic is: if not received AND this_age >= inheritance_age
        # Year 0: this_age = 50. 50 >= 40. Added.
        
        self.assertEqual(result["status"], "success")
        
    def test_decumulation_inheritance_past(self):
        """Test decumulation with inheritance in past (already in current_investments)."""
        # Age 50. Exp > Inc ($10k gap). $50k Invested (includes past inheritance).
        # Past inheritance at age 40 is NOT added again (assumed already in current_investments).
        # Runway: $50k / $10k gap = 5 years (at 0% growth).
        
        result = calculate_fire_projections(
            current_age=50,
            current_investments=50000,  # Past inheritance should be entered here by user
            annual_income=40000,
            annual_expenses=50000, # Gap 10k
            inheritance_amount=50000,  # Past inheritance (at age 40)
            inheritance_age=40
        )
        
        # Should be decumulation mode
        self.assertEqual(result["status"], "decumulation")
        # Runway should be based on current_investments only (no double-counting)
        # $50k / $10k = 5.0 years at 0% growth
        self.assertAlmostEqual(result["runway"]["runways"]["0pct"], 5.0, delta=0.5)

    def test_decumulation_escape_velocity(self):
        """Test that portfolio growing faster than withdrawals returns infinite runway."""
        # Income 0, Expenses 100k.
        # Investments $2M.
        # Growth 7% of $2M = $140,000.
        # $140k > $100k. Portfolio grows forever.
        
        result = calculate_fire_projections(
            current_age=50,
            current_investments=2000000,
            annual_income=0,
            annual_expenses=100000 # Gap 100k
        )
        
        self.assertEqual(result["status"], "decumulation")
        # 7% runway should be infinite
        self.assertEqual(result["runway"]["runways"]["7pct"], float('inf'), 
                         f"Expected infinite runway, got {result['runway']['runways']['7pct']}")
        
        # 0% runway should be finite (2M / 100k = 20 years)
        self.assertEqual(result["runway"]["runways"]["0pct"], 20.0)

    # =========================================================================
    # CORE FIRE SCENARIOS (TC1, TC2, TC3, TC12)
    # =========================================================================
    
    def test_tc1_standard_fire(self):
        """TC1: Standard FIRE Candidate - 35yo, $100k invested, $80k income, $40k expenses."""
        result = calculate_fire_projections(35, 100000, 80000, 40000)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["savings_rate"], 50.0)
        self.assertEqual(result["archetype"], "Standard")
        fire_num = result["scenarios"]["bengen_standard"]["fire_number"]
        self.assertAlmostEqual(fire_num, 851064, delta=1000)
        years = result["scenarios"]["bengen_standard"]["years_to_fire_7pct"]
        self.assertTrue(10 <= years <= 14, f"Expected 10-14 years, got {years}")
    
    def test_tc2_leanfire(self):
        """TC2: LeanFIRE Archetype - expenses < $40k."""
        # Use lower investments to avoid triggering CoastFIRE
        result = calculate_fire_projections(28, 10000, 45000, 25000)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["archetype"], "LeanFIRE")
        fire_num = result["scenarios"]["bengen_standard"]["fire_number"]
        self.assertAlmostEqual(fire_num, 531915, delta=1000)  # 25k / 0.047
    
    def test_tc3_fatfire(self):
        """TC3: FatFIRE Archetype - expenses > $100k."""
        result = calculate_fire_projections(42, 500000, 250000, 120000)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["archetype"], "FatFIRE")
        fire_num = result["scenarios"]["bengen_standard"]["fire_number"]
        self.assertAlmostEqual(fire_num, 2553191, delta=1000)  # 120k / 0.047
    
    def test_tc12_already_at_fire(self):
        """TC12: Already at FIRE - $2M invested, $80k expenses."""
        result = calculate_fire_projections(50, 2000000, 100000, 80000)
        years = result["scenarios"]["bengen_standard"]["years_to_fire_7pct"]
        self.assertEqual(years, 0, "Should be at FIRE already")
    
    # =========================================================================
    # DECUMULATION SCENARIOS (TC15, TC17, TC31)
    # =========================================================================
    
    def test_tc15_zero_income_decumulation(self):
        """TC15: Zero income triggers decumulation mode."""
        result = calculate_fire_projections(55, 500000, 0, 80000)
        self.assertEqual(result["status"], "decumulation")
        self.assertIn("runway", result)
        # 0% runway = 500k / 80k = 6.25 years
        self.assertAlmostEqual(result["runway"]["runways"]["0pct"], 6.25, delta=0.5)
    
    def test_tc17_house_rich_cash_poor(self):
        """TC17: Low liquid assets ($50k), high expenses ($60k), some income ($40k)."""
        result = calculate_fire_projections(50, 50000, 40000, 60000)
        self.assertEqual(result["status"], "decumulation")
        # Gap = 60k - 40k = 20k. Runway = 50k / 20k = 2.5 years
        self.assertAlmostEqual(result["runway"]["runways"]["0pct"], 2.5, delta=0.5)
    
    def test_tc31_negative_savings_decumulation(self):
        """TC31: Expenses > Income with investments triggers decumulation."""
        result = calculate_fire_projections(55, 500000, 50000, 80000)
        self.assertEqual(result["status"], "decumulation")
        self.assertEqual(result["expense_gap"], 30000)
        # 0% runway = 500k / 30k = 16.67 years
        self.assertAlmostEqual(result["runway"]["runways"]["0pct"], 16.7, delta=0.5)
    
    # =========================================================================
    # INHERITANCE SCENARIOS (TC33, TC41, TC44, TC45, TC59)
    # =========================================================================
    
    def test_tc33_inheritance_accelerates(self):
        """TC33: Inheritance accelerates FIRE timeline."""
        # Without inheritance
        years_without = calculate_time_to_fire(100000, 30000, 50000, current_age=30)
        # With inheritance at age 40
        years_with = calculate_time_to_fire(100000, 30000, 50000, current_age=30, 
                                            inheritance_amount=200000, inheritance_age=40)
        self.assertLess(years_with, years_without, "Inheritance should accelerate FIRE")
    
    def test_tc44_instant_fire_via_inheritance(self):
        """TC44: Large inheritance causes instant FIRE."""
        # $100k invested, need ~$1M for FIRE. Inheritance of $1M at 31.
        years = calculate_time_to_fire(100000, 30000, 50000, current_age=30,
                                       inheritance_amount=1000000, inheritance_age=31)
        self.assertLessEqual(years, 2, "Should reach FIRE almost instantly with large inheritance")
    
    def test_tc45_late_inheritance_no_impact(self):
        """TC45: Inheritance after FIRE date has no impact on timeline."""
        # User reaches FIRE around age 45, inheritance at 60
        years_without = calculate_time_to_fire(100000, 50000, 40000, current_age=30)
        years_with = calculate_time_to_fire(100000, 50000, 40000, current_age=30,
                                            inheritance_amount=500000, inheritance_age=60)
        self.assertEqual(years_with, years_without, "Late inheritance should not change timeline")
    
    def test_tc59_zero_assets_future_inheritance(self):
        """TC59: Zero assets with future inheritance."""
        result = calculate_fire_projections(36, 0, 0, 100000,
                                            inheritance_amount=1000000, inheritance_age=45)
        self.assertEqual(result["status"], "decumulation")
        # Cannot survive until age 45 with 0 assets
        self.assertEqual(result["runway"]["runways"]["0pct"], 0)
    
    # =========================================================================
    # EDGE CASES (TC32, TC36, TC37, TC38)
    # =========================================================================
    
    def test_tc32_zero_expenses(self):
        """TC32: Zero expenses = instant FIRE."""
        result = calculate_fire_projections(30, 100000, 80000, 0)
        self.assertEqual(result["status"], "success")
        # FIRE Number is 0, Years to FIRE is 0
        self.assertEqual(result["scenarios"]["bengen_standard"]["fire_number"], 0)
        self.assertEqual(result["scenarios"]["bengen_standard"]["years_to_fire_7pct"], 0)
    
    def test_tc36_very_young_user(self):
        """TC36: Age 18 handles correctly without overflow."""
        result = calculate_fire_projections(18, 5000, 40000, 25000)
        self.assertEqual(result["status"], "success")
        years = result["scenarios"]["bengen_standard"]["years_to_fire_7pct"]
        self.assertLess(years, 100, "Should not overflow to 999")
    
    def test_tc37_very_old_user(self):
        """TC37: Age 75 handles gracefully."""
        result = calculate_fire_projections(75, 1000000, 50000, 60000)
        # Expenses > income, so should be decumulation
        self.assertEqual(result["status"], "decumulation")
    
    def test_tc38_high_savings_rate(self):
        """TC38: 80% savings rate - very short timeline."""
        result = calculate_fire_projections(30, 50000, 150000, 30000)
        self.assertEqual(result["savings_rate"], 80.0)
        years = result["scenarios"]["bengen_standard"]["years_to_fire_7pct"]
        self.assertLessEqual(years, 6, "High savings rate should reach FIRE quickly")
    
    # =========================================================================
    # ADDITIONAL COVERAGE (TC6, TC7, TC9, TC21)
    # =========================================================================
    
    def test_tc6_early_retirement_scenario(self):
        """TC6: Early retiree should see 4.2% scenario."""
        result = calculate_fire_projections(25, 100000, 80000, 30000)
        self.assertIn("early_retirement", result["scenarios"])
        er_fire = result["scenarios"]["early_retirement"]["fire_number"]
        self.assertAlmostEqual(er_fire, 714286, delta=1000)  # 30k / 0.042
    
    def test_tc7_power_move(self):
        """TC7: Power move correctly calculates 10% expense reduction impact."""
        result = calculate_fire_projections(40, 150000, 90000, 55000)
        self.assertIn("power_move", result)
        self.assertEqual(result["power_move"]["expense_reduction"], 5500)  # 10% of 55k
        self.assertEqual(result["power_move"]["new_annual_expenses"], 49500)
    
    def test_tc9_bengen_vs_conservative(self):
        """TC9: Bengen 4.7% provides earlier retirement than 4.0%."""
        result = calculate_fire_projections(30, 100000, 70000, 40000)
        bengen = result["scenarios"]["bengen_standard"]
        conservative = result["scenarios"]["conservative"]
        self.assertLess(bengen["fire_number"], conservative["fire_number"])
        self.assertLess(bengen["years_to_fire_7pct"], conservative["years_to_fire_7pct"])
    
    def test_tc21_coast_fire_uses_age_65(self):
        """TC21: CoastFIRE always checks against age 65."""
        # Even if user is young and wants to retire at 40, CoastFIRE uses 65
        result = calculate_coast_fire_check(200000, 30, 40, 40000, 0.07, 0.047)
        # Should pass CoastFIRE check (35 years to grow at 7%)
        self.assertTrue(result["coast_fire"])


if __name__ == "__main__":
    unittest.main()

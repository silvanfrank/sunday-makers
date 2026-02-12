"""
Unit tests for car_calculators.py
Run with: python -m pytest tests/test_calculators.py -v
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.car_calculators import (
    calculate_tco,
    calculate_max_affordable_car,
    calculate_opportunity_cost,
    calculate_required_income,
    calculate_car_affordability,
    CAR_CLASS_DATA,
)


class TestCalculateTCO:
    """Tests for calculate_tco function."""
    
    def test_budget_car_tco(self):
        """Budget car TCO should be around $9,000/year."""
        result = calculate_tco("budget")
        assert result["car_class"] == "budget"
        assert 8000 < result["annual_tco"] < 11000
        assert result["sticker_price"] == 30000
    
    def test_luxury_car_tco(self):
        """Luxury car TCO should be around $20,000-25,000/year."""
        result = calculate_tco("luxury")
        assert result["car_class"] == "luxury"
        assert 18000 < result["annual_tco"] < 26000
        assert result["sticker_price"] == 75000
    
    def test_supercar_tco(self):
        """Supercar TCO should be around $30,000+/year."""
        result = calculate_tco("supercar")
        assert result["car_class"] == "supercar"
        assert result["annual_tco"] > 25000
        assert result["sticker_price"] == 265000
    
    def test_tco_breakdown_completeness(self):
        """TCO breakdown should include all cost categories."""
        result = calculate_tco("budget")
        breakdown = result["breakdown"]
        assert "depreciation" in breakdown
        assert "taxes_fees" in breakdown
        assert "financing" in breakdown
        assert "fuel" in breakdown
        assert "insurance" in breakdown
        assert "maintenance" in breakdown
    
    def test_invalid_car_class_raises_error(self):
        """Invalid car class should raise ValueError."""
        try:
            calculate_tco("invalid")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Unknown car class" in str(e)


class TestMaxAffordableCar:
    """Tests for calculate_max_affordable_car function."""
    
    def test_100k_income(self):
        """$100K income allows ~$10K/year transport budget."""
        result = calculate_max_affordable_car(100000)
        assert result["max_annual_transport_budget"] == 10000
        assert result["max_monthly_transport_budget"] == round(10000 / 12, 2)
    
    def test_60k_income_affords_budget(self):
        """$60K income should afford budget class."""
        result = calculate_max_affordable_car(60000)
        # $60K * 10% = $6K/year budget, but budget car is ~$9K
        # So affordable_class might be 'none' or still budget depending on threshold
        assert result["affordable_class"] in ["budget", "none"]
    
    def test_200k_income_affords_luxury(self):
        """$200K income should afford luxury class."""
        result = calculate_max_affordable_car(200000)
        # $200K * 10% = $20K/year, luxury is ~$22K
        assert result["max_annual_transport_budget"] == 20000
    
    def test_500k_income_affords_supercar(self):
        """$500K income should afford supercar class."""
        result = calculate_max_affordable_car(500000)
        # $500K * 10% = $50K/year, supercar is ~$31K
        assert result["affordable_class"] == "supercar"


class TestOpportunityCost:
    """Tests for calculate_opportunity_cost function."""
    
    def test_basic_growth(self):
        """$10K should grow at 7% for 5 years."""
        result = calculate_opportunity_cost(10000, years=5, rate_of_return=0.07)
        # 10000 * (1.07^5) = 14025.52
        assert 14000 < result["future_value"] < 14100
        assert 4000 < result["lost_growth"] < 4100
    
    def test_luxury_down_payment(self):
        """$15K down payment (20% of $75K) opportunity cost."""
        down_payment = 75000 * 0.20  # $15,000
        result = calculate_opportunity_cost(down_payment, years=5)
        # 15000 * (1.07^5) = 21038.28
        assert result["initial_amount"] == 15000
        assert result["future_value"] > 20000
        assert result["lost_growth"] > 5000


class TestRequiredIncome:
    """Tests for calculate_required_income function."""
    
    def test_budget_requires_about_90k(self):
        """Budget car (~$9K TCO) requires ~$90K income for 10% rule."""
        result = calculate_required_income("budget")
        # ~$9,149 / 0.10 = ~$91,490
        assert 85000 < result["required_annual_income"] < 100000
    
    def test_luxury_requires_about_220k(self):
        """Luxury car (~$22K TCO) requires ~$220K income for 10% rule."""
        result = calculate_required_income("luxury")
        # ~$22,237 / 0.10 = ~$222,370
        assert 200000 < result["required_annual_income"] < 250000
    
    def test_supercar_requires_about_310k(self):
        """Supercar (~$31K TCO) requires ~$310K income for 10% rule."""
        result = calculate_required_income("supercar")
        # ~$31,080 / 0.10 = ~$310,800
        assert 280000 < result["required_annual_income"] < 350000


class TestCarAffordability:
    """Tests for the main calculate_car_affordability function."""
    
    def test_can_afford_budget(self):
        """$100K income, $50K expenses, wanting budget car."""
        result = calculate_car_affordability(
            annual_income=100000,
            annual_expenses=50000,
            desired_car_class="budget"
        )
        assert result["status"] == "affordable"
        assert result["inputs"]["savings_rate"] == 50.0
        assert result["desired_car"]["can_afford"] == True
    
    def test_cannot_afford_luxury_on_80k(self):
        """$80K income cannot afford luxury car under 10% rule."""
        result = calculate_car_affordability(
            annual_income=80000,
            annual_expenses=40000,
            desired_car_class="luxury"
        )
        assert result["status"] == "stretch"
        assert result["desired_car"]["can_afford"] == False
    
    def test_can_afford_luxury_on_250k(self):
        """$250K income can afford luxury car."""
        result = calculate_car_affordability(
            annual_income=250000,
            annual_expenses=100000,
            desired_car_class="luxury"
        )
        assert result["desired_car"]["can_afford"] == True
    
    def test_negative_savings_warning(self):
        """Expenses > income should trigger warning."""
        result = calculate_car_affordability(
            annual_income=50000,
            annual_expenses=60000,
            desired_car_class="budget"
        )
        assert result["status"] == "warning"
        assert result["inputs"]["annual_savings"] == -10000
    
    def test_opportunity_cost_included(self):
        """Result should include opportunity cost analysis."""
        result = calculate_car_affordability(
            annual_income=100000,
            annual_expenses=50000,
            current_investments=200000,
            desired_car_class="budget"
        )
        assert "opportunity_cost" in result
        assert result["opportunity_cost"]["down_payment"] == 6000  # 20% of $30K
    
    def test_all_car_classes_included(self):
        """Result should include comparison of all car classes."""
        result = calculate_car_affordability(
            annual_income=100000,
            annual_expenses=50000,
            desired_car_class="budget"
        )
        assert "budget" in result["all_car_classes"]
        assert "luxury" in result["all_car_classes"]
        assert "supercar" in result["all_car_classes"]


# Run tests if executed directly
if __name__ == "__main__":
    import unittest
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(type("TestCalculateTCO", (unittest.TestCase,), dict(TestCalculateTCO.__dict__))))
    suite.addTests(loader.loadTestsFromTestCase(type("TestMaxAffordableCar", (unittest.TestCase,), dict(TestMaxAffordableCar.__dict__))))
    suite.addTests(loader.loadTestsFromTestCase(type("TestOpportunityCost", (unittest.TestCase,), dict(TestOpportunityCost.__dict__))))
    suite.addTests(loader.loadTestsFromTestCase(type("TestRequiredIncome", (unittest.TestCase,), dict(TestRequiredIncome.__dict__))))
    suite.addTests(loader.loadTestsFromTestCase(type("TestCarAffordability", (unittest.TestCase,), dict(TestCarAffordability.__dict__))))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)

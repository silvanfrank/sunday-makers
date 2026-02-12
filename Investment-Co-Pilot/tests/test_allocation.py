"""
test_allocation.py

Automated tests for Investment Co-Pilot allocation logic.
Maps to test_cases.md TC1-16.
"""
# import pytest (Removed for dependency-free execution)
import sys
import unittest
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.financial_utils import calculate_holistic_allocation


class TestSafetyRules(unittest.TestCase):
    """TC2, TC3: Debt and Liquidity rules - highest priority"""
    
    def test_debt_triggers_debt_payoff(self):
        """TC2: High-interest debt should stop investing"""
        result = calculate_holistic_allocation(
            age=40, 
            has_high_interest_debt=True
        )
        assert result['strategy'] == 'DEBT_PAYOFF'
        assert result['equity_pct'] == 0
        assert result['bonds_pct'] == 0
    
    def test_low_savings_triggers_cash_builder(self):
        """TC3: < 3 months savings should build buffer first"""
        result = calculate_holistic_allocation(
            age=30, 
            months_savings=1
        )
        assert result['strategy'] == 'CASH_BUILDER'
        assert result['equity_pct'] == 0
    
    def test_exactly_3_months_is_ok(self):
        """TC15: Exactly 3 months should NOT trigger CASH_BUILDER"""
        result = calculate_holistic_allocation(
            age=30,
            months_savings=3
        )
        assert result['strategy'] == 'LIFECYCLE_V2'
        assert result['equity_pct'] > 0


class TestLifecycle(unittest.TestCase):
    """TC1, TC12, TC13: Age-based allocation"""
    
    def test_young_aggressive_gets_100_equity(self):
        """TC1: 25yo aggressive should get 100% equity"""
        result = calculate_holistic_allocation(age=25, risk_profile='aggressive')
        assert result['equity_pct'] == 100
        assert result['bonds_pct'] == 0
        assert result['strategy'] == 'LIFECYCLE_V2'
    
    def test_age_50_boundary(self):
        """TC12: Equity should drop at age 50"""
        r49 = calculate_holistic_allocation(age=49, risk_profile='moderate')
        r50 = calculate_holistic_allocation(age=50, risk_profile='moderate')
        assert r49['equity_pct'] > r50['equity_pct']
    
    def test_age_65_boundary(self):
        """TC13: Equity should drop at age 65"""
        r64 = calculate_holistic_allocation(age=64, risk_profile='moderate')
        r65 = calculate_holistic_allocation(age=65, risk_profile='moderate')
        assert r64['equity_pct'] > r65['equity_pct']
    
    def test_aggressive_retiree_cap(self):
        """Verify that aggressive retirees (65+) are capped at 75% equity"""
        result = calculate_holistic_allocation(age=68, risk_profile='aggressive', housing_status='rent')
        assert result['equity_pct'] == 75, f"Expected 75%, got {result['equity_pct']}%"


class TestHousing(unittest.TestCase):
    """TC14: Housing adjustment"""
    
    def test_homeowner_reduces_equity(self):
        """TC14: Homeowner should have 10% less equity"""
        renter = calculate_holistic_allocation(
            age=25, risk_profile='aggressive', 
            housing_status='rent'
        )
        owner = calculate_holistic_allocation(
            age=25, risk_profile='aggressive', 
            housing_status='own'  # Or 'own_no_mortgage'
        )
        assert renter['equity_pct'] - owner['equity_pct'] == 10
        assert owner['housing_adjustment'] == True
        assert renter['housing_adjustment'] == False


class TestGoals(unittest.TestCase):
    """TC4: Goal-based overrides"""
    
    def test_legacy_gets_high_equity(self):
        """TC4: Legacy goal should get 90% equity regardless of age"""
        result = calculate_holistic_allocation(age=75, goal='legacy')
        assert result['strategy'] == 'LEGACY_GROWTH'
        assert result['equity_pct'] == 100


class TestFunBucket(unittest.TestCase):
    """TC6, TC11: Speculation allocation"""
    
    def test_100_percent_fun_bucket(self):
        """TC11: 100% fun bucket should be SPECULATION_ONLY"""
        result = calculate_holistic_allocation(age=30, fun_bucket_pct=100)
        assert result['strategy'] == 'SPECULATION_ONLY'
        assert result['fun_bucket_pct'] == 100
        assert result['equity_pct'] == 0


class TestRelationships(unittest.TestCase):
    """Relationship tests - verify internal consistency"""
    
    def test_risk_ordering(self):
        """More aggressive = more equity (same age)"""
        cons = calculate_holistic_allocation(age=40, risk_profile='conservative')
        mod = calculate_holistic_allocation(age=40, risk_profile='moderate')
        agg = calculate_holistic_allocation(age=40, risk_profile='aggressive')
        
        assert agg['equity_pct'] > mod['equity_pct'] > cons['equity_pct']
    
    def test_age_reduces_equity(self):
        """Older = less equity (same risk profile)"""
        young = calculate_holistic_allocation(age=25, risk_profile='moderate')
        mid = calculate_holistic_allocation(age=55, risk_profile='moderate')
        old = calculate_holistic_allocation(age=70, risk_profile='moderate')
        
        assert young['equity_pct'] >= mid['equity_pct'] >= old['equity_pct']
    
    def test_homeowner_never_increases_equity(self):
        """Housing rule should never INCREASE equity at any age"""
        for age in [25, 40, 50, 65, 75]:
            renter = calculate_holistic_allocation(
                age=age, 
                housing_status='rent'
            )
            owner = calculate_holistic_allocation(
                age=age, 
                housing_status='own'
            )
            assert owner['equity_pct'] <= renter['equity_pct'], f"Failed at age {age}"


# if __name__ == "__main__":
#     pytest.main([__file__, "-v"])

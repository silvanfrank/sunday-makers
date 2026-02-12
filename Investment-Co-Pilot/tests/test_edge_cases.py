"""
test_edge_cases.py

Robustness tests for Investment Co-Pilot.
Focuses on rule conflicts, boundary conditions, and override logic.
"""
import sys
import unittest
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.financial_utils import calculate_holistic_allocation


class TestRulePriority(unittest.TestCase):
    """Verify which rule wins when multiple triggers are present"""
    
    def test_debt_trumps_liquidity(self):
        """
        Scenario: User has high interest debt AND < 3 months savings.
        Expected: DEBT_PAYOFF (Rule 1) should win over CASH_BUILDER (Rule 2).
        Reasoning: High interest debt is a guaranteed negative return.
        """
        result = calculate_holistic_allocation(
            age=30,
            has_high_interest_debt=True,
            months_savings=1  # Also triggers liquidity rule
        )
        assert result['strategy'] == 'DEBT_PAYOFF'
        assert result['equity_pct'] == 0


class TestGoalOverrides(unittest.TestCase):
    """Verify that Goal trumps Risk Profile"""
    
    def test_liquidity_goal_overrides_aggressive_risk(self):
        """
        Scenario: User wants money in 2 years (Liquidity) but is Aggressive.
        Expected: LIQUIDITY_FOCUS (20% Equity)
        Reasoning: Time horizon forces safety regardless of psychological risk tolerance.
        """
        result = calculate_holistic_allocation(
            age=30,
            goal='liquidity',
            risk_profile='aggressive'
        )
        assert result['strategy'] == 'LIQUIDITY_FOCUS'
        assert result['equity_pct'] <= 25  # Should be low
    
    def test_legacy_goal_overrides_conservative_risk(self):
        """
        Scenario: User wants Legacy (Growth) but is Conservative.
        Expected: LEGACY_GROWTH (90% Equity)
        Reasoning: Endowment model horizon overrides personal risk aversion.
        """
        result = calculate_holistic_allocation(
            age=70,
            goal='legacy',
            risk_profile='conservative'
        )
        assert result['strategy'] == 'LEGACY_GROWTH'
        assert result['equity_pct'] == 100


class TestBoundaries(unittest.TestCase):
    """Verify edge values for inputs"""
    
    def test_age_18_youngest_adult(self):
        """
        Scenario: 18 year old.
        Expected: Max equity (LifeCycle).
        """
        result = calculate_holistic_allocation(age=18, risk_profile='aggressive')
        assert result['strategy'] == 'LIFECYCLE_V2'
        assert result['equity_pct'] == 100
    
    def test_age_100_centenarian(self):
        """
        Scenario: 100 year old.
        Expected: Minimum equity floor (Legacy logic might apply if goal changed, but standard is floor).
        """
        result = calculate_holistic_allocation(age=100, risk_profile='conservative')
        assert result['strategy'] == 'LIFECYCLE_V2'
        assert result['equity_pct'] == 50  # Conservative floor
    
    def test_zero_savings(self):
        """
        Scenario: 0 months savings.
        Expected: CASH_BUILDER.
        """
        result = calculate_holistic_allocation(age=30, months_savings=0)
        assert result['strategy'] == 'CASH_BUILDER'
        assert result['equity_pct'] == 0

    def test_negative_savings(self):
        """
        Scenario: -1 savings (logic error or debt representation).
        Expected: CASH_BUILDER (since -1 < 3).
        """
        result = calculate_holistic_allocation(age=30, months_savings=-1)
        assert result['strategy'] == 'CASH_BUILDER'

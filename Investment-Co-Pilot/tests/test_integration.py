"""
test_integration.py

Verifies the 'wiring' between the Agent's logic and the IPS Generator.
Ensures that data is not lost during transformation (e.g. Goal mapping).
"""
import sys
import unittest
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.data_mapper import build_ips_context


class TestDataMapper(unittest.TestCase):
    """Verifies build_ips_context logic"""
    
    def test_maps_liquidity_goal(self):
        """Verify 'liquidity' string becomes correct IPS dict"""
        args = {"goal": "liquidity"}
        alloc = {"age": 30, "region": "US"}
        
        ctx = build_ips_context(alloc, args)
        
        assert ctx["goals"] == {'liquidity': 'Short-term Goal'}
        
    def test_maps_legacy_goal(self):
        """Verify 'legacy' string becomes correct IPS dict"""
        args = {"goal": "legacy"}
        alloc = {"age": 70, "region": "EU"}
        
        ctx = build_ips_context(alloc, args)
        
        assert ctx["goals"] == {'longevity': 'Legacy'}
        
    def test_maps_default_retirement(self):
        """Verify default becomes Retirement"""
        args = {"goal": "longevity"}
        alloc = {"age": 40}
        
        ctx = build_ips_context(alloc, args)
        
        assert ctx["goals"] == {'longevity': 'Retirement'}
        
    def test_prefers_allocation_values(self):
        """Verify that values calculated by financial_utils take precedence"""
        args = {"age": 30, "region": "US"} # User input
        alloc = {"age": 31, "region": "EU"} # Calculated/Corrected
        
        ctx = build_ips_context(alloc, args)
        
        assert ctx["age"] == 31
        assert ctx["region"] == "EU"

    def test_passes_wealth_context(self):
        """Verify nested wealth context is built correctly"""
        args = {
            "housing_status": "own",
            "risk_profile": "aggressive",
            "has_high_interest_debt": True
        }
        alloc = {"income_stability": "volatile"}
        
        ctx = build_ips_context(alloc, args)
        
        wc = ctx["wealth_context"]
        assert wc["housing_status"] == "own"
        assert wc["risk_profile"] == "aggressive"
        assert wc["has_high_interest_debt"] == True
        assert wc["income_stability"] == "volatile"

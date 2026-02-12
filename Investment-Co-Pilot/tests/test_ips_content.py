"""
test_ips_content.py

Verifies the actual English text output of the IPS generator.
Ensures that the 'Input Impact' table displays the correct rationales.
"""
import sys
import unittest
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.generate_ips import generate_ips_markdown


class TestIPSContent(unittest.TestCase):
    """Verifies the Markdown output contains expected phrases"""

    def test_legacy_goal_display(self):
        """TC: Goal=Legacy -> Display 'High Equity (Growth)'"""
        # 1. Setup Input
        ips_text = generate_ips_markdown(
            age=70,
            goals={'longevity': 'Legacy'},
            allocation={'strategy': 'LEGACY_GROWTH'}
        )
        
        # 2. Verify Table Row
        # Expect: | 1. Goal | Legacy | High Equity (Growth)... |
        assert "| **1. Goal** | **Legacy** | **High Equity (Growth).**" in ips_text
        assert "| **3. Age** | **70** | **Ignored.** Investment horizon is infinite" in ips_text
        
    def test_liquidity_goal_display(self):
        """TC: Goal=Liquidity -> Display 'High Bonds (Safety)'"""
        ips_text = generate_ips_markdown(
            age=30,
            goals={'liquidity': 'Short-term Goal'},
            allocation={'strategy': 'LIQUIDITY_FOCUS'}
        )
        
        # Expect: | 1. Goal | Short-term Goal | High Bonds (Safety)... |
        assert "| **1. Goal** | **Short-term Goal** | **High Bonds (Safety).**" in ips_text

    def test_aggressive_risk_display(self):
        """TC: Risk=Aggressive -> Display 'Maximized Equity'"""
        ips_text = generate_ips_markdown(
            age=30,
            wealth_context={'risk_profile': 'aggressive'},
            allocation={'strategy': 'LIFECYCLE_V2'}
        )
        
        # Expect: | 2. Risk Profile | Aggressive | Maximized Equity... |
        assert "| **2. Risk Profile** | **Aggressive** | **Maximized Equity.**" in ips_text

    def test_renter_housing_display(self):
        """TC: Housing=Rent -> Display 'Neutral'"""
        ips_text = generate_ips_markdown(
            age=30,
            wealth_context={'housing_status': 'rent'},
            allocation={'strategy': 'LIFECYCLE_V2'}
        )
        
        # Expect: | 4. Housing | Rent | Neutral... |
        assert "| **4. Housing** | **Rent** | **Neutral.**" in ips_text
        
    def test_owner_housing_display(self):
        """TC: Housing=Own -> Display 'Reduced Equity'"""
        ips_text = generate_ips_markdown(
            age=30,
            wealth_context={'housing_status': 'own'},
            allocation={'strategy': 'LIFECYCLE_V2', 'housing_adjustment': True}
        )
        
        # Expect: | 4. Housing | Own | Reduced Equity... |
        assert "| **4. Housing** | **Own** | **Reduced Equity.**" in ips_text

    def test_human_capital_transparency(self):
        """TC: Verify explicit explanation when Age suggestion is overridden by Risk."""
        # Setup: Age 55 (Diminishing earnings) but Aggressive Risk (Max Growth) -> 100% Equity
        ips_text = generate_ips_markdown(
            age=55,
            region="US",
            goals={'longevity': 'Retirement'},
            wealth_context={'risk_profile': 'aggressive', 'housing_status': 'rent'},
            allocation={'equity_pct': 100, 'bonds_pct': 0, 'strategy': 'LIFECYCLE_V2'}
        )
        
        # Expect the standard warning about age
        assert "diminishing" in ips_text
        assert "standard theory suggests a higher fixed income buffer" in ips_text.lower()
        
        # Expect the transparency override (Aggressive)
        assert "Aggressive Risk Profile" in ips_text
        assert "overrides this to maximize growth" in ips_text

    def test_housing_transparency_override(self):
        """TC: Verify explicit explanation when Housing suggestion is overridden by Goal."""
        # Setup: Homeowner (usually -10% equity) but Legacy Goal (100% equity)
        ips_text = generate_ips_markdown(
            age=60,
            region="US",
            goals={'longevity': 'Legacy'},
            wealth_context={'housing_status': 'own_no_mortgage'},
            allocation={'strategy': 'LEGACY_GROWTH', 'equity_pct': 100}
        )
        
        # Expect recognition of bond nature of home
        assert "acts like a Bond" in ips_text
        
        # Expect the transparency override (Legacy/Strategy)
        assert "chosen Strategy overrides this" in ips_text
        assert "model reduced your equity" not in ips_text

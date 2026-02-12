from typing import Dict, Any, List, Literal

# The Essential Investment Universe
# Simple. Cheap. Safe. Easy.
INVESTMENT_UNIVERSE = {
    "equity": {
        "standard": {
            "us_domiciled": "VT",
            "eu_domiciled": "VWCE",
            "name": "Vanguard Total World Stock ETF",
            "description": "The One-Stop Shop. Owns ~9,000 stocks globally."
        },
        "esg": {
            "us_domiciled": "ESGV (65%) + VSGX (35%)",
            "eu_domiciled": "V3AA",
            "name": "Vanguard ESG Global All Cap",
            "description": "The Responsible One-Stop Shop. Global exposure excluding vice/fossil fuels."
        }
    },
    "fixed_income": {
        "corporate": {
            "us_domiciled": "LQD",
            "eu_domiciled": "LQDA or IEAA",
            "name": "Investment Grade Corporate Bond ETF",
            "description": "Yield Booster. High quality debt."
        }
    },
    "speculation": {
        "gold": {
            "us_domiciled": "GLD",
            "eu_domiciled": "SGLD",
            "name": "Gold",
            "description": "Insurance/Hedge."
        },
        "bitcoin": {
            "us_domiciled": "IBIT",
            "eu_domiciled": "BTCE",
            "name": "Bitcoin",
            "description": "Speculation (Fun Bucket). High Risk. Max 10% recommended."
        }
    }
}

def get_recommended_portfolio(region: str, esg: bool = False) -> dict:
    """
    Returns the core equity tickers based on region and ESG preference.
    """
    key = "esg" if esg else "standard"
    domicile_key = "us_domiciled" if region.lower() == "us" else "eu_domiciled"
    
    return {
        "equity_ticker": INVESTMENT_UNIVERSE["equity"][key][domicile_key],
        "equity_name": INVESTMENT_UNIVERSE["equity"][key]["name"]
    }



def calculate_holistic_allocation(
    age: int, 
    region: Literal["EU", "US"] = "EU",
    risk_profile: Literal["aggressive", "moderate", "conservative"] = "moderate", 
    goal: Literal["longevity", "legacy", "liquidity"] = "longevity", 
    fun_bucket_pct: int = 0,
    esg_preference: bool = False,
    housing_status: Literal["rent", "own_no_mortgage", "own_with_mortgage"] = "rent",
    has_high_interest_debt: bool = False,
    months_savings: int = 6,
    income_stability: str = "stable",
    has_pension: bool = True
) -> dict:
    """
    Calculates portfolio allocation based on user profile.
    
    This is the MAIN TOOL for the Investment Co-Pilot. Call this after gathering
    all user inputs during the discovery phase.
    
    Args:
        age: User's current age (required)
        region: "US" or "EU" for ETF recommendations
        risk_profile: "aggressive", "moderate", or "conservative"
        goal: "longevity" (retirement) or "legacy" (for heirs)
        fun_bucket_pct: Percentage for speculation (0-100, typically 0-10)
        esg_preference: Whether user prefers sustainable/ESG funds
        housing_status: "own" or "rent"
        has_high_interest_debt: True if user has debt with interest > 5%
        months_savings: Number of months of emergency savings (minimum 3 required)
        income_stability: "stable" or "volatile" (affects savings target)
        has_pension: Whether user has a pension
        
    Returns:
        Dictionary with equity_pct, bonds_pct, fun_bucket_pct, strategy, and notes
    """
    
    trace = []

    # 1. Debt Rule (Guaranteed Return)
    if has_high_interest_debt:
        trace.append("⛔ DEBT RULE: High-interest debt detected (>5%). Priority is payoff.")
        return {
            "equity_pct": 0, "bonds_pct": 0, "fun_bucket_pct": 0,
            "strategy": "DEBT_PAYOFF",
            "note": "Guaranteed return on debt payoff > market return. Stop investing.",
            "region": region,
            "esg_preference": esg_preference,
            "trace": trace
        }

    # 2. Liquidity Rule (Safety First)
    if months_savings < 3:
        trace.append(f"⛔ LIQUIDITY RULE: Only {months_savings} months savings. Priority is survival buffer.")
        return {
            "equity_pct": 0, "bonds_pct": 0, "fun_bucket_pct": 0,
            "strategy": "CASH_BUILDER",
            "note": "Priority Zero is survival. Build 3 months cash buffer first.",
            "region": region,
            "esg_preference": esg_preference,
            "trace": trace
        }
    
    # Cap Fun Bucket? NO. User requested flexibility.
    
    # Ensure remaining capital is non-negative
    if fun_bucket_pct >= 100:
        trace.append("⚠️ SPECULATION RULE: User requested 100% Fun Bucket.")
        return {
            "equity_pct": 0, "bonds_pct": 0, "fun_bucket_pct": 100,
            "strategy": "SPECULATION_ONLY",
            "note": "WARNING: 100% Speculation. Extremely risky.",
            "region": region,
            "esg_preference": esg_preference,
            "trace": trace
        }
        
    remaining_capital_pct = 100 - fun_bucket_pct
    trace.append(f"1. Starting Capital: {remaining_capital_pct}% (after {fun_bucket_pct}% Fun Bucket)")

    # 3. Liquidity Rule (Short-term Focus)
    # For goals with < 5 year horizon (house deposit, major purchase)
    # Keep mostly bonds/cash to preserve capital
    if goal.lower() == "liquidity":
        trace.append("2. GOAL OVERRIDE (Liquidity): Short-term horizon forces 20/80 split.")
        # 20/80 split - prioritize capital preservation
        equity_pct = int(remaining_capital_pct * 0.20)
        bonds_pct = remaining_capital_pct - equity_pct
        return {
            "equity_pct": equity_pct, "bonds_pct": bonds_pct, "fun_bucket_pct": fun_bucket_pct,
            "strategy": "LIQUIDITY_FOCUS",
            "note": "Short-term horizon (< 5 years). Prioritizing capital preservation over growth.",
            "region": region,
            "esg_preference": esg_preference,
            "age": age,
            "income_stability": income_stability,
            "has_pension": has_pension,
            "trace": trace
        }

    # 4. Legacy Rule (Endowment Model)
    if goal.lower() == "legacy":
        trace.append("2. GOAL OVERRIDE (Legacy): Infinite horizon forces 100% Equity.")
        # 100% split of the remaining capital
        equity_pct = int(remaining_capital_pct * 1.0)
        bonds_pct = remaining_capital_pct - equity_pct
        return {
            "equity_pct": equity_pct, "bonds_pct": bonds_pct, "fun_bucket_pct": fun_bucket_pct,
            "strategy": "LEGACY_GROWTH",
            "note": "Legacy horizon is infinite (beyond life). Volatility is irrelevant.",
            "region": region,
            "esg_preference": esg_preference,
            "age": age,
            "income_stability": income_stability,
            "has_pension": has_pension,
            "trace": trace
        }

    # 5. Standard Lifecycle (Human Capital Theory)
    # Refined based on Campbell's view: Human Capital is a Bond. 
    # If active logic (High HC) -> High Equity. 
    # In retirement (Low HC) -> Portfolio must support consumption, BUT if risk_profile is high, 
    # we shouldn't force high bonds (which risk longevity failure).
    
    core_equity_ratio = 0.60 # Default
    
    if risk_profile == "aggressive":
        # Aggressive: 100% Equity until 55 (Maximize HC leverage).
        # In Retirement: 80% Equity (Longevity risk is the main enemy).
        if age < 55: core_equity_ratio = 1.0
        elif 55 <= age < 65: core_equity_ratio = 0.9
        else: core_equity_ratio = 0.75 # Cap at 75% for Safe Withdrawal Rate survival
        
    elif risk_profile == "conservative":
        # Conservative: Still High Equity young (HC Bond), but glides earlier.
        # Retirement Floor: 50% (Minimum for 4% rule survival).
        if age < 50: core_equity_ratio = 0.8
        elif 50 <= age < 65: core_equity_ratio = 0.65
        else: core_equity_ratio = 0.50
        
    else: # Moderate (Standard)
        # Moderate: 90% until 50. Glides gently.
        # Retirement Floor: 65% (Required for Bengen's 4.7% rule).
        if age < 50: core_equity_ratio = 0.9
        elif 50 <= age < 65: core_equity_ratio = 0.75
        else: core_equity_ratio = 0.65

    # 5. Housing Rule (Home Equity as Bond / Background Risk)
    # Theory (Campbell, "Strategic Asset Allocation" & "Fixed"):
    # 1. Consumption Hedge: Owning a home hedges rent risk. This stream of "imputed rent" is Bond-like (Safe).
    # 2. Background Risk: However, a home is a single, leveraged, illiquid asset. This concentration risk lowers the user's ability to take risk elsewhere.
    # 3. Committed Expenditure: If they have a mortgage, they have fixed liabilities. High fixed liabilities REDUCE Risk Capacity.
    # Conclusion: Homeowners should hold a SAFER financial portfolio (More Bonds) to counterbalance the leverage and lack of liquidity in their housing.
    housing_adjustment = False
    
    trace.append(f"2. Base Equity Ratio: {int(core_equity_ratio*100)}% (Age {age}, Risk '{risk_profile}')")

    if housing_status.lower().startswith("own"):
        core_equity_ratio = max(0.40, core_equity_ratio - 0.10) # Decrease equity by 10%, floor at 40%
        housing_adjustment = True
        trace.append("3. Housing Adjustment: -10% (Real Estate exposure adjustment)")
    else:
        trace.append("3. Housing Adjustment: None (Renter - no real estate exposure)")

    # Apply Core Split to Remaining Capital
    equity_pct = int(remaining_capital_pct * core_equity_ratio)
    bonds_pct = remaining_capital_pct - equity_pct
    
    trace.append(f"4. Final Equity: {equity_pct}%")

    return {
        "equity_pct": equity_pct,
        "bonds_pct": bonds_pct,
        "fun_bucket_pct": fun_bucket_pct,
        "housing_adjustment": housing_adjustment,
        "strategy": "LIFECYCLE_V2",
        "note": f"Adjusted Lifecycle Allocation for Age {age} (Risk: {risk_profile.title()}).",
        "region": region,
        "esg_preference": esg_preference,
        "age": age,
        "income_stability": income_stability,
        "has_pension": has_pension,
        "trace": trace
    }



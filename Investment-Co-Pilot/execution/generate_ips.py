import json
import argparse
import os
from datetime import datetime
from execution.financial_utils import get_recommended_portfolio, INVESTMENT_UNIVERSE

def generate_ips_markdown(
    age: int = 30,
    region: str = "US",
    esg_preference: bool = False,
    goals: dict = None,
    wealth_context: dict = None,
    allocation: dict = None,
    **kwargs
):
    """
    Generates the Investment Policy Statement (IPS) in Markdown format.
    
    Args:
        age: Age of the investor.
        region: "US" or "EU".
        esg_preference: Boolean for ESG focus.
        goals: Dict containing 'liquidity' and 'longevity' goals.
        wealth_context: Dict containing 'housing_status', 'income_stability', 'has_high_interest_debt'.
        allocation: Dict containing 'equity_pct', 'bonds_pct', 'fun_bucket_pct'.
    """
    
    # Defaults
    if goals is None: goals = {"liquidity": "Emergency Fund", "longevity": "Retirement"}
    if wealth_context is None: wealth_context = {}
    if allocation is None: allocation = {"equity_pct": 90, "bonds_pct": 10, "fun_bucket_pct": 0}

    # Extract Inputs & Normalize
    # Handle boolean inputs from LLM (common error)
    raw_liq = goals.get("liquidity")
    if isinstance(raw_liq, bool):
        liquidity_goal = "Emergency Fund" if not raw_liq else "Short-term Liquidity"
    else:
        liquidity_goal = raw_liq or "Emergency Fund"
        
    raw_long = goals.get("longevity")
    if isinstance(raw_long, bool):
        longevity_goal = "Longevity (Retirement Growth)" if raw_long else "Wealth Preservation"
    else:
        val = (raw_long or "Retirement").title()
        if "Retirement" in val or "Longevity" in val:
            longevity_goal = "Longevity (Retirement)"
        else:
            longevity_goal = val

    housing_status = wealth_context.get("housing_status", "rent").lower()
    income_stability = wealth_context.get("income_stability", "stable").lower()
    has_debt = wealth_context.get("has_high_interest_debt", False)
    
    equity_pct = allocation.get("equity_pct", 90)
    bonds_pct = allocation.get("bonds_pct", 10)
    fun_bucket_pct = allocation.get("fun_bucket_pct", 0)
    
    # Get Tickers - Normalize region (agent should pass "US" or "EU")
    region_upper = (region or "US").upper().strip()
    if region_upper not in ["US", "EU"]:
        region_upper = "US"  # Fallback for unexpected values
    
    core_equity = get_recommended_portfolio(region_upper, esg_preference)
    domicile = "us_domiciled" if region_upper == "US" else "eu_domiciled"
    bond_ticker = INVESTMENT_UNIVERSE["fixed_income"]["corporate"][domicile]
    
    # Date
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Display Helpers
    strategy_raw = allocation.get('strategy', 'Custom')
    strategy_display = strategy_raw.replace('_', ' ').title().replace(' V2', '')
    
    housing_display = housing_status.replace('_', ' ').title()
    risk_display = wealth_context.get('risk_profile', 'moderate').title()

    # Pre-calculate Table Logic to avoid f-string mess
    if strategy_raw == 'LIQUIDITY_FOCUS':
        impact_goal = "**High Bonds (Safety).** Short-term goals requires protecting capital from volatility."
        impact_risk = "**Ignored.** Safety is mandatory for short-term liquidity goals."
        impact_age = "**Ignored.** Time horizon is fixed (< 5 years) regardless of age."
        impact_housing = "**Ignored.** Strategy overrides housing constraints."
    elif strategy_raw == 'LEGACY_GROWTH':
        impact_goal = "**High Equity (Growth).** Long-term horizons allow you to ignore volatility and capture growth."
        impact_risk = "**Ignored.** Legacy goals require maximum growth regardless of volatility tolerance."
        impact_age = "**Ignored.** Time horizon is infinite (beyond life) regardless of age."
        impact_housing = "**Ignored.** Strategy overrides housing constraints."
    else:
        # Lifecycle / Custom
        impact_goal = "**Balanced Approach.** Defined the baseline strategy."
        
        if risk_display.lower() == 'aggressive':
            impact_risk = "**Maximized Equity.** You accepted volatility to maximize long-term returns."
        elif risk_display.lower() == 'moderate':
            impact_risk = "**Balanced Mix.** You traded some upside to reduce the severity of crashes."
        else:
            impact_risk = "**High Bonds.** You prioritized sleep-at-night stability over maximum returns."
            
        if age < 50:
            impact_age = "**Equity Bias.** Your 'Human Capital' (future earnings) acts as a bond, allowing your portfolio to take more risk."
        else:
            impact_age = "**Bond Bias.** As you approach retirement, we lock in gains and reduce sequence of returns risk."
            
        if allocation.get('housing_adjustment') or housing_status.lower().startswith('own'):
            impact_housing = "**Reduced Equity.** Your home is a concentrated, illiquid asset. We hold more bonds to balance this risk."
        else:
            impact_housing = "**Neutral.** Renting gives you flexibility, allowing your portfolio to focus purely on financial goals."

    table_content = f"""| Factor | Your Input | Impact on Allocation |
| :--- | :--- | :--- |
| **1. Goal** | **{liquidity_goal if strategy_raw == 'LIQUIDITY_FOCUS' else longevity_goal}** | {impact_goal} |
| **2. Risk Profile** | **{risk_display}** | {impact_risk} |
| **3. Age** | **{age}** | {impact_age} |
| **4. Housing** | **{housing_display}** | {impact_housing} |"""

    # Pre-calculate Human Capital Note Logic
    human_capital_note = ""
    if age < 50:
         human_capital_note = f"At age {age}, future earnings are likely your largest asset. This typically supports a higher equity allocation."
    else:
        human_capital_note = f"At age {age}, future earnings are likely diminishing. Standard theory suggests a higher fixed income buffer."
        if bonds_pct < 10:
            override_reason = "Aggressive Risk Profile" if risk_display == 'Aggressive' else "Legacy Goal"
            human_capital_note += f" **However, your '{override_reason}' overrides this to maximize growth.**"

    # Pre-calculate Housing Note
    housing_note = ""
    # Check if housing logic was actually applied (Lifecycle strategies only)
    housing_is_relevant = strategy_raw not in ['LIQUIDITY_FOCUS', 'LEGACY_GROWTH']
    
    if housing_status.startswith("own"):
        if housing_is_relevant:
            housing_note = "Your home acts like a giant 'Bond' (it provides guaranteed shelter, like a bond provides guaranteed interest). However, homes also introduce **leverage risk** (mortgage = debt) and **liquidity constraints** (can't sell a bedroom for groceries). Research by John Y. Campbell suggests homeowners should hold a **more conservative** financial portfolio to balance this. **The model reduced your equity allocation by ~10%** to account for this."
        else:
            housing_note = "Your home typically acts like a Bond, suggesting a lower equity allocation. **However, your chosen Strategy overrides this to focus on the specific Goal.**"
    else:
        housing_note = "You are currently renting. This provides flexibility. Surplus cash flow should flood the Core Portfolio. **Guidance:** Buy only if planning to stay >5 years."

    
    # Build Logic Trace Section
    trace_content = ""
    trace_list = allocation.get("trace", [])
    if trace_list:
        formatted_trace = "\n".join([f"*   {item}" for item in trace_list])
        trace_content = f"""
### 🧮 How We Calculated This (Logic Trace)
This portfolio was derived through the following decision chain:
{formatted_trace}
"""

    
    # Build Glide Path Section
    glide_path_msg = ""
    # Only relevant for Lifecycle strategy (not Debt, Liquidity, etc.)
    if strategy_raw == 'LIFECYCLE_V2' and longevity_goal != 'Legacy': 
        if age < 50:
             glide_path_msg = "You are in the **Wealth Accumulation Phase**. As you approach age 50, standard advice serves to reduce risk. Expect your equity target to gently step down."
        elif 50 <= age < 65:
             glide_path_msg = "You are in the **Pre-Retirement Transition**. As you approach age 65, your equity target will glide toward your final retirement allocation to secure your income."
        else:
             glide_path_msg = "You are in the **Withdrawal Phase**. Maintain this allocation to balance growth with safe withdrawal rates. Review annually."
    elif 'Legacy' in longevity_goal or strategy_raw == 'LEGACY_GROWTH':
        glide_path_msg = "Your **Legacy Goal** implies an infinite time horizon. Your high-equity allocation does not need to change with age unless your goal changes."
    else:
        glide_path_msg = "Your strategy is focused on immediate priorities (Debt/Liquidity). Once resolved, you will transition to a Lifecycle strategy."

    glide_path_section = f"""## 5. Looking Ahead: The Glide Path
{glide_path_msg}
*   **Action:** Re-run this Co-Pilot simulation every year or when life circumstances change (e.g., new job, marriage, retirement)."""

    # Build Simulation Notes Section
    simulation_section = f"""## 6. Simulation Notes
*   **Human Capital:** {human_capital_note}
*   **Housing ({housing_status.title()}):** {housing_note}
*   **Insurance Audit:**
    *   **Action:** Consider raising deductibles on Home/Auto insurance to the maximum affordable level (Self-Insure small risks).
    *   **Coverage:** Check coverage for '{ "Disability (Income Protection)" if age < 60 else "Longevity (Annuities)" }' and Catastrophic loss. Avoid insuring small appliances.
{f"*   **Debt Management:** WARNING. High interest debt is present. **Priority #1:** The 'Cheap' principle suggests paying this off immediately. A 6%+ guaranteed loss on debt outweighs potential market gains.*" if has_debt else ""}"""

    ips_content = f"""# Investment Policy Statement (IPS)
**Date:** {date_str}

> **⚠️ DISCLAIMER:** This Investment Policy Statement is an educational document generated by an AI simulation based on user inputs. It does **NOT** constitute financial, legal, or tax advice. It is a roadmap for your personal use to discuss with a qualified professional.

---

## 1. Executive Summary
This document outlines a proposed investment strategy. It acts as a commitment device to encourage discipline, low costs, and safety during all market conditions.

**Primary Mission:**
To aim for {longevity_goal} while prioritizing sufficient {liquidity_goal}.

## 2. Investment Philosophy
This portfolio model is built on the principles of **Simple, Cheap, Safe, and Easy**:
1.  **Simple:** Uses broad Index Funds to avoid complexity.
2.  **Cheap:** Prioritizes minimizing fees.
3.  **Safe:** Manages risk through diversification limits and liquidity buffers.
4.  **Easy:** Designed for automated decision-making.

## 3. Asset Allocation Strategy (SAA)
**Target Allocation:**
*   **Equities (Growth):** {equity_pct}%
*   **Fixed Income (Safety):** {bonds_pct}%
{f"*   **Fun Bucket (Speculation):** {fun_bucket_pct}%" if fun_bucket_pct > 0 else ""}

### 🧠 Why This Allocation?

The model constructed your portfolio by weighing **4 key factors**. Here is how each input shaped the result:

{table_content}

> **Summary:** This allocation is the mathematical result of balancing these conflicting forces.

{trace_content}

### The Core Portfolio
Based on the region ({region}) and preferences (ESG: {"Yes" if esg_preference else "No"}), the model suggests:

| Asset Class | Ticker | Name | Allocation |
| :--- | :--- | :--- | :--- |
| **Global Equity** | **{core_equity['equity_ticker']}** | {core_equity['equity_name']} | **{equity_pct}%** |
| **Fixed Income** | **{bond_ticker}** | Inv. Grade Corp Bonds | **{bonds_pct}%** |
{f"| **Speculation (Fun)** | **VARIOUS** | Crypto / Picks | **{fun_bucket_pct}%** |" if fun_bucket_pct > 0 else ""}

{f"***Note:** {fun_bucket_pct}% is allocated to a 'Fun Bucket' for speculative assets. This separates gambling from savings.*" if fun_bucket_pct > 0 else ""}

## 4. Risk Management Rules
*   **Rebalancing:** Review annually. Rebalance if any asset class drifts >5% from its target.
*   **Liquidity:** Maintain { "6" if income_stability == "volatile" else "3" }-6 months of living expenses in a High-Yield Savings Account.
    *   **Panic Protocol:** In the event of a market crash (>20% drop), the policy is to **do nothing** or **buy more**. Selling violates this policy.

{glide_path_section}

{simulation_section}

---

### Legal Disclaimer and User Acknowledgment
**Important Disclaimer: For Educational and Informational Purposes Only.**

The information and investment allocations provided by this tool, including any analysis, commentary, or potential scenarios, are generated by an AI model and are for educational and informational purposes only. They do not constitute, and should not be interpreted as, financial advice, investment recommendations, endorsements, or offers to buy or sell any securities or other financial instruments.

LongtermTrends and its affiliates make no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability, or availability with respect to the information provided. Any reliance you place on such information is therefore strictly at your own risk.

This is not an offer to buy or sell any security. Investment decisions should not be made based solely on the information provided here. Financial markets are subject to risks, and past performance is not indicative of future results. You should conduct your own thorough research and consult with a qualified independent financial advisor before making any investment decisions.

By using this tool and reviewing these allocations, you acknowledge that you understand this disclaimer and agree that LongtermTrends and its affiliates are not liable for any losses or damages arising from your use of or reliance on this information.

---
*Generated by the Investment Co-Pilot based on principles from John Y. Campbell's "Fixed" (2024).*
"""
    return ips_content

def main():
    parser = argparse.ArgumentParser(description="Generate an IPS Markdown file.")
    parser.add_argument("--input", required=True, help="Path to JSON input file")
    parser.add_argument("--output", required=True, help="Path to output Markdown file")
    
    args = parser.parse_args()
    print(f"DEBUG: Input arg: '{args.input}'")
    print(f"DEBUG: Output arg: '{args.output}'")
    import os
    print(f"DEBUG: CWD: {os.getcwd()}")
    
    with open(args.input, 'r') as f:
        data = json.load(f)
    
    # Unpack data as kwargs for the function
    markdown_content = generate_ips_markdown(**data)
    
    # Ensure directory exists if specified
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    with open(args.output, 'w') as f:
        f.write(markdown_content)
        
    print(f"Success: IPS generated at {args.output}")

if __name__ == "__main__":
    main()

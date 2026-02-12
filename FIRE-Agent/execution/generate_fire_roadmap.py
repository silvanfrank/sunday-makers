"""
Generate FIRE Roadmap (Markdown report).
Takes calculation results and renders them in a user-friendly format.
Version 2: Lead with one answer, clear math transparency.
"""
import json
from typing import Dict, Any
from datetime import datetime

from execution.financial_calculators import calculate_time_to_fire


def format_currency(amount: float) -> str:
    """Format number as currency."""
    return f"${amount:,.0f}"


def format_percentage(value: float) -> str:
    """Format number as percentage."""
    return f"{value:.1f}%"


def format_runway(years):
    """Format runway years for display."""
    if years == float('inf'):
        return "Indefinite (Portfolio grows annually)"
    elif years >= 100:
        return "> 100 years"
    else:
        return f"{years} years"

def format_exhaustion_age(current_age, years):
    """Format exhaustion age for display."""
    if years == float('inf'):
        return "Never"
    elif years >= 100:
        return f"> Age {current_age + 100}"
    else:
        return f"Age {current_age + years}"

def generate_fire_roadmap(data: Dict[str, Any]) -> str:
    """
    Generate the FIRE Roadmap markdown document (v2).
    
    Args:
        data: Output from calculate_fire_projections() as a dictionary
        
    Returns:
        Markdown-formatted roadmap
    """

    # Error Case
    if data.get("status") == "error":
        return f"""# ⚠️ Simulation Error

{data.get("message", "An unknown error occurred.")}

**Current Inputs:**
- Savings Rate: {format_percentage(data.get("savings_rate", 0))}

This simulation requires positive cash flow. 

---
*Generated on {datetime.now().strftime("%B %d, %Y")}*
"""
    
    # Decumulation Mode (expenses > income, but has investments)
    # Decumulation Mode (expenses > income, but has investments)
    if data.get("status") == "decumulation":
        d = data
        runway = d["runway"]
        runways = runway["runways"]

        # FI Status Check
        current_wr = d.get("current_withdrawal_rate", 0)
        fire_number = d.get("fire_number", 0)
        safe_expense = d["current_investments"] * 0.047
        
        fi_status = ""
        if d["current_investments"] >= fire_number:
            fi_status = f"""> ✅ **You ARE Financially Independent.**

Your current assets ({format_currency(d["current_investments"])}) exceed your FIRE Number ({format_currency(fire_number)}).
"""
        else:
            fi_status = f"""> ⚠️ **You are NOT Financially Independent.**

| Metric | Your Value | Safe Threshold |
|--------|------------|----------------|
| FIRE Number | {format_currency(fire_number)} | — |
| Current Assets | {format_currency(d["current_investments"])} | — |
| Gap | **{format_currency(fire_number - d["current_investments"])}** | — |
| Annual Net Withdrawal | {format_currency(d["annual_expenses"] - d["annual_income"])} | — |
| Current Withdrawal Rate | **{current_wr:.1f}%** | ≤ 4.7% |

{"Your current withdrawal rate (" + f"{current_wr:.1f}%" + ") exceeds the safe rate (4.7%)." if current_wr > 4.7 else ""}

**Safe Expense Level:** At your current assets, a sustainable withdrawal is **{format_currency(safe_expense)}/year**.
"""
        
        markdown = f"""# 🏖️ Your Decumulation Roadmap

**Date:** {datetime.now().strftime("%B %d, %Y")}

> **⚠️ DISCLAIMER:** This is an educational simulation based on historical data. It is **NOT** financial advice. Past performance does not guarantee future results.

---

## 🏁 Executive Summary

{fi_status}

---

## 📍 Your Situation

{d["message"]}

| Metric | Value |
|--------|-------|
| **Current Age** | {d["current_age"]} |
| **Current Investments** | {format_currency(d["current_investments"])} |
| **Annual Income** | {format_currency(d["annual_income"])} |
| **Annual Expenses** | {format_currency(d["annual_expenses"])} |
| **Annual Gap** | {format_currency(d["expense_gap"])} |

You are drawing down your portfolio by **{format_currency(d["expense_gap"])}/year** to cover the gap between income and expenses.

---

## ⏳ Portfolio Runway

How long will your investments last?

| Growth Assumption | Years | Exhaustion Age |
|-------------------|-------|----------------|
| **0% (Worst Case)** | {format_runway(runways["0pct"]).replace(" (Portfolio grows annually)", "")} | {format_exhaustion_age(d["current_age"], runways["0pct"])} |
| 5% (Pessimistic) | {format_runway(runways["5pct"]).replace(" (Portfolio grows annually)", "")} | {format_exhaustion_age(d["current_age"], runways["5pct"])} |
| **7% (Moderate)** | **{format_runway(runways["7pct"])}** | **{format_exhaustion_age(d["current_age"], runways["7pct"])}** |
| 9% (Aggressive) | {format_runway(runways["9pct"]).replace(" (Portfolio grows annually)", "")} | {format_exhaustion_age(d["current_age"], runways["9pct"])} |

*Note: This analysis assumes your {format_currency(d["expense_gap"])} annual gap remains constant in real terms (adjusted for inflation).*

"""
        
        # Inheritance Impact Section (if applicable)
        inheritance_amount = d.get("inheritance_amount", 0) or 0
        inheritance_age = d.get("inheritance_age", 65) or 65
        
        if inheritance_amount > 0:
            runway_with_inh = runway.get("with_inheritance", runways["7pct"])
            exhaustion_with_inh = runway.get("exhaustion_age_with_inheritance", d["current_age"] + runways["7pct"])
            
            # Calculate years extended (handle inf)
            if runway_with_inh == float('inf') and runways["7pct"] == float('inf'):
                years_extended_str = "0 (Already Indefinite)"
                years_extended_val = 0
            elif runway_with_inh == float('inf'):
                years_extended_str = "To Indefinite"
                years_extended_val = 100 # Just a flag for message
            else:
                diff = runway_with_inh - runways["7pct"]
                years_extended_str = f"+{diff} years"
                years_extended_val = diff
            
            # Pre-calc strings to handle inf properly 
            r_no_inh_str = format_runway(runways["7pct"]).replace(" (Portfolio grows annually)", "")
            ex_no_inh_str = format_exhaustion_age(d["current_age"], runways["7pct"])
            
            r_with_inh_str = format_runway(runway_with_inh)
            
            # Recalculate exhaustion age correctly for inf case
            if runway_with_inh == float('inf'):
                ex_with_inh_str = "Never"
            elif runway_with_inh >= 100:
                ex_with_inh_str = f"> Age {d['current_age'] + 100}"
            else:
                ex_with_inh_str = f"Age {d['current_age'] + runway_with_inh}"

            markdown += f"""---

## 🎁 Inheritance Impact

You indicated an expected inheritance of **{format_currency(inheritance_amount)}** at age **{inheritance_age}**.

### Runway Comparison (at 7% Growth)

| Scenario | Years | Exhaustion Age |
|----------|-------|----------------|
| **Without Inheritance** | {r_no_inh_str} | {ex_no_inh_str} |
| **With Inheritance** | {r_with_inh_str} | {ex_with_inh_str} |
| **Years Extended** | **{years_extended_str}** | |

{"🎉 Your expected inheritance extends your runway! (" + years_extended_str + ")" if years_extended_val > 0 else ""}

**⚠️ Risk Warning:** Inheritance is uncertain. Your baseline runway (without inheritance) is {r_no_inh_str}.

"""

        # CoastFIRE Section (Adapted for Decumulation)
        cf = d.get("coast_fire")
        if cf:
            current_inv = d["current_investments"]
            future_val = cf.get("future_value_at_retirement", current_inv)
            fire_needed = cf.get("fire_number_needed", 0)
            target_ret_age = d.get("target_retirement_age", 65)
            
            markdown += f"""---
## 🏖️ CoastFIRE Status

"""
            
            if cf.get("reason") == "Already at or past target retirement age":
                markdown += f"""> ⚠️ **NOT APPLICABLE**

You are already at or past your target retirement age ({target_ret_age}). CoastFIRE analysis is designed for people with years remaining until retirement.
"""
            elif cf.get("coast_fire"):
                markdown += f"""> ✅ **ACHIEVED**

Your current portfolio of **{format_currency(current_inv)}** is projected to grow to **{format_currency(future_val)}** by age {target_ret_age} (assuming 7% growth and no further contributions).

This exceeds your FIRE Number requirement of **{format_currency(fire_needed)}**.

### 🏖️ What is CoastFIRE?
"CoastFIRE" is the point where you have enough invested today that — **without contributing another cent** — your portfolio will grow to cover your retirement at age {target_ret_age} purely through compound interest.

**The Test:**
- **Success (Passed):** You can stop saving for retirement today. You only need to earn enough to cover your current annual expenses. Any extra work is optional.
- **Failure (Not Yet):** If you stopped saving today, you would run out of money in old age. You must continue contributing to your investments.

**Why this matters:**
CoastFIRE is the first major milestone of financial independence. It transforms your career from "I need to save for the future" to "I just need to cover today."
"""
            else:
                markdown += f"""> ❌ **NOT YET**

Your current portfolio of **{format_currency(current_inv)}** is projected to grow to **{format_currency(future_val)}** by age {target_ret_age} (assuming 7% growth and no further contributions).

This falls short of your FIRE Number requirement of **{format_currency(fire_needed)}**.

**Current Gap:** **{format_currency(max(0, fire_needed - future_val))}**

*Note: CoastFIRE is calculated assuming traditional retirement at age {target_ret_age}.*
"""

        markdown += f"""---
## ⚖️ Strategy Comparison

Even in decumulation, understanding sustainable withdrawal rates is critical.

| Strategy | Rate | Safe Withdrawal | Assumption |
|----------|------|-----------------|------------|
| **Standard (Bengen)** | 4.7% | **{format_currency(d["current_investments"] * 0.047)}** | **Safe for 30 Years.** The gold standard. Targets typical retirement duration. |
| **Early Retirement** | 4.1% | {format_currency(d["current_investments"] * 0.041)} | **Safe for 50+ Years.** Hedged against longevity risk. |
| **Ultra-Conservative** | 4.0% | {format_currency(d["current_investments"] * 0.040)} | **Legacy / Perpetuity.** The Original Rule (1994). Historically preserves principal for heirs. |
"""
        wr = d["current_withdrawal_rate"]
        wr_str = f"{wr:.1f}%" if wr != float('inf') else "Infinite (Assets Depleted)"
        markdown += f"""**Your Situation:** You are currently withdrawing **{wr_str}**.
"""
        markdown += f"""---
## 📉 Scenario: Reducing Expenses

**What if you cut expenses by 10% ({format_currency(d["annual_expenses"] * 0.10)})?**

"""
        # Calculate runway extension with 10% cut
        reduced_expenses = d["annual_expenses"] * 0.90
        reduced_gap = reduced_expenses - d["annual_income"]
        
        # Calculate new runway for "Likely" scenario (7%)
        # Logic mirrors calculate_fire_projections runway loop but simplified for report
        effective_start = d["current_investments"] 
        if inheritance_amount > 0 and inheritance_age <= d["current_age"]:
             # Already included in current investments based on prompt logic, but if logic isn't fixed yet, 
             # relying on what's in d['current_investments'] is safer for display consistency
             pass
             
        # Recalculate runway with reduced gap
        portfolio = effective_start
        new_runway_years = 0
        
        if reduced_gap <= 0:
             new_runway_years = float('inf')
        else:
             # Fast simulation
             for _ in range(100):
                  if portfolio * 1.07 < reduced_gap:
                       break
                  portfolio = portfolio * 1.07 - reduced_gap
                  new_runway_years += 1
             
             if portfolio > 0 and new_runway_years == 100: 
                  new_runway_years = float('inf')

        # Compare with baseline
        baseline_runway = runways["7pct"]
        
        if baseline_runway == float('inf'):
             markdown += f"""**Current Status:** Your portfolio already lasts indefinitely at current spending. Reducing expenses simply increases your safety margin and legacy.
"""
        elif new_runway_years == float('inf'):
             markdown += f"""| Metric | Current | With 10% Cut |
|--------|---------|--------------|
| **Annual Gap** | {format_currency(d["expense_gap"])} | {format_currency(reduced_gap)} |
| **Runway (7%)** | {baseline_runway} years | **Indefinite** |

🎉 **Result:** Cutting expenses by 10% allows your portfolio to last **FOREVER** (Escape Velocity reached).
"""
        else:
             extension = new_runway_years - baseline_runway
             markdown += f"""| Metric | Current | With 10% Cut |
|--------|---------|--------------|
| **Annual Gap** | {format_currency(d["expense_gap"])} | {format_currency(reduced_gap)} |
| **Runway (7%)** | {baseline_runway} years | **{new_runway_years} years** |

Result: You gain **+{extension} years** of runway by cutting 10%.
"""

        markdown += f"""---

## 📝 Assumptions & Disclaimers

### What We Assumed
| Assumption | Value | Why |
|------------|-------|-----|
| Stock Allocation | **~65% Equities** | Bengen recommends 65% stocks for most retirees (range: 50-75%). Below 50% reduces growth; above 75% increases volatility without improving outcomes. |
| Equity Glide Path | **U-Shaped (Dynamic)** | Research suggests reducing equity exposure to ~45-50% in early retirement (to weather sequence risk), then gradually increasing back to 65%+ as you age. This "U-shaped" path is superior to static allocation. |
| Safe Withdrawal Rate | 4.7% (or 4.1%) | Bengen's updated research (2020-2024). Assumes diversified portfolio. |
| Accumulation Growth | 7% real | Historical average for diversified equity portfolio, after inflation |
| Inflation | Accounted for | All numbers are in "today's dollars". **The Safe Withdrawal Rate rule assumes you give yourself a "raise" each year (matching inflation) to maintain purchasing power.** |
| Home Equity | **Excluded** | Primary residence is illiquid — you cannot buy groceries with a bedroom |

### What We Ignored
- Taxes (varies by jurisdiction)
- Expense changes over time (lifestyle inflation, healthcare costs)
- Sequence of returns risk during early retirement

### 💡 Note on Pensions & Social Security
This tool calculates how much **portfolio** you need. It doesn't natively model recurring future income.
*   **Recurring Income (Pension/SS):** If you expect a significant pension or Social Security, simply **reduce your Annual Expenses input** by that amount. This effectively calculates the portfolio needed to cover the *gap*.
*   **One-Time Payout (Cashout/Commuted Value):** If you cash out your pension, treat it as a 'windfall'. Enter the full payout amount as an Inheritance above.

### 🏠 About Home Equity
We excluded your home equity{f" (**{format_currency(d['home_equity'])}**)" if d.get('home_equity', 0) > 0 else ""} from the *investment portfolio* because it is not liquid capital that you can withdraw from to buy groceries. However, owning a home plays a crucial role in FIRE:

1.  **Reduced Expenses:** A paid-off home significantly lowers your required annual expenses, which lowers your FIRE Number.
2.  **Implicit Bond:** Owning acts like a long-term bond, locking in your shelter costs and hedging against future rent inflation.
3.  **Potential Liquidity:** If absolutely needed, equity can be accessed via downsizing, reverse mortgages, or selling to become a renter in later years.
4.  **Leveraged Growth:** Given the leverage with a mortgage, even a small increase in home value can produce substantial gains on your invested capital (equity).

*Key Takeaway: Your home acts as a "Consumption Hedge"—an inflation-indexed bond that stabilizes your essential expenses, reducing the portfolio size needed for FIRE.*

---

### Legal Disclaimer and User Acknowledgment
**Important Disclaimer: For Educational and Informational Purposes Only.**

The information and FIRE projections provided by this tool, including any analysis, commentary, or potential scenarios, are generated by an AI model and are for educational and informational purposes only. They do not constitute, and should not be interpreted as, financial advice, investment recommendations, endorsements, or offers to buy or sell any securities or other financial instruments.

LongtermTrends and its affiliates make no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability, or availability with respect to the information provided. Any reliance you place on such information is therefore strictly at your own risk.

This is not an offer to buy or sell any security. Investment decisions should not be made based solely on the information provided here. Financial markets are subject to risks, and past performance is not indicative of future results. You should conduct your own thorough research and consult with a qualified independent financial advisor before making any investment decisions.

By using this tool and reviewing these projections, you acknowledge that you understand this disclaimer and agree that LongtermTrends and its affiliates are not liable for any losses or damages arising from your use of or reliance on this information.

---
*Generated on {datetime.now().strftime("%B %d, %Y")}*
"""
        return markdown
    
    # Extract data for convenience
    d = data
    
    # =========================================================================
    # 🧹 ISOLATE INHERITANCE: Clean Scenarios for Main Report
    # =========================================================================
    # We strip inheritance from all baseline scenarios to ensure consistency 
    # in Sensitivity, Strategy, and Power Move sections.
    
    def get_clean_scenario(wr_rate):
        return {
            "years_to_fire_5pct": calculate_time_to_fire(d["current_investments"], d["annual_savings"], d["annual_expenses"], 0.05, wr_rate, d["current_age"], 0, 65),
            "years_to_fire_7pct": calculate_time_to_fire(d["current_investments"], d["annual_savings"], d["annual_expenses"], 0.07, wr_rate, d["current_age"], 0, 65),
            "years_to_fire_9pct": calculate_time_to_fire(d["current_investments"], d["annual_savings"], d["annual_expenses"], 0.09, wr_rate, d["current_age"], 0, 65),
            "fire_number": d["annual_expenses"] / wr_rate
        }

    # Overwrite scenario data with clean (no inheritance) values
    pure_bs = get_clean_scenario(0.047)
    pure_er = get_clean_scenario(0.041)
    pure_cons = get_clean_scenario(0.040)
    
    # Primary answer Selection logic (Dynamic Baseline)
    years_to_fire_bs = pure_bs["years_to_fire_7pct"]
    
    # Calculate projected retirement age using Bengen Standard first
    proj_fire_age = d["current_age"] + years_to_fire_bs if isinstance(years_to_fire_bs, (int, float)) else 999
    
    # Calculate retirement duration (using default life expectancy of 90)
    life_expectancy = 90
    retirement_duration = life_expectancy - proj_fire_age
    
    # DECISION: If retirement duration > 30 years, use Early Retirement (4.1%) as baseline
    # Otherwise, use Bengen Standard (4.7%)
    use_early_retirement = retirement_duration > 30
    
    if use_early_retirement:
        primary_scenario = pure_er
        primary_rate = "4.1%"
        primary_swr_val = 0.041
        primary_name = "Early Retirement"
        # Recalculate ACTUAL retirement duration based on this scenario's timeline
        actual_fire_age = d["current_age"] + pure_er["years_to_fire_7pct"]
        actual_retirement_duration = life_expectancy - actual_fire_age
        baseline_desc = f"Based on your inputs, **since you plan to retire early**, we use a safer 4.1% withdrawal rate (designed for 50+ year horizons):"
        swr_explanation = f"""**Why 4.1%? (The Early Retirement Standard)**
        
Bill Bengen's famous "4.7% Rule" is designed for a standard 30-year retirement. Since you're retiring at age {actual_fire_age} (with a ~{actual_retirement_duration:.0f} year horizon to age {life_expectancy}), we use the safer **4.1%** rate to hedge against "longevity risk". This rate is designed for retirements lasting 50+ years and represents the floor for very long planning horizons."""
    else:
        primary_scenario = pure_bs
        primary_rate = "4.7%"
        primary_swr_val = 0.047
        primary_name = "Bengen Standard"
        baseline_desc = "Based on your inputs, here is your baseline FIRE calculation:"
        swr_explanation = """**What is 4.7%? (The Historical Stress Test)**
 
This is Bill Bengen's "Safemax" — the highest withdrawal rate that historically survived **every** 30-year retirement period since 1926. It's a *safety floor*, not a return prediction."""

    years_to_fire = primary_scenario["years_to_fire_7pct"]
    year_now = datetime.now().year
    # Recalculate fire_age based on the SELECTED scenario
    fire_age = d["current_age"] + int(years_to_fire) if isinstance(years_to_fire, (int, float)) else "Unknown"

    markdown = f"""# 🔥 Your FIRE Roadmap

**Date:** {datetime.now().strftime("%B %d, %Y")}

> **⚠️ DISCLAIMER:** This is an educational simulation based on historical data. It is **NOT** financial advice. Past performance does not guarantee future results.

---

## 🏁 Executive Summary

| Baseline Target | Years to FIRE | Target Year | Retirement Age |
|-----------------|----------|-------------|----------------|
| **{format_currency(primary_scenario["fire_number"])}** | **{primary_scenario["years_to_fire_7pct"]} years** | **{year_now + primary_scenario["years_to_fire_7pct"]}** | **{d["current_age"] + primary_scenario["years_to_fire_7pct"]}** |

{baseline_desc}



---

## 📐 How We Calculated This

### Step 1: The FIRE Number Formula

```text
FIRE Number = Annual Expenses ÷ Safe Withdrawal Rate
```

| Input | Value |
|-------|-------|
| Your Annual Expenses | {format_currency(d["annual_expenses"])} |
| Safe Withdrawal Rate ({primary_name}) | {primary_rate} |
| **FIRE Number** | {format_currency(d["annual_expenses"])} ÷ {primary_swr_val} = **{format_currency(primary_scenario["fire_number"])}** |

{swr_explanation}

**Concrete Examples:** Imagine you retired with $1,000,000 on January 1st of these worst-case years:

| Retirement Year | What Happened Next | Outcome at 4.7% |
|-----------------|-------------------|-----------------|
| **1929** | The Great Depression. Markets fell 89% by 1932. | ✅ **Survived.** Your portfolio recovered and lasted 30+ years. |
| **1968** | The "Big Bang." 15 years of stagflation, oil crises, 14% inflation. | ✅ **Survived.** This was the *actual worst case* in history. You finished with money. |
| **2000** | The Dot-Com Crash, then 2008 Financial Crisis. Two crashes in 8 years. | ✅ **Survived.** Even this double-punch didn't break a 4.7% withdrawal. |

**The Takeaway:** 4.7% is the rate that survived 100 years of market history, including scenarios that felt like the end of the world at the time.

### Step 2: Years to FIRE

We use a **year-by-year simulation** to solve for the exact year where your portfolio meets the target.

| Input | Value |
|-------|-------|
| Current Investments | {format_currency(d["current_investments"])} |
| Target (FIRE Number) | {format_currency(primary_scenario["fire_number"])} |
| Annual Savings | {format_currency(d["annual_income"])} - {format_currency(d["annual_expenses"])} = **{format_currency(d["annual_savings"])}** |
| Assumed Growth Rate | 7% real (after inflation) |
| **Years to FIRE** | **{primary_scenario["years_to_fire_7pct"]} years** |

{f'''
**Where the money comes from:**
- **Principal:** {format_currency(d["current_investments"])} (Start) + {format_currency(d["annual_savings"] * primary_scenario["years_to_fire_7pct"])} (Saved) = **{format_currency(d["current_investments"] + (d["annual_savings"] * primary_scenario["years_to_fire_7pct"]))}**
- **Compound Growth:** **{format_currency(primary_scenario["fire_number"] - (d["current_investments"] + (d["annual_savings"] * primary_scenario["years_to_fire_7pct"])))}** (The power of 7% returns!)
''' if isinstance(primary_scenario["years_to_fire_7pct"], (int, float)) and primary_scenario["years_to_fire_7pct"] > 0 else ""}

**Note:** The 7% growth rate is your *accumulation assumption* (how fast your money grows while working). This is separate from the {primary_rate} withdrawal rate (how much you spend in retirement).

---
"""




    # Inheritance Impact Section (if applicable)
    inheritance_amount = d.get("inheritance_amount", 0) or 0  # Handle None
    inheritance_age = d.get("inheritance_age", 65) or 65  # Handle None
    
    if inheritance_amount > 0:
        current_age = d["current_age"]
        
        # Calculate WITH inheritance using SAME parameters as primary scenario (Growth 7%, SWR 4.2/4.7%)
        years_with_inheritance = calculate_time_to_fire(
            d["current_investments"],
            d["annual_savings"],
            d["annual_expenses"],
            0.07,
            primary_swr_val,
            current_age,
            inheritance_amount,
            inheritance_age
        )
        
        fire_age_with = current_age + years_with_inheritance
        years_without = primary_scenario["years_to_fire_7pct"] # Use the clean baseline we just defined
        
        years_saved = years_without - years_with_inheritance
        inheritance_before_fire = inheritance_age <= fire_age_with
        
        markdown += f"""## 🎁 Inheritance Impact

You indicated an expected inheritance of **{format_currency(inheritance_amount)}** at age **{inheritance_age}**.

### Timeline Comparison

| Scenario | Years to FIRE | Retirement Age |
|----------|---------------|----------------|
| **Without Inheritance** | {years_without} years | Age {current_age + years_without} |
| **With Inheritance** | {years_with_inheritance} years | Age {fire_age_with} |
| **Years Saved** | **{years_saved} years** | |

"""
        if years_saved > 0:
            markdown += f"""🎉 **Your expected inheritance accelerates retirement by {years_saved} year(s)!**

"""
        elif inheritance_before_fire:
            # Inheritance arrives before FIRE but didn't change timeline
            markdown += f"""📝 **Note:** The inheritance arrives before your FIRE date (age {inheritance_age} vs retirement at {fire_age_with}), but your savings trajectory already reaches FIRE — the inheritance provides extra cushion rather than acceleration.

"""
        else:
            # Inheritance arrives after FIRE
            markdown += f"""📝 **Note:** The inheritance arrives after your projected FIRE date (age {inheritance_age} vs retirement at {fire_age_with}), so it doesn't affect your timeline — but it provides additional security in retirement.

"""
        
        if years_saved > 0:
            before_fire_text = "Yes — accelerates timeline"
        elif inheritance_before_fire:
            before_fire_text = "Yes — but doesn't change timeline (extra cushion)"
        else:
            before_fire_text = "No — arrives after FIRE (extra cushion)"
        
        markdown += f"""### How Inheritance Is Calculated
        
Inheritance is a **one-time boost** to your portfolio:

| Factor | Your Situation |
|--------|----------------|
| **Amount** | {format_currency(inheritance_amount)} |
| **Timing** | Added to portfolio at age {inheritance_age} |
| **Before FIRE?** | {before_fire_text} |

**⚠️ Risk Warning:** Inheritance is uncertain. This simulation assumes it arrives as expected. Your "Without Inheritance" baseline shows you can still reach FIRE in {years_without} years on your own.

---
"""


    # CoastFIRE Section
    cf = d["coast_fire"]
    
    # Use d["current_investments"] since cf may not have it
    current_inv = d["current_investments"]
    future_val = cf.get("future_value_at_retirement", current_inv)
    fire_needed = cf.get("fire_number_needed", pure_bs["fire_number"])  # Use pure for consistency
    target_ret_age = d.get("target_retirement_age", 65)
    
    # Handle edge case: already at or past target retirement age
    if cf.get("reason") == "Already at or past target retirement age":
        markdown += f"""## 🏖️ CoastFIRE Status

> ⚠️ **NOT APPLICABLE**

You are already at or past your target retirement age ({target_ret_age}). CoastFIRE analysis is designed for people with years remaining until retirement.

**Your Current Situation:**
- Current Portfolio: **{format_currency(current_inv)}**
- FIRE Number Needed: **{format_currency(fire_needed)}**
- Gap: **{format_currency(max(0, fire_needed - current_inv))}**

{"✅ **You have enough to retire now!**" if current_inv >= fire_needed else "❌ **You need to continue saving or reduce expenses.**"}

"""
    elif cf["coast_fire"]:
        markdown += f"""## 🏖️ CoastFIRE Status

> ✅ **ACHIEVED**

Your current portfolio of **{format_currency(current_inv)}** is projected to grow to **{format_currency(future_val)}** by age {target_ret_age} (assuming 7% growth and no further contributions).

This exceeds your FIRE Number requirement of **{format_currency(fire_needed)}**.

### 🏖️ What is CoastFIRE?
"CoastFIRE" is the point where you have enough invested today that — **without contributing another cent** — your portfolio will grow to cover your retirement at age {target_ret_age} purely through compound interest.

**The Test:**
- **Success (Passed):** You can stop saving for retirement today. You only need to earn enough to cover your current annual expenses. Any extra work is optional.
- **Failure (Not Yet):** If you stopped saving today, you would run out of money in old age. You must continue contributing to your investments.

**Why this matters:**
CoastFIRE is the first major milestone of financial independence. It transforms your career from "I need to save for the future" to "I just need to cover today."

"""
    else:
        markdown += f"""## 🏖️ CoastFIRE Status

> ❌ **NOT YET**

Your current portfolio of **{format_currency(current_inv)}** is projected to grow to **{format_currency(future_val)}** by age {target_ret_age} (assuming 7% growth and no further contributions).

This falls short of your FIRE Number requirement of **{format_currency(fire_needed)}**.

**Current Gap:** **{format_currency(max(0, fire_needed - future_val))}**
Continued contributions are required to secure your target retirement.

{f"**💡 Perspective:** While you haven't reached CoastFIRE (the ability to *stop* saving today), your current savings rate puts you on track to retire in **{pure_bs['years_to_fire_7pct']} years** — long before age {target_ret_age}!" if isinstance(pure_bs['years_to_fire_7pct'], (int, float)) and pure_bs['years_to_fire_7pct'] < (target_ret_age - d["current_age"]) else ""}

*Note: CoastFIRE is calculated assuming traditional retirement at age {target_ret_age}. Your "Years to FIRE" above shows when you can retire earlier.*

*📖 **What is CoastFIRE?** The point where you have enough invested that compound interest alone will grow your portfolio to your FIRE target by age {target_ret_age} — without saving another cent. It's the first milestone of financial independence.*

"""

    markdown += f"""
---

## 📊 Sensitivity: What If Markets Differ?

Your "Years to FIRE" depends on growth rates you won't know in advance. Here's how the timeline shifts:

| Growth Assumption | Years to FIRE | Retirement Age |
|-------------------|---------------------|----------------|
| 5% (Pessimistic) | {pure_bs["years_to_fire_5pct"]} years | {d["current_age"] + pure_bs["years_to_fire_5pct"]} |
| **7% (Moderate)** | **{pure_bs["years_to_fire_7pct"]} years** | **{d["current_age"] + pure_bs["years_to_fire_7pct"]}** |
| 9% (Aggressive) | {pure_bs["years_to_fire_9pct"]} years | {d["current_age"] + pure_bs["years_to_fire_9pct"]} |

---
---
"""

    # Use pre-calculated pure scenarios from the calculator
    # (Pure = expenses-only for strategy comparison)
    
    markdown += f"""## ⚖️ Strategy Comparison

The FIRE Number above (4.7%) is a **Preservation Strategy**. It is designed to ensure you **never** run out of money.

### 1. Preservation Strategies (The "Forever" Pot)
These strategies aim to preserve your principal. In most market scenarios (median outcomes), these portfolios grow significantly, leaving a large legacy.

| Strategy | Rate | FIRE Number | Years to FIRE | Assumption |
|----------|------|-------------|----------------|------------|
| **Standard (Bengen)** | 4.7% | **{format_currency(pure_bs['fire_number'])}** | **{pure_bs['years_to_fire_7pct']}** | **Safe for 30 Years.** Bengen's "Safemax" (2020 update). Targets typical retirement duration. |
| **Early Retirement** | 4.1% | {format_currency(pure_er['fire_number'])} | {pure_er['years_to_fire_7pct']} | **Safe for 50+ Years.** Bengen's adjustment for early retirees. Covers extended longevity risk. |
| **Ultra-Conservative** | 4.0% | {format_currency(pure_cons['fire_number'])} | {pure_cons['years_to_fire_7pct']} | **Legacy / Perpetuity.** The Original Rule (1994). Historically preserves principal for heirs. |




---

## 📉 Scenario: Reducing Expenses

**What if you cut expenses by 10% ({format_currency(d['power_move']['expense_reduction'])})?**

"""
    
    pure_reduced_fire = d['power_move']['new_annual_expenses'] / 0.047  # Pure: just expenses / SWR
    
    # Calculate pure years to FIRE reduced target
    pure_reduced_years = calculate_time_to_fire(d["current_investments"], d["annual_savings"], d["power_move"]["new_annual_expenses"], 0.07, 0.047, d["current_age"], 0, 65)
    
    # Simple simulation to find years to FIRE pure_reduced_fire
    pure_reduced_years = 999 # Default if never reached
    
    if d['current_investments'] >= pure_reduced_fire:
        pure_reduced_years = 0
    elif d['annual_savings'] > 0:
        portfolio = d['current_investments']
        # With 10% cut, savings increase by the expense reduction
        new_savings = d['annual_savings'] + d['power_move']['expense_reduction']
        for year in range(1, 100):
            portfolio = portfolio * 1.07 + new_savings
            if portfolio >= pure_reduced_fire:
                pure_reduced_years = year
                break
    
    years_saved = pure_bs['years_to_fire_7pct'] - pure_reduced_years
    
    markdown += f"""| Metric | Current | With 10% Cut |
|--------|---------|--------------| 
| Expenses | {format_currency(d['annual_expenses'])} | {format_currency(d['power_move']['new_annual_expenses'])} |
| FIRE Number | {format_currency(pure_bs['fire_number'])} | {format_currency(pure_reduced_fire)} |
| Years to FIRE | {pure_bs['years_to_fire_7pct']} | **{pure_reduced_years}** |

{f"**Result:** You could potentially retire **{years_saved} years earlier** by cutting 10%." if years_saved > 0 else ""}

---

## 📝 Assumptions & Disclaimers

### What We Assumed
| Assumption | Value | Why |
|------------|-------|-----|
| Stock Allocation | **~65% Equities** | Bengen recommends 65% stocks for most retirees (range: 50-75%). Below 50% reduces growth; above 75% increases volatility without improving outcomes. |
| Equity Glide Path | **U-Shaped (Dynamic)** | Research suggests reducing equity exposure to ~45-50% in early retirement (to weather sequence risk), then gradually increasing back to 65%+ as you age. This "U-shaped" path is superior to static allocation. |
| Safe Withdrawal Rate | 4.7% (or 4.1%) | Bengen's updated research (2020-2024). Assumes diversified portfolio. |
| Accumulation Growth | 7% real | Historical average for diversified equity portfolio, after inflation |
| Inflation | Accounted for | All numbers are in "today's dollars". **The Safe Withdrawal Rate rule assumes you give yourself a "raise" each year (matching inflation) to maintain purchasing power.** |
| Home Equity | **Excluded** | Primary residence is illiquid — you cannot buy groceries with a bedroom |

### What We Ignored
- Taxes (varies by jurisdiction)
- Expense changes over time (lifestyle inflation, healthcare costs)
- Sequence of returns risk during early retirement

### 💡 Note on Pensions & Social Security
This tool calculates how much **portfolio** you need. It doesn't natively model recurring future income.
*   **Recurring Income (Pension/SS):** If you expect a significant pension or Social Security, simply **reduce your Annual Expenses input** by that amount. This effectively calculates the portfolio needed to cover the *gap*.
*   **One-Time Payout (Cashout/Commuted Value):** If you cash out your pension, treat it as a 'windfall'. Enter the full payout amount as an Inheritance above.

### 🏠 About Home Equity
We excluded your home equity{f" (**{format_currency(d['home_equity'])}**)" if d.get('home_equity', 0) > 0 else ""} from the *investment portfolio* because it is not liquid capital that you can withdraw from to buy groceries. However, owning a home plays a crucial role in FIRE:

1.  **Reduced Expenses:** A paid-off home significantly lowers your required annual expenses, which lowers your FIRE Number.
2.  **Implicit Bond:** Owning acts like a long-term bond, locking in your shelter costs and hedging against future rent inflation.
3.  **Potential Liquidity:** If absolutely needed, equity can be accessed via downsizing, reverse mortgages, or selling to become a renter in later years.
4.  **Leveraged Growth:** Given the leverage with a mortgage, even a small increase in home value can produce substantial gains on your invested capital (equity).

*Key Takeaway: Your home acts as a "Consumption Hedge"—an inflation-indexed bond that stabilizes your essential expenses, reducing the portfolio size needed for FIRE.*

---

### Legal Disclaimer and User Acknowledgment
**Important Disclaimer: For Educational and Informational Purposes Only.**

The information and FIRE projections provided by this tool, including any analysis, commentary, or potential scenarios, are generated by an AI model and are for educational and informational purposes only. They do not constitute, and should not be interpreted as, financial advice, investment recommendations, endorsements, or offers to buy or sell any securities or other financial instruments.

LongtermTrends and its affiliates make no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability, or availability with respect to the information provided. Any reliance you place on such information is therefore strictly at your own risk.

This is not an offer to buy or sell any security. Investment decisions should not be made based solely on the information provided here. Financial markets are subject to risks, and past performance is not indicative of future results. You should conduct your own thorough research and consult with a qualified independent financial advisor before making any investment decisions.

By using this tool and reviewing these projections, you acknowledge that you understand this disclaimer and agree that LongtermTrends and its affiliates are not liable for any losses or damages arising from your use of or reliance on this information.

"""
    
    return markdown

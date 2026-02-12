"""
Generate Car Affordability Report.
Creates a Markdown report from the calculator outputs.
"""
from typing import Dict, Any


def generate_car_report(calculation_result: Dict[str, Any]) -> str:
    """
    Generate a comprehensive Car Affordability Report in Markdown format.
    
    Args:
        calculation_result: Output from calculate_car_affordability()
        
    Returns:
        Formatted Markdown string
    """
    inputs = calculation_result["inputs"]
    rule = calculation_result["ten_percent_rule"]
    desired = calculation_result["desired_car"]
    all_cars = calculation_result["all_car_classes"]
    opp_cost = calculation_result["opportunity_cost"]
    status = calculation_result["status"]
    recommendation = calculation_result["recommendation"]
    
    # Build the report
    report = []
    
    # Header
    report.append("# 🚗 Car Affordability Report")
    report.append("")
    
    # Status banner
    if status == "affordable":
        report.append("> ✅ **Status: Affordable** — Your desired car fits within the 10% Rule.")
    elif status == "stretch":
        report.append("> ⚠️ **Status: Stretch** — This car exceeds the recommended 10% guideline.")
    else:
        report.append("> 🚨 **Status: Warning** — Review your financial situation before proceeding.")
    report.append("")
    
    # Financial Snapshot
    report.append("## 📊 Your Financial Snapshot")
    report.append("")
    report.append(f"| Metric | Value |")
    report.append(f"|--------|-------|")
    report.append(f"| Annual Income (After Tax) | ${inputs['annual_income']:,.0f} |")
    report.append(f"| Annual Expenses | ${inputs['annual_expenses']:,.0f} |")
    report.append(f"| Annual Savings | ${inputs['annual_savings']:,.0f} |")
    report.append(f"| Savings Rate | {inputs['savings_rate']:.1f}% |")
    if inputs['current_investments'] > 0:
        report.append(f"| Current Investments | ${inputs['current_investments']:,.0f} |")
    report.append("")
    
    # The 10% Rule
    report.append("## 📏 The 10% Rule Analysis")
    report.append("")
    report.append("The 10% Rule states that your **total transportation costs** (payment + insurance + fuel + maintenance) should be **less than 10% of your NET monthly income** (after taxes). This provides a safer, more conservative estimate than using gross income.")
    report.append("")
    report.append(f"| Your Budget | Amount |")
    report.append(f"|-------------|--------|")
    report.append(f"| Max Annual Transport Budget | **${rule['max_annual_transport']:,.0f}/year** |")
    report.append(f"| Max Monthly Transport Budget | **${rule['max_monthly_transport']:,.0f}/month** |")
    report.append(f"| Estimated Max Sticker Price | ~${rule['estimated_max_sticker']:,.0f} |")
    report.append(f"| Affordable Class | **{rule['affordable_class'].title() if rule['affordable_class'] != 'none' else 'None (income too low)'}** |")
    report.append("")
    
    # Car Class Comparison
    report.append("## 🚗 Car Class Comparison")
    report.append("")
    report.append("| Class | Example | Sticker | Annual TCO | Fits 10% Rule? |")
    report.append("|-------|---------|---------|------------|----------------|")
    for car_class in ["budget", "luxury", "supercar"]:
        car = all_cars[car_class]
        fits = "✅ Yes" if car["can_afford"] else "❌ No"
        report.append(f"| **{car['name']}** | {car['example']} | ${car['sticker_price']:,} | ${car['annual_tco']:,}/yr | {fits} |")
    report.append("")
    
    # Desired Car Deep Dive
    report.append(f"## 🎯 Your Desired Car: {desired['name']} Class")
    report.append("")
    report.append(f"**Example:** {desired['example']}")
    report.append(f"**Sticker Price:** ${desired['sticker_price']:,}")
    report.append("")
    report.append("### Total Cost of Ownership (Annual)")
    report.append("")
    report.append("| Cost Category | Annual Amount |")
    report.append("|---------------|---------------|")
    report.append(f"| Depreciation | ${desired['breakdown']['depreciation']:,} |")
    report.append(f"| Taxes & Fees | ${desired['breakdown']['taxes_fees']:,} |")
    report.append(f"| Financing | ${desired['breakdown']['financing']:,} |")
    report.append(f"| Fuel | ${desired['breakdown']['fuel']:,} |")
    report.append(f"| Insurance | ${desired['breakdown']['insurance']:,} |")
    report.append(f"| Maintenance | ${desired['breakdown']['maintenance']:,} |")
    report.append(f"| **Total** | **${desired['annual_tco']:,}/year** |")
    report.append(f"| Monthly Equivalent | ${desired['monthly_tco']:,.0f}/month |")
    report.append("")
    
    # Can You Afford It?
    report.append("### Can You Afford It?")
    report.append("")
    if desired["can_afford"]:
        percent_used = (desired["annual_tco"] / inputs["annual_income"]) * 100
        report.append(f"✅ **Yes.** This car would use **{percent_used:.1f}%** of your net income, within the 10% guideline.")
    else:
        percent_used = (desired["annual_tco"] / inputs["annual_income"]) * 100
        report.append(f"❌ **Exceeds guideline.** This car would use **{percent_used:.1f}%** of your net income.")
        report.append(f"")
        report.append(f"To afford this car within the 10% Rule, you would need a net income of **${desired['required_income']:,.0f}/year**.")
    report.append("")
    
    # Opportunity Cost
    report.append("## 💰 Opportunity Cost")
    report.append("")
    report.append("Money spent on a car is money not invested. Here's what a typical 20% down payment could become if invested instead:")
    report.append("")
    report.append(f"| Metric | Value |")
    report.append(f"|--------|-------|")
    report.append(f"| Down Payment (20%) | ${opp_cost['down_payment']:,.0f} |")
    report.append(f"| Value After 5 Years (7% return) | ${opp_cost['future_value_5yr']:,.0f} |")
    report.append(f"| **Lost Growth** | **${opp_cost['lost_growth']:,.0f}** |")
    report.append("")
    report.append(f"*The 'lost growth' of ${opp_cost['lost_growth']:,.0f} is the true opportunity cost of the down payment.*")
    report.append("")
    
    # Recommendation
    report.append("## 📋 Recommendation")
    report.append("")
    report.append(recommendation)
    report.append("")
    
    # Tips
    report.append("## 💡 Tips to Save on Cars")
    report.append("")
    report.append("1. **Buy 3-5 years used** — Most depreciation has already occurred, but the car is still reliable.")
    report.append("2. **Pay cash or pay off quickly** — Avoid financing costs if possible.")
    report.append("3. **Find a trusted mechanic** — Avoid dealership markup on maintenance.")
    report.append("4. **Consider the total cost** — The sticker price is just the beginning.")
    report.append("")
    
    # Disclaimer
    report.append("---")
    report.append("")
    report.append("*Disclaimer: This is an educational simulation based on industry averages (Edmunds TCO data). Your actual costs may vary based on location, driving habits, and specific vehicle. This is not financial advice.*")
    
    return "\n".join(report)

"""
Car affordability calculators.
Pure deterministic math - no LLM logic here.

Based on Edmunds TCO data and the 10% Rule for car affordability.
"""
from typing import Dict, Any, Optional


# Reference TCO data (annual costs) from the video transcript
# Source: Edmunds True Cost to Own + McLaren owner interview
CAR_CLASS_DATA = {
    "budget": {
        "name": "Budget",
        "example": "2024 Toyota Camry SE",
        "sticker_price": 30000,
        "depreciation": 2890,         # $14,449 / 5 years
        "taxes_fees": 716,            # $3,578 / 5 years
        "financing": 1272,            # $6,361 / 5 years (10% down, 5yr term)
        "fuel": 2500,                 # $12,500 / 5 years
        "insurance": 1433,            # $7,164 / 5 years
        "maintenance": 938,           # $4,691 / 5 years
    },
    "luxury": {
        "name": "Luxury",
        "example": "Mercedes GL Class SUV",
        "sticker_price": 75000,
        "depreciation": 7845,         # $39,225 / 5 years
        "taxes_fees": 1506,           # $7,529 / 5 years
        "financing": 2289,            # $11,443 / 5 years
        "fuel": 3745,                 # $18,726 / 5 years
        "insurance": 1634,            # ~$8,170 / 5 years
        "maintenance": 2618,          # $13,092 / 5 years
    },
    "supercar": {
        "name": "Supercar",
        "example": "McLaren Artura",
        "sticker_price": 265000,
        "depreciation": 13250,        # ~$66,250 / 5 years (25% depreciation)
        "taxes_fees": 2000,           # Registration ~$2k/year
        "financing": 7630,            # Est. based on 10% down, 5yr term
        "fuel": 700,                  # ~$70/fillup × 10 fillups/year
        "insurance": 4500,            # $4,500/year for limited mileage
        "maintenance": 3000,          # $1,500 service + parts
    },
}


def calculate_tco(car_class: str) -> Dict[str, Any]:
    """
    Calculate the Total Cost of Ownership for a car class.
    
    Args:
        car_class: One of 'budget', 'luxury', 'supercar'
        
    Returns:
        Dict with annual and 5-year TCO breakdown
    """
    if car_class not in CAR_CLASS_DATA:
        raise ValueError(f"Unknown car class: {car_class}. Must be one of: {list(CAR_CLASS_DATA.keys())}")
    
    data = CAR_CLASS_DATA[car_class]
    
    annual_tco = (
        data["depreciation"] +
        data["taxes_fees"] +
        data["financing"] +
        data["fuel"] +
        data["insurance"] +
        data["maintenance"]
    )
    
    return {
        "car_class": car_class,
        "name": data["name"],
        "example": data["example"],
        "sticker_price": data["sticker_price"],
        "annual_tco": annual_tco,
        "five_year_tco": annual_tco * 5,
        "breakdown": {
            "depreciation": data["depreciation"],
            "taxes_fees": data["taxes_fees"],
            "financing": data["financing"],
            "fuel": data["fuel"],
            "insurance": data["insurance"],
            "maintenance": data["maintenance"],
        },
        "monthly_tco": round(annual_tco / 12, 2),
    }


def calculate_max_affordable_car(annual_net_income: float) -> Dict[str, Any]:
    """
    Calculate the maximum affordable car using the 10% Rule.
    
    The 10% Rule: Transportation costs should be < 10% of NET income.
    (We use Net Income for a more conservative and realistic estimate).
    
    Args:
        annual_net_income: Annual income after taxes
        
    Returns:
        Dict with max annual transportation budget and estimated max car price
    """
    max_annual_transport = annual_net_income * 0.10
    max_monthly_transport = max_annual_transport / 12
    
    # Estimate max car price based on typical TCO structure
    # TCO is roughly 30-35% of sticker price per year for budget cars
    # For budget cars: ~$9,150 TCO on $30K car = 30.5%
    # For luxury cars: ~$22,250 TCO on $75K car = 29.7%
    # We'll use 30% as a rough estimate
    estimated_max_sticker = max_annual_transport / 0.30
    
    # Determine which car class fits
    affordable_class = "none"
    for class_name in ["supercar", "luxury", "budget"]:
        class_data = CAR_CLASS_DATA[class_name]
        class_tco = calculate_tco(class_name)["annual_tco"]
        if class_tco <= max_annual_transport:
            affordable_class = class_name
            break
    
    return {
        "annual_net_income": annual_net_income,
        "max_annual_transport_budget": round(max_annual_transport, 2),
        "max_monthly_transport_budget": round(max_monthly_transport, 2),
        "estimated_max_sticker_price": round(estimated_max_sticker, 2),
        "affordable_class": affordable_class,
        "rule": "10% of net income",
    }


def calculate_opportunity_cost(
    amount: float,
    years: int = 5,
    rate_of_return: float = 0.07
) -> Dict[str, Any]:
    """
    Calculate the opportunity cost of spending money on a car vs. investing it.
    
    Args:
        amount: The amount being spent (e.g., down payment or sticker price)
        years: Number of years to project
        rate_of_return: Expected annual return (default: 7% real return)
        
    Returns:
        Dict with future value and lost growth
    """
    future_value = amount * ((1 + rate_of_return) ** years)
    lost_growth = future_value - amount
    
    return {
        "initial_amount": amount,
        "years": years,
        "rate_of_return": rate_of_return,
        "future_value": round(future_value, 2),
        "lost_growth": round(lost_growth, 2),
        "explanation": f"${amount:,.0f} invested at {rate_of_return*100:.0f}% for {years} years would grow to ${future_value:,.0f}. The 'lost growth' is ${lost_growth:,.0f}."
    }


def calculate_required_income(car_class: str, rule_percent: float = 0.10) -> Dict[str, Any]:
    """
    Calculate the income required to afford a car class using the 10% Rule.
    
    Args:
        car_class: One of 'budget', 'luxury', 'supercar'
        rule_percent: The percentage of income for transportation (default: 10%)
        
    Returns:
        Dict with required income to afford this car class
    """
    tco = calculate_tco(car_class)
    required_income = tco["annual_tco"] / rule_percent
    
    return {
        "car_class": car_class,
        "annual_tco": tco["annual_tco"],
        "required_annual_income": round(required_income, 2),
        "required_monthly_income": round(required_income / 12, 2),
        "rule": f"{rule_percent*100:.0f}% of gross income",
    }


def calculate_car_affordability(
    annual_income: float,
    annual_expenses: float,
    current_investments: float = 0,
    desired_car_class: str = "budget"
) -> Dict[str, Any]:
    """
    Main calculation function that generates all car affordability projections.
    This is the function that gets called by the orchestrator.
    
    Args:
        annual_income: Annual NET income (after taxes)
        annual_expenses: Annual expenses
        current_investments: Current invested assets (for opportunity cost)
        desired_car_class: The car class the user is interested in
        
    Returns:
        Comprehensive affordability analysis
    """
    # Normalize car class input
    desired_car_class = desired_car_class.lower().strip()
    if desired_car_class not in CAR_CLASS_DATA:
        # Try to match partial names
        if "budget" in desired_car_class or "cheap" in desired_car_class or "camry" in desired_car_class.lower():
            desired_car_class = "budget"
        elif "luxury" in desired_car_class or "mercedes" in desired_car_class.lower():
            desired_car_class = "luxury"
        elif "super" in desired_car_class or "mclaren" in desired_car_class.lower():
            desired_car_class = "supercar"
        else:
            desired_car_class = "budget"  # Default
    
    # Calculate savings rate
    annual_savings = annual_income - annual_expenses
    savings_rate = (annual_savings / annual_income * 100) if annual_income > 0 else 0
    
    # Calculate max affordable car
    affordability = calculate_max_affordable_car(annual_income)
    
    # Calculate TCO for all car classes
    all_car_tcos = {}
    for car_class in CAR_CLASS_DATA:
        all_car_tcos[car_class] = calculate_tco(car_class)
    
    # Get TCO for desired car
    desired_tco = all_car_tcos[desired_car_class]
    
    # Determine if desired car is affordable
    can_afford = desired_tco["annual_tco"] <= affordability["max_annual_transport_budget"]
    
    # Calculate required income for desired car
    required_income = calculate_required_income(desired_car_class)
    
    # Calculate opportunity cost (using 20% of sticker as typical down payment)
    down_payment = desired_tco["sticker_price"] * 0.20
    opportunity = calculate_opportunity_cost(down_payment, years=5)
    
    # Determine status and recommendation
    if can_afford:
        status = "affordable"
        recommendation = f"Based on the 10% Rule (using net income), a {desired_tco['name']} class car fits within your budget."
    else:
        status = "stretch"
        percent_of_income = (desired_tco["annual_tco"] / annual_income) * 100
        recommendation = f"A {desired_tco['name']} class car would consume {percent_of_income:.1f}% of your net income, exceeding the 10% guideline."
    
    # Check if they have negative savings
    if annual_savings <= 0:
        status = "warning"
        recommendation = "Your expenses exceed your income. Consider reducing expenses before taking on a car payment."
    
    return {
        "status": status,
        "inputs": {
            "annual_income": annual_income,
            "annual_expenses": annual_expenses,
            "annual_savings": annual_savings,
            "savings_rate": round(savings_rate, 1),
            "current_investments": current_investments,
            "desired_car_class": desired_car_class,
        },
        "ten_percent_rule": {
            "max_annual_transport": affordability["max_annual_transport_budget"],
            "max_monthly_transport": affordability["max_monthly_transport_budget"],
            "estimated_max_sticker": affordability["estimated_max_sticker_price"],
            "affordable_class": affordability["affordable_class"],
        },
        "desired_car": {
            "class": desired_car_class,
            "name": desired_tco["name"],
            "example": desired_tco["example"],
            "sticker_price": desired_tco["sticker_price"],
            "annual_tco": desired_tco["annual_tco"],
            "monthly_tco": desired_tco["monthly_tco"],
            "breakdown": desired_tco["breakdown"],
            "can_afford": can_afford,
            "required_income": required_income["required_annual_income"],
        },
        "all_car_classes": {
            car_class: {
                "name": data["name"],
                "example": data["example"],
                "sticker_price": data["sticker_price"],
                "annual_tco": data["annual_tco"],
                "can_afford": data["annual_tco"] <= affordability["max_annual_transport_budget"],
            }
            for car_class, data in all_car_tcos.items()
        },
        "opportunity_cost": {
            "down_payment": down_payment,
            "future_value_5yr": opportunity["future_value"],
            "lost_growth": opportunity["lost_growth"],
        },
        "recommendation": recommendation,
    }

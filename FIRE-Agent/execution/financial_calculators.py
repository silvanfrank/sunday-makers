"""
Financial calculators for FIRE planning.
Pure deterministic math - no LLM logic here.
"""
import math
from typing import Dict, Any, List


def calculate_savings_rate(annual_income: float, annual_expenses: float) -> float:
    """
    Calculate the savings rate.
    
    Args:
        annual_income: Post-tax annual income
        annual_expenses: Annual expenses
        
    Returns:
        Savings rate as a percentage (0-100)
    """
    if annual_income <= 0:
        return 0.0
    
    savings = annual_income - annual_expenses
    return (savings / annual_income) * 100


def calculate_fire_number(annual_expenses: float, withdrawal_rate: float = 0.047) -> float:
    """
    Calculate the FIRE number based on annual expenses and withdrawal rate.
    
    Args:
        annual_expenses: Annual expenses in retirement
        withdrawal_rate: Safe withdrawal rate (default: 4.7% per Bengen 2024)
        
    Returns:
        Target portfolio size
    """
    return annual_expenses / withdrawal_rate


def calculate_time_to_fire(
    current_investments: float,
    annual_savings: float,
    annual_expenses: float,
    rate_of_return: float = 0.07,
    withdrawal_rate: float = 0.047,
    current_age: int = 30,
    inheritance_amount: float = 0.0,
    inheritance_age: int = 65
) -> int:
    """
    Calculate years until FIRE using compound growth formula, accounting for inheritance.
    
    Target Logic:
    1. FIRE Number: Annual Expenses / SWR.
    2. Inheritance: One-time lump sum added to portfolio at inheritance_age.
    """
    
    # FIRE Target
    fire_target = annual_expenses / withdrawal_rate
    
    # Track if inheritance has been received
    # If inheritance age is in the past or present, we assume it is ALREADY included in current_investments.
    # We do NOT add it again.
    inheritance_received = inheritance_age <= current_age
        
    portfolio = current_investments
    years = 0
    max_years = 100
    
    while years < max_years:
        this_age = current_age + years
        
        # Calculate Dynamic Target
        if portfolio >= fire_target:
            return years
        
        
        
        # Add inheritance if this is the year
        # Standard logic: Only add if we haven't received it yet
        if not inheritance_received and inheritance_amount > 0 and this_age >= inheritance_age:
            portfolio += inheritance_amount
            inheritance_received = True
            # Re-check after inheritance
            if portfolio >= fire_target:
                return years
            
        # Grow for next year
        portfolio = portfolio * (1 + rate_of_return) + annual_savings
        years += 1
    
    return 999


def calculate_coast_fire_check(
    current_investments: float,
    current_age: int,
    target_retirement_age: int,
    annual_expenses: float,
    rate_of_return: float = 0.07,
    withdrawal_rate: float = 0.047
) -> Dict[str, Any]:
    """
    Check if user has reached CoastFIRE status.
    
    Args:
        current_investments: Current invested assets
        current_age: Current age
        target_retirement_age: Target retirement age (IGNORED - Defaults to 65 for Coast check)
        annual_expenses: Annual expenses
        rate_of_return: Expected real return
        withdrawal_rate: Safe withdrawal rate
        
    Returns:
        Dict with coast_fire status and details
    """
    # STRICTLY enforce checking against Age 65 (Traditional Retirement)
    # Only "coast" if you can reach Age 65 target without further contributions.
    # Ignoring user's specific target_retirement_age for this check.
    years_to_retirement = 65 - current_age
    
    if years_to_retirement <= 0:
        return {
            "coast_fire": False,
            "reason": "Already at or past target retirement age"
        }
    
    # Calculate what portfolio would grow to with no new contributions
    future_value = current_investments * ((1 + rate_of_return) ** years_to_retirement)
    
    # Calculate what is NEEDED at target_retirement_age
    fire_number = calculate_fire_number(annual_expenses, withdrawal_rate)
    
    coast_fire = future_value >= fire_number
    
    return {
        "coast_fire": coast_fire,
        "current_investments": current_investments,
        "future_value_at_retirement": future_value,
        "fire_number_needed": fire_number,
        "years_to_retirement": years_to_retirement,
        "surplus_or_gap": future_value - fire_number
    }



def calculate_fire_projections(
    current_age: int,
    current_investments: float,
    annual_income: float,
    annual_expenses: float,
    target_retirement_age: int = None,
    home_equity: float = 0.0,
    inheritance_amount: float = 0.0,
    inheritance_age: int = 65
) -> Dict[str, Any]:
    """
    Main calculation function that generates all FIRE projections.
    This is the function that gets called by the orchestrator.
    
    Args:
        current_age: Current age
        current_investments: Current invested assets
        annual_income: Post-tax annual income
        annual_expenses: Annual expenses
        target_retirement_age: Optional target retirement age (default: 65)

        home_equity: Value of home equity (not liquid, but useful context)
        inheritance_amount: Expected one-time inheritance (lump sum)
        inheritance_age: Age when inheritance is expected
        
    Returns:
        Comprehensive FIRE analysis dictionary
    """
    if target_retirement_age is None:
        target_retirement_age = 65
    
    # Calculate savings (can be negative in decumulation)
    annual_savings = annual_income - annual_expenses
    savings_rate = calculate_savings_rate(annual_income, annual_expenses)
    
    # Handle Decumulation Mode (expenses > income)
    if annual_expenses > annual_income:
        # Check if user has resources to fund the gap
        expense_gap = annual_expenses - annual_income
        
        # If they have investments OR immediate/past inheritance, calculate runway
        has_immediate_funds = current_investments > 0
        has_past_inheritance = inheritance_amount > 0 and inheritance_age <= current_age
        
        if has_immediate_funds or has_past_inheritance or inheritance_amount > 0:
            # Calculate runway: How many years can they fund the gap?
            if (current_investments > 0 or has_past_inheritance) and expense_gap > 0:
                # Calculate runways for different growth rates
                runways = {}
                growth_rates = [0.0, 0.05, 0.07, 0.09]
                
                # Determine effective starting balance
                # BUGFIX: Do NOT add past inheritance. Assume current_investments includes it.
                effective_start_balance = current_investments
                # if has_past_inheritance:
                #    effective_start_balance += inheritance_amount
                
                for r in growth_rates:
                    # Check for "Indefinite" runway (Escape Velocity)
                    # If growth on starting balance exceeds annual withdraw needs, it lasts forever.
                    initial_growth = effective_start_balance * r
                    if r > 0 and initial_growth >= expense_gap:
                        if r == 0.05: runways["5pct"] = float('inf')
                        elif r == 0.07: runways["7pct"] = float('inf')
                        elif r == 0.09: runways["9pct"] = float('inf')
                        continue

                    portfolio = effective_start_balance
                    years = 0
                    while portfolio > 0 and years < 100:
                        portfolio = portfolio * (1 + r) - expense_gap
                        years += 1
                        # Double check if we inadvertently hit Escape Velocity logic during drawdown
                        # (Unlikely if we failed the initial check, unless expenses decrease - which they don't here)
                    
                    # Store as integers (capped at 100) or float for 0% simple
                    if r == 0.0:
                        runways["0pct"] = round(effective_start_balance / expense_gap, 1) # Expected decimal for 0%
                    elif r == 0.05:
                        runways["5pct"] = years
                    elif r == 0.07:
                        runways["7pct"] = years
                    elif r == 0.09:
                        runways["9pct"] = years

            elif (current_investments > 0 or has_past_inheritance) and expense_gap <= 0:
                # Edge case: expenses exactly equal income (no gap to fund)
                runways = {
                    "0pct": float('inf'),
                    "5pct": float('inf'),
                    "7pct": float('inf'),
                    "9pct": float('inf')
                }
            else:
                # Case: 0 investments (but has future inheritance entry)
                runways = {
                    "0pct": 0,
                    "5pct": 0,
                    "7pct": 0,
                    "9pct": 0
                }
            
            # Calculate current withdrawal rate
            effective_investments = current_investments
            # BUGFIX: Do NOT add past inheritance for withdrawal rate check either
            # if has_past_inheritance:
            #    effective_investments += inheritance_amount
                
            current_withdrawal_rate = (expense_gap / effective_investments) * 100 if effective_investments > 0 else float('inf')
            
            # Calculate FIRE number for reference
            fire_number = annual_expenses / 0.047
            
            # Calculate runway WITH inheritance (using 7% growth as standard)
            # Make sure we don't double count if it's already in effective_start_balance
            runway_with_inheritance = runways["7pct"]
            
            # Only run the complex simulation if inheritance is FUTURE
            # If past, it's already in runways["7pct"]
            if inheritance_amount > 0 and not has_past_inheritance:
                r = 0.07
                portfolio = current_investments
                years = 0
                inheritance_received = False
                escape_velocity = False
                
                while portfolio > 0 and years < 100:
                    this_age = current_age + years
                    # Add inheritance if this is the year
                    if not inheritance_received and this_age >= inheritance_age:
                        portfolio += inheritance_amount
                        inheritance_received = True
                        
                        # CHECK FOR ESCAPE VELOCITY UPON RECEIVING INHERITANCE
                        # If new balance * growth > expense gap, it's indefinite
                        if (portfolio * r) >= expense_gap:
                            escape_velocity = True
                            break
                            
                    portfolio = portfolio * (1 + r) - expense_gap
                    years += 1
                
                if escape_velocity:
                    runway_with_inheritance = float('inf')
                else:
                    runway_with_inheritance = years
            
            # Calculate CoastFIRE status
            # For decumulation, we still check if current assets can grow to support typical retirement
            # independently of the current drawdown context (as a reference point).
            fire_number_coast = calculate_fire_number(annual_expenses, 0.047)
            coast_fire_status = calculate_coast_fire_check(
                current_investments,
                current_age,
                target_retirement_age,
                annual_expenses,
                0.07,
                0.047
            )
            
            return {
                "status": "decumulation",
                "message": f"You are in Decumulation Mode (expenses exceed income by ${expense_gap:,.0f}/year).",
                "current_age": current_age,
                "current_investments": current_investments,
                "home_equity": home_equity,
                "annual_income": annual_income,
                "annual_expenses": annual_expenses,
                "annual_savings": annual_savings,  # Negative
                "savings_rate": savings_rate,  # Negative
                "expense_gap": expense_gap,
                "current_withdrawal_rate": current_withdrawal_rate,
                "fire_number": fire_number,
                "inheritance_amount": inheritance_amount,
                "inheritance_age": inheritance_age,
                "runway": {
                    "runways": runways,
                    "with_inheritance": runway_with_inheritance,
                    "exhaustion_age_7pct": current_age + runways["7pct"],
                    "exhaustion_age_with_inheritance": current_age + runway_with_inheritance
                },
                "coast_fire": coast_fire_status,
                "archetype": "Decumulation"
            }
        else:
            # No investments - true error
            return {
                "status": "error",
                "message": "Annual expenses exceed income and you have no investments. You must reduce expenses or increase income.",
                "savings_rate": savings_rate
            }
    
    annual_savings = annual_income - annual_expenses
    savings_rate = calculate_savings_rate(annual_income, annual_expenses)
    
    # =========================================================================
    # SCENARIOS
    # =========================================================================
    
    def _get_scenario_data(name, wr, rate_return):
        """Calculate scenario data."""
        years = calculate_time_to_fire(
            current_investments, annual_savings, annual_expenses, 
            rate_return, wr, 
            current_age,
            inheritance_amount, inheritance_age
        )
        
        # Calculate the Target Portfolio needed
        total_target = annual_expenses / wr
        return years, total_target

    # Bengen 4.7%
    ben_years_5, ben_target_5 = _get_scenario_data("Bengen", 0.047, 0.05)
    ben_years_7, ben_target_7 = _get_scenario_data("Bengen", 0.047, 0.07)
    ben_years_9, ben_target_9 = _get_scenario_data("Bengen", 0.047, 0.09)

    # Conservative 4.0%
    cons_years_5, cons_target_5 = _get_scenario_data("Cons", 0.040, 0.05)
    cons_years_7, cons_target_7 = _get_scenario_data("Cons", 0.040, 0.07)
    cons_years_9, cons_target_9 = _get_scenario_data("Cons", 0.040, 0.09)

    # Early 4.2%
    early_years_5, early_target_5 = _get_scenario_data("Early", 0.042, 0.05)
    early_years_7, early_target_7 = _get_scenario_data("Early", 0.042, 0.07)
    early_years_9, early_target_9 = _get_scenario_data("Early", 0.042, 0.09)

    scenarios = {
        "bengen_standard": {
            "name": "Bengen Standard (4.7%)",
            "withdrawal_rate": 0.047,
            "fire_number": ben_target_7,
            "years_to_fire_5pct": ben_years_5,
            "years_to_fire_7pct": ben_years_7,
            "years_to_fire_9pct": ben_years_9,
        },
        "conservative": {
            "name": "Conservative (4.0%)",
            "withdrawal_rate": 0.040,
            "fire_number": cons_target_7,
            "years_to_fire_5pct": cons_years_5,
            "years_to_fire_7pct": cons_years_7,
            "years_to_fire_9pct": cons_years_9,
        },
        "early_retirement": {
            "name": "Early Retirement (4.2% - 50+ year horizon)",
            "withdrawal_rate": 0.042,
            "fire_number": early_target_7,
            "years_to_fire_5pct": early_years_5,
            "years_to_fire_7pct": early_years_7,
            "years_to_fire_9pct": early_years_9,
        },
    }
    




    
    # CoastFIRE check
    coast_fire = calculate_coast_fire_check(
        current_investments,
        current_age,
        target_retirement_age,
        annual_expenses,
        0.07, # Default return
        0.047, # Default SWR
    )
    
    # Determine archetype
    archetype = "Standard"
    if annual_expenses < 40000:
        archetype = "LeanFIRE"
    elif annual_expenses > 100000:
        archetype = "FatFIRE"
    
    if coast_fire["coast_fire"]:
        archetype = "CoastFIRE"
    
    # Calculate "Power Move" - impact of cutting 10% of expenses
    expense_reduction = annual_expenses * 0.10  # 10% reduction
    reduced_expenses = annual_expenses - expense_reduction
    increased_savings = annual_savings + expense_reduction
    
    power_move_years = calculate_time_to_fire(
        current_investments,
        increased_savings,
        reduced_expenses,
        0.07,
        0.047,
        current_age
    )
    
    power_move_fire_number = reduced_expenses / 0.047
    
    current_years = scenarios["bengen_standard"]["years_to_fire_7pct"]
    years_saved = current_years - power_move_years
    

    
    return {
        "status": "success",
        "current_age": current_age,
        "current_investments": current_investments,
        "annual_income": annual_income,
        "annual_expenses": annual_expenses,
        "home_equity": home_equity,
        "inheritance_amount": inheritance_amount,
        "inheritance_age": inheritance_age,
        "annual_savings": annual_savings,
        "savings_rate": savings_rate,
        "archetype": archetype,
        "scenarios": scenarios,
        "coast_fire": coast_fire,
        "power_move": {
            "expense_reduction": expense_reduction,
            "new_annual_expenses": reduced_expenses,
            "new_fire_number": power_move_fire_number,
            "years_to_fire": power_move_years,
            "years_saved": years_saved
        }
    }

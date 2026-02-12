
from execution.financial_calculators import calculate_time_to_fire

def test_past_inheritance_bug():
    print("--- Testing Past Inheritance Logic ---")
    
    # CASE 1: Future Inheritance
    # Current Age: 30, Inheritance Age: 35. Should be added.
    # Start: 0. Savings: 20k. Expenses: 40k. Target: ~851k.
    # In 5 years (Age 35), add 1M. Should reach FIRE instantly at 35.
    years_future = calculate_time_to_fire(
        current_investments=0,
        annual_savings=20000,
        annual_expenses=40000,
        current_age=30,
        inheritance_amount=1000000,
        inheritance_age=35
    )
    print(f"Future Inheritance (Age 35): {years_future} years to FIRE")
    
    # CASE 2: Past Inheritance
    # Current Age: 36. Inheritance Age: 35.
    # Current Investments: 1M (Assumption: User already received it).
    # Annual Expenses: 40k. Target: ~851k.
    # User is ALREADY FI (1M > 851k). Should return 0 years.
    # BUT, strict logic might return 0 anyway because 1M > target.
    
    # Let's try a case where they are NOT FI yet, but inheritance happened.
    # Target: 2M. Current: 1M. Inheritance: 1M at age 35.
    # If double counted, portfolio becomes 2M immediately -> 0 years.
    # If handled correctly, portfolio stays 1M -> some years to grow.
    
    print("\n--- logic check: Double Counting ---")
    current_inv = 1000000
    target_portfolio = 2000000
    # Expenses to create typical FIRE number of 2M (2M * 0.047 = 94k)
    expenses = 2000000 * 0.047 
    
    # PAST INHERITANCE
    # Age 36. Inheritance was at 35.
    # Should ignore inheritance amount (assumed in current_inv).
    years_past = calculate_time_to_fire(
        current_investments=current_inv,
        annual_savings=0, 
        annual_expenses=expenses,
        current_age=36,
        inheritance_amount=1000000,
        inheritance_age=35
    )
    
    # NO INHERITANCE (Control)
    years_control = calculate_time_to_fire(
        current_investments=current_inv,
        annual_savings=0,
        annual_expenses=expenses,
        current_age=36,
        inheritance_amount=0,
        inheritance_age=0
    )
    
    print(f"Control (No Inheritance param): {years_control} years")
    print(f"Past Inheritance (Age 35): {years_past} years")
    
    if years_past < years_control:
        print("❌ BUG DETECTED: Past inheritance reduced time to FIRE (Double Counting).")
    else:
        print("✅ Correct: Past inheritance did not affect simulation.")

if __name__ == "__main__":
    test_past_inheritance_bug()

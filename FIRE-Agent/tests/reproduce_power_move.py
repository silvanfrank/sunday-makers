
from execution.generate_fire_roadmap import generate_fire_roadmap

# Mock data simulating "Already FIRE" scenario where Power Move breaks
data = {
    'current_age': 50,
    'current_investments': 1702128, # Exactly enough for 80k expenses at 4.7%
    'annual_income': 100000,
    'annual_expenses': 80000,
    'annual_savings': 20000,
    'life_expectancy': 90,
    'home_equity': 0,
    'coast_fire': {'coast_fire': True, 'fire_number_needed': 1702128, 'future_value_at_retirement': 3000000},
    'power_move': {
        'expense_reduction': 8000, # 10%
        'new_annual_expenses': 72000 # 90%
    },
    'scenarios': {
        'bengen_standard': {'fire_number': 1702128, 'years_to_fire_7pct': 0}, # Already FIRE
    },
    'pure_scenarios': {
        'bengen_standard': {'fire_number': 1702128, 'years_to_fire_7pct': 0},
    }
}

print("Generating roadmap...")
roadmap = generate_fire_roadmap(data)

# Check specifically for the Power Move table content
if "Scenario: Reducing Expenses" in roadmap:
    print("\n--- Power Move Section ---")
    start = roadmap.find("## 📉 Scenario: Reducing Expenses")
    end = roadmap.find("##", start + 5)
    print(roadmap[start:end])
else:
    print("Power Move section not found.")

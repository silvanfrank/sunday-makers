
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from execution.financial_calculators import calculate_fire_projections
from execution.generate_fire_roadmap import generate_fire_roadmap

# Scenario: $200k, 1M inheritance at 55. 40k expenses.
result = calculate_fire_projections(
    current_age=50,
    current_investments=1000000,
    annual_income=80000,
    annual_expenses=100000,
    inheritance_amount=1000000,
    inheritance_age=55
)

markdown = generate_fire_roadmap(result)
print(markdown)

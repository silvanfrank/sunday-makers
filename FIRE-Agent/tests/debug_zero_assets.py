
from execution.financial_calculators import calculate_fire_projections
from execution.generate_fire_roadmap import generate_fire_roadmap
import json

def test_zero_assets_future_inheritance():
    print("--- Testing Zero Assets + Future Inheritance ---")
    
    # User Inputs
    # Age: 36
    # Invested: 0
    # Income: 0
    # Expenses: 100k
    # Inheritance: 1M at 45
    
    # 1. Calculate Projections
    result = calculate_fire_projections(
        current_age=36,
        current_investments=0,
        annual_income=0,
        annual_expenses=100000,
        inheritance_amount=1000000,
        inheritance_age=45
    )
    
    print("Calculation Result:")
    print(json.dumps(result, indent=2))
    
    # 2. Try to Generate Roadmap (if possible)
    try:
        if result.get("status") == "error":
            print("\nStatus is ERROR. Skipping generate_fire_roadmap (LLM usually handles this).")
        else:
            roadmap = generate_fire_roadmap(result)
            print("\nRoadmap Generation Successful:")
            # print(roadmap[:200])
            if "Infinite (Assets Depleted)" in roadmap:
                print("✅ Found 'Infinite (Assets Depleted)' in output.")
            else:
                print("❌ 'Infinite (Assets Depleted)' NOT found.")
                print(roadmap) # Print full roadmap for debugging
    except Exception as e:
        print(f"\nCRASH during Roadmap Generation: {e}")

if __name__ == "__main__":
    test_zero_assets_future_inheritance()

import argparse
import json
from financial_utils import calculate_holistic_allocation

def main():
    parser = argparse.ArgumentParser(description="Calculate recommended asset allocation.")
    parser.add_argument("--age", type=int, required=True, help="Investor's age")
    parser.add_argument("--risk", type=str, default="moderate", choices=["aggressive", "moderate", "conservative"], help="Risk profile")
    parser.add_argument("--debt", action="store_true", help="Has high interest debt")
    parser.add_argument("--savings", type=int, default=6, help="Months of savings")
    parser.add_argument("--goal", type=str, default="longevity", help="Primary goal (liquidity/longevity/legacy)")
    parser.add_argument("--fun_bucket", type=int, default=0, help="Fun bucket percentage (0-100)")
    parser.add_argument("--housing", type=str, default="rent", choices=["own", "rent"], help="Housing status (own/rent)")
    
    args = parser.parse_args()
    
    wealth_context = {
        "has_high_interest_debt": args.debt,
        "months_savings": args.savings,
        "housing_status": args.housing
    }
    
    recommendation = calculate_holistic_allocation(args.age, args.risk, wealth_context, args.goal, args.fun_bucket)
    
    print(json.dumps(recommendation, indent=2))

if __name__ == "__main__":
    main()


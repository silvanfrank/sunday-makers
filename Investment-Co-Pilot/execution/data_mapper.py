"""
data_mapper.py

Pure function utility for transforming user/agent inputs into
arguments for the IPS Generator.
"""

def build_ips_context(allocation_result: dict, original_args: dict) -> dict:
    """
    Constructs the exact dictionary expected by generate_ips.py
    
    Args:
        allocation_result: The output from calculate_holistic_allocation
        original_args: The raw arguments passed by the LLM (func_args)
    
    Returns:
        Dictionary ready to be unpacked as **kwargs for generate_ips_markdown
    """
    user_goal = original_args.get("goal", "longevity").lower()
    
    # 1. Map Goal String -> IPS Goal Dict
    goals_map = {}
    if user_goal == 'liquidity':
        goals_map = {'liquidity': 'Short-term Goal'} 
    elif user_goal == 'legacy':
        goals_map = {'longevity': 'Legacy'}
    else:
        # Default fallback
        goals_map = {'longevity': 'Retirement'}

    # 2. Build Context
    # We prefer the allocation_result value (trusted source) over original_args if available
    return {
        "allocation": allocation_result,
        "goals": goals_map,
        "age": allocation_result.get("age", original_args.get("age", 40)),
        "region": allocation_result.get("region", original_args.get("region", "EU")),
        "esg_preference": allocation_result.get("esg_preference", original_args.get("esg_preference", False)),
        "wealth_context": {
            "housing_status": original_args.get("housing_status", "rent"),
            "risk_profile": original_args.get("risk_profile", "moderate"),
            "income_stability": allocation_result.get("income_stability", "stable"),
            "has_high_interest_debt": original_args.get("has_high_interest_debt", False),
        },
    }

import argparse
import json

def check_rebalancing(current_portfolio, target_allocation, total_value):
    """
    Calculates rebalancing needs based on 5% drift threshold.
    """
    
    # Calculate current percentages
    # Simplified: Assuming portfolio is categorized into Equity, Bonds, Fun
    
    current_equity = current_portfolio.get("equity_value", 0)
    current_bonds = current_portfolio.get("bonds_value", 0)
    current_fun = current_portfolio.get("fun_value", 0)
    current_cash = current_portfolio.get("cash_value", 0) # For buying
    
    # Calculate Total Invested Value (excluding cash for now, or including? 
    # Usually rebalancing is done on the Investment Portfolio. 
    # But if we buy, we need cash. Let's assume Total Portfolio Value = Equity + Bonds + Fun
    # Cash is separate unless we are deploying it.
    
    invested_value = current_equity + current_bonds + current_fun
    if invested_value == 0:
        return "Portfolio is empty."

    curr_equity_pct = (current_equity / invested_value) * 100
    curr_bonds_pct = (current_bonds / invested_value) * 100
    curr_fun_pct = (current_fun / invested_value) * 100
    
    target_equity_pct = target_allocation.get("equity_pct", 0)
    target_bonds_pct = target_allocation.get("bonds_pct", 0)
    target_fun_pct = target_allocation.get("fun_bucket_pct", 0)
    
    drift_equity = curr_equity_pct - target_equity_pct
    drift_bonds = curr_bonds_pct - target_bonds_pct
    
    THRESHOLD = 5.0
    
    report = {
        "status": "Balanced",
        "actions": [],
        "analysis": {
            "equity": {"current_pct": round(curr_equity_pct, 2), "target_pct": target_equity_pct, "drift": round(drift_equity, 2)},
            "bonds": {"current_pct": round(curr_bonds_pct, 2), "target_pct": target_bonds_pct, "drift": round(drift_bonds, 2)}
        }
    }
    
    # Logic: If drift > 5%, trigger rebalance
    if abs(drift_equity) > THRESHOLD or abs(drift_bonds) > THRESHOLD:
        report["status"] = "Drift Detected"
        
        # Calculate Amount to Move
        # Target Value for Equity
        target_equity_val = invested_value * (target_equity_pct / 100.0)
        diff_equity_val = target_equity_val - current_equity
        
        target_bonds_val = invested_value * (target_bonds_pct / 100.0)
        diff_bonds_val = target_bonds_val - current_bonds
        
        if diff_equity_val > 0:
            report["actions"].append(f"BUY Equity: ${round(diff_equity_val, 2)}")
        else:
            report["actions"].append(f"SELL Equity: ${round(abs(diff_equity_val), 2)}")
            
        if diff_bonds_val > 0:
            report["actions"].append(f"BUY Bonds: ${round(diff_bonds_val, 2)}")
        else:
            report["actions"].append(f"SELL Bonds: ${round(abs(diff_bonds_val), 2)}")
            
    else:
        report["actions"].append("No Action Needed. Drift is within 5% tolerance.")
        
    return report

def main():
    parser = argparse.ArgumentParser(description="Check portfolio for rebalancing needs.")
    parser.add_argument("--current", required=True, help="JSON file with current values")
    parser.add_argument("--targets", required=True, help="JSON file with target %")
    
    args = parser.parse_args()
    
    try:
        with open(args.current, 'r') as f:
            current = json.load(f)
        with open(args.targets, 'r') as f:
            targets = json.load(f)
            
        # If input has 'allocation', use that
        if "allocation" in targets:
            targets = targets["allocation"]
            
        report = check_rebalancing(current, targets, 0)
        print(json.dumps(report, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

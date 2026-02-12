import os
import json
import subprocess
import sys

def run_command(command):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def main():
    print("--- Testing Rebalancing Logic ---")
    
    # Target: 80% Equity, 20% Bonds
    targets = {
        "allocation": {
            "equity_pct": 80,
            "bonds_pct": 20,
            "fun_bucket_pct": 0
        }
    }
    
    # Scenario: Market Crash. Stocks fell.
    # Start: $100k -> $80k Equities, $20k Bonds.
    # Crash: Equities fall to $60k. Bonds gain to $22k.
    # Total: $82k.
    # Current Allocation: $60k/$82k = 73% Equity. (Target 80%). Drift -7%.
    # Should Trigger BUY Equity.
    
    current = {
        "equity_value": 60000,
        "bonds_value": 22000,
        "fun_value": 0
    }
    
    os.makedirs(".tmp", exist_ok=True)
    with open(".tmp/test_current.json", "w") as f:
        json.dump(current, f)
    with open(".tmp/test_targets.json", "w") as f:
        json.dump(targets, f)
        
    output = run_command("python3 execution/check_rebalancing.py --current .tmp/test_current.json --targets .tmp/test_targets.json")
    print("\nOutput Report:")
    print(output)
    
    report = json.loads(output)
    if report["status"] == "Drift Detected":
        print("\n[Pass] Correctly detected drift.")
    else:
        print("\n[Fail] Did not detect drift.")

if __name__ == "__main__":
    main()

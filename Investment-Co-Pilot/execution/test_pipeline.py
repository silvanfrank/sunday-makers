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
    print("--- Testing Investment Co-Pilot Pipeline ---")
    
    # 1. Test Calculation Tool
    print("\n[Step 1] Creating Allocation for 35yo Moderate Investor...")
    allocation_json = run_command("python3 execution/calculate_allocation.py --age 35 --risk moderate")
    print(f"Allocation Output: {allocation_json}")
    
    allocation = json.loads(allocation_json)
    
    # 2. Prepare Input Data
    print("\n[Step 2] Preparing IPS Input...")
    input_data = {
        "name": "Test User",
        "age": 35,
        "region": "US",
        "esg_preference": False,
        "goals": {
            "liquidity": "6 months savings",
            "longevity": "Retire at 60"
        },
        "allocation": allocation
    }
    
    # Write to tmp
    os.makedirs(".tmp", exist_ok=True)
    with open(".tmp/test_input.json", "w") as f:
        json.dump(input_data, f, indent=2)
        
    print("Input saved to .tmp/test_input.json")
    
    # 3. Generate IPS
    print("\n[Step 3] Generating IPS...")
    output_path = ".tmp/Deliverables/Test_IPS.md"
    run_command(f"python3 execution/generate_ips.py --input .tmp/test_input.json --output '{output_path}'")
    
    # 4. Verify Output
    if os.path.exists(output_path):
        print(f"\n[Success] IPS generated at {output_path}")
        with open(output_path, 'r') as f:
            print("\nPreview of Output Content:")
            print("-" * 20)
            print(f.read()[:500] + "\n...")
            print("-" * 20)
    else:
        print("\n[Fail] Output file not found!")

if __name__ == "__main__":
    main()

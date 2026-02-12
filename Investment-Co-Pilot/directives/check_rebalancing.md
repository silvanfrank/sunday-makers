# Directive: Check Portfolio Rebalancing

**Goal:** Analyze the user's current portfolio to see if it has drifted from their Target Asset Allocation (defined in their IPS).

## 1. Discovery Phase
You need to know the current value of their holdings.
Ask the user for the approximate total value of their:
1.  **Equity Holdings** (Stocks/ETFs)
2.  **Fixed Income Holdings** (Bonds)
3.  **Speculative Holdings** (Fun Bucket/Crypto)

*Note: You also need their "Target Allocation" (e.g., 90/10). If they did not just create an IPS with you, ask them what their target is.*
13: 
14: ### Operating Rules
15: 1.  **Cheap (Drift Threshold):** We only rebalance if an asset class drifts by >5% (absolute). This minimizes transactions fees and taxes.
16: 2.  **Safe (Buy Low):** Rebalancing forces us to sell what's expensive and buy what's cheap. This is a safety mechanism.
17: 3.  **Easy (Inflow First):** If the user has new cash to invest, advise them to use it to buy the underweight asset *before* selling anything. This is tax-efficient.

## 2. Execution Phase
### Step 1: Create Input Files
Create two temporary JSON files.

`.tmp/current_portfolio.json`:
```json
{
  "equity_value": 85000,
  "bonds_value": 15000,
  "fun_value": 0
}
```

`.tmp/target_allocation.json` (or just reuse their IPS input):
```json
{
  "allocation": {
    "equity_pct": 80,
    "bonds_pct": 20,
    "fun_bucket_pct": 0
  }
}
```

### Step 2: Run Rebalancing Check
Execute the script to check for >5% drift.

```bash
python3 execution/check_rebalancing.py --current .tmp/current_portfolio.json --targets .tmp/target_allocation.json
```

### Step 3: Interpret Result
*   **If Drift Detected:** Advise the user to execute the recommended trades (Buy/Sell) to get back to safety. Remind them that buying when the market is down is hard but necessary (Buy Low).
*   **If Balanced:** Congratulate them on being disciplined. Tell them to do nothing.

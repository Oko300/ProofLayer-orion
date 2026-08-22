from typing import Dict
import time

def compute_position_cost(position: Dict) -> Dict:
    """
    Computes various cost and risk metrics for a given perpetual futures position.

    Args:
        position: A dictionary containing position details. Expected keys:
            "chain": str,
            "market": str,
            "size_usd": float,
            "leverage": float,
            "entry_price": float,
            "current_price": float,
            "funding_rate_8h": float,       # as decimal e.g. 0.0003
            "mark_fill_spread_pct": float,  # as decimal e.g. 0.001
            "insurance_fund_health": float, # 0.0 to 1.0
            "entry_timestamp": int,         # Unix timestamp
            "current_timestamp": int        # Unix timestamp

    Returns:
        A dictionary with computed cost, liquidation, risk, and recommendation metrics.
    """

    # Constants
    TAKER_FEE_RATE = 0.0005  # 0.05%
    HOURS_IN_DAY = 24
    SECONDS_IN_HOUR = 3600
    FUNDING_RATE_ESCALATION_THRESHOLD = 0.001


    # Extract input values with defaults for safety
    size_usd = position.get("size_usd", 0.0)
    leverage = position.get("leverage", 1.0)
    entry_price = position.get("entry_price", 0.0)
    current_price = position.get("current_price", 0.0)
    funding_rate_8h = position.get("funding_rate_8h", 0.0)
    mark_fill_spread_pct = position.get("mark_fill_spread_pct", 0.0)
    insurance_fund_health = position.get("insurance_fund_health", 1.0)
    entry_timestamp = position.get("entry_timestamp", int(time.time()))
    current_timestamp = position.get("current_timestamp", int(time.time()))

    # Ensure leverage is not zero to prevent division errors
    if leverage == 0:
        leverage = 1.0

    # 1. Taker Fee Cost
    taker_fee_usd = size_usd * TAKER_FEE_RATE

    # 2. Mark/Fill Spread Cost
    mark_fill_spread_usd = size_usd * mark_fill_spread_pct

    # 3. Funding Costs
    # Funding cost per 8-hour settlement
    funding_cost_8h_usd_per_settlement = size_usd * funding_rate_8h

    # Escalated 1-hour funding rate (3x original 8h rate, but for 1/8th of the period)
    funding_rate_1h_escalated = funding_rate_8h * 3 / 8
    funding_cost_1h_usd_per_settlement = size_usd * funding_rate_1h_escalated

    # Daily costs under calm and stress
    daily_cost_calm_usd = funding_cost_8h_usd_per_settlement * (HOURS_IN_DAY / 8) # 3 settlements per day
    daily_cost_stress_usd = funding_cost_1h_usd_per_settlement * (HOURS_IN_DAY / 1) # 24 settlements per day

    # Current Daily Cost (based on dynamic settlement escalation)
    current_daily_cost_usd = 0.0
    current_settlement_period_hours = 8 # Default to 8 hours
    current_funding_rate_per_period = funding_rate_8h

    if funding_rate_8h > FUNDING_RATE_ESCALATION_THRESHOLD:
        current_settlement_period_hours = 1
        current_funding_rate_per_period = funding_rate_1h_escalated
        current_daily_cost_usd = daily_cost_stress_usd
    else:
        current_daily_cost_usd = daily_cost_calm_usd
    
    # 4. Margin Drained (Total funding paid since entry)
    time_elapsed_seconds = max(0, current_timestamp - entry_timestamp)
    num_settlements_elapsed = time_elapsed_seconds // (current_settlement_period_hours * SECONDS_IN_HOUR)
    margin_drained_usd = num_settlements_elapsed * size_usd * current_funding_rate_per_period

    # 5. Liquidation Price (assuming a long position)
    initial_margin_ratio = 1 / leverage
    liquidation_price_nominal = entry_price * (1 - initial_margin_ratio)

    # Effective liquidation price (adjusted for margin drained by funding)
    # Drained margin effectively reduces available margin, thus raising liquidation price for long
    if size_usd > 0:
        liquidation_price_effective = liquidation_price_nominal + (margin_drained_usd / size_usd * entry_price)
    else:
        liquidation_price_effective = liquidation_price_nominal # No adjustment if size_usd is zero

    # Nominal liquidation price (based purely on initial margin)
    # 6. ADL Score
    adl_score = min(100, int(leverage * (1 - insurance_fund_health) * 20))


    liquidation_price_nominal = entry_price * (1 - initial_margin_ratio)

    # Effective liquidation price (adjusted for margin drained by funding)
    # Drained margin effectively reduces available margin, thus raising liquidation price for long
    if size_usd > 0:
        liquidation_price_effective = liquidation_price_nominal + (margin_drained_usd / size_usd * entry_price)
    else:
        liquidation_price_effective = liquidation_price_nominal # No adjustment if size_usd is zero

    # 6. ADL Score
    # 7. Edge Cost Ratio
    price_change_usd = (current_price - entry_price) * size_usd
    edge_cost_ratio = 0.0
    if current_daily_cost_usd != 0:
        edge_cost_ratio = price_change_usd / current_daily_cost_usd
    elif price_change_usd > 0: # If daily cost is zero, but profit, ratio is effectively infinite positive
        edge_cost_ratio = float('inf')
    elif price_change_usd < 0: # If daily cost is zero, but loss, ratio is effectively infinite negative
        edge_cost_ratio = float('-inf')

    # 8. Recommendation
    recommendation = "HOLD"
    if adl_score > 70 or edge_cost_ratio < -1.0:
        recommendation = "EXIT"
    elif adl_score > 40 or edge_cost_ratio < -0.5:
        recommendation = "REVIEW"




    return {
        "daily_cost_calm_usd": daily_cost_calm_usd,
        "daily_cost_stress_usd": daily_cost_stress_usd,
        "current_daily_cost_usd": current_daily_cost_usd,
        "cost_breakdown": {
            "taker_fee_usd": taker_fee_usd,
            "funding_cost_8h_usd": funding_cost_8h_usd_per_settlement,
            "funding_cost_1h_usd": funding_cost_1h_usd_per_settlement,
            "mark_fill_spread_usd": mark_fill_spread_usd
        },
        "liquidation_price_nominal": liquidation_price_nominal,
        "liquidation_price_effective": liquidation_price_effective,
        "margin_drained_usd": margin_drained_usd,
        "adl_score": adl_score,
        "edge_cost_ratio": edge_cost_ratio,
        "recommendation": recommendation
    }

if __name__ == "__main__":
    current_time = int(time.time())

    # Example 1: Calm Market Position
    calm_entry_time = current_time - (24 * 3600) # 24 hours ago, 3 * 8h settlements
    calm_position = {
        "chain": "Ethereum",
        "market": "ETH-USD",
        "size_usd": 10000.0,
        "leverage": 5.0,
        "entry_price": 2000.0,
        "current_price": 2010.0, # Slight profit
        "funding_rate_8h": 0.0001,       # 0.01% - below escalation threshold
        "mark_fill_spread_pct": 0.0002,  # 0.02%
        "insurance_fund_health": 0.95,   # Healthy
        "entry_timestamp": calm_entry_time,
        "current_timestamp": current_time
    }
    calm_result = compute_position_cost(calm_position)
    print("--- Calm Market Position ---")
    for k, v in calm_result.items():
        if isinstance(v, dict):
            print(f"{k}:")
            for sk, sv in v.items():
                print(f"  {sk}: {sv:.4f}")
        elif isinstance(v, float):
            print(f"{k}: {v:.4f}")
        else:
            print(f"{k}: {v}")
    print("\n")

    # Example 2: Stressed Market Position
    stressed_entry_time = current_time - (12 * 3600) # 12 hours ago, 12 * 1h settlements if escalated
    stressed_position = {
        "chain": "Arbitrum",
        "market": "ARB-USD",
        "size_usd": 50000.0,
        "leverage": 20.0,
        "entry_price": 1.0,
        "current_price": 0.98,          # Significant loss
        "funding_rate_8h": 0.002,       # 0.2% - above escalation threshold
        "mark_fill_spread_pct": 0.001,  # 0.1%
        "insurance_fund_health": 0.5,   # Unhealthy
        "entry_timestamp": stressed_entry_time,
        "current_timestamp": current_time
    }
    stressed_result = compute_position_cost(stressed_position)
    print("--- Stressed Market Position ---")
    for k, v in stressed_result.items():
        if isinstance(v, dict):
            print(f"{k}:")
            for sk, sv in v.items():
                print(f"  {sk}: {sv:.4f}")
        elif isinstance(v, float):
            print(f"{k}: {v:.4f}")
        else:
            print(f"{k}: {v}")
    print("\n")



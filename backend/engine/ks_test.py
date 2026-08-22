import numpy as np
from scipy.stats import ks_2samp, expon, uniform
from typing import List, Dict

def detect_wash_trading(trade_sizes: List[float], inter_trade_times: List[float]) -> Dict:
    """
    Detects wash trading patterns based on trade sizes and inter-trade times using
    Kolmogorov-Smirnov (KS) tests by comparing against synthetic 'normal' distributions.

    Args:
        trade_sizes: A list of trade sizes for a suspect entity.
        inter_trade_times: A list of time differences between consecutive trades (in seconds)
                           for the suspect entity.

    Returns:
        A dictionary indicating if wash trading is detected, KS statistic, p-value,
        adjusted volume percentage, and a confidence string.
    """
    len_trades = len(trade_sizes)
    len_times = len(inter_trade_times)

    # Minimum data points for KS test and meaningful analysis
    min_samples = 10
    if len_trades < min_samples or len_times < min_samples:
        return {
            "ks_statistic": 0.0,
            "p_value": 1.0, # High p-value indicates no significant difference (no wash trade detected)
            "wash_trade_detected": False,
            "adjusted_volume_pct": 0.0,
            "confidence_str": "Insufficient data for robust analysis"
        }

    np_trade_sizes = np.array(trade_sizes)
    np_inter_trade_times = np.array(inter_trade_times)

    # Generate synthetic "normal" distributions for comparison
    # For trade sizes, assume a 'normal' market might have a distribution within a range.
    # Let's generate a uniform distribution within the observed range of trade_sizes.
    # If the observed trade sizes are *too* uniform or *too* specific, a low p-value here could indicate it.
    min_trade_size = np_trade_sizes.min() if len_trades > 0 else 1.0
    max_trade_size = np_trade_sizes.max() if len_trades > 0 else 1000.0
    synthetic_trade_sizes = uniform.rvs(loc=min_trade_size, scale=max_trade_size - min_trade_size, size=len_trades * 2, random_state=42)

    # For inter-trade times, assume a 'normal' market might follow an exponential distribution.
    # The rate parameter for exponential can be derived from the observed mean or a typical market mean.
    # If observed inter-trade times deviate significantly, especially towards very fast, it's suspicious.
    # Let's use the mean of observed inter_trade_times for the scale parameter (1/lambda).
    mean_inter_trade_time = np_inter_trade_times.mean()
    # Avoid zero or very small mean causing issues with expon.rvs
    if mean_inter_trade_time <= 0:
        mean_inter_trade_time = 1.0 # Default to 1 second average
    synthetic_inter_trade_times = expon.rvs(scale=mean_inter_trade_time, size=len_times * 2, random_state=42)

    # Perform 2-sample Kolmogorov-Smirnov test
    # Null hypothesis: The two samples are drawn from the same continuous distribution.
    # If p_value is low, we reject the null hypothesis, suggesting distributions are different.
    ks_stat_sizes, p_value_sizes = ks_2samp(np_trade_sizes, synthetic_trade_sizes)
    ks_stat_times, p_value_times = ks_2samp(np_inter_trade_times, synthetic_inter_trade_times)

    # Wash trade detection logic
    # Look for significant deviation in inter-trade times (p_value_times < threshold)
    # AND potentially supporting evidence from trade sizes (p_value_sizes < threshold)
    # AND a heuristic check for very fast trades in the observed data.

    wash_trade_detected = False
    confidence_str = "none"
    adjusted_volume_pct = 0.0

    # Heuristic for very fast trades: a significant portion of inter_trade_times are very low.
    # Let's define "very low" as below a fixed small value (e.g., < 0.1 seconds).
    fast_trade_threshold = 0.1 # 100 milliseconds
    num_fast_trades = np.sum(np_inter_trade_times < fast_trade_threshold)
    pct_fast_trades = num_fast_trades / len_times

    # Combined decision: low p-value for times, and high percentage of fast trades
    if p_value_times < 0.05 and pct_fast_trades > 0.2: # 20% of trades are very fast
        wash_trade_detected = True
        adjusted_volume_pct = min(1.0, pct_fast_trades * (1 - p_value_times)) # Proportionate to fast trades and deviation
        if p_value_times < 0.01 and pct_fast_trades > 0.4: # Stronger evidence
            confidence_str = "high"
        elif p_value_times < 0.05 and pct_fast_trades > 0.3:
            confidence_str = "medium"
        else:
            confidence_str = "low"
    elif p_value_times < 0.1 and pct_fast_trades > 0.1: # Weaker but still suspicious
        wash_trade_detected = True
        adjusted_volume_pct = min(1.0, pct_fast_trades * (1 - p_value_times) / 2)
        confidence_str = "low"

    # Overall K-S statistic and p-value for the output can be based on the most indicative test,
    # or an aggregation. Let's prioritize inter-trade times.
    return {
        "ks_statistic": float(ks_stat_times),
        "p_value": float(p_value_times),
        "wash_trade_detected": wash_trade_detected,
        "adjusted_volume_pct": float(adjusted_volume_pct),
        "confidence_str": confidence_str
    }

if __name__ == "__main__":
    # Test Case 1: Likely Wash Trade (fast, uniform-ish trades)
    trade_sizes_wt = [100.0, 100.1, 99.9, 100.2, 100.0, 99.8, 100.0, 100.1, 99.9, 100.0]
    inter_trade_times_wt = [0.01, 0.02, 0.01, 0.03, 0.01, 0.02, 0.01, 0.02, 0.01, 0.03]
    result1 = detect_wash_trading(trade_sizes_wt, inter_trade_times_wt)
    print(f"Test 1 (Likely Wash Trade): Sizes={trade_sizes_wt[:5]}..., Times={inter_trade_times_wt[:5]}...")
    print(f"Result: {result1}")
    # Expected: wash_trade_detected: True, confidence_str: high/medium, adjusted_volume_pct: > 0

    # Test Case 2: Normal Trading (more varied times, sizes)
    trade_sizes_normal = [50.0, 120.5, 300.0, 80.2, 150.0, 20.0, 400.0, 110.0, 90.0, 250.0]
    inter_trade_times_normal = [5.2, 12.1, 3.5, 8.8, 1.2, 10.0, 6.7, 4.1, 9.3, 2.8]
    result2 = detect_wash_trading(trade_sizes_normal, inter_trade_times_normal)
    print(f"\nTest 2 (Normal Trading): Sizes={trade_sizes_normal[:5]}..., Times={inter_trade_times_normal[:5]}...")
    print(f"Result: {result2}")
    # Expected: wash_trade_detected: False, confidence_str: none, adjusted_volume_pct: 0

    # Test Case 3: Insufficient data
    trade_sizes_small = [10.0, 20.0, 30.0]
    inter_trade_times_small = [1.0, 2.0, 3.0]
    result3 = detect_wash_trading(trade_sizes_small, inter_trade_times_small)
    print(f"\nTest 3 (Insufficient Data): Sizes={trade_sizes_small}, Times={inter_trade_times_small}")
    print(f"Result: {result3}")
    # Expected: wash_trade_detected: False, confidence_str: Insufficient data

    # Test Case 4: Some fast trades, but not enough to trigger strong wash trade
    trade_sizes_mixed = [100, 200, 105, 110, 300, 100, 120, 100, 90, 250]
    inter_trade_times_mixed = [0.05, 0.1, 5.0, 0.06, 10.0, 0.07, 2.0, 0.05, 8.0, 0.08]
    result4 = detect_wash_trading(trade_sizes_mixed, inter_trade_times_mixed)
    print(f"\nTest 4 (Mixed Trades): Sizes={trade_sizes_mixed[:5]}..., Times={inter_trade_times_mixed[:5]}...")
    print(f"Result: {result4}")
    # Expected: wash_trade_detected: True (low), adjusted_volume_pct: >0

    # Test Case 5: Inter-trade times are somewhat regular but not extremely fast (might be algorithmic)
    trade_sizes_algo = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100]
    inter_trade_times_algo = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    result5 = detect_wash_trading(trade_sizes_algo, inter_trade_times_algo)
    print(f"\nTest 5 (Algorithmic-like): Sizes={trade_sizes_algo[:5]}..., Times={inter_trade_times_algo[:5]}...")
    print(f"Result: {result5}")
    # Expected: wash_trade_detected: True (due to deviation from exponential), adjusted_volume_pct: related to p-value


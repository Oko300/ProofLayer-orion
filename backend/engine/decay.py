from typing import Dict
import time

def compute_decay(signal_type: str, detected_at_unix: int, current_unix: int) -> Dict:
    """
    Computes the decay of a signal's strength based on its type and elapsed time.

    Args:
        signal_type: The type of signal (e.g., "onchain_transfer", "funding_anomaly").
        detected_at_unix: Unix timestamp (seconds) when the signal was detected.
        current_unix: Current Unix timestamp (seconds).

    Returns:
        A dictionary containing the original confidence (placeholder), decay percentage,
        remaining strength, and effective confidence.
    """

    # Define half-lives in seconds for each signal type
    half_lives_seconds = {
        "onchain_transfer": 24 * 3600,  # 24 hours
        "funding_anomaly": 4 * 3600,   # 4 hours
        "social_sentiment": 1 * 3600,  # 1 hour
        "volume_spike": 8 * 3600,      # 8 hours
    }

    if signal_type not in half_lives_seconds:
        return {
            "original_confidence": "unknown",
            "decay_pct": 0.0,
            "remaining_strength": 0.0,
            "effective_confidence": "invalid_type"
        }

    half_life = half_lives_seconds[signal_type]
    time_elapsed_seconds = current_unix - detected_at_unix

    if time_elapsed_seconds < 0:
        return {
            "original_confidence": "high", # Assuming original confidence was high at detection
            "decay_pct": 0.0,
            "remaining_strength": 1.0,
            "effective_confidence": "high"
        }

    # Calculate number of half-lives passed
    # Ensure half_life is not zero to prevent division by zero, though unlikely with these values
    if half_life == 0:
        num_half_lives = float('inf') if time_elapsed_seconds > 0 else 0.0
    else:
        num_half_lives = time_elapsed_seconds / half_life

    # Remaining strength follows an exponential decay model: S = S0 * (0.5)^(t / T_half)
    remaining_strength = 0.5 ** num_half_lives
    decay_pct = 1.0 - remaining_strength

    # Determine effective confidence string
    effective_confidence = "negligible"
    if remaining_strength > 0.8:
        effective_confidence = "high"
    elif remaining_strength >= 0.5:
        effective_confidence = "medium"
    elif remaining_strength >= 0.2:
        effective_confidence = "low"

    return {
        "original_confidence": "high", # Placeholder, as original confidence isn't an input
        "decay_pct": float(decay_pct),
        "remaining_strength": float(remaining_strength),
        "effective_confidence": effective_confidence
    }

if __name__ == "__main__":
    current_time = int(time.time())

    # Test Case 1: Onchain transfer, 24 hours elapsed (1 half-life)
    signal_type1 = "onchain_transfer"
    detected_at1 = current_time - (24 * 3600) # 24 hours ago
    result1 = compute_decay(signal_type1, detected_at1, current_time)
    print(f"Test 1 (Onchain, 1 half-life): Signal={signal_type1}, Detected={detected_at1}, Current={current_time}")
    print(f"Result: {result1}")
    # Expected: remaining_strength around 0.5, decay_pct around 0.5, effective_confidence: medium

    # Test Case 2: Social sentiment, 1 hour elapsed (1 half-life)
    signal_type2 = "social_sentiment"
    detected_at2 = current_time - (1 * 3600) # 1 hour ago
    result2 = compute_decay(signal_type2, detected_at2, current_time)
    print(f"\nTest 2 (Social, 1 half-life): Signal={signal_type2}, Detected={detected_at2}, Current={current_time}")
    print(f"Result: {result2}")
    # Expected: remaining_strength around 0.5, decay_pct around 0.5, effective_confidence: medium

    # Test Case 3: Funding anomaly, 8 hours elapsed (2 half-lives for a 4h half-life signal)
    signal_type3 = "funding_anomaly"
    detected_at3 = current_time - (8 * 3600) # 8 hours ago
    result3 = compute_decay(signal_type3, detected_at3, current_time)
    print(f"\nTest 3 (Funding, 2 half-lives): Signal={signal_type3}, Detected={detected_at3}, Current={current_time}")
    print(f"Result: {result3}")
    # Expected: remaining_strength around 0.25, decay_pct around 0.75, effective_confidence: low

    # Test Case 4: Volume spike, no time elapsed
    signal_type4 = "volume_spike"
    detected_at4 = current_time
    result4 = compute_decay(signal_type4, detected_at4, current_time)
    print(f"\nTest 4 (Volume, no elapsed time): Signal={signal_type4}, Detected={detected_at4}, Current={current_time}")
    print(f"Result: {result4}")
    # Expected: remaining_strength: 1.0, decay_pct: 0.0, effective_confidence: high

    # Test Case 5: Very long time elapsed (decay to negligible)
    signal_type5 = "social_sentiment"
    detected_at5 = current_time - (10 * 24 * 3600) # 10 days ago
    result5 = compute_decay(signal_type5, detected_at5, current_time)
    print(f"\nTest 5 (Social, long elapsed time): Signal={signal_type5}, Detected={detected_at5}, Current={current_time}")
    print(f"Result: {result5}")
    # Expected: remaining_strength: very low, decay_pct: close to 1.0, effective_confidence: negligible

    # Test Case 6: Invalid signal type
    signal_type6 = "invalid_signal"
    detected_at6 = current_time - 3600
    result6 = compute_decay(signal_type6, detected_at6, current_time)
    print(f"\nTest 6 (Invalid Signal Type): Signal={signal_type6}")
    print(f"Result: {result6}")
    # Expected: effective_confidence: invalid_type


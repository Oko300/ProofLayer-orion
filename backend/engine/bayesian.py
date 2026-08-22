from typing import Dict, List
import numpy as np

def compute_attribution(features: Dict[str, any]) -> Dict:
    """
    Performs simple Bayesian inference for wallet attribution based on given features.

    Args:
        features: A dictionary of features including:
                  "transfer_size_usd": float,
                  "counterparty_type": str (e.g., "CEX", "DEX", "Whale", "Retail"),
                  "time_of_day": int (0-23),
                  "frequency_7d": int

    Returns:
        A dictionary containing the probabilities for different attribution labels,
        the most likely label, and a confidence level.
    """

    # --- Simple Bayesian Priors (example values, these would be learned in a real system) ---
    # P(Type)
    priors = {
        "exchange": 0.3,
        "accumulator": 0.3,
        "market_maker": 0.2,
        "unknown": 0.2,
    }

    # --- Simplified Likelihoods (example conditional probabilities) ---
    # These are illustrative and would be more complex and data-driven in a real application.
    # They represent P(Feature | Type)

    likelihoods = {
        "exchange": {
            "transfer_size_usd": lambda x: 0.8 if x > 1_000_000 else (0.5 if x > 100_000 else 0.2),
            "counterparty_type": lambda x: 0.9 if x in ["CEX", "DEX"] else 0.1,
            "time_of_day": lambda x: 0.6, # Evenly distributed
            "frequency_7d": lambda x: 0.9 if x > 20 else (0.5 if x > 5 else 0.1),
        },
        "accumulator": {
            "transfer_size_usd": lambda x: 0.8 if x > 10_000 and x < 1_000_000 else (0.3 if x > 1_000_000 else 0.6),
            "counterparty_type": lambda x: 0.9 if x == "Whale" else 0.3,
            "time_of_day": lambda x: 0.8 if x < 8 or x > 20 else 0.4, # Off-peak hours
            "frequency_7d": lambda x: 0.7 if x > 5 and x <= 20 else 0.3,
        },
        "market_maker": {
            "transfer_size_usd": lambda x: 0.7 if x > 50_000 and x < 500_000 else (0.3 if x > 1_000_000 else 0.5),
            "counterparty_type": lambda x: 0.8 if x == "Market Maker" else 0.2,
            "time_of_day": lambda x: 0.8 if x >= 9 and x <= 17 else 0.4, # Business hours
            "frequency_7d": lambda x: 0.9 if x > 50 else 0.2,
        },
        "unknown": {
            "transfer_size_usd": lambda x: 0.5,
            "counterparty_type": lambda x: 0.5,
            "time_of_day": lambda x: 0.5,
            "frequency_7d": lambda x: 0.5,
        },
    }

    # Calculate P(Type | Features) using Bayes' Theorem (simplified approach)
    # P(Type | Features) propto P(Features | Type) * P(Type)
    posterior_probabilities = {label: prior for label, prior in priors.items()}

    for label, prior in priors.items():
        for feature_name, feature_value in features.items():
            if feature_name in likelihoods[label]:
                posterior_probabilities[label] *= likelihoods[label][feature_name](feature_value)

    # Normalize probabilities
    total_prob = sum(posterior_probabilities.values())
    if total_prob == 0:
        # Fallback if all probabilities are zero (shouldn't happen with current likelihoods)
        normalized_probabilities = {label: 1.0 / len(priors) for label in priors}
    else:
        normalized_probabilities = {label: prob / total_prob for label, prob in posterior_probabilities.items()}

    # Determine the most likely label and confidence
    if normalized_probabilities:
        label = max(normalized_probabilities, key=normalized_probabilities.get)
        confidence_value = normalized_probabilities[label]
    else:
        label = "unknown"
        confidence_value = 0.0

    confidence_str = "uncertain"
    if confidence_value > 0.8:
        confidence_str = "high"
    elif confidence_value > 0.6:
        confidence_str = "medium"
    elif confidence_value > 0.4:
        confidence_str = "low"

    return {
        "p_exchange": float(normalized_probabilities.get("exchange", 0.0)),
        "p_accumulator": float(normalized_probabilities.get("accumulator", 0.0)),
        "p_market_maker": float(normalized_probabilities.get("market_maker", 0.0)),
        "p_unknown": float(normalized_probabilities.get("unknown", 0.0)),
        "label": label,
        "confidence": confidence_str
    }

if __name__ == "__main__":
    # Test Case 1: Likely Exchange
    features1 = {
        "transfer_size_usd": 2_500_000,
        "counterparty_type": "CEX",
        "time_of_day": 14,
        "frequency_7d": 30
    }
    result1 = compute_attribution(features1)
    print(f"Test 1 (Likely Exchange): Features={features1}")
    print(f"Result: {result1}")
    # Expected: High p_exchange, label: exchange, confidence: high/medium

    # Test Case 2: Likely Accumulator
    features2 = {
        "transfer_size_usd": 50_000,
        "counterparty_type": "Whale",
        "time_of_day": 3,
        "frequency_7d": 10
    }
    result2 = compute_attribution(features2)
    print(f"\nTest 2 (Likely Accumulator): Features={features2}")
    print(f"Result: {result2}")
    # Expected: High p_accumulator, label: accumulator, confidence: high/medium

    # Test Case 3: Likely Market Maker
    features3 = {
        "transfer_size_usd": 200_000,
        "counterparty_type": "Market Maker",
        "time_of_day": 10,
        "frequency_7d": 60
    }
    result3 = compute_attribution(features3)
    print(f"\nTest 3 (Likely Market Maker): Features={features3}")
    print(f"Result: {result3}")
    # Expected: High p_market_maker, label: market_maker, confidence: high/medium

    # Test Case 4: Ambiguous/Unknown
    features4 = {
        "transfer_size_usd": 1000,
        "counterparty_type": "Retail",
        "time_of_day": 12,
        "frequency_7d": 1
    }
    result4 = compute_attribution(features4)
    print(f"\nTest 4 (Ambiguous/Unknown): Features={features4}")
    print(f"Result: {result4}")
    # Expected: More even distribution, label: unknown, confidence: uncertain/low

    # Test Case 5: Edge case - missing feature for a type - not handled by simplified lambda for now
    # Features with no clear strong signals
    features5 = {
        "transfer_size_usd": 500000,
        "counterparty_type": "Institution", # Not explicitly defined in likelihoods
        "time_of_day": 12,
        "frequency_7d": 15
    }
    result5 = compute_attribution(features5)
    print(f"\nTest 5 (Mixed Signals): Features={features5}")
    print(f"Result: {result5}")


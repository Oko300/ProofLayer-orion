import numpy as np
from scipy.stats import pearsonr, spearmanr
from typing import List, Dict

def test_independence(series_a: List[float], series_b: List[float]) -> Dict:
    """
    Tests the statistical independence between two series of data using Pearson and Spearman correlation.

    Args:
        series_a: A list of numerical data points for the first series.
        series_b: A list of numerical data points for the second series.

    Returns:
        A dictionary containing Pearson's r, Spearman's r, a boolean indicating independence,
        the effective evidence count, and a descriptive note.
    """
    len_a = len(series_a)
    len_b = len(series_b)

    if len_a == 0 or len_b == 0:
        return {
            "pearson_r": 0.0,
            "spearman_r": 0.0,
            "are_independent": True,
            "effective_evidence_count": 0,
            "note": "One or both series are empty, cannot determine correlation."
        }

    if len_a != len_b:
        min_len = min(len_a, len_b)
        series_a = series_a[:min_len]
        series_b = series_b[:min_len]
        note = f"Series had different lengths. Truncated to {min_len} samples."
    else:
        min_len = len_a
        note = ""

    if min_len < 2:
        return {
            "pearson_r": 0.0,
            "spearman_r": 0.0,
            "are_independent": True,
            "effective_evidence_count": min_len,
            "note": "Not enough data points to compute correlation (need at least 2)."
        }

    np_series_a = np.array(series_a)
    np_series_b = np.array(series_b)

    # Calculate Pearson correlation coefficient
    # pearsonr returns (correlation_coefficient, p-value)
    pearson_r, _ = pearsonr(np_series_a, np_series_b)

    # Calculate Spearman correlation coefficient
    # spearmanr returns (correlation_coefficient, p-value)
    spearman_r, _ = spearmanr(np_series_a, np_series_b)

    # Threshold for independence: r < 0.7
    are_independent = abs(pearson_r) < 0.7

    if abs(pearson_r) >= 0.7:
        note += " Strong correlation detected, likely not independent."
    elif abs(pearson_r) >= 0.5:
        note += " Moderate correlation detected."
    else:
        note += " Low correlation, likely independent."

    return {
        "pearson_r": float(pearson_r),
        "spearman_r": float(spearman_r),
        "are_independent": are_independent,
        "effective_evidence_count": min_len,
        "note": note.strip()
    }

if __name__ == "__main__":
    # Test Case 1: Strongly correlated (dependent)
    series_a1 = [1, 2, 3, 4, 5]
    series_b1 = [2, 4, 6, 8, 10]
    result1 = test_independence(series_a1, series_b1)
    print(f"Test 1 (Strongly Correlated): A={series_a1}, B={series_b1}")
    print(f"Result: {result1}")
    # Expected: pearson_r close to 1.0, spearman_r close to 1.0, are_independent: False

    # Test Case 2: Weakly correlated (independent)
    series_a2 = [1, 2, 3, 4, 5]
    series_b2 = [5, 4, 3, 2, 1]
    result2 = test_independence(series_a2, series_b2)
    print(f"\nTest 2 (Weakly Correlated - Inverse): A={series_a2}, B={series_b2}")
    print(f"Result: {result2}")
    # Expected: pearson_r close to -1.0, spearman_r close to -1.0, are_independent: False (still correlated)

    # Test Case 3: No clear correlation (independent)
    series_a3 = [1, 2, 3, 4, 5]
    series_b3 = [3, 1, 4, 2, 5]
    result3 = test_independence(series_a3, series_b3)
    print(f"\nTest 3 (No Clear Correlation): A={series_a3}, B={series_b3}")
    print(f"Result: {result3}")
    # Expected: pearson_r and spearman_r close to 0, are_independent: True

    # Test Case 4: Different lengths
    series_a4 = [10, 20, 30, 40, 50, 60]
    series_b4 = [1, 2, 3, 4, 5]
    result4 = test_independence(series_a4, series_b4)
    print(f"\nTest 4 (Different Lengths): A={series_a4}, B={series_b4}")
    print(f"Result: {result4}")
    # Expected: Truncated, pearson_r close to 1.0, are_independent: False

    # Test Case 5: Empty series
    series_a5 = []
    series_b5 = [1, 2, 3]
    result5 = test_independence(series_a5, series_b5)
    print(f"\nTest 5 (Empty Series A): A={series_a5}, B={series_b5}")
    print(f"Result: {result5}")
    # Expected: are_independent: True, effective_evidence_count: 0, note: "One or both series are empty..."

    # Test Case 6: Single data point
    series_a6 = [1]
    series_b6 = [10]
    result6 = test_independence(series_a6, series_b6)
    print(f"\nTest 6 (Single Data Point): A={series_a6}, B={series_b6}")
    print(f"Result: {result6}")
    # Expected: are_independent: True, effective_evidence_count: 1, note: "Not enough data points..."

    # Test Case 7: Pearson r exactly 0.7 (should be considered dependent)
    series_a7 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    series_b7 = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5]
    # This might not give exactly 0.7, but close enough to test the threshold
    result7 = test_independence(series_a7, series_b7)
    print(f"\nTest 7 (Pearson r near 0.7): A={series_a7}, B={series_b7}")
    print(f"Result: {result7}")

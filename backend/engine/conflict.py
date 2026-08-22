from typing import Dict, List

def detect_conflict(source_a: Dict, source_b: Dict) -> Dict:
    """
    Detects conflicts between two data sources by comparing their values and margins of error.

    Args:
        source_a: A dictionary representing the first data source with 'value', 'margin_of_error', and 'label'.
        source_b: A dictionary representing the second data source with 'value', 'margin_of_error', and 'label'.

    Returns:
        A dictionary indicating if a conflict is detected, the confidence intervals for each source,
        and a possible cause if a conflict exists.
    """

    value_a = source_a.get("value", 0.0)
    moe_a = source_a.get("margin_of_error", 0.0)
    label_a = source_a.get("label", "Source A")

    value_b = source_b.get("value", 0.0)
    moe_b = source_b.get("margin_of_error", 0.0)
    label_b = source_b.get("label", "Source B")

    # Calculate Confidence Intervals (CI)
    ci_a_lower = value_a - moe_a
    ci_a_upper = value_a + moe_a
    source_a_ci = [float(ci_a_lower), float(ci_a_upper)]

    ci_b_lower = value_b - moe_b
    ci_b_upper = value_b + moe_b
    source_b_ci = [float(ci_b_lower), float(ci_b_upper)]

    # Determine conflict: No overlap means conflict
    # Overlap if max(lower_bound_A, lower_bound_B) <= min(upper_bound_A, upper_bound_B)
    # Conflict if NOT (max(ci_a_lower, ci_b_lower) <= min(ci_a_upper, ci_b_upper))
    conflict = False
    possible_cause = f"{label_a} and {label_b} are consistent."

    # Check for non-overlap
    if ci_a_upper < ci_b_lower:
        conflict = True
        possible_cause = f"Conflict detected: {label_a} ({value_a:.2f} +/- {moe_a:.2f}) is significantly lower than {label_b} ({value_b:.2f} +/- {moe_b:.2f})."
    elif ci_b_upper < ci_a_lower:
        conflict = True
        possible_cause = f"Conflict detected: {label_b} ({value_b:.2f} +/- {moe_b:.2f}) is significantly lower than {label_a} ({value_a:.2f} +/- {moe_a:.2f})."

    return {
        "conflict": conflict,
        "source_a_ci": source_a_ci,
        "source_b_ci": source_b_ci,
        "possible_cause": possible_cause
    }

if __name__ == "__main__":
    # Test Case 1: No Conflict (overlapping CIs)
    source_a1 = {"value": 10.0, "margin_of_error": 1.0, "label": "Price Feed A"}
    source_b1 = {"value": 10.5, "margin_of_error": 0.8, "label": "Price Feed B"}
    result1 = detect_conflict(source_a1, source_b1)
    print(f"Test 1 (No Conflict): A={source_a1}, B={source_b1}")
    print(f"Result: {result1}")
    # Expected: conflict: False, CIs overlap

    # Test Case 2: Conflict (A is lower than B)
    source_a2 = {"value": 5.0, "margin_of_error": 0.5, "label": "Oracle X"}
    source_b2 = {"value": 7.0, "margin_of_error": 0.5, "label": "Oracle Y"}
    result2 = detect_conflict(source_a2, source_b2)
    print(f"\nTest 2 (Conflict A < B): A={source_a2}, B={source_b2}")
    print(f"Result: {result2}")
    # Expected: conflict: True, possible_cause: Oracle X is lower than Oracle Y

    # Test Case 3: Conflict (B is lower than A)
    source_a3 = {"value": 20.0, "margin_of_error": 1.0, "label": "Exchange A"}
    source_b3 = {"value": 17.0, "margin_of_error": 1.5, "label": "Exchange B"}
    result3 = detect_conflict(source_a3, source_b3)
    print(f"\nTest 3 (Conflict B < A): A={source_a3}, B={source_b3}")
    print(f"Result: {result3}")
    # Expected: conflict: True, possible_cause: Exchange B is lower than Exchange A

    # Test Case 4: Edge case - CIs touch at a point (no conflict)
    source_a4 = {"value": 10.0, "margin_of_error": 1.0, "label": "Sensor 1"}
    source_b4 = {"value": 11.0, "margin_of_error": 0.0, "label": "Sensor 2"}
    result4 = detect_conflict(source_a4, source_b4)
    print(f"\nTest 4 (CIs Touch): A={source_a4}, B={source_b4}")
    print(f"Result: {result4}")
    # Expected: conflict: False

    # Test Case 5: Large margins of error, leading to overlap
    source_a5 = {"value": 100.0, "margin_of_error": 20.0, "label": "Model Alpha"}
    source_b5 = {"value": 130.0, "margin_of_error": 5.0, "label": "Model Beta"}
    result5 = detect_conflict(source_a5, source_b5)
    print(f"\nTest 5 (Large MOE, Overlap): A={source_a5}, B={source_b5}")
    print(f"Result: {result5}")
    # Expected: conflict: False

    # Test Case 6: Zero margin of error (exact values)
    source_a6 = {"value": 50.0, "margin_of_error": 0.0, "label": "Fixed Value 1"}
    source_b6 = {"value": 50.0, "margin_of_error": 0.0, "label": "Fixed Value 2"}
    result6 = detect_conflict(source_a6, source_b6)
    print(f"\nTest 6 (Zero MOE, Equal): A={source_a6}, B={source_b6}")
    print(f"Result: {result6}")
    # Expected: conflict: False

    source_a7 = {"value": 50.0, "margin_of_error": 0.0, "label": "Fixed Value 1"}
    source_b7 = {"value": 50.1, "margin_of_error": 0.0, "label": "Fixed Value 2"}
    result7 = detect_conflict(source_a7, source_b7)
    print(f"\nTest 7 (Zero MOE, Different): A={source_a7}, B={source_b7}")
    print(f"Result: {result7}")
    # Expected: conflict: True


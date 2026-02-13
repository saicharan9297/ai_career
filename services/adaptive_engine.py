def adjust_difficulty(last_scores, current_level):
    """
    Adjust difficulty based on last 3 performance scores.
    last_scores: list of scores between 0 and 1
    current_level: int (1 to 3)
    """

    # If not enough data, keep same level
    if len(last_scores) < 3:
        return current_level

    # Calculate average of last 3 scores
    avg_score = sum(last_scores[-3:]) / 3

    # Increase difficulty
    if avg_score > 0.8:
        return min(current_level + 1, 3)

    # Decrease difficulty
    elif avg_score < 0.4:
        return max(current_level - 1, 1)

    # Keep same level
    else:
        return current_level

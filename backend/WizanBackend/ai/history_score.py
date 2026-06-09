# backend/ai/history_score.py

def calculate_history_score(user) -> dict:
    """
    Measures: cognitive state TREND over last 7 days
    Data source: CognitiveLog.score (quiz scores only)
    Nothing to do with tasks.
    """
    from cognitive_logs.models import CognitiveLog

    # recent days weighted more heavily than older days
    day_weights = [0.30, 0.25, 0.20, 0.10, 0.07, 0.05, 0.03]

    last_7 = list(
        CognitiveLog.objects
        .filter(user=user)
        .exclude(score__isnull=True)   # exclude skipped days
        .order_by("-log_date")
        .values_list("score", flat=True)[:7]
    )

    days_available = len(last_7)

    if days_available == 0:
        return {
            "history_score": None,
            "days_available": 0,
            "is_first_time": True,
        }

    # renormalize weights to whatever days we have
    active_weights = day_weights[:days_available]
    total_weight   = sum(active_weights)
    normalized     = [w / total_weight for w in active_weights]

    score = sum(s * w for s, w in zip(last_7, normalized))

    return {
        "history_score":  round(score, 2),
        "days_available": days_available,
        "is_first_time":  False,
    }


#test
# at the bottom of history_score.py
if __name__ == "__main__":
    # test with fake data — no DB needed
    print("Testing with 3 days of history...")
    
    # simulate what the function returns for a new user
    result = {
        "history_score": None,
        "days_available": 0,
        "is_first_time": True,
    }
    print("First time user:", result)
    print("✅ history_score.py works")
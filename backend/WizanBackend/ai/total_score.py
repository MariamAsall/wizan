# backend/ai/total_score.py

from ai.history_score import calculate_history_score
from ai.behavioral_score import calculate_behavioral_score


def calculate_total_score(user, quiz_score: int) -> dict:
    """
    Handles all real-world cases:
    - First time user
    - User skipping quiz (quiz_score=None)
    - User returning after days away
    """

    history_data    = calculate_history_score(user)
    behavioral_data = calculate_behavioral_score(user)

    history_score    = history_data["history_score"]
    behavioral_score = behavioral_data["behavioral_score"]
    is_first_time    = history_data["is_first_time"]

    # ── CASE 1: First time user ──────────────────────────────
    # no history, no behavioral data worth using
    # quiz score IS the final score — simple and honest
    if is_first_time:
        final = quiz_score
        note  = "first_time"

    # ── CASE 2: User skipped quiz today ─────────────────────
    # carry yesterday's score forward with a small decay
    # this prevents gaming the system by always skipping
    elif quiz_score is None:
        yesterday_score = history_score   # weighted average already calculated
        decay           = 5              # lose 5 points per skipped day, feels fair
        final           = max(0, round(yesterday_score - decay))
        note            = "quiz_skipped_decay_applied"

    # ── CASE 3: Normal day — has quiz + some history ─────────
    # fewer history days = quiz matters more
    # more history days = full 3-component formula
    else:
        days = history_data["days_available"]

        if days < 3:
            # not enough history — quiz dominates
            weights = {"quiz": 0.80, "history": 0.15, "behavioral": 0.05}
        elif days < 7:
            # building history — gradually shift weight
            weights = {"quiz": 0.60, "history": 0.25, "behavioral": 0.15}
        else:
            # full data — balanced formula
            weights = {"quiz": 0.50, "history": 0.30, "behavioral": 0.20}

        final = (
            quiz_score       * weights["quiz"]       +
            history_score    * weights["history"]    +
            behavioral_score * weights["behavioral"]
        )
        final = round(max(0, min(100, final)))
        note  = f"full_calculation_{days}_days_history"

    # ── Zone determination using YOUR ranges ─────────────────
    if final <= 30:
        zone, label, allowed_tasks, tone = (
            "high_load", "High Cognitive Load", 1, "gentle"
        )
    elif final <= 60:
        zone, label, allowed_tasks, tone = (
            "medium_load", "Medium Cognitive Load", 3, "calm"
        )
    else:
        zone, label, allowed_tasks, tone = (
            "low_load", "Low Cognitive Load", 5, "energetic"
        )

    return {
        "final_score":        final,
        "quiz_score":         quiz_score,
        "history_score":      history_score,
        "behavioral_score":   behavioral_score,
        "zone":               zone,
        "label":              label,
        "allowed_tasks":      allowed_tasks,
        "tone":               tone,
        "calculation_note":   note,   # useful for debugging + Langfuse tracing
        "is_first_time":      is_first_time,
    }
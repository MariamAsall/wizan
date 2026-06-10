def get_limits(score):
    """
    Returns hard and soft limits based on cognitive score.
    Hard limit  → task is ALWAYS blocked, user cannot override
    Soft limit  → task is warned but user CAN override
    """

    # Boundary scores 
    if score == 0:
        return {
            "hard_block": ["high", "medium", "low"],
            "soft_warn": [],
            "message": "Your cognitive load is at maximum. No tasks are allowed today. Please rest."
        }

    if score == 100:
        return {
            "hard_block": [],
            "soft_warn": [],
            "message": "You are at peak performance. All tasks are allowed today."
        }

    # High load (score 1–30) 
    if score <= 30:
        return {
            "hard_block": ["high"],
            "soft_warn": ["medium"],
            "message": "Your cognitive load is high. Only easy tasks are recommended today."
        }

    # Medium load (score 31–60) 
    if score <= 60:
        return {
            "hard_block": [],
            "soft_warn": ["high"],
            "message": "Your cognitive load is moderate. High priority tasks may be challenging."
        }

    # Low load (score 61–99) 
    return {
        "hard_block": [],
        "soft_warn": [],
        "message": "Your cognitive load is low. All tasks are allowed today."
    }


def apply_limits(tasks, score):
    """
    Takes a list of tasks and a score,
    returns each task tagged with its status.
    """
    limits = get_limits(score)
    result = []

    for task in tasks:
        priority = task.get("priority", "medium")

        if priority in limits["hard_block"]:
            result.append({
                **task,
                "status": "blocked",
                "can_override": False,
                "reason": limits["message"]
            })

        elif priority in limits["soft_warn"]:
            result.append({
                **task,
                "status": "warned",
                "can_override": True,
                "reason": limits["message"]
            })

        else:
            result.append({
                **task,
                "status": "allowed",
                "can_override": False,
                "reason": ""
            })

    return result, limits["message"]
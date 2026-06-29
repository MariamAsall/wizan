# # backend/ai/behavioral_score.py

# def calculate_behavioral_score(user) -> dict:
#     """
#     Measures two habits:
#     1. Task follow-through  — did user complete tasks Wizan allowed? (60pts max)
#     2. App consistency      — did user show up and take quiz this week? (40pts max)

#     Data sources:
#     - Task model: only tasks with source="wizan_assigned" (not personal tasks)
#     - CognitiveLog: counts days user took the quiz this week
#     """
#     from cognitive_logs.models import CognitiveLog
#     from tasks.models import Task
#     from django.utils.timezone import localdate
#     from datetime import timedelta

#     one_week_ago = localdate() - timedelta(days=7)

#     # ── Habit 1: Task follow-through ────────────────────────
#     # only count tasks that Wizan assigned — not personal to-do items
#     # your Task model needs a field like: source = "wizan_assigned" or "user_added"
#     wizan_tasks = Task.objects.filter(
#         user=user,
#         created_at__date__gte=one_week_ago,
#         source="wizan_assigned"       # only tasks the system gave them
#     )

#     total_assigned = wizan_tasks.count()
#     total_completed = wizan_tasks.filter(status="completed").count()

#     if total_assigned == 0:
#         # new user — no tasks assigned yet
#         # give neutral score, not punishment
#         completion_bonus = 30.0
#         completion_rate  = None
#     else:
#         completion_rate  = total_completed / total_assigned
#         completion_bonus = completion_rate * 60

#     # ── Habit 2: App consistency ─────────────────────────────
#     # how many days this week did they actually take the quiz?
#     quiz_days = CognitiveLog.objects.filter(
#         user=user,
#         log_date__gte=one_week_ago,
#         score__isnull=False            # skipped days don't count
#     ).values_list("log_date", flat=True).distinct().count()

#     consistency_bonus = (quiz_days / 7) * 40

#     behavioral = round(min(100.0, completion_bonus + consistency_bonus), 2)

#     return {
#         "behavioral_score":    behavioral,
#         "completion_bonus":    round(completion_bonus, 2),
#         "consistency_bonus":   round(consistency_bonus, 2),
#         "completion_rate":     completion_rate,
#         "quiz_days_this_week": quiz_days,
#         "wizan_tasks_assigned": total_assigned,
#         "wizan_tasks_completed": total_completed,
#     }


# #test
# # at the bottom of behavioral_score.py
# if __name__ == "__main__":
#     print("Behavioral score week 1 version")
#     print("consistency_bonus formula: (quiz_days/7) × 40")
#     print("completion_bonus fixed at: 30.0")
#     print("max possible:", 30.0 + 40.0, "= 70.0")
#     print("✅ behavioral_score.py structure is correct")


# backend/WizanBackend/ai/behavioral_score.py

def calculate_behavioral_score(user) -> dict:
    from cognitive_logs.models import CognitiveLog
    from django.utils.timezone import localdate
    from datetime import timedelta

    one_week_ago = localdate() - timedelta(days=7)

    # ── Habit 1: Task follow-through ──────────────
    # tasks app doesn't exist yet — Week 2
    try:
        from tasks.models import Task
        wizan_tasks = Task.objects.filter(
            user=user,
            created_at__date__gte=one_week_ago,
            source="wizan_assigned"
        )
        total_assigned   = wizan_tasks.count()
        total_completed  = wizan_tasks.filter(status="completed").count()
        completion_rate  = total_completed / total_assigned if total_assigned > 0 else None
        completion_bonus = (completion_rate * 60) if completion_rate else 30.0
    except ModuleNotFoundError:
        # tasks app not built yet — neutral score, not punishment
        total_assigned   = 0
        total_completed  = 0
        completion_rate  = None
        completion_bonus = 30.0

    # ── Habit 2: App consistency ───────────────────
    quiz_days = CognitiveLog.objects.filter(
        user=user,
        log_date__gte=one_week_ago,
        score__isnull=False
    ).values_list("log_date", flat=True).distinct().count()

    consistency_bonus = (quiz_days / 7) * 40
    behavioral        = round(min(100.0, completion_bonus + consistency_bonus), 2)

    return {
        "behavioral_score":      behavioral,
        "completion_bonus":      completion_bonus,
        "consistency_bonus":     round(consistency_bonus, 2),
        "completion_rate":       completion_rate,
        "quiz_days_this_week":   quiz_days,
        "wizan_tasks_assigned":  total_assigned,
        "wizan_tasks_completed": total_completed,
    }
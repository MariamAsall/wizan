# ai/task_regulator_tools.py

from cognitive_logs.models import CognitiveLog
from datetime import date

def check_score(user_id):
    try:
        log = CognitiveLog.objects.filter(user_id=user_id).latest('created_at')
        return {"score": log.final_score, "zone": get_zone(log.final_score)}
    except CognitiveLog.DoesNotExist:
        return {"score": 50, "zone": "medium_load"}

def get_zone(score):
    if score <= 30: return "high_load"
    if score <= 60: return "medium_load"
    return "low_load"

def get_tasks(user_id):
    try:
        from tasks.models import Task
        tasks = Task.objects.filter(user_id=user_id, status="pending")
        return [
            {
                "id": str(t.id),
                "name": t.name,
                "priority": t.priority,
                "cognitive_cost": t.cognitive_cost,
                "deadline": str(t.deadline) if t.deadline else None,
            }
            for t in tasks
        ]
    except Exception:
        return []

def postpone_task(task_id, postpone_to_date):
    try:
        from tasks.models import Task
        Task.objects.filter(id=task_id).update(
            status="postponed",
            postponed_to=postpone_to_date
        )
        return {"success": True, "task_id": task_id, "postponed_to": postpone_to_date}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─── Tool declarations for Gemini ───────────────────────────────────────────

def get_tool_declarations():
    return [
        {
            "function_declarations": [
                {
                    "name": "check_score",
                    "description": "Gets the user's cognitive score for today. Always call this first before making any task decisions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "The ID of the user"
                            }
                        },
                        "required": ["user_id"]
                    }
                },
                {
                    "name": "get_tasks",
                    "description": "Gets the list of pending tasks for the user including priority, deadline, and cognitive cost.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "The ID of the user"
                            }
                        },
                        "required": ["user_id"]
                    }
                },
                {
                    "name": "postpone_task",
                    "description": "Postpones a task to a later date. Only call this after checking the score and deciding the task is too heavy for today.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The ID of the task to postpone"
                            },
                            "postpone_to_date": {
                                "type": "string",
                                "description": "The date to postpone to, in YYYY-MM-DD format"
                            }
                        },
                        "required": ["task_id", "postpone_to_date"]
                    }
                }
            ]
        }
    ]
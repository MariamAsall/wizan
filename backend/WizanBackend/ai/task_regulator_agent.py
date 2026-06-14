# import uuid
# import os
# from pathlib import Path
# from dotenv import load_dotenv

# from google import genai
# from google.genai import types

# from .task_regulator_tools import check_score, get_tasks, postpone_task, get_tool_declarations
# from .task_regulator_memory import get_session, save_session
# from .task_regulator_limits import apply_limits
# from .prompt_builder import build_system_prompt
# from .memory_manager import save_session_summary, load_past_summaries

# env_path = Path(__file__).resolve().parent.parent / ".env"
# load_dotenv(env_path, override=True)

# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# BASE_PROMPT = """
# You are the Task Regulator Agent for Wizan.
# Your job is to look at the user's cognitive score and their tasks,
# then decide which tasks are allowed today and which should be postponed.
# Always call check_score() first, then get_tasks(), then make your decisions.
# Rules:
# - blocked tasks must be postponed, user cannot override them
# - warned tasks should be postponed but user can override if they insist
# - allowed tasks should stay as they are
# """

# TOOLS = {
#     "check_score": check_score,
#     "get_tasks":   get_tasks,
#     "postpone_task": postpone_task,
# }


# def _get_score_data(user_id: int) -> dict:
#     """
#     Why this function instead of calculate_total_score()?
#     Because by the time this agent runs, the user already took the quiz.
#     The signal already calculated final_score and saved it to CognitiveLog.
#     We just read it — no recalculation, no extra DB queries.
#     """
#     try:
#         from cognitive_logs.models import CognitiveLog
#         log = CognitiveLog.objects.filter(user_id=user_id).latest('created_at')
#         s   = log.final_score or 50
#         if s <= 30:
#             return {"final_score": s, "zone": "high_load",   "tone": "gentle",    "allowed_tasks": 1, "label": "High Cognitive Load",   "is_first_time": False}
#         elif s <= 60:
#             return {"final_score": s, "zone": "medium_load", "tone": "calm",      "allowed_tasks": 3, "label": "Medium Cognitive Load", "is_first_time": False}
#         else:
#             return {"final_score": s, "zone": "low_load",    "tone": "energetic", "allowed_tasks": 5, "label": "Low Cognitive Load",    "is_first_time": False}
#     except Exception:
#         return {"final_score": 50, "zone": "medium_load", "tone": "calm", "allowed_tasks": 3, "label": "Medium Cognitive Load", "is_first_time": False}


# def run_task_regulator(user_id, user_message, session_memory, session_id=None):

#     # generate session ID if new session
#     if session_id is None:
#         session_id = f"session_{user_id}_{uuid.uuid4().hex[:8]}"

#     # Step 1 — read score from DB (already calculated by signal)
#     score_data    = _get_score_data(user_id)
#     current_score = score_data["final_score"]

#     # Step 2 — load past session summaries + build system prompt
#     past_summaries = load_past_summaries(user_id, count=3)
#     system_prompt  = build_system_prompt(BASE_PROMPT, score_data, past_summaries)

#     # Step 3 — build tool config for new google.genai SDK
#     tools  = types.Tool(
#         function_declarations=get_tool_declarations()[0]["function_declarations"]
#     )
#     config = types.GenerateContentConfig(
#         system_instruction=system_prompt,
#         tools=[tools]
#     )

#     # Step 4 — add user message to memory
#     session_memory.append({
#         "role": "user",
#         "parts": [{"text": user_message}]
#     })

#     # Step 5 — agent loop (max 3 iterations to save quota)
#     # Why 3? check_score → get_tasks → postpone+reply = 3 max
#     for _ in range(3):
#         # In task_regulator_agent.py, wrap the generate call:

#         try:
#             response = client.models.generate_content(
#                 model="gemini-2.5-flash",
#                 contents=session_memory,
#                 config=config
#             )
#         except Exception as e:
#             if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
#                 save_session_summary(user_id, session_id, session_memory)
#                 return {
#                     "response": "The system is currently busy. Please try again in a few minutes.",
#                     "memory": session_memory,
#                     "session_id": session_id
#                 }
#             raise  # any other error — still crash loudly
#         # response  = client.models.generate_content(
#         #     model="gemini-2.5-flash",
#         #     contents=session_memory,
#         #     config=config
#         # )
#         candidate = response.candidates[0]
#         tool_calls = [p for p in candidate.content.parts if hasattr(p, 'function_call')]

#         if not tool_calls:
#             # No more tool calls — Gemini has the final answer
#             final_text = candidate.content.parts[0].text
#             session_memory.append({
#                 "role": "model",
#                 "parts": [{"text": final_text}]
#             })
#             save_session_summary(user_id, session_id, session_memory)
#             return {
#                 "response":   final_text,
#                 "memory":     session_memory,
#                 "session_id": session_id
#             }

#         # Execute each tool Gemini requested
#         tool_results = []
#         for tc in tool_calls:
#             fn_name = tc.function_call.name
#             fn_args = dict(tc.function_call.args)
#             fn_args["user_id"] = str(user_id)

#             result = TOOLS[fn_name](**fn_args)

#             # After get_tasks — tag each task with allowed/warned/blocked
#             if fn_name == "get_tasks":
#                 tagged_tasks, limit_message = apply_limits(result, current_score)
#                 result = {"tasks": tagged_tasks, "limit_message": limit_message}

#             tool_results.append({
#                 "function_response": {
#                     "name":     fn_name,
#                     "response": result
#                 }
#             })

#         session_memory.append({"role": "model", "parts": tool_calls})
#         session_memory.append({"role": "user",  "parts": tool_results})

#     # Hit max iterations without finishing
#     save_session_summary(user_id, session_id, session_memory)
#     return {
#         "response":   "Could not complete task regulation.",
#         "memory":     session_memory,
#         "session_id": session_id
#     }


import uuid
import os
import json
from pathlib import Path
from dotenv import load_dotenv

from .task_regulator_tools import check_score, get_tasks, postpone_task
from .task_regulator_limits import apply_limits
from .prompt_builder import build_system_prompt
from .memory_manager import save_session_summary, load_past_summaries
from ai.llm import safe_llm_call   # ← works with both Gemini and Groq

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path, override=True)

BASE_PROMPT = """
You are the Task Regulator Agent for Wizan.
You will be given the user's cognitive score and their task list.
Based on this information, decide which tasks are allowed today and which should be postponed.

Rules:
- blocked tasks must be postponed, user cannot override them
- warned tasks should be postponed but user can override if they insist  
- allowed tasks should stay as they are

Respond in a clear, supportive message explaining your decisions.
"""


def _get_score_data(user_id: int) -> dict:
    """
    Read already-saved score from DB.
    Why not recalculate? Because the signal already did it after the quiz.
    """
    try:
        from cognitive_logs.models import CognitiveLog
        log = CognitiveLog.objects.filter(user_id=user_id).latest('created_at')
        s   = log.final_score or 50
        if s <= 30:
            return {"final_score": s, "zone": "high_load",   "tone": "gentle",    "allowed_tasks": 1, "label": "High Cognitive Load",   "is_first_time": False}
        elif s <= 60:
            return {"final_score": s, "zone": "medium_load", "tone": "calm",      "allowed_tasks": 3, "label": "Medium Cognitive Load", "is_first_time": False}
        else:
            return {"final_score": s, "zone": "low_load",    "tone": "energetic", "allowed_tasks": 5, "label": "Low Cognitive Load",    "is_first_time": False}
    except Exception:
        return {"final_score": 50, "zone": "medium_load", "tone": "calm", "allowed_tasks": 3, "label": "Medium Cognitive Load", "is_first_time": False}


def run_task_regulator(user_id, user_message, session_memory, session_id=None):

    if session_id is None:
        session_id = f"session_{user_id}_{uuid.uuid4().hex[:8]}"

    # Step 1 — get score from DB (no LLM call needed)
    score_data    = _get_score_data(user_id)
    current_score = score_data["final_score"]

    # Step 2 — run the tools ourselves in Python (no LLM needed here)
    # Why? Because we don't need Gemini to "decide" to call these.
    # We ALWAYS need the score and tasks — so we just fetch them directly.
    score_result = check_score(user_id)
    tasks_result = get_tasks(user_id)

    # Step 3 — apply limits to tag each task
    tagged_tasks, limit_message = apply_limits(tasks_result, current_score)

    # Step 4 — build context string with all the data
    # Why a string? Because safe_llm_call takes one prompt.
    # We give Groq everything it needs to make a decision.
    tasks_text = ""
    for task in tagged_tasks:
        status    = task.get("status", "allowed")
        name      = task.get("name", "Unknown task")
        priority  = task.get("priority", "medium")
        deadline  = task.get("deadline", "no deadline")
        tasks_text += f"- {name} | priority: {priority} | deadline: {deadline} | status: {status}\n"

    if not tasks_text:
        tasks_text = "No pending tasks found."

    # Step 5 — load past session summaries for context
    past_summaries = load_past_summaries(user_id, count=3)

    # Step 6 — build system prompt
    system_prompt = build_system_prompt(BASE_PROMPT, score_data, past_summaries)

    # Step 7 — build one complete prompt for the LLM
    # Why one prompt? Because safe_llm_call is one call, one response.
    # We give the LLM all context and ask for one clear decision.
    full_prompt = f"""{system_prompt}

=== TODAY'S DATA ===
Cognitive Score: {current_score}/100
Zone: {score_data['zone']}
Tone: {score_data['tone']}
Max tasks allowed: {score_data['allowed_tasks']}

Tasks:
{tasks_text}

System limit message: {limit_message}

=== USER MESSAGE ===
{user_message}

Based on the above, give the user a clear, supportive response about:
1. What tasks they can do today (allowed ones)
2. What tasks are postponed and why
3. One encouraging sentence based on their cognitive state
"""

    # Step 8 — one LLM call (Gemini first, Groq fallback)
    # Why safe_llm_call? Because it handles quota automatically.
    # No loop needed — all data is already in the prompt.
    response_text = safe_llm_call(full_prompt)

    # Step 9 — handle postponements
    # If any tasks are blocked, postpone them automatically
    from datetime import date, timedelta
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    for task in tagged_tasks:
        if task.get("status") == "blocked":
            postpone_task(task["id"], tomorrow)

    # Step 10 — update session memory
    session_memory.append({"role": "user",  "parts": [{"text": user_message}]})
    session_memory.append({"role": "model", "parts": [{"text": response_text}]})

    # Step 11 — save session summary
    save_session_summary(user_id, session_id, session_memory)

    return {
        "response":   response_text,
        "memory":     session_memory,
        "session_id": session_id
    }
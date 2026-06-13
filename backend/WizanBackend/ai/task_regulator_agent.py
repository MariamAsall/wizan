import uuid                                                          # ← NEW
import google.generativeai as genai
from .task_regulator_tools import check_score, get_tasks, postpone_task, get_tool_declarations
from .task_regulator_memory import get_session, save_session
from .task_regulator_limits import apply_limits
from .prompt_builder import build_system_prompt
from .total_score import calculate_total_score
from .memory_manager import save_session_summary, load_past_summaries  # ← NEW

from django.contrib.auth import get_user_model

BASE_PROMPT = """
You are the Task Regulator Agent for Wizan.
Your job is to look at the user's cognitive score and their tasks,
then decide which tasks are allowed today and which should be postponed.
Always call check_score() first, then get_tasks(), then make your decisions.
Rules:
- blocked tasks must be postponed, user cannot override them
- warned tasks should be postponed but user can override if they insist
- allowed tasks should stay as they are
"""

TOOLS = {
    "check_score": check_score,
    "get_tasks": get_tasks,
    "postpone_task": postpone_task,
}

def run_task_regulator(user_id, user_message, session_memory, session_id=None):  # ← NEW: session_id param

    User = get_user_model()
    user = User.objects.get(id=user_id)

    # Step 1 — calculate score for this user
    score_data = calculate_total_score(user, None)
    current_score = score_data.get("final_score", 50)

    # NEW: generate a session ID if this is a brand new session
    if session_id is None:
        session_id = f"session_{user_id}_{uuid.uuid4().hex[:8]}"

    # Step 1.5 — load past summaries and inject into prompt  ← NEW BLOCK
    past_summaries = load_past_summaries(user_id, count=3)
    system_prompt = build_system_prompt(
        BASE_PROMPT,
        score_data,
        past_summaries
    )

    # Step 2 — (was build_system_prompt, now handled above with summaries)

    # Step 3 — create the Gemini model with that system prompt
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=system_prompt,
        tools=get_tool_declarations()
    )

    # Step 4 — add user message to memory
    session_memory.append({
        "role": "user",
        "parts": [{"text": user_message}]
    })

    # Step 5 — agent loop (unchanged)
    max_iterations = 5

    for _ in range(max_iterations):

        response = model.generate_content(session_memory)
        candidate = response.candidates[0]

        tool_calls = [
            p for p in candidate.content.parts
            if hasattr(p, "function_call")
        ]

        if not tool_calls:

            final_text = candidate.content.parts[0].text

            session_memory.append({
                "role": "model",
                "parts": [{"text": final_text}]
            })

            # NEW: save this session's summary to DB before returning
            save_session_summary(
                user_id,
                session_id,
                session_memory
            )

            return {
                "response": final_text,
                "memory": session_memory,
                "session_id": session_id  # ← NEW: return it so view can store it
            }

        tool_results = []

        for tc in tool_calls:

            fn_name = tc.function_call.name
            fn_args = dict(tc.function_call.args)

            fn_args["user_id"] = str(user_id)

            result = TOOLS[fn_name](**fn_args)

            # apply limits right after get_tasks()
            if fn_name == "get_tasks":

                tagged_tasks, limit_message = apply_limits(
                    result,
                    current_score
                )

                result = {
                    "tasks": tagged_tasks,
                    "limit_message": limit_message
                }

            tool_results.append({
                "function_response": {
                    "name": fn_name,
                    "response": result
                }
            })

        session_memory.append({
            "role": "model",
            "parts": tool_calls
        })

        session_memory.append({
            "role": "user",
            "parts": tool_results
        })

    # NEW: also save if we hit max iterations without finishing
    save_session_summary(
        user_id,
        session_id,
        session_memory
    )

    return {
        "response": "Could not complete task regulation.",
        "memory": session_memory,
        "session_id": session_id
    }
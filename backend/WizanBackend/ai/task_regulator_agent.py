import google.generativeai as genai
from .task_regulator_tools import check_score, get_tasks, postpone_task, get_tool_declarations
from .task_regulator_memory import get_session, save_session
from .prompt_builder import build_system_prompt       # ← your prompt builder
from .total_score import calculate_total_score        # ← your existing score pipeline

BASE_PROMPT = """
You are the Task Regulator Agent for Wizan.
Your job is to look at the user's cognitive score and their tasks,
then decide which tasks are allowed today and which should be postponed.
Always call check_score() first, then get_tasks(), then make your decisions.
"""

TOOLS = {
    "check_score": check_score,
    "get_tasks": get_tasks,
    "postpone_task": postpone_task,
}

def run_task_regulator(user_id, user_message, session_memory):

    # Step 1 — calculate score for this user
    score_data = calculate_total_score(user_id)   # returns the full dict

    # Step 2 — build the system prompt by injecting score data
    system_prompt = build_system_prompt(BASE_PROMPT, score_data)

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

    # Step 5 — agent loop
    max_iterations = 5
    for _ in range(max_iterations):
        response = model.generate_content(session_memory)
        candidate = response.candidates[0]

        tool_calls = [p for p in candidate.content.parts if hasattr(p, 'function_call')]

        if not tool_calls:
            final_text = candidate.content.parts[0].text
            session_memory.append({
                "role": "model",
                "parts": [{"text": final_text}]
            })
            return {"response": final_text, "memory": session_memory}

        tool_results = []
        for tc in tool_calls:
            fn_name = tc.function_call.name
            fn_args = dict(tc.function_call.args)
            fn_args["user_id"] = str(user_id)

            result = TOOLS[fn_name](**fn_args)
            tool_results.append({
                "function_response": {
                    "name": fn_name,
                    "response": result
                }
            })

        session_memory.append({"role": "model", "parts": tool_calls})
        session_memory.append({"role": "user", "parts": tool_results})

    return {"response": "Could not complete task regulation.", "memory": session_memory}
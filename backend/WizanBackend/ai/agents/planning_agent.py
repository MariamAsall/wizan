# ai/planning_agent.py

from datetime import date
from ai.llm import safe_llm_call              # ← changed from get_llm
from ai.memory_manager import get_session, save_session
from ai.prompt_builder import build_system_prompt
from ai.prompt_loader import load_prompt

from ai.llm import safe_llm_call  # Changed import


AGENT_NAME = "planning_agent"


def run_planning_agent(user_message: str, score_data: dict, user, session_id: str) -> str:
    """
    One turn of the Planning Agent.
    Makes exactly 1 LLM call per user message.
    """

    # Step 1 — load and format system prompt from YAML
    yaml_data         = load_prompt(AGENT_NAME)
    raw_template      = yaml_data.get("system_prompt", "")
    formatted_base    = raw_template.format(
        score        = score_data.get("score", score_data.get("final_score", 50)),
        zone         = score_data.get("zone", "MEDIUM"),
        tone         = score_data.get("tone", "calm"),
        allowed_tasks= score_data.get("allowed_tasks", 3),
        today        = date.today().isoformat(),
        language     = getattr(user, "language", "en"),
    )

    system_prompt = build_system_prompt(
        base_prompt = formatted_base,
        score_data  = {
            **score_data,
            "final_score": score_data.get("final_score", score_data.get("score", 50)),
            "label":       score_data.get("label", f"{score_data.get('zone','Medium')} Cognitive Load"),
        },
    )

    # Step 2 — load past conversation from DB
    # Why? So the agent remembers what the user said earlier today.
    history = get_session(session_id, user=user)

    # Step 3 — append user message
    history.append({"role": "user", "content": user_message})

    # Step 4 — build one prompt string: system + full conversation history
    # Why one string? Because safe_llm_call takes a single prompt.
    conversation = f"SYSTEM:\n{system_prompt}\n\n"
    for turn in history:
        role = "USER" if turn["role"] == "user" else "ASSISTANT"
        conversation += f"{role}: {turn['content']}\n"

    # Step 5 — one LLM call (Gemini first, Groq fallback on quota)
    # Why not a loop? Because planning agent is conversational —
    # one user message → one assistant reply. No loop needed.
    reply = safe_llm_call(conversation)

    # Step 6 — save assistant reply to history
    # Why "assistant" not "model"?
    # LangChain uses "assistant". "model" is Gemini's raw SDK word.
    # Using wrong role causes silent failures on next turn.
    history.append({"role": "assistant", "content": reply})  # ← fixed role name

    # Step 7 — save updated history to DB
    save_session(session_id, history, user=user)

    return reply
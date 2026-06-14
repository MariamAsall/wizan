# ai/planning_agent.py

from datetime import date, timedelta
from ai.llm import safe_llm_call
from ai.memory_manager import get_session, save_session
from ai.prompt_builder import build_system_prompt
from ai.prompt_loader import load_prompt
from ai.task_regulator_tools import postpone_task  # to update DB status

AGENT_NAME = "planning_agent"

# ─────────────────────────────────────────────
# Priority weight — used to sort tasks smartly.
# Why a dict? Because "high" > "medium" > "low" has no numeric meaning
# by default. We assign numbers so Python can sort them.
# ─────────────────────────────────────────────
PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}


def _days_until_deadline(deadline_str: str) -> int:
    """
    Convert a deadline string like '2025-06-20' into how many days away it is.
    Why? So we can sort by urgency — closer deadline = higher urgency.
    If no deadline exists, we treat it as very far away (999 days).
    """
    if not deadline_str or deadline_str == "no deadline":
        return 999
    try:
        deadline_date = date.fromisoformat(deadline_str)
        return (deadline_date - date.today()).days
    except ValueError:
        return 999


def _select_tasks_to_allow(tagged_tasks: list, max_allowed: int) -> tuple[list, list]:
    """
    From the full task list, pick which tasks stay 'allowed' today
    and which get changed to 'postponed'.

    Selection logic:
    1. Tasks already blocked by the Regulator → always postponed (we don't touch those).
    2. Among the rest (allowed/warned), sort by:
       - Priority (high first)
       - Then deadline (sooner first)
    3. Keep the top `max_allowed` tasks → they stay allowed.
    4. Everything else → postponed.

    Why do we sort in Python and not ask the LLM?
    Because sorting is deterministic logic — fast, free, always correct.
    The LLM is for language, not arithmetic.
    """
    # Separate blocked tasks — they're already decided by the Regulator
    blocked = [t for t in tagged_tasks if t.get("status") == "blocked"]

    # Candidates = tasks the Regulator didn't hard-block
    candidates = [t for t in tagged_tasks if t.get("status") != "blocked"]

    # Sort candidates: highest priority first, then soonest deadline first
    candidates.sort(
        key=lambda t: (
            -PRIORITY_WEIGHT.get(t.get("priority", "medium"), 2),  # negative → descending
            _days_until_deadline(t.get("deadline", ""))             # ascending → sooner first
        )
    )

    # Take the top N as allowed; the rest become postponed
    will_allow   = candidates[:max_allowed]
    will_postpone = candidates[max_allowed:]

    return will_allow, blocked + will_postpone


def run_planning_agent(
    user_message: str,
    score_data: dict,
    user,
    session_id: str,
    tagged_tasks: list = None,   # ← NEW: task list from the Regulator Agent
) -> str:
    """
    One turn of the Planning Agent.

    Now receives tagged_tasks from the Task Regulator Agent.
    It decides which tasks stay allowed (by priority + deadline),
    updates the DB for postponed ones, then asks the LLM to
    build a concrete plan and explain it to the user.

    Makes exactly 1 LLM call per user message.
    """

    # Fallback: if no tasks were passed in, plan with empty list
    # Why not crash? Because the agent should still be able to respond.
    if tagged_tasks is None:
        tagged_tasks = []

    max_allowed = score_data.get("allowed_tasks", 3)

    # ── Step 1: Select which tasks are allowed vs postponed ──────────────
    # This is pure Python logic — no LLM involved here.
    will_allow, will_postpone = _select_tasks_to_allow(tagged_tasks, max_allowed)

    # ── Step 2: Update DB — change status to 'postponed' ─────────────────
    # Why only change to postponed, never to allowed?
    # Because 'allowed' is the default. We only override downward.
    # We also never change 'blocked' tasks — the Regulator already handled those.
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    for task in will_postpone:
        if task.get("status") != "blocked":  # don't double-handle blocked tasks
            postpone_task(task["id"], tomorrow)
            task["status"] = "postponed"     # update in-memory too so the prompt reflects it

    # ── Step 3: Build the task summary for the LLM ───────────────────────
    # We format the task list clearly so the LLM just explains — not decides.
    def format_task_list(tasks, label):
        if not tasks:
            return f"{label}: None\n"
        lines = f"{label}:\n"
        for t in tasks:
            priority = t.get("priority", "medium")
            deadline = t.get("deadline", "no deadline")
            name     = t.get("name", "Unknown task")
            lines += f"  • {name} | priority: {priority} | deadline: {deadline}\n"
        return lines

    tasks_context = (
        format_task_list(will_allow,    "✅ Allowed today")
        + "\n"
        + format_task_list(will_postpone, "⏸ Postponed to tomorrow")
    )

    # ── Step 4: Load and format the YAML system prompt ───────────────────
    yaml_data      = load_prompt(AGENT_NAME)
    raw_template   = yaml_data.get("system_prompt", "")
    formatted_base = raw_template.format(
        score         = score_data.get("score", score_data.get("final_score", 50)),
        zone          = score_data.get("zone", "MEDIUM"),
        tone          = score_data.get("tone", "calm"),
        allowed_tasks = max_allowed,
        today         = date.today().isoformat(),
        language      = getattr(user, "language", "en"),
    )

    system_prompt = build_system_prompt(
        base_prompt = formatted_base,
        score_data  = {
            **score_data,
            "final_score": score_data.get("final_score", score_data.get("score", 50)),
            "label":       score_data.get("label", f"{score_data.get('zone', 'Medium')} Cognitive Load"),
        },
    )

    # ── Step 5: Load conversation history ────────────────────────────────
    history = get_session(session_id, user=user)
    history.append({"role": "user", "content": user_message})

    # ── Step 6: Build the full prompt ────────────────────────────────────
    # The LLM gets: system context + task decisions already made + user message.
    # The LLM's job = explain the plan clearly + suggest how to approach each task.
    # It does NOT re-decide what's allowed — we already did that in Python.
    conversation = f"SYSTEM:\n{system_prompt}\n\n"
    conversation += f"=== TASK DECISIONS (already finalized) ===\n{tasks_context}\n\n"
    conversation += f"=== TODAY'S DATE: {date.today().isoformat()} ===\n\n"

    for turn in history:
        role = "USER" if turn["role"] == "user" else "ASSISTANT"
        conversation += f"{role}: {turn['content']}\n"

    conversation += (
        "\nASSISTANT: Based on the task decisions above, "
        "explain the plan to the user in a warm and concrete way. "
        "For allowed tasks, suggest an order and rough time estimate. "
        "For postponed tasks, give one reassuring sentence about why they're deferred. "
        "Do not re-decide what's allowed — those decisions are final.\n"
    )

    # ── Step 7: One LLM call ─────────────────────────────────────────────
    reply = safe_llm_call(conversation)

    # ── Step 8: Save history ─────────────────────────────────────────────
    history.append({"role": "assistant", "content": reply})
    save_session(session_id, history, user=user)

    # ── Step 9: Return reply + structured task data ───────────────────────
    # Why return task lists too?
    # So the caller (your view/API) can pass them to the frontend
    # to update the UI without a second DB query.
    return {
        "reply":         reply,
        "allowed_tasks": will_allow,
        "postponed_tasks": will_postpone,
    }
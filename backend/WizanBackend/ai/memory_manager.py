from ai.models import AgentMemory

def save_session_summary(user_id, session_id, conversation_history):
    """
    Called at the END of every session.
    Sends the conversation to Gemini, gets a summary, saves to DB.
    """
    import google.generativeai as genai

    # Build a readable transcript from the history list
    transcript = ""
    for turn in conversation_history:
        role = turn["role"]
        for part in turn["parts"]:
            if isinstance(part, dict) and "text" in part:
                transcript += f"{role}: {part['text']}\n"

    if not transcript.strip():
        return  # nothing to summarize

    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""
Summarize this conversation in 2-3 lines maximum.
Focus on: what tasks were allowed, what was postponed, and how the user felt.
Be factual and brief.

Conversation:
{transcript}
"""
    response = model.generate_content(prompt)
    summary_text = response.text.strip()

    AgentMemory.objects.create(
        user_id=user_id,
        session_id=session_id,
        summary=summary_text
    )


def load_past_summaries(user_id, count=3):
    """
    Called at the START of every session.
    Returns the last N session summaries as a single string.
    """
    records = AgentMemory.objects.filter(
        user_id=user_id
    ).order_by('-created_at')[:count]

    if not records:
        return ""

    lines = []
    for i, record in enumerate(reversed(records), 1):
        lines.append(f"Session {i} ({record.created_at.date()}): {record.summary}")

    return "\n".join(lines)
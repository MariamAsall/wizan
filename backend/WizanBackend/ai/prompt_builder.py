# backend/ai/prompt_builder.py

def build_system_prompt(base_prompt: str, score_data: dict , past_summaries: str = "")  -> str:
    """
    Called by EVERY agent before talking to Gemini.
    base_prompt  = the agent's own instructions (comes from the agent file)
    score_data   = dict from calculate_total_score()
    """

    final_score   = score_data.get("final_score", 50)
    zone          = score_data.get("zone", "medium_load")
    tone          = score_data.get("tone", "calm")
    allowed_tasks = score_data.get("allowed_tasks", 3)
    label         = score_data.get("label", "Medium Cognitive Load")
    is_first_time = score_data.get("is_first_time", False)

    tone_guide = {
        "gentle": (
            "User is overloaded. Be very gentle and supportive. "
            "Keep response short. Max 1 task. Never use complex language."
        ),
        "calm": (
            "User has moderate capacity. Be calm and structured. "
            "Max 3 tasks. Clear and organized language."
        ),
        "energetic": (
            "User is sharp today. Be motivating and detailed. "
            "Max 5 tasks. Challenge them appropriately."
        ),
    }

    first_time_note = (
        "\nNOTE: First time user — welcome them warmly.\n"
        if is_first_time else ""
    )

    # ← THIS is where the injection sits — between the two triple quotes
    injection = f"""
=== USER COGNITIVE STATE ===
Final Score:    {final_score}/100
Status:         {label}
Tone:           {tone}
Allowed Tasks:  {allowed_tasks} maximum today
{first_time_note}
Quiz inputs considered:
Sleep hours, Sleep quality, Stress level,
Energy level, Focus level, Mood (all rated 1-5)

Score Zones:
- 0  to 30:  High Load   → max 1 task, gentle tone
- 31 to 60:  Medium Load → max 3 tasks, calm tone
- 61 to 100: Low Load    → max 5 tasks, energetic tone

Tone Instructions:
{tone_guide[tone]}
============================

"""
    memory_section = ""
    if past_summaries:
        memory_section = f"""   
    === PAST SESSION MEMORY ===
{past_summaries}

Use this to understand the user's recent patterns.
If the user has been struggling for multiple sessions, be extra gentle.
===========================
"""
    
    # injection goes FIRST, then the agent's own base_prompt follows
    
    return base_prompt + memory_section + injection


if __name__ == "__main__":
    fake_score_data = {
        "final_score":   25,
        "zone":          "high_load",
        "tone":          "gentle",
        "allowed_tasks": 1,
        "label":         "High Cognitive Load",
        "is_first_time": False,
    }
    base = "You are the Wizan Planning Agent. Help break tasks into steps."
    print(build_system_prompt(base, fake_score_data))


    #test
    # at the bottom of prompt_builder.py
if __name__ == "__main__":
    fake = {
        "final_score": 25,
        "zone": "high_load",
        "tone": "gentle",
        "allowed_tasks": 1,
        "label": "High Cognitive Load",
        "is_first_time": False,
    }
    result = build_system_prompt("You are a test agent.", fake)
    print(result)
    assert "25/100" in result, "❌ score not injected"
    assert "gentle" in result, "❌ tone not injected"
    assert "1 maximum" in result, "❌ allowed tasks not injected"
    print("✅ prompt_builder.py works")
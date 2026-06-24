# ai/cognitive_agent.py

from ai.llm import safe_llm_call              # ← changed from get_llm
from ai.prompt_builder import build_system_prompt
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Literal
import json
from ai.filters.pii_filter import filter_pii

class CognitiveResponse(BaseModel):
    message:        str                              = Field(description="Supportive message about user's state today")
    tone:           Literal["gentle","calm","energetic"] = Field(description="Tone matching cognitive zone")
    allowed_tasks:  int                              = Field(description="Tasks user can handle today, 1 to 5")
    recommendation: str                              = Field(description="One practical first action for the user")


def run_cognitive_agent(user, final_score: int, zone: str = None) -> dict:
    """
    Called after quiz submission signal saves the score.
    Does NOT recalculate — just reads final_score and calls Gemini once.
    """

    # Step 1 — build score_data from final_score
    # Why here instead of importing calculate_total_score?
    # Because the signal already calculated and saved it.
    # We just map it to what prompt_builder expects.
    if final_score <= 30:
        score_data = {
            "final_score":   final_score,
            "zone":          "high_load",
            "label":         "High Cognitive Load",
            "tone":          "gentle",
            "allowed_tasks": 1,
            "is_first_time": "first_time" in (zone or ""),
        }
    elif final_score <= 60:
        score_data = {
            "final_score":   final_score,
            "zone":          "medium_load",
            "label":         "Medium Cognitive Load",
            "tone":          "calm",
            "allowed_tasks": 3,
            "is_first_time": "first_time" in (zone or ""),
        }
    else:
        score_data = {
            "final_score":   final_score,
            "zone":          "low_load",
            "label":         "Low Cognitive Load",
            "tone":          "energetic",
            "allowed_tasks": 5,
            "is_first_time": "first_time" in (zone or ""),
        }

    # Step 2 — build system prompt with cognitive state injected
    base_prompt = """
You are the Wizan Cognitive Agent.
Generate a personalized daily briefing based on the user's cognitive state above.

RULES:
- Respond in valid JSON ONLY — no text outside the JSON
- allowed_tasks must NEVER exceed the Allowed Tasks number stated above
- Match tone exactly to Tone Instructions above
- Acknowledge the user's state before giving advice
- Respond in Arabic if user writes in Arabic, English otherwise

Return exactly this structure:
{
    "message": "your supportive message here",
    "tone": "gentle" or "calm" or "energetic",
    "allowed_tasks": number between 1 and 5,
    "recommendation": "one practical sentence"
}
"""
    full_system = build_system_prompt(base_prompt, score_data)

    # Step 3 — call LLM safely (Gemini first, Groq fallback)
    # Why safe_llm_call instead of get_llm().invoke()?
    # Because if Gemini quota hits, it switches to Groq automatically.
    # The chain (prompt | llm | parser) approach requires get_llm() directly,
    # so we call safe_llm_call and parse the JSON ourselves instead.
    prompt_text = full_system + "\n\nGenerate my cognitive briefing for today."
    raw = safe_llm_call(prompt_text)

    # Step 4 — parse JSON response
    try:
        cleaned = raw.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        # Safe fallback if Gemini returns non-JSON
        result = {
            "message":        "Let's take today one step at a time.",
            "tone":           score_data["tone"],
            "allowed_tasks":  score_data["allowed_tasks"],
            "recommendation": "Start with your easiest task first."
        }

    # Step 5 — attach score metadata
    result["final_score"] = final_score
    result["zone"]        = score_data["zone"]

    result["message"] = filter_pii(result.get("message", ""))
    result["recommendation"] = filter_pii(result.get("recommendation", ""))

    return result
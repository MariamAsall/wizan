# # backend/ai/cognitive_agent.py

# import os
# import django
# from pathlib import Path
# from dotenv import load_dotenv

# # ── Django setup — needed because we query the DB ──────────
# load_dotenv(Path(__file__).resolve().parent.parent / ".env")
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WizanBackend.settings")  # ← change "core" to your Django project folder name
# django.setup()
# # ────────────────────────────────────────────────────────────

# from ai.llm import get_llm
# from ai.prompt_builder import build_system_prompt
# from ai.total_score import calculate_total_score
# from ai.cognitive_score import calculate_cognitive_score
# from langchain_core.output_parsers import JsonOutputParser
# from langchain_core.prompts import ChatPromptTemplate
# from pydantic import BaseModel, Field
# from typing import Literal


# # Step 1 — define the exact JSON shape you want from Gemini
# class CognitiveResponse(BaseModel):
#     message: str = Field(
#         description="Supportive message about the user's state today"
#     )
#     tone: Literal["gentle", "calm", "energetic"] = Field(
#         description="Tone used — must match cognitive zone"
#     )
#     allowed_tasks: int = Field(
#         description="Number of tasks user can handle today, 1 to 5"
#     )
#     recommendation: str = Field(
#         description="One practical sentence for what user should do first"
#     )


# def run_cognitive_agent(user, quiz_answers: dict) -> dict:
#     """
#     Main function — called from the Django view after quiz submission.

#     user         = request.user (Django User object)
#     quiz_answers = {
#         "sleep_hours": 3,
#         "sleep_quality": 2,
#         "stress_level": 4,
#         "energy_level": 2,
#         "focus_level": 2,
#         "mood": 2
#     }
#     """

#     # Step 2 — convert quiz answers to quiz_score number
#     quiz_score = calculate_cognitive_score(quiz_answers)

#     # Step 3 — combine with history + behavioral to get final score
#     score_data = calculate_total_score(user=user, quiz_score=quiz_score)

#     # Step 4 — the cognitive agent's own base instructions
#     base_prompt = """
# You are the Wizan Cognitive Agent.
# Your job is to read the user's cognitive state and generate a personalized daily briefing.

# RULES:
# - Respond in valid JSON ONLY — no extra text outside the JSON
# - allowed_tasks in your response must NEVER exceed the number stated above
# - Match tone exactly to Tone Instructions above
# - Always acknowledge the user's state before giving advice
# - Respond in Arabic if user writes in Arabic, English otherwise

# Return exactly this structure:
# {
#     "message": "your supportive message here",
#     "tone": "gentle" or "calm" or "energetic",
#     "allowed_tasks": number between 1 and 5,
#     "recommendation": "one practical sentence"
# }
# """

#     # Step 5 — inject cognitive state into the prompt
#     full_system = build_system_prompt(base_prompt, score_data)

#     # Step 6 — build LangChain chain: prompt → llm → json parser
#     llm    = get_llm()
#     parser = JsonOutputParser(pydantic_object=CognitiveResponse)

#     prompt = ChatPromptTemplate.from_messages([
#         ("system", full_system),
#         ("human", "Generate my cognitive briefing for today."),
#     ])

#     chain = prompt | llm | parser

#     # Step 7 — call Gemini and get structured JSON back
#     result = chain.invoke({})

#     # Step 8 — attach score metadata to the response
#     result["final_score"]       = score_data["final_score"]
#     result["zone"]              = score_data["zone"]
#     result["is_first_time"]     = score_data["is_first_time"]
#     result["calculation_note"]  = score_data["calculation_note"]

#     return result


# # ── Test block ──────────────────────────────────────────────
# if __name__ == "__main__":
#     import json
#     from django.contrib.auth import get_user_model

#     User = get_user_model()
#     user = User.objects.first()   # uses first user in your DB

#     if not user:
#         print("No users in DB yet — create one first via Django admin")
#     else:
#         quiz_answers = {
#             "sleep_hours":   3,
#             "sleep_quality": 2,
#             "stress_level":  4,
#             "energy_level":  2,
#             "focus_level":   2,
#             "mood":          2,
#         }

#         response = run_cognitive_agent(user=user, quiz_answers=quiz_answers)
#         print(json.dumps(response, indent=2, ensure_ascii=False))


# backend/WizanBackend/ai/cognitive_agent.py

from ai.llm import get_llm
from ai.prompt_builder import build_system_prompt
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Literal


class CognitiveResponse(BaseModel):
    message: str = Field(description="Supportive message about user's state today")
    tone: Literal["gentle", "calm", "energetic"] = Field(description="Tone matching cognitive zone")
    allowed_tasks: int = Field(description="Tasks user can handle today, 1 to 5")
    recommendation: str = Field(description="One practical first action for the user")


def run_cognitive_agent(user, final_score: int, zone: str = None) -> dict:
    """
    Reads final_score that signal already saved.
    No recalculation — just builds prompt and calls Gemini.

    final_score = already calculated and saved in CognitiveLog.final_score
    zone        = from CognitiveLog.calculation_note
    """

    # build score_data from the ready final_score
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

    llm    = get_llm()
    parser = JsonOutputParser(pydantic_object=CognitiveResponse)

    prompt = ChatPromptTemplate.from_messages([
        ("system", full_system),
        ("human", "Generate my cognitive briefing for today."),
    ])

    chain  = prompt | llm | parser
    result = chain.invoke({})

    result["final_score"] = final_score
    result["zone"]        = score_data["zone"]

    return result
import json
import base64
import logging
import re
import time

from google import genai
from google.api_core.exceptions import ResourceExhausted
from groq import Groq
from django.conf import settings

logger = logging.getLogger(__name__)

# --------------------------------------------------
# AI CLIENTS
# --------------------------------------------------

gemini_client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)

groq_client = Groq(
    api_key=settings.GROQ_API_KEY
)


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise ValueError("No JSON found in AI response")

    return json.loads(match.group())


# --------------------------------------------------
# GEMINI TRANSCRIPTION
# --------------------------------------------------

def transcribe_with_gemini(audio_file):
    audio_file.seek(0)
    audio_bytes = audio_file.read()

    mime_type = getattr(audio_file, "content_type", None)

    if not mime_type:
        mime_type = "audio/mpeg"

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": base64.b64encode(audio_bytes).decode("utf-8"),
                        }
                    },
                    {
                        "text": "Transcribe this audio and return only the spoken text."
                    }
                ]
            }
        ],
    )

    return response.text.strip()


# --------------------------------------------------
# GROQ TRANSCRIPTION
# --------------------------------------------------

def transcribe_with_groq(audio_file):
    audio_file.seek(0)
    audio_bytes = audio_file.read()

    transcription = groq_client.audio.transcriptions.create(
        file=(audio_file.name, audio_bytes),
        model="whisper-large-v3",
    )

    return transcription.text.strip()


# --------------------------------------------------
# MAIN TRANSCRIPTION FUNCTION
# --------------------------------------------------

def transcribe_audio(audio_file):

    for attempt in range(2):
        try:
            return transcribe_with_gemini(audio_file)

        except ResourceExhausted as error:
            logger.warning(f"Gemini quota exceeded: {error}")
            break

        except Exception as error:
            logger.error(f"Gemini transcription failed: {error}")

            if attempt < 1:
                time.sleep(2)
            else:
                break

    try:
        return transcribe_with_groq(audio_file)

    except Exception as error:
        logger.error(f"Groq transcription failed: {error}")

        return "Unable to transcribe audio at the moment."


# --------------------------------------------------
# GEMINI STRUCTURING
# --------------------------------------------------

def structure_with_ai(prompt):

    gemini_prompt = f"""
{prompt}

Return ONLY valid JSON.

Schema:
{{
    "name": "",
    "priority": "",
    "deadline": ""
}}

No markdown.
No explanations.
"""

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=gemini_prompt
        )

        result = extract_json(response.text)

        return {
            "name": result.get("name", "Untitled task"),
            "priority": result.get("priority", "medium"),
            "deadline": result.get("deadline")
        }

    except ResourceExhausted as error:
        logger.warning(f"Gemini quota exceeded: {error}")

    except Exception as error:
        logger.error(f"Gemini structuring failed: {error}")

    # --------------------------------------------------
    # GROQ FALLBACK
    # --------------------------------------------------

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": f"""
{prompt}

Return ONLY valid JSON.

Schema:
{{
    "name": "",
    "priority": "",
    "deadline": ""
}}

No markdown.
No explanations.
"""
                }
            ],
        )

        result = extract_json(
            response.choices[0].message.content
        )

        return {
            "name": result.get("name", "Untitled task"),
            "priority": result.get("priority", "medium"),
            "deadline": result.get("deadline")
        }

    except Exception as error:
        logger.error(f"Groq structuring failed: {error}")

        return {
            "name": "Untitled task",
            "priority": "medium",
            "deadline": None
        }
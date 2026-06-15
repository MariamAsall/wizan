

# services.py

import base64
from google import genai
from openai import OpenAI
from django.conf import settings

gemini_client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)

grok_client = OpenAI(
    api_key=settings.GROK_API_KEY,
    base_url="https://api.x.ai/v1"
)




# Gemini Function


def transcribe_with_gemini(audio_file):
    audio_bytes = audio_file.read()

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": audio_file.content_type,
                            "data": base64.b64encode(
                                audio_bytes
                            ).decode("utf-8"),
                        }
                    },
                    {
                        "text":
                        "Transcribe this audio and return only the spoken text."
                    }
                ]
            }
        ],
    )

    return response.text.strip()




# Grok Function


def transcribe_with_grok(audio_file):
    audio_file.seek(0)

    transcription = grok_client.audio.transcriptions.create(
        model="llama-3.3-70b-versatile",
        file=audio_file,
    )

    return transcription.text.strip()



# Main Function With Fallback


def transcribe_audio(audio_file):
    try:
        return transcribe_with_gemini(audio_file)

    except Exception as gemini_error:
        print(
            "Gemini failed:",
            str(gemini_error)
        )

        try:
            audio_file.seek(0)

            return transcribe_with_grok(
                audio_file
            )

        except Exception as grok_error:
            print(
                "Grok failed:",
                str(grok_error)
            )

            raise Exception(
                f"Gemini failed: {gemini_error}. "
                f"Grok failed: {grok_error}"
            )




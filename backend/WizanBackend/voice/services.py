from google import genai
from groq import Groq
from django.conf import settings
import base64

gemini_client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)

grok_client = Groq(
    api_key=settings.GROQ_API_KEY
)


def transcribe_with_gemini(audio_file):
    audio_file.seek(0)
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


def transcribe_with_grok(audio_file):
    audio_file.seek(0)

    transcription = grok_client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-large-v3",
    )

    return transcription.text.strip()


def transcribe_audio(audio_file):
    try:
        return transcribe_with_gemini(audio_file)

    except Exception as gemini_error:
        print(f"Gemini failed: {gemini_error}")

        try:
            return transcribe_with_grok(audio_file)

        except Exception as grok_error:
            print(f"Grok failed: {grok_error}")

            raise Exception(
                f"Gemini failed: {gemini_error}. "
                f"Grok failed: {grok_error}"
            )
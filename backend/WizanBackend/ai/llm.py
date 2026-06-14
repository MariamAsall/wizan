
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

def get_llm(fallback=False):
    """
    fallback=False → use Gemini (default)
    fallback=True  → use Groq (when Gemini quota is hit)

    Why this design?
    We don't want to touch every agent file when we switch providers.
    One parameter here controls everything.
    """
    if fallback:
        return _get_groq()
    return _get_gemini()


def _get_gemini():
    # Your original code — unchanged
  
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.3,
        max_tokens=1000,
    )


def _get_groq():
    """
    Groq is free, fast, and has generous limits.
    Uses Llama 3.1 70B — strong enough for planning and summarization.
    Install: pip install langchain-groq
    Key: console.groq.com (free, 2 minutes to get)
    """
    from langchain_groq import ChatGroq
    return ChatGroq(
        model="llama-3.1-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3,
        max_tokens=1000,
    )


# def safe_llm_call(prompt: str) -> str:
#     """
#     The function every agent calls.
#     Tries Gemini first. If quota error → automatically switches to Groq.

#     Why safe_llm_call instead of calling get_llm() directly?
#     Because agents don't need to know about quota errors.
#     They just call this and always get an answer.
#     """
#     try:
#         llm = get_llm(fallback=False)
#         response = llm.invoke(prompt)
#         return response.content

#     except Exception as e:
#         error_message = str(e).lower()
#         # These are the exact error types Gemini throws on quota
#         if "quota" in error_message or "429" in error_message or "rate" in error_message:
#             print("[llm.py] Gemini quota hit — switching to Groq")
#             llm = get_llm(fallback=True)
#             response = llm.invoke(prompt)
#             return response.content
#         # Any other error — raise it so we know about it
#         raise


# # ── quick test ──────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     result = safe_llm_call("say hello in Arabic in one word")
#     print(result)

def safe_llm_call(messages):
    try:
        llm = get_llm(fallback=False)
        response = llm.invoke(messages)
        return response.content

    except Exception as e:
        error_message = str(e).lower()

        if any(
            x in error_message
            for x in [
                "quota",
                "429",
                "rate",
                "403",
                "permissiondenied",
                "denied access",
                "resourceexhausted",
            ]
        ):
            print("[llm.py] Gemini unavailable — switching to Groq")

            llm = get_llm(fallback=True)
            response = llm.invoke(messages)
            return response.content

        raise
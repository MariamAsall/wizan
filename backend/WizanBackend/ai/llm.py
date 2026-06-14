# ai/llm.py

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pathlib import Path
import os

# Why this path? Because llm.py is inside ai/ folder
# parent = ai/
# parent.parent = WizanBackend/  ← where .env lives
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path, override=True)  # override=True forces reload every time

# ── safety check ─────────────────────────────────────────────────────────────
# Why? So you get a clear error message instead of a confusing Pydantic crash
_api_key = os.getenv("GEMINI_API_KEY")
if not _api_key:
    raise EnvironmentError(
        f"\n\n❌ GEMINI_API_KEY not found.\n"
        f"   .env path checked: {env_path}\n"
        f"   File exists: {env_path.exists()}\n"
        f"   Fix: open that .env file and add GEMINI_API_KEY=your_key_here\n"
    )

# ── providers ────────────────────────────────────────────────────────────────

def _get_gemini():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=_api_key,
        temperature=0.3,
        max_tokens=1000,
    )

def _get_groq():
    from langchain_groq import ChatGroq
    groq_key = os.getenv("GROQ_API_KEY")

    if not groq_key:
        raise EnvironmentError("GROQ_API_KEY not found in .env")

    return ChatGroq(
        model="llama-3.3-70b-versatile",  # ✅ UPDATED
        api_key=groq_key,
        temperature=0.3,
        max_tokens=1000,
    )

def get_llm(fallback=False):
    """
    fallback=False → Gemini (default)
    fallback=True  → Groq (when Gemini quota is hit)
    """
    return _get_groq() if fallback else _get_gemini()

# ── THE function every other file calls ──────────────────────────────────────

def safe_llm_call(prompt: str) -> str:
    """
    Why this function?
    Every agent calls this one function instead of touching Gemini directly.
    If Gemini hits quota → automatically switches to Groq.
    Agents don't need to know any of this — they just call safe_llm_call().
    """
    try:
        llm = get_llm(fallback=False)
        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        msg = str(e).lower()
        # These are the exact words Gemini puts in quota/rate errors
        if any(word in msg for word in ["quota", "429", "rate limit", "resource exhausted"]):
            print("[llm.py] ⚠️  Gemini quota hit — switching to Groq automatically")
            llm = get_llm(fallback=True)
            response = llm.invoke(prompt)
            return response.content
        raise  # any other error should still crash loudly

# ── quick test — run: python ai/llm.py ───────────────────────────────────────
if __name__ == "__main__":
    result = safe_llm_call("say hello in Arabic in one word")
    print("Response:", result)

# ai/llm.py

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pathlib import Path
import os

from ai.resilience.circuit_breaker import gemini_breaker

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
    # Why Groq? Free, fast, generous quota — perfect backup
    # Get key at: console.groq.com (2 minutes, free)
    from langchain_groq import ChatGroq
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise EnvironmentError("GROQ_API_KEY not found in .env")
    return ChatGroq(
        # REPLACE with:
        model="llama-3.3-70b-versatile",
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

    CIRCUIT BREAKER BEHAVIOR (added on top of the original quota-only
    fallback): before even attempting Gemini, we check
    gemini_breaker.allow_request(). If Gemini has failed
    failure_threshold times in a row, the breaker is OPEN and we skip
    straight to Groq — no point paying Gemini's failure latency again
    when it's already shown it's not responding.

    FAILURE DEFINITION: any exception from the Gemini call now counts
    as a circuit-breaker failure, not just the quota/rate-limit keyword
    match. The keyword check below still decides which provider to
    fall back to on a SINGLE call, but the breaker's failure counter
    increments regardless of the specific error — a timeout is just as
    much "Gemini isn't working right now" as a quota error is.
    """
    if gemini_breaker.allow_request():
        try:
            llm = get_llm(fallback=False)
            response = llm.invoke(prompt)
            gemini_breaker.record_success()
            return response.content

        except Exception as e:
            gemini_breaker.record_failure()
            msg = str(e).lower()
            # These are the exact words Gemini puts in quota/rate errors.
            # Kept as-is for logging clarity, but no longer gates whether
            # we fall back — see broadened failure definition above.
            if any(word in msg for word in ["quota", "429", "rate limit", "resource exhausted"]):
                print("[llm.py] ⚠️  Gemini quota hit — switching to Groq automatically")
            else:
                print(f"[llm.py] ⚠️  Gemini call failed ({e}) — switching to Groq automatically")
    else:
        print("[llm.py] ⚠️  Circuit breaker OPEN for Gemini — skipping straight to Groq")

    # Either the breaker was open, or Gemini just failed above.
    # Groq has no breaker of its own: if Groq fails too, that's a
    # genuine "no provider available" situation, and the exception
    # should propagate up loudly rather than be swallowed silently.
    llm = get_llm(fallback=True)
    response = llm.invoke(prompt)
    return response.content

# ── quick test — run: python ai/llm.py ───────────────────────────────────────
if __name__ == "__main__":
    result = safe_llm_call("say hello in Arabic in one word")
    print("Response:", result)
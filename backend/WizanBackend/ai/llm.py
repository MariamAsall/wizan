# ai/llm.py

import os
from pathlib import Path
import requests
from dotenv import load_dotenv

from ai.resilience.circuit_breaker import CircuitBreaker


from google import genai
from groq import Groq
from django.conf import settings
from google.api_core.exceptions import ResourceExhausted
import logging
logger = logging.getLogger(__name__)


gemini_client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)

groq_client = Groq(
    api_key=settings.GROQ_API_KEY
)
# Why this path? Because llm.py is inside ai/ folder
# parent = ai/
# parent.parent = WizanBackend/  ← where .env lives
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path, override=True)  # override=True forces reload every time

# ── safety check ─────────────────────────────────────────────────────────────
# Why? So you get a clear error message instead of a confusing requests crash.
_api_key = os.getenv("SBG_API_KEY")
_base_url = os.getenv("SBG_BASE_URL")

if not _api_key or not _base_url:
    raise EnvironmentError(
        f"\n\n❌ SBG_API_KEY and/or SBG_BASE_URL not found.\n"
        f"   .env path checked: {env_path}\n"
        f"   File exists: {env_path.exists()}\n"
        f"   Fix: open that .env file and add:\n"
        f"     SBG_API_KEY=sbg_...your_key...\n"
        f"     SBG_BASE_URL=http://apiaccess.iti.net.eg/api/v1\n"
    )

# ── providers ────────────────────────────────────────────────────────────────
# We're not calling AWS or Gemini/Groq directly anymore. Everything now
# goes through ITI's Student Bedrock Gateway (SBG) — a single HTTP API
# in front of Bedrock that validates our key, model, and budget before
# forwarding the call. Both "primary" and "fallback" below are Claude
# models reached through the SAME gateway/endpoint — only the model_id
# in the payload changes.

PRIMARY_MODEL_ID = os.getenv("SBG_PRIMARY_MODEL_ID", "anthropic.claude-sonnet-4-6")
FALLBACK_MODEL_ID = os.getenv("SBG_FALLBACK_MODEL_ID", "anthropic.claude-haiku-4-5-20251001")

VOICE_MODEL_ID = os.getenv(
    "SBG_VOICE_MODEL_ID",
    "deepseek.r1-v1:0"
)

def structure_with_gemini(prompt):
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text.strip()

def structure_with_groq(prompt):
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )

    return response.choices[0].message.content.strip()



_CHAT_URL = f"{_base_url.rstrip('/')}/student/chat"


class _GatewayResponse:
    """Thin wrapper so the rest of the app keeps using `.content`,
    exactly like it did with the langchain ChatGoogleGenerativeAI /
    ChatGroq response objects before. Nothing downstream has to change."""
    def __init__(self, content: str):
        self.content = content


def _extract_text(data: dict) -> str:
    """
    The gateway's exact response shape isn't documented anywhere we've
    seen yet (the example in the dashboard only does `print(response.json())`
    without showing what it prints). This tries the shapes most APIs like
    this use, in order, so we don't crash the moment the real shape
    differs from a guess.

    IMPORTANT: run ai/test_sbg_connection.py and check the printed raw
    JSON — if none of these match, add the real key here.
    """
    if isinstance(data, dict):
        if "output_text" in data and isinstance(data["output_text"], str):
            return data["output_text"]
        if "content" in data and isinstance(data["content"], str):
            return data["content"]
        if "message" in data and isinstance(data["message"], dict):
            return data["message"].get("content", "")
        if "choices" in data and data["choices"]:
            choice = data["choices"][0]
            if isinstance(choice, dict):
                if "message" in choice:
                    return choice["message"].get("content", "")
                if "text" in choice:
                    return choice["text"]
        if "completion" in data:
            return data["completion"]
    raise ValueError(f"Unrecognized gateway response shape: {data}")


def _call_gateway(prompt: str, model_id: str) -> str:
    payload = {
        "model_id": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "system_prompt": "",
        "max_tokens": 1000,
    }
    response = requests.post(
        _CHAT_URL,
        headers={
            "Authorization": f"Bearer {_api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    return _extract_text(response.json())


def voice_llm_call(prompt):
    try:
        return structure_with_gemini(prompt)

    except ResourceExhausted:
        logger.warning("Gemini quota exceeded. Falling back to Groq.")

    except Exception as e:
        logger.error(f"Gemini failed: {e}")

    return structure_with_groq(prompt)

def get_llm(fallback=False):
    """
    fallback=False → Claude Sonnet via the gateway (default)
    fallback=True  → Claude Haiku via the gateway (when Sonnet is unavailable)

    Returns a tiny callable wrapper so safe_llm_call below can keep
    calling `llm.invoke(prompt)` the exact same way it always has.
    """
    model_id = FALLBACK_MODEL_ID if fallback else PRIMARY_MODEL_ID

    class _LLM:
        def invoke(self, prompt: str):
            text = _call_gateway(prompt, model_id)
            return _GatewayResponse(text)

    return _LLM()


# One breaker, now tracking the gateway's primary model (Sonnet) instead
# of Gemini. Same CircuitBreaker class as before — only the thing being
# watched changed.
sbg_primary_breaker = CircuitBreaker(
    name="sbg-sonnet",
    failure_threshold=3,
    cooldown_seconds=60,
)

# ── THE function every other file calls ──────────────────────────────────────

def safe_llm_call(prompt: str) -> str:
    """
    Why this function?
    Every agent calls this one function instead of touching the gateway
    directly. If Claude Sonnet fails or the gateway's budget/throttle
    limit is hit → automatically switches to Claude Haiku. Agents don't
    need to know any of this — they just call safe_llm_call().

    CIRCUIT BREAKER BEHAVIOR: before even attempting Sonnet, we check
    sbg_primary_breaker.allow_request(). If Sonnet has failed
    failure_threshold times in a row, the breaker is OPEN and we skip
    straight to Haiku — no point paying Sonnet's failure latency again
    when it's already shown it's not responding.

    FAILURE DEFINITION: any exception (HTTP error, timeout, unrecognized
    response shape) counts as a circuit-breaker failure, not just a
    budget/quota keyword match.
    """
    if sbg_primary_breaker.allow_request():
        try:
            llm = get_llm(fallback=False)
            response = llm.invoke(prompt)
            sbg_primary_breaker.record_success()
            return response.content

        except Exception as e:
            sbg_primary_breaker.record_failure()
            msg = str(e).lower()
            if any(word in msg for word in ["budget", "429", "rate limit", "throttl", "quota"]):
                print("[llm.py] ⚠️  Gateway budget/rate limit hit on Sonnet — switching to Haiku automatically")
            else:
                print(f"[llm.py] ⚠️  Sonnet call via gateway failed ({e}) — switching to Haiku automatically")
    else:
        print("[llm.py] ⚠️  Circuit breaker OPEN for Sonnet — skipping straight to Haiku")

    # Either the breaker was open, or Sonnet just failed above.
    # Haiku has no breaker of its own: if Haiku fails too, that's a
    # genuine "no provider available" situation, and the exception
    # should propagate up loudly rather than be swallowed silently.
    llm = get_llm(fallback=True)
    response = llm.invoke(prompt)
    return response.content

# ── quick test — run: python ai/llm.py ───────────────────────────────────────
if __name__ == "__main__":
    result = safe_llm_call("say hello in Arabic in one word")
    print("Response:", result)

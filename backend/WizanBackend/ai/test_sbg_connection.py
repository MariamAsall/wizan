# ai/test_sbg_connection.py
#
# Run this FIRST, before touching any app code, to confirm your gateway
# key works and to see the EXACT shape of a real response (so we can
# fix _extract_text() in ai/llm.py if needed):
#
#   python ai/test_sbg_connection.py
#
# This does NOT print your API key.

import os
import json
from pathlib import Path
from dotenv import load_dotenv
import requests

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path, override=True)

api_key = os.environ["SBG_API_KEY"]
base_url = os.environ["SBG_BASE_URL"].rstrip("/")

payload = {
    "model_id": os.getenv("SBG_PRIMARY_MODEL_ID", "anthropic.claude-sonnet-4-6"),
    "messages": [{"role": "user", "content": "say hi in one word"}],
    "system_prompt": "You are a concise assistant.",
    "max_tokens": 50,
}

print(f"POST {base_url}/student/chat")
print(f"model_id: {payload['model_id']}\n")

response = requests.post(
    f"{base_url}/student/chat",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json=payload,
    timeout=60,
)

print("Status code:", response.status_code)
print("Raw JSON response:")
print(json.dumps(response.json(), indent=2))

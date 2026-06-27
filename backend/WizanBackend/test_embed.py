import requests

# Hardcoding the values directly for an instant, foolproof test
base_url = "http://apiaccess.iti.net.eg/api/v1"
api_key = "sbg_LCKonZDfmOj--f16LymKmP-jp0oH-LPr"  # <-- Replace this with your real SBG API key string

payload = {
  "model_id": "amazon.titan-embed-text-v2:0:8k",
  "texts": [
    "Algorithms are step-by-step instructions for solving problems."
  ],
  "input_type": "search_document"
}

print(f"Sending request to: {base_url}/student/embed")
try:
    response = requests.post(
        f"{base_url}/student/embed",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    print("Status:", response.status_code)
    print("Response JSON:")
    print(response.json())
except Exception as e:
    print("An error occurred:", e)

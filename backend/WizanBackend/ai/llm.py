from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pathlib import Path
import os

# path goes: wizan/backend/ai/ → wizan/backend/ → .env
env_path = Path(__file__).resolve().parent.parent / ".env"
# env_path = Path(__file__).resolve().parent.parent / "backend" / ".env"
load_dotenv(env_path)

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.3,
        max_tokens=1000,
    )

if __name__ == "__main__":
    llm = get_llm()
    response = llm.invoke("say hello in Arabic in one word")
    print(response.content)

# run this anytime you get a 404 to see what's available
# import google.generativeai as genai
# genai.configure(api_key="YOUR_KEY_HERE")

# for m in genai.list_models():
#     if "generateContent" in m.supported_generation_methods:
#         print(m.name)


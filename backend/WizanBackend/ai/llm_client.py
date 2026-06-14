# import os

# PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # switch here

# def get_completion(system_prompt: str, user_message: str) -> str:
#     """
#     Single function all agents call.
#     Swap provider in .env — no agent code changes needed.
#     """
#     if PROVIDER == "gemini":
#         return _gemini(system_prompt, user_message)
#     elif PROVIDER == "groq":
#         return _groq(system_prompt, user_message)
#     else:
#         raise ValueError(f"Unknown provider: {PROVIDER}")


# def _gemini(system_prompt: str, user_message: str) -> str:
#     import google.generativeai as genai
#     genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
#     model = genai.GenerativeModel(
#         model_name=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
#         system_instruction=system_prompt
#     )
#     response = model.generate_content(user_message)
#     return response.text


# def _groq(system_prompt: str, user_message: str) -> str:
#     from groq import Groq
#     client = Groq(api_key=os.getenv("GROQ_API_KEY"))
#     response = client.chat.completions.create(
#         model="llama-3.1-70b-versatile",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user",   "content": user_message}
#         ]
#     )
#     return response.choices[0].message.content


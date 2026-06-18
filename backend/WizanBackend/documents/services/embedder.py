import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

EMBED_MODEL = "models/gemini-embedding-001"
DIMENSIONS = 768  # truncate from 3072 → 768, works with HNSW

def embed_texts(texts: list[str]) -> list[list[float]]:
    result = []
    for text in texts:
        response = genai.embed_content(
            model=EMBED_MODEL,
            content=text,
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=DIMENSIONS,  # ← key fix
        )
        result.append(response['embedding'])
    return result

def embed_query(query: str) -> list[float]:
    response = genai.embed_content(
        model=EMBED_MODEL,
        content=query,
        task_type="RETRIEVAL_QUERY",
        output_dimensionality=DIMENSIONS,      # ← key fix
    )
    return response['embedding']
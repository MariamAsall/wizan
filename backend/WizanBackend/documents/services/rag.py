# import json
# import google.generativeai as genai
# from django.conf import settings
# from pgvector.django import CosineDistance
# from ..models import Embedding

# genai.configure(api_key=settings.GEMINI_API_KEY)
# model = genai.GenerativeModel("models/gemini-2.0-flash") 

# def search_chunks(query_vector, document_id, top_k=5):
#     return (
#         Embedding.objects
#         .filter(document_id=document_id)
#         .annotate(distance=CosineDistance('embedding', query_vector))
#         .order_by('distance')[:top_k]
#     )

# def ask_document(query: str, document_id: str) -> dict:
#     from .embedder import embed_query
#     query_vector = embed_query(query)
#     chunks = search_chunks(query_vector, document_id)
#     context = "\n\n".join([c.content for c in chunks])

#     response = model.generate_content(
#         f"Answer based only on this context:\n\n{context}\n\nQuestion: {query}"
#     )
#     return {
#         "answer": response.text,
#         "source_chunks": [
#             {"index": c.chunk_index, "content": c.content[:200]}
#             for c in chunks
#         ],
#     }

# def suggest_tasks_from_document(document_id: str) -> list[dict]:
#     chunks = (
#         Embedding.objects
#         .filter(document_id=document_id)
#         .order_by('chunk_index')[:10]
#     )
#     context = "\n\n".join([c.content for c in chunks])

#     response = model.generate_content(
#         f"""Extract study tasks from this content.
# Return ONLY valid JSON, no markdown, no extra text.
# Format: {{"tasks": [{{"title": str, "description": str, "priority": "low|medium|high"}}]}}

# Content:
# {context}"""
#     )

#     data = json.loads(response.text)
#     return data.get("tasks", [])

import json
import google.generativeai as genai
from groq import Groq
from django.conf import settings
from pgvector.django import CosineDistance
from ..models import Embedding


genai.configure(api_key=settings.GEMINI_API_KEY)
groq_client = Groq(api_key=settings.GROQ_API_KEY)

def _generate(prompt: str) -> str:
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def search_chunks(query_vector, document_id, top_k=5):
    return (
        Embedding.objects
        .filter(document_id=document_id)
        .annotate(distance=CosineDistance('embedding', query_vector))
        .order_by('distance')[:top_k]
    )

def ask_document(query: str, document_id: str) -> dict:
    from .embedder import embed_query
    query_vector = embed_query(query)
    chunks = search_chunks(query_vector, document_id)
    context = "\n\n".join([c.content for c in chunks])

    answer = _generate(
        f"Answer based only on this context:\n\n{context}\n\nQuestion: {query}"
    )
    return {
        "answer": answer,
        "source_chunks": [
            {"index": c.chunk_index, "content": c.content[:200]}
            for c in chunks
        ],
    }

def suggest_tasks_from_document(document_id: str) -> list[dict]:
    chunks = (
        Embedding.objects
        .filter(document_id=document_id)
        .order_by('chunk_index')[:3]
    )
    context = "\n\n".join([c.content for c in chunks])

    text = _generate(
        f"""Extract study tasks from this content.
Return ONLY valid JSON, no markdown, no extra text.
Format: {{"tasks": [{{"title": str, "description": str, "priority": "low|medium|high"}}]}}

Content:
{context}"""
    )

    clean = text.strip().strip("```json").strip("```").strip()
    data = json.loads(clean)
    return data.get("tasks", [])

def study_chat(query: str, user_id: int) -> dict:
    from .embedder import embed_query
    from .resource_agent import run_resource_agent

    query_vector = embed_query(query)

    chunks = (
        Embedding.objects
        .filter(document__user_id=user_id, document__status='ready')
        .annotate(distance=CosineDistance('embedding', query_vector))
        .order_by('distance')[:5]
    )

    if not chunks:
        return {"answer": "No study materials found. Please upload a document first.", "sources": []}

    context = "\n\n".join([c.content for c in chunks])

    answer = run_resource_agent(query, context)

    return {
        "answer": answer,
        "sources": [
            {
                "source": c.metadata.get("source", "Unknown"),
                "page":   c.metadata.get("page", "?"),
                "excerpt": c.content[:200],
            }
            for c in chunks
        ],
    }
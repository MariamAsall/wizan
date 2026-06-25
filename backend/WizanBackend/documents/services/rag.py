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

# from backend.WizanBackend.documents import tasks
from ..models import Embedding
# from rank_bm25 import BM25Okapi
from ai.filters.pii_filter import filter_pii


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
    answer = filter_pii(answer)

    return {
        "answer": answer,

        "source_chunks": [
            {"index": c.chunk_index, "content": filter_pii(c.content[:200])}
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
    tasks = data.get("tasks", [])
    for task in tasks:
        task["title"] = filter_pii(task.get("title", ""))
        task["description"] = filter_pii(task.get("description", ""))
    return tasks

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
    answer = filter_pii(answer)

    return {
        "answer": answer,
        "sources": [
            {
                "source": c.metadata.get("source", "Unknown"),
                "page":   c.metadata.get("page", "?"),
                "excerpt": filter_pii(c.content[:200]),
            }
            for c in chunks
        ],
    }

#====================== Phase 5: study chat ======================================#

# def _get_all_user_chunks(user_id: int):
#     """Fetch all ready chunks for a user — used for BM25 index."""
#     return list(
#         Embedding.objects
#         .filter(document__user_id=user_id, document__status='ready')
#         .order_by('chunk_index')
#     )

# def _bm25_search(query: str, all_chunks: list, top_k: int = 10) -> list:
#     """Keyword search using BM25."""
#     tokenized_corpus = [c.content.lower().split() for c in all_chunks]
#     bm25 = BM25Okapi(tokenized_corpus)
#     scores = bm25.get_scores(query.lower().split())
#     top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
#     return [all_chunks[i] for i in top_indices]

# def _dense_search(query_vector, user_id: int, top_k: int = 10) -> list:
#     """Vector similarity search."""
#     return list(
#         Embedding.objects
#         .filter(document__user_id=user_id, document__status='ready')
#         .annotate(distance=CosineDistance('embedding', query_vector))
#         .order_by('distance')[:top_k]
#     )

# def _rrf_fusion(dense_chunks: list, bm25_chunks: list, k: int = 60) -> list:
#     """Reciprocal Rank Fusion — merges two ranked lists into one."""
#     scores = {}
#     # score by rank position in each list
#     for rank, chunk in enumerate(dense_chunks):
#         scores[chunk.id] = scores.get(chunk.id, 0) + 1 / (k + rank + 1)
#     for rank, chunk in enumerate(bm25_chunks):
#         scores[chunk.id] = scores.get(chunk.id, 0) + 1 / (k + rank + 1)

#     # build a deduplicated chunk map
#     chunk_map = {c.id: c for c in dense_chunks + bm25_chunks}
#     sorted_ids = sorted(scores, key=lambda cid: scores[cid], reverse=True)
#     return [chunk_map[cid] for cid in sorted_ids]

# def _multi_query(query: str) -> list[str]:
    """Rewrite the query into 3 versions using the LLM."""
    prompt = (
        f"You are an AI that rewrites search queries to improve document retrieval. "
        f"Given the query below, write 3 different versions of it that mean the same thing "
        f"but use different words. Return ONLY the 3 queries as a numbered list, nothing else.\n\n"
        f"Query: {query}"
    )
    raw = _generate(prompt)
    lines = [l.strip() for l in raw.strip().split('\n') if l.strip()]
    # strip numbering like "1." or "1)"
    queries = []
    for line in lines[:3]:
        cleaned = line.lstrip('0123456789.)- ').strip()
        if cleaned:
            queries.append(cleaned)
    # always include the original
    return list(dict.fromkeys([query] + queries))  # dedupe, original first

# def study_chat(query: str, user_id: int) -> dict:
#     from .embedder import embed_query
#     from .reranker import rerank

#     # 1. Get all user chunks for BM25
#     all_chunks = _get_all_user_chunks(user_id)
#     if not all_chunks:
#         return {
#             "answer": "No study materials found. Please upload a document first.",
#             "sources": []
#         }

#     # 2. MultiQuery — expand the query into multiple versions
#     queries = _multi_query(query)

#     # 3. Dense search for each query version, merge results
#     dense_results = []
#     for q in queries:
#         qvec = embed_query(q)
#         dense_results += _dense_search(qvec, user_id, top_k=5)

#     # 4. BM25 search on original query only
#     bm25_results = _bm25_search(query, all_chunks, top_k=10)

#     # 5. RRF fusion — combine and deduplicate
#     fused = _rrf_fusion(dense_results, bm25_results)

#     # 6. Rerank top 10 fused results, keep top 5
#     top_chunks = rerank(query, fused[:10])[:5]

#     # 7. Build context and generate answer
#     context = "\n\n".join([c.content for c in top_chunks])

#     from .resource_agent import run_resource_agent
#     answer = run_resource_agent(query, context)

#     return {
#         "answer": answer,
#         "sources": [
#             {
#                 "source": c.metadata.get("source", "Unknown"),
#                 "page":   c.metadata.get("page", "?"),
#                 "excerpt": c.content[:200],
#             }
#             for c in top_chunks
#         ],
#     }
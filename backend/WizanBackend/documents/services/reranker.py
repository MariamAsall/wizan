# from sentence_transformers import CrossEncoder

# _model = None

# def get_reranker():
#     global _model
#     if _model is None:
#         _model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
#     return _model

# def rerank(query: str, chunks: list) -> list:
#     """Takes a list of Embedding objects, returns them sorted by reranker score."""
#     model = get_reranker()
#     pairs = [(query, c.content) for c in chunks]
#     scores = model.predict(pairs)
#     ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
#     return [chunk for _, chunk in ranked]
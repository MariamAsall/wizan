import tiktoken

def chunk_text(text: str, size: int = 512, overlap: int = 50) -> list[dict]:
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append({
            "text": enc.decode(chunk_tokens),
            "token_start": start,
            "token_end": end,
        })
        start += size - overlap
    return chunks
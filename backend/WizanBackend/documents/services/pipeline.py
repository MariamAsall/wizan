from ..models import Document, Embedding
from .chunker import chunk_text
from .embedder import embed_texts
from .content_guard import guard_chunks, DocumentRejected


def run_pipeline(document_id: str) -> None:
    doc = Document.objects.get(id=document_id)
    doc.status = 'processing'
    doc.save(update_fields=['status'])

    try:
        chunks = chunk_text(doc.raw_text)

        # Defense-in-depth: the upload view already rejects suspicious
        # text before a Document row exists, but this re-checks at the
        # chunk level in case a Document ever reaches the pipeline by
        # another path (admin-created row, manual retry, future
        # ingestion route that bypasses DocumentUploadView).
        guard_chunks(chunks)

        texts  = [c['text'] for c in chunks]
        vectors = embed_texts(texts)

        Embedding.objects.filter(document=doc).delete()  # re-run safe

        Embedding.objects.bulk_create([
            Embedding(
                document=doc,
                chunk_index=i,
                content=chunks[i]['text'],
                embedding=vectors[i],
                metadata={
                    'source':      doc.filename,
                    'page':        (chunks[i]['token_start'] // 400) + 1,  # rough page estimate
                    'chunk_index': i,
                    'model':       'gemini-embedding-001',
                }
            )
            for i in range(len(chunks))
        ])

        doc.status = 'ready'

    except Exception as e:
        doc.status = 'failed'
        raise e

    finally:
        doc.save(update_fields=['status'])
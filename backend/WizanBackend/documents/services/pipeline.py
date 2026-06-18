from ..models import Document, Embedding
from .chunker import chunk_text
from .embedder import embed_texts

def run_pipeline(document_id: str) -> None:
    doc = Document.objects.get(id=document_id)
    doc.status = 'processing'
    doc.save(update_fields=['status'])

    try:
        chunks = chunk_text(doc.raw_text)
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
                    'token_start': chunks[i]['token_start'],
                    'token_end':   chunks[i]['token_end'],
                    'model':       'text-embedding-3-small',
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
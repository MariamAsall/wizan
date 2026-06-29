import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WizanBackend.settings")
django.setup()

from documents.tasks import process_document_async
from documents.models import Document
from django.contrib.auth import get_user_model

User = get_user_model()

def run_test_ingest():
    print("⏳ Starting upload and processing of the test document...")
    
    try:
        user_obj = User.objects.get(id=4)
    except User.DoesNotExist:
        user_obj = User.objects.first() 
    
    doc = Document.objects.create(
        user=user_obj,
        filename="data_structures.pdf",
        raw_text="A binary search tree is a data structure used for storing data. It allows fast lookup, addition, and removal of items.",
        status="processing"
    )
    print("✅ Document successfully created in the database!")
    print(f"🆔 Document UUID: {doc.id}")
    print("🚀 Running the pipeline in the background via Celery...")
    
    process_document_async.delay(str(doc.id))
    print("👍 Success! You can now proceed to Postman to complete testing.")

if __name__ == "__main__":
    run_test_ingest()
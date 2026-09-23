import os
import tempfile

from fastapi import APIRouter, UploadFile, File, Form, Depends
from configuration import app_config
from configuration.app_config import get_app_config, AppConfig
from src.services.rag_service import RAGService
from src.services.store_document_service import StoreDocumentService


retriever_route = APIRouter(prefix="/retriever", tags=["Retriever"])


def get_rag_service() -> RAGService:
    return RAGService(rag_config=get_app_config().chroma_retriever_config)

def get_chroma_retriever() -> StoreDocumentService:
    return StoreDocumentService(app_config=get_app_config().chroma_retriever_config)
import os
import tempfile
from fastapi import File, Form, UploadFile


@retriever_route.post("/retrieve_documents")
def retrieve_documents(
    prompt: str = Form(...),
    file: UploadFile = File(...),
    app_config: AppConfig = Depends(get_app_config),  # Fixed casing: Depends
    rag_service: RAGService = Depends(get_rag_service),
    document_store: StoreDocumentService = Depends(get_chroma_retriever),
):
    file_ext = os.path.splitext(file.filename)[1]

    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        # 1. Write the uploaded bytes into the temporary file
        content = file.file.read()
        tmp_file.write(content)
        temp_file_path = tmp_file.name

    try:
        # 2. Process the file now that it is written and closed
        document_store.execute_service(temp_file_path)
        answer = rag_service.execute_service(prompt)

        # 3. Return the response
        return {"answer": answer}

    finally:
        # 4. Clean up the temp file from disk to prevent storage leaks
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
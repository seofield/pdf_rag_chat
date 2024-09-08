import logging
import os
from typing import Optional

from fastapi import File, UploadFile

from app.models.knowledge_document import KnowledgeDocument
from app.schema import KnowledgeDocumentSchema
from app.settings import DOCUMENTS_DIR
from app.tasks.knowledge_document import parse_document
from app.vectorstore import BaseElasticSearch

logger = logging.getLogger(__name__)


async def create_knowledge_document(file: UploadFile = File(...)):
    file_path = await async_download_file(file)
    if not file_path:
        return {"message": "Failed to upload file."}
    file_name = file.filename
    file_type = os.path.splitext(file_name)[1]
    file_size = file.size

    new_doc = KnowledgeDocument(
        file_name=file_name,
        file_type=file_type,
        file_path=file_path,
        file_size=file_size,
        status="uploaded",
    )
    parse_document.apply_async(args=[file_path])
    await new_doc.insert()
    return {"message": "File uploaded successfully."}


async def get_knowledge_documents():
    documents = await KnowledgeDocument.all().to_list()
    document_list = [
        KnowledgeDocumentSchema(
            file_name=doc.file_name,
            file_type=doc.file_type,
            file_path=doc.file_path,
            file_size=doc.file_size,
            status=doc.status,
        )
        for doc in documents
    ]
    return {"documents": document_list}


async def delete_knowledge_document(file_path: str):
    await KnowledgeDocument.find({"file_path": file_path}).delete()
    BaseElasticSearch.delete_documents_by_source(file_path)
    delete_file(file_path)
    return {"message": "File deleted successfully."}


async def async_download_file(file: UploadFile) -> Optional[str]:
    if not os.path.exists(DOCUMENTS_DIR):
        os.makedirs(DOCUMENTS_DIR)
    file_path = os.path.join(DOCUMENTS_DIR, file.filename)
    if os.path.exists(file_path):
        return

    with open(file_path, "wb") as f:
        f.write(await file.read())
    return file_path


def delete_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
    return {"message": "File deleted successfully."}

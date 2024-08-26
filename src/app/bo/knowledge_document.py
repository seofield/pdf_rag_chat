import logging
import os

from fastapi import File, UploadFile

from app.database import init_db
from app.models.knowledge_document import KnowledgeDocument
from app.tasks.knowledge_document import parse_document

logger = logging.getLogger(__name__)


async def create_knowledge_document(file_path: str, file: UploadFile = File(...)):
    await init_db()
    file_name = file.name
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
    await init_db()
    documents = await KnowledgeDocument.all().to_list()
    return documents


async def delete_knowledge_document(file_path: str):
    await init_db()
    await KnowledgeDocument.find({"file_path": file_path}).delete()
    return {"message": "File deleted successfully."}

from fastapi import APIRouter, File, UploadFile

from app.bo.knowledge_document import (
    create_knowledge_document,
    delete_knowledge_document,
    get_knowledge_documents,
)
from app.schema import (
    FileDeleteResponse,
    FileUploadResponse,
    KnowledgeDocumentsResponse,
)

router = APIRouter()


@router.post("/upload/", response_model=FileUploadResponse)
async def upload(file: UploadFile = File(...)):
    return await create_knowledge_document(file)


@router.get("/", response_model=KnowledgeDocumentsResponse)
async def documents():
    return await get_knowledge_documents()


@router.delete("/", response_model=FileDeleteResponse)
async def documents(file_path: str):
    return await delete_knowledge_document(file_path)

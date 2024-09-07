from typing import List

from pydantic import BaseModel


class FileUploadRequest(BaseModel):
    file_path: str


class FileUploadResponse(BaseModel):
    message: str


class KnowledgeDocumentSchema(BaseModel):
    file_name: str
    file_type: str
    file_path: str
    file_size: int
    status: str


class KnowledgeDocumentsResponse(BaseModel):
    documents: List[KnowledgeDocumentSchema]


class FileDeleteRequest(BaseModel):
    file_path: str


class FileDeleteResponse(BaseModel):
    message: str

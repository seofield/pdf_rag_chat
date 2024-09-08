import asyncio
import logging

from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.celery import celery_app
from app.database import init_db
from app.models.knowledge_document import KnowledgeDocument
from app.settings import es_connection_details
from app.vectorstore import vectorstore

logger = logging.getLogger(__name__)


@celery_app.task
def parse_document(local_path: str):
    try:
        result = asyncio.run(async_parse_document(local_path))
        return result
    except Exception as e:
        return {"status": "failed", "error": str(e)}


async def async_parse_document(local_path: str):
    await init_db()
    await KnowledgeDocument.find({"file_path": local_path}).update(
        {"$set": {"status": "parsing"}}
    )
    try:
        loader = PyPDFLoader(local_path)
        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700, chunk_overlap=200
        )
        docs = text_splitter.split_documents(data)
        vectorstore.from_documents(
            documents=docs,
            embedding=OpenAIEmbeddings(),
            **es_connection_details,
        )
        status = "success"
    except Exception as e:
        logger.exception(e)
        status = "failed"
    await KnowledgeDocument.find({"file_path": local_path}).update(
        {"$set": {"status": status}}
    )
    return {"status": status, "document_path": local_path}

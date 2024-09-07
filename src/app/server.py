from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from langchain_teddynote import logging
from langserve import add_routes
from rag_elasticsearch import chain as rag_elasticsearch_chain

from app import settings
from app.api import knowledge_document
from app.database import init_db

logging.langsmith(settings.PROJECT_NAME)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.on_event("startup")
async def start_db() -> None:
    await init_db()


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/rag-elasticsearch/playground")


add_routes(
    app,
    rag_elasticsearch_chain,
    enable_feedback_endpoint=True,
    enable_public_trace_link_endpoint=True,
    playground_type="chat",
    path="/rag-elasticsearch",
)

app.include_router(
    knowledge_document.router,
    prefix="/knowledge_document",
    tags=["Knowledge Documents"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

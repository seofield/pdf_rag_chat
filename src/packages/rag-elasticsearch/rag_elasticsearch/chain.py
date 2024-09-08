import logging
from operator import itemgetter
from typing import List, Optional, Tuple

from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import format_document
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_elasticsearch import ElasticsearchStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.messages.chat import ChatMessage
from app.settings import es_connection_details

from .prompts import CONDENSE_QUESTION_PROMPT, DOCUMENT_PROMPT, LLM_CONTEXT_PROMPT

logger = logging.getLogger(__name__)

# Setup connecting to Elasticsearch
vectorstore = ElasticsearchStore(
    **es_connection_details,
    embedding=OpenAIEmbeddings(),
)
retriever = vectorstore.as_retriever()

# Set up LLM to user
llm = ChatOpenAI(temperature=0)


def _combine_documents(
    docs, document_prompt=DOCUMENT_PROMPT, document_separator="\n\n"
):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)


def _format_chat_history(chat_history: List[ChatMessage]) -> str:
    buffer = ""
    for chat_message in chat_history:
        if chat_message.role == "user":
            human = "Human: " + chat_message.content
            buffer += human + "\n"
        elif chat_message.role == "assistant":
            ai = "Assistant: " + chat_message.content
            buffer += ai + "\n"
    return buffer


class ChainInput(BaseModel):
    chat_history: Optional[List[BaseMessage]] = Field(
        description="Previous chat messages."
    )
    question: str = Field(..., description="The question to answer.")


_inputs = RunnableParallel(
    standalone_question=RunnablePassthrough.assign(
        chat_history=lambda x: _format_chat_history(x["chat_history"])
    )
    | CONDENSE_QUESTION_PROMPT
    | llm
    | StrOutputParser(),
)

_context = {
    "context": itemgetter("standalone_question") | retriever | _combine_documents,
    "question": lambda x: x["standalone_question"],
}

chain = _inputs | _context | LLM_CONTEXT_PROMPT | llm | StrOutputParser()

chain = chain.with_types(input_type=ChainInput)

import asyncio
import logging as lg
import os

import nest_asyncio
import requests
from langchain_core.messages.chat import ChatMessage
from langchain_teddynote import logging
from rag_elasticsearch import chain as rag_elasticsearch_chain

import streamlit as st
from app import settings
from app.settings import DOCUMENTS_DIR
from streamlit.runtime.uploaded_file_manager import UploadedFile

nest_asyncio.apply()
loop = asyncio.get_event_loop()

logger = lg.getLogger(__name__)

logging.langsmith(settings.PROJECT_NAME)

BASE_URL = "http://langserve:8000/knowledge_document/"
UPLOAD_URL = "http://langserve:8000/knowledge_document/upload/"


def upload_document(uploaded_file: UploadedFile):
    response = requests.post(
        UPLOAD_URL,
        files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)},
    )
    if response.status_code == 200:
        st.success("Files uploaded successfully to FastAPI!")
    else:
        st.error(f"Failed to upload files: {response.content.decode()}")


def fetch_documents():
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        return response.json().get("documents", [])
    else:
        st.error("Failed to fetch documents from server.")
        return []


def delete_document(file_path: str):
    file_name = file_path.split("/")[-1]
    response = requests.delete(BASE_URL, params={"file_path": file_path})
    if response.status_code == 200:
        st.warning(f"{file_name} has been deleted!")
    else:
        st.error(f"Failed to delete document: {response.content.decode()}")


def print_messages():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)


def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


########################################################################
# Interface
########################################################################

if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("PDF RAG CHAT")

# sidebar
with st.sidebar:
    clear_btn = st.button("Reset Chat")

    st.header("Documents")
    uploaded_files = st.file_uploader(
        "Upload", type=["pdf"], accept_multiple_files=True
    )
    if uploaded_files:
        for uploaded_file in uploaded_files:
            upload_document(uploaded_file)

    if os.listdir(DOCUMENTS_DIR):
        st.header("List")
        documents = fetch_documents()
        if documents:
            for document in documents:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(document["file_name"])
                with col2:
                    st.write(document["status"])
                with col3:
                    if st.button("Delete", key=document):
                        delete_document(document["file_path"])

# reset
if clear_btn:
    st.session_state["messages"] = []

print_messages()

# user input!
user_input = st.chat_input("질문을 입력하세요.")
if user_input:
    response = rag_elasticsearch_chain.stream(
        {"question": user_input, "chat_history": st.session_state["messages"]}
    )

    st.chat_message("user").write(user_input)

    with st.chat_message("assistant"):
        container = st.empty()

        ai_answer = ""
        for token in response:
            ai_answer += token
            container.markdown(ai_answer)

        add_message("user", user_input)
        add_message("assistant", ai_answer)

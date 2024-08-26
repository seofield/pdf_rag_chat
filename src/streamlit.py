import asyncio
import logging as lg
import os

import nest_asyncio
from langchain_core.messages.chat import ChatMessage
from langchain_teddynote import logging
from rag_elasticsearch import chain as rag_elasticsearch_chain

import streamlit as st
from app import settings
from app.bo.knowledge_document import (
    create_knowledge_document,
    delete_knowledge_document,
    get_knowledge_documents,
)

nest_asyncio.apply()
loop = asyncio.get_event_loop()

logger = lg.getLogger(__name__)

DOCUMENTS_DIR = "./documents/"

logging.langsmith(settings.PROJECT_NAME)


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

if "store" not in st.session_state:
    st.session_state["store"] = {}

# sidebar
with st.sidebar:
    clear_btn = st.button("Reset Chat")

    # upload file
    if not os.path.exists(DOCUMENTS_DIR):
        os.makedirs(DOCUMENTS_DIR)

    st.header("Documents")
    uploaded_files = st.file_uploader(
        "Upload", type=["pdf"], accept_multiple_files=True
    )
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(DOCUMENTS_DIR, uploaded_file.name)
            if os.path.exists(file_path):
                st.write(f"File {uploaded_file.name} already exists.")
                continue
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            loop.run_until_complete(create_knowledge_document(file_path, uploaded_file))

    if os.listdir(DOCUMENTS_DIR):
        st.header("List")
        documents = loop.run_until_complete(get_knowledge_documents())
        if documents:
            for document in documents:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(document.file_name)
                with col2:
                    st.write(document.status)
                with col3:
                    if st.button("Delete", key=document):
                        file_path = document.file_path
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        loop.run_until_complete(delete_knowledge_document(file_path))
                        st.warning(f"{document.file_name} has been deleted!")


# reset
if clear_btn:
    st.session_state["messages"] = []

print_messages()

# user input!
user_input = st.chat_input("질문을 입력하세요.")
if user_input:
    response = rag_elasticsearch_chain.stream(
        {"question": user_input},
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

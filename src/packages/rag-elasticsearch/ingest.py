import os

from langchain_community.document_loaders import JSONLoader, PyPDFLoader
from langchain_elasticsearch import ElasticsearchStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

ES_URL = os.getenv("ES_URL", "http://localhost:9200")

es_connection_details = {"es_url": ES_URL}

loader = PyPDFLoader("./data/test.pdf")
data = loader.load()

# Split docs
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
docs = text_splitter.split_documents(data)

# Add to vectorDB
vectorstore = ElasticsearchStore.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    **es_connection_details,
    index_name="workplace-search-example",
)

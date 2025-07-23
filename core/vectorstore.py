from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

embedding_model = OllamaEmbeddings(model="yxchia/multilingual-e5-base:latest")
CHROMA_PATH = "db/chroma_db"
os.makedirs(CHROMA_PATH, exist_ok=True)

def get_vectorstore():
    return Chroma(
        collection_name="minh_store",
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_model
        )

def add_texts_to_vectorstore(texts: list[str]):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    documents = text_splitter.create_documents(texts)

    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents)
    vectorstore.persist()
    print(f"Đã thêm {len(documents)} đoạn vào vector store.")

def search_similar(query: str, k: int = 3):
    vectorstore = get_vectorstore()
    return vectorstore.similarity_search(query, k=k)
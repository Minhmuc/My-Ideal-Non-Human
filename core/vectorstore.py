from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from chromadb import PersistentClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
from datetime import datetime
import os

embedding_model = OllamaEmbeddings(model="yxchia/multilingual-e5-base:latest")
CHROMA_PATH = "db/chroma_db"
os.makedirs(CHROMA_PATH, exist_ok=True)

def get_vectorstore():
    client = PersistentClient(path=CHROMA_PATH)
    return Chroma(
        client=client,
        collection_name="minh_store",
        embedding_function=embedding_model
    )


#  Thêm hàm lưu với thời gian
def add_texts_to_vectorstore(texts: list[str]):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    documents = text_splitter.create_documents(
        texts,
        metadatas=[{"timestamp": now, "type": "chat"} for _ in texts]
    )

    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents)
    print(f"✅ Đã thêm {len(documents)} đoạn vào vector store.")

#  Truy vấn và ưu tiên theo thời gian gần nhất nếu điểm tương tự giống nhau
def search_similar(query: str, k: int = 3):
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(query, k=k)

    # Sắp xếp lại nếu các đoạn có timestamp
    if all("timestamp" in doc.metadata for doc in results):
        results.sort(key=lambda d: d.metadata["timestamp"], reverse=True)

    return results

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from chromadb import PersistentClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
from datetime import datetime
import os
import hashlib

embedding_model = OllamaEmbeddings(model="bge-m3")
CHROMA_PATH = "db/chroma_db"
os.makedirs(CHROMA_PATH, exist_ok=True)


def get_vectorstore():
    client = PersistentClient(path=CHROMA_PATH)
    return Chroma(
        client=client,
        collection_name="minh_store",
        embedding_function=embedding_model
    )


def clean_text_for_storage(text: str) -> str:
    return text.lower().strip()

def add_texts_to_vectorstore(texts: list[str]):
    """
    Lưu nội dung vào vectorstore với timestamp, tránh trùng lặp bằng hash id.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cleaned_texts = [clean_text_for_storage(t) for t in texts]
    documents = text_splitter.create_documents(
        cleaned_texts,
        metadatas=[
            {
                "timestamp": now,
                "type": "chat",
                "chunk_id": i,
                "role": "user" if i % 2 == 0 else "assistant"
            }
            for i, _ in enumerate(cleaned_texts)
        ]
    )

    # Tạo id duy nhất từ nội dung
    ids = [hashlib.md5(doc.page_content.encode("utf-8")).hexdigest() for doc in documents]

    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents, ids=ids)
    print(f"✅ Đã thêm {len(documents)} đoạn vào vector store (tránh trùng lặp bằng id).")



def search_similar(query: str, k: int = 5, score_threshold: float = 0.78):
    vectorstore = get_vectorstore()
    try:
        results_with_scores = vectorstore.similarity_search_with_score(query, k=k*2)
        # Lọc tài liệu rác + score thấp
        filtered_results = []
        for doc, score in results_with_scores:
            if score < score_threshold:
                continue
            content = doc.page_content.lower()
            # Bỏ qua câu xin lỗi hoặc nội dung không liên quan
            if any(bad in content for bad in ["tôi xin lỗi", "i'm sorry", "lỗi khi tìm kiếm"]):
                continue
            filtered_results.append((doc, score))

        # Lấy top-k tài liệu tốt nhất
        return filtered_results[:k] if filtered_results else []
    except Exception:
        return vectorstore.similarity_search(query, k=k)


# print(search_similar("ming kong là ai?"))

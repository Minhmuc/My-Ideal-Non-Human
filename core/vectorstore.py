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


def clean_text_for_storage(text: str) -> str:
    """
    Loại bỏ prefix Người dùng / MINH để tránh phá nhân cách khi retrieve.
    """
    text = text.replace("Người dùng:", "").replace("MINH:", "").strip()
    return text


def add_texts_to_vectorstore(texts: list[str]):
    """
    Lưu nội dung vào vectorstore với timestamp.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=40)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cleaned_texts = [clean_text_for_storage(t) for t in texts]
    documents = text_splitter.create_documents(
        cleaned_texts,
        metadatas=[{"timestamp": now, "type": "chat"} for _ in cleaned_texts]
    )

    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents)
    print(f"✅ Đã thêm {len(documents)} đoạn vào vector store.")


def search_similar(query: str, k: int = 3):
    """
    Truy vấn và ưu tiên theo similarity trước, timestamp sau nếu similarity bằng nhau.
    """
    vectorstore = get_vectorstore()

    # Lấy cả điểm similarity
    results_with_scores = vectorstore.similarity_search_with_score(query, k=k * 2)

    # Sắp theo similarity trước, rồi timestamp nếu similarity bằng nhau
    results_with_scores.sort(
        key=lambda x: (
            -x[1],  # similarity score giảm dần
            x[0].metadata.get("timestamp", "0000")  # timestamp mới nhất trước
        ),
        reverse=False  # Vì score nhỏ hơn nghĩa là giống hơn trong một số lib
    )

    # Lấy top-k cuối cùng
    final_results = [doc for doc, _ in results_with_scores[:k]]

    # Wrap dữ liệu để LLM không dùng làm nhân cách
    for doc in final_results:
        doc.page_content = f"[THÔNG TIN THAM KHẢO - KHÔNG THAY ĐỔI NHÂN CÁCH]\n{doc.page_content}"

    return final_results

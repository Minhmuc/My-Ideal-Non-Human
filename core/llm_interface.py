from core.models import model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from core.memory import ConversationBufferMemory
from core.prompts import get_prompt
from core.webSearch import search_web
from data.realtime_data import get_current_datetime, get_weather
from core.prompt_engineering import should_search, extract_location_from_question, is_weather_intent, is_date_time_intent, date_time_response, weather_response
from core.vectorstore import search_similar, add_texts_to_vectorstore


template = """
Đây là danh tính của bạn: {system_prompt}
Dữ liệu liên quan từ hệ thống (nếu có): {retrieved_info}
Câu hỏi hiện tại: {question}
Trả lời tự nhiên, ngắn gọn, súc tích và chính xác, ưu tiên sử dụng dữ liệu đã lưu nếu liên quan. Nếu không rõ, hãy hỏi lại người dùng để làm rõ.
"""
prompt = ChatPromptTemplate.from_template(template)
chain: Runnable = prompt | model

def ask_llm_with_context(question: str, history: str = "", retrieved_info: str = "") -> str:
    """Hỏi LLM kèm ngữ cảnh từ web và vectorstore."""
    return chain.invoke({
        "system_prompt": get_prompt("system"),
        "question": question,
        "history": history,
        "retrieved_info": retrieved_info
    })
def provide_data_via_chat(user_input: str, memory: ConversationBufferMemory) -> str:
    """
    Cho phép người dùng cung cấp dữ liệu trực tiếp qua chat. Nếu câu hỏi bắt đầu bằng 'dữ liệu:' hoặc 'data:', lưu nội dung vào vectorstore.
    """
    if user_input.lower().startswith(('dữ liệu:', 'data:')):
        data_content = user_input.split(':', 1)[-1].strip()
        if data_content:
            add_texts_to_vectorstore([f"Dữ liệu người dùng: {data_content}"])
            memory.add("Người dùng", user_input)
            memory.add("MINH", "Đã lưu dữ liệu của sếp vào hệ thống. Sếp có thể hỏi lại bất cứ lúc nào!")
            return "Đã lưu dữ liệu của sếp vào hệ thống. Sếp có thể hỏi lại bất cứ lúc nào!"
        else:
            return "Sếp cần nhập nội dung dữ liệu sau 'dữ liệu:' hoặc 'data:' nhé!"
    return None

def ask_llm_with_memory(question: str, memory: ConversationBufferMemory) -> str:

    history = memory.get_history()

    # 🧠 Tìm trong Vector Store
    vector_results = search_similar(question, k=5)
        # Nếu kết quả là tuple (Document, score)
    if vector_results and isinstance(vector_results[0], tuple) and len(vector_results[0]) == 2:
        vector_info = "\n".join([doc.page_content for doc, score in vector_results if score > 0.7])
        if not vector_info:
            vector_info = "\n".join([doc.page_content for doc, score in vector_results[:3]])
    else:
        vector_info = "\n".join([doc.page_content for doc in vector_results]) if vector_results else ""

    web_info = ""
    # 🌐 Nếu nên search web → tìm
    if should_search(question):
        web_info = search_web(question)

    # 🧠 Ưu tiên vector_info + web_info
    retrieved_info = vector_info.strip()
    if web_info:
        retrieved_info += f"\nThông tin mới tìm kiếm: {web_info.strip()}"

    # 💬 Hỏi LLM
    answer = ask_llm_with_context(question, "", retrieved_info)

    # ❓ Nếu LLM trả lời không rõ → thử tìm web lần nữa (nếu chưa tìm)
    if answer.strip().lower() in ["", "tôi không biết.", "tôi không rõ."] and not web_info:
        web_info = search_web(question)
        retrieved_info = f"{vector_info}\n{web_info}".strip()
        answer = chain.invoke({
            "system_prompt": get_prompt("system"),
            "question": question,
            "history": history,
            "retrieved_info": retrieved_info
        })

    memory.add("Người dùng", question)
    memory.add("MINH", answer)
    qa_pair = f"Người dùng: {question}\nMINH: {answer}"
    add_texts_to_vectorstore([qa_pair])

    return answer
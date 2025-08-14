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
{system_prompt}
Câu hỏi: {question}
Ngữ cảnh: {history}
Thống tin tìm kiếm: {retrieved_info}
"""
prompt = ChatPromptTemplate.from_template(template)
chain: Runnable = prompt | model

def ask_llm_with_context(question: str, history: str = "", retrieved_info: str = "") -> str:
    """Hỏi LLM kèm ngữ cảnh từ web."""
    return chain.invoke({
        "system_prompt": get_prompt("system"),
        "question": question,
        "history": history,
        "retrieved_info": retrieved_info
    })

def ask_llm_with_memory(question: str, memory: ConversationBufferMemory) -> str:
    if is_date_time_intent(question):
        return date_time_response(question, get_current_datetime())

    if is_weather_intent(question):
        location = extract_location_from_question(question)
        return weather_response(question, get_weather(location))


    history = memory.get_history()

    # 🧠 Tìm trong Vector Store
    vector_results = search_similar(question)
    vector_info = "\n".join([doc.page_content for doc in vector_results]) if vector_results else ""

    web_info = ""
    # 🌐 Nếu nên search web → tìm
    if should_search(question):
        web_info = search_web(question)

    # 🧠 Ưu tiên vector_info + web_info
    retrieved_info = f"{vector_info}\n{web_info}".strip()

    # 💬 Hỏi LLM
    answer = ask_llm_with_context(question, history, retrieved_info)

    # ❓ Nếu LLM trả lời không rõ → thử tìm web lần nữa (nếu chưa tìm)
    if (
        answer.strip().lower() in ["", "tôi không biết.", "tôi không rõ."]
    ) and not web_info:
        web_info = search_web(question)
        retrieved_info = f"{vector_info}\n{web_info}".strip()
        answer = ask_llm_with_context(question, history, retrieved_info)

    memory.add("Người dùng", question)
    memory.add("MINH", answer)
    qa_pair = f"Người dùng: {question}\nMINH: {answer}"
    add_texts_to_vectorstore([qa_pair])

    return answer
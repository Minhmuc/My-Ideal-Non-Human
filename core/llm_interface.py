from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from core.memory import ConversationBufferMemory
from core.prompts import get_prompt
from core.webSearch import search_web
from data.realtime_data import get_current_datetime, get_weather
from core.prompt_engineering import should_search, extract_location_from_question
from core.vectorstore import search_similar

model = OllamaLLM(model="llama3.1:8b")

template = get_prompt("system") + "\n{history}\nThông tin tìm được:\n{web_info}\nNgười dùng: {question}"
prompt = ChatPromptTemplate.from_template(template)
chain: Runnable = prompt | model

def ask_llm_with_context(question: str, history: str = "", web_info: str = "") -> str:
    """Hỏi LLM kèm ngữ cảnh từ web."""
    custom_prompt = ChatPromptTemplate.from_template(template)
    custom_chain = custom_prompt | model
    return custom_chain.invoke({
        "question": question,
        "history": history,
        "web_info": web_info
    })

def ask_llm_with_memory(question: str, memory: ConversationBufferMemory) -> str:
    if any(kw in question.lower() for kw in ["ngày mấy", "hôm nay là", "bây giờ là", "thứ mấy"]):
        return get_current_datetime()

    if any(kw in question.lower() for kw in ["thời tiết", "thời tiết hôm nay", "nắng", "mưa"]):
        location = extract_location_from_question(question)
        return get_weather(location)


    history = memory.get_history()

    # 🧠 Tìm trong Vector Store
    vector_results = search_similar(question)
    vector_info = "\n".join([doc.page_content for doc in vector_results]) if vector_results else ""

    web_info = ""
    # 🌐 Nếu nên search web → tìm
    if should_search(question):
        web_info = search_web(question)

    # 🧠 Ưu tiên vector_info + web_info
    combined_info = f"{vector_info}\n{web_info}".strip()

    # 💬 Hỏi LLM
    answer = ask_llm_with_context(question, history, combined_info)

    # ❓ Nếu LLM trả lời không rõ → thử tìm web lần nữa (nếu chưa tìm)
    if (
        answer.strip().lower() in ["", "tôi không biết.", "tôi không rõ."] or
        len(answer.strip()) < 30 or
        "không biết" in answer.lower() or
        "không rõ" in answer.lower()
    ) and not web_info:
        web_info = search_web(question)
        combined_info = f"{vector_info}\n{web_info}".strip()
        answer = ask_llm_with_context(question, history, combined_info)

    memory.add("user", question)
    memory.add("bot", answer)

    return answer

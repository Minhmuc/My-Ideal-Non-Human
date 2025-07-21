from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from core.memory import ConversationBufferMemory
from core.prompts import get_prompt
from core.webSearch import search_web
from data.realtime_data import get_current_datetime, get_weather
from core.prompt_engineering import should_search

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
    """
    Hỏi mô hình LLM có kèm bộ nhớ.
    Nếu câu hỏi liên quan thời gian hoặc thời tiết → trả lời trực tiếp.
    Nếu LLM trả lời không rõ ràng → tự động tìm kiếm web và hỏi lại.
    """
    if any(kw in question.lower() for kw in ["ngày mấy", "hôm nay là", "bây giờ là", "thứ mấy"]):
        return get_current_datetime()

    if any(kw in question.lower() for kw in ["thời tiết", "trời có mưa", "nhiệt độ", "trời nắng không"]):
        return get_weather()

    if should_search(question):
        return search_web(question)

    history = memory.get_history()
    web_info = ""

    answer = ask_llm_with_context(question, history, web_info)

    if (
        answer.strip().lower() in ["", "tôi không biết.", "tôi không rõ."] or
        len(answer.strip()) < 30 or
        "không biết" in answer.lower() or
        "không rõ" in answer.lower()
    ):
        web_info = search_web(question)
        if web_info:
            answer = ask_llm_with_context(question, history, web_info)

    memory.add("user", question)
    memory.add("bot", answer)

    return answer

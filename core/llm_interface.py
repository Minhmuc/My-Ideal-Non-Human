from core.models import model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from core.memory import ConversationBufferMemory
from core.prompts import get_prompt
from core.webSearch import search_web
from data.realtime_data import get_current_datetime, get_weather
from core.prompt_engineering import date_time_response, weather_response,extract_search_query, extract_location_from_question
from core.vectorstore import search_similar, add_texts_to_vectorstore
from data.Intent_ex import detect_intent


template = """
Đây là bạn: {system_prompt}
Dữ liệu liên quan từ hệ thống và tra trên google: {retrieved_info}
Câu hỏi hiện tại: {question}
hãy phân tích kỹ và trả lời rõ ràng, chỉ sử dụng thông tin liên quan.
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
    """Cho phép người dùng cung cấp dữ liệu trực tiếp qua chat."""
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


async def ask_llm_with_memory(question: str, memory: ConversationBufferMemory) -> str:

    try:
        # 1. Dùng Intent Detector
        intent = await detect_intent(question)
        intent = intent.lower().strip()

        # 2. Xử lý intent đặc biệt
        if intent == "datetime":
            return date_time_response(question, get_current_datetime())
        elif intent == "weather":
            return weather_response(question, get_weather(extract_location_from_question(question)))

        history = ""

        # 3. Tìm trong Vector Store
        vector_results = search_similar(question, k=5)
        vector_info = ""
        if vector_results:
            if isinstance(vector_results[0], tuple):
                vector_info = "\n".join(
                    [doc.page_content for doc, score in vector_results if score > 0.7]
                ) or "\n".join([doc.page_content for doc, _ in vector_results[:3]])
            else:
                vector_info = "\n".join([doc.page_content for doc in vector_results])

        # 4. Nếu intent = search → search web
        web_info = ""
        if intent == "search":
            web_info = search_web(extract_search_query(question))

        # 5. Kết hợp thông tin
        retrieved_info = vector_info.strip()
        if web_info:
            retrieved_info += f"\nThông tin mới tìm kiếm: {web_info.strip()}"

        # 6. Gửi câu hỏi cho LLM chỉ với retrieved_info từ vectorstore và web
        answer = ask_llm_with_context(question, "", retrieved_info)

        # 7. Nếu LLM không trả lời được → fallback search web
        if not answer.strip() or answer.lower().strip() in ["tôi không biết.", "tôi không rõ."]:
            if not web_info:
                web_info = search_web(question)
                retrieved_info = f"{vector_info}\n{web_info}".strip()
                answer = chain.invoke({
                    "system_prompt": get_prompt("system"),
                    "question": question,
                    "history": history,
                    "retrieved_info": retrieved_info
                })

        # 8. Chỉ lưu vào vectorstore
        qa_pair = f"Người dùng: {question}\nMINH: {answer}"
        add_texts_to_vectorstore([qa_pair])
        return answer

    except Exception as e:
        print(f"[ask_llm_with_memory] Lỗi: {e}")
        return "Xin lỗi sếp, có lỗi khi xử lý yêu cầu!"

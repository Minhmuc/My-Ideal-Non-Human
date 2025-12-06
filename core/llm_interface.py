from core.models import model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from core.prompts import get_prompt
from core.webSearch import search_web
from data.realtime_data import get_current_datetime, get_weather
from core.prompt_engineering import date_time_response, weather_response,extract_search_query, extract_location_from_question
from core.vectorstore import search_similar, add_texts_to_vectorstore
from data.Intent_ex import detect_intent

template = """
Dữ liệu tham khảo: {retrieved_info}

Câu hỏi: {question}

Hãy trả lời câu hỏi một cách TỰ NHIÊN và TRỰC TIẾP như thể bạn đang biết thông tin đó.
KHÔNG được nhắc đến "tìm trên web", "tra cứu", "theo thông tin" hay bất kỳ nguồn nào trừ khi người dùng HỎI NGUỒN.
Chỉ trả lời nội dung chính, ngắn gọn và rõ ràng.
Nếu không có đủ thông tin, chỉ nói: "Tôi không biết."
"""
prompt = ChatPromptTemplate.from_template(template)
chain: Runnable = prompt | model

def ask_llm_with_context(question: str, retrieved_info: str = "") -> str:
    """Hỏi LLM kèm ngữ cảnh từ web và vectorstore."""
    return chain.invoke({
        "system_prompt": get_prompt("system"),
        "question": question,
        "retrieved_info": retrieved_info
    })

def provide_data_via_chat(user_input: str) -> str:
    """Cho phép người dùng cung cấp dữ liệu trực tiếp qua chat."""
    if user_input.lower().startswith(('dữ liệu:', 'data:')):
        data_content = user_input.split(':', 1)[-1].strip()
        if data_content:
            add_texts_to_vectorstore([f"{data_content}"])
            return "Đã lưu dữ liệu của sếp vào hệ thống. Sếp có thể hỏi lại bất cứ lúc nào!"
        else:
            return "Sếp cần nhập nội dung dữ liệu sau 'dữ liệu:' hoặc 'data:' nhé!"
    return None
# Không dùng ConversationBufferMemory nữa, chỉ dùng vectorstore
async def ask_llm_with_memory(question: str) -> str:

    try:
        # 1. Dùng Intent Detector
        intent = await detect_intent(question)
        intent = intent.lower().strip()

        # 2. Xử lý intent đặc biệt
        if intent == "datetime":
            return date_time_response(question, get_current_datetime())
        elif intent == "weather":
            return weather_response(question, get_weather(extract_location_from_question(question)))

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
        answer = ask_llm_with_context(question,  retrieved_info)

        # 7. Nếu LLM không trả lời được → fallback search web
        if not answer.strip() or any(phrase in answer.lower().strip() for phrase in ["tôi không biết", "tôi không rõ", "không có thông tin"]):
            if not web_info:
                # Cải thiện query trước khi search
                search_query = extract_search_query(question) if extract_search_query(question) else question
                print(f"[Fallback Search] Searching for: {search_query}")
                web_info = search_web(search_query)
                retrieved_info = f"{vector_info}\n\nThông tin tìm kiếm từ web:\n{web_info}".strip()
                
                # Retry với prompt rõ ràng hơn
                fallback_template = """
Dựa trên thông tin bên dưới, hãy trả lời câu hỏi một cách TỰ NHIÊN như thể bạn đang biết.
KHÔNG được nhắc "tìm trên web", "tra cứu", hay bất kỳ nguồn nào.
Chỉ trả lời nội dung trực tiếp, ngắn gọn và chính xác.

Thông tin tham khảo:
{retrieved_info}

Câu hỏi: {question}

Trả lời:
"""
                fallback_prompt = ChatPromptTemplate.from_template(fallback_template)
                fallback_chain = fallback_prompt | model
                answer = fallback_chain.invoke({
                    "question": question,
                    "retrieved_info": retrieved_info
                })

        # 8. Chỉ lưu vào vectorstore
        qa_pair = f"Người dùng: {question}\nMINH: {answer}"
        add_texts_to_vectorstore([qa_pair])
        return answer

    except Exception as e:
        print(f"[ask_llm_with_memory] Lỗi: {e}")
        return "Xin lỗi sếp, có lỗi khi xử lý yêu cầu!"

from core.models import model, hf_model, tokenizer
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from core.prompts import get_prompt
from core.webSearch import search_web
from data.realtime_data import get_current_datetime, get_weather
from core.prompt_engineering import date_time_response, weather_response,extract_search_query, extract_location_from_question
from core.vectorstore import search_similar, add_texts_to_vectorstore
from data.Intent_ex import detect_intent

def ask_llm_with_context(question: str, retrieved_info: str = "") -> str:
    """Hỏi LLM kèm ngữ cảnh từ web và vectorstore - Direct generation."""
    
    # Build prompt trực tiếp
    system_msg = """Bạn là MINH - trợ lý AI thông minh, thân thiện của sếp.
Trả lời NGẮN GỌN (2-3 câu), TỰ NHIÊN như con người.
KHÔNG giải thích process, KHÔNG nhắc "tìm kiếm" hay "tra cứu"."""
    
    if retrieved_info:
        prompt = f"{system_msg}\n\nThông tin tham khảo:\n{retrieved_info}\n\nCâu hỏi: {question}\n\nTrả lời:"
    else:
        prompt = f"{system_msg}\n\nCâu hỏi: {question}\n\nTrả lời:"
    
    # Generate với tokenizer trực tiếp
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": question if not retrieved_info else f"Dựa vào: {retrieved_info}\n\nCâu hỏi: {question}"}
    ]
    
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    inputs = tokenizer([text], return_tensors="pt").to(hf_model.device)
    
    outputs = hf_model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.8,
        top_p=0.85,
        repetition_penalty=1.15,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id
    )
    
    response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    return response.strip()

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

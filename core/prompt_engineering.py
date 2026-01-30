from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from core.prompts import get_prompt
from core.models import model, minh_model
from data.realtime_data import get_current_datetime, get_weather


personality = get_prompt("system")
def clean_input(text: str) -> str:
    return text.strip()

# ===== Should search on web =====
_search_prompt = ChatPromptTemplate.from_template(
    "Câu sau có cần tìm kiếm thông tin trên web không? Trả lời chính xác 'có' nếu người dùng bảo tra cứu, tìm kiếm, wiki.\nCâu hỏi: {question}"
)

def should_search(question: str) -> bool:
    result = (_search_prompt | model).invoke({"question": question})
    return "có" in result.lower()

exit_intent_confidence_prompt = PromptTemplate(
    input_variables=["user_input"],
    template="""
nhiệm vụ của bạn là đánh giá mức độ ý định kết thúc cuộc trò chuyện của người dùng dựa trên câu họ vừa nhập.

Ví dụ:
- Người dùng nói: "Cảm ơn nhé" → thấp
- Người dùng nói: "Tạm biệt, hẹn gặp lại" → cao
- Người dùng nói: "Thế thôi" → trung bình
- Người dùng nói: "Thế là xong rồi nhỉ" → trung bình
- Người dùng nói: "Ok cảm ơn, mình thoát đây" → cao

Dựa vào câu người dùng dưới đây, hãy trả lời đúng một trong ba mức: "cao", "trung bình", "thấp".

Nếu người dùng chỉ chat những từ khóa sau:"shutdown", "quit",  "exit", disconnect" thì tính là mức: "cao"
Không giải thích. Chỉ trả lời 1 từ.

Người dùng nói: "{user_input}"
"""
)


def exit_intent_confidence(user_input: str) -> str:
    return (exit_intent_confidence_prompt | model).invoke({"user_input": user_input}).lower()


weather_intent_prompt = PromptTemplate.from_template(
    """
Câu hỏi: {question}
nhiệm vụ của bạn là xác định xem câu hỏi có liên quan đến thời tiết hay không.
Chỉ trả lời đúng một từ: "có" hoặc "không".

Ví dụ:
- "Hôm nay Hà Nội có mưa không?" → có
- "Thời tiết ở Sài Gòn như nào?" → có
- "Mở nhạc lên giúp tôi" → không
- "Tôi muốn biết thời tiết ở Huế" → có
- "Bạn tên là gì?" → không
- "Dự báo mưa ở Đà Nẵng" → có
- "Đang nóng quá trời!" → có
- "Mở trình duyệt" → không
- "nhiệt độ hôm nay" → có
Trả lời:
"""
)


def is_weather_intent(question: str) -> bool:
    return "có" in (weather_intent_prompt | model).invoke({"question": question}).lower()

def extract_location_from_question(question: str) -> str:
    """
    Trích xuất tên địa điểm từ câu hỏi.
    Sử dụng minh_model với max_new_tokens thấp để chỉ trả tên địa điểm.
    """
    prompt_text = f"""Câu hỏi: {question}
Địa điểm được nhắc tới là gì? CHỈ trả lời tên địa điểm, không giải thích.
Nếu không có địa điểm thì trả lời "không có".

Ví dụ:
- "Thời tiết Hà Nội?" → "Hà Nội"
- "Sài Gòn hôm nay mưa không?" → "Sài Gòn"
- "Mấy giờ rồi?" → "không có"

Trả lời chỉ 1 dòng:"""

    from config.model_config import GENERATION_CONFIG
    config = GENERATION_CONFIG.copy()
    config['max_new_tokens'] = 20
    
    inputs = minh_model.tokenizer([prompt_text], return_tensors="pt").to(minh_model.device)
    outputs = minh_model.model.generate(
        **inputs,
        **config,
        pad_token_id=minh_model.tokenizer.eos_token_id,
        eos_token_id=minh_model.tokenizer.eos_token_id
    )
    
    location = minh_model.tokenizer.decode(
        outputs[0][inputs['input_ids'].shape[1]:], 
        skip_special_tokens=True
    ).strip()
    
    # Clean up
    import re
    location = re.sub(r'^\s*\[?\s*minh\s*\]?\s*:\s*', '', location, flags=re.IGNORECASE)
    location = location.split('\n')[0].strip()
    
    if location.lower() in ["không có", "none", ""]:
        return "Hanoi"
    return location


date_time_intent_prompt = PromptTemplate.from_template(
    """
Bạn là hệ thống phân loại intent. Nhiệm vụ của bạn: Xác định xem câu hỏi của người dùng CÓ yêu cầu cung cấp thông tin về NGÀY/GIỜ hiện tại hay không.

Chỉ trả về một trong hai từ khóa:
- "yes"  → nếu câu hỏi **trực tiếp** hỏi về ngày, giờ, hôm nay, hôm qua, hôm sau, hoặc giờ hiện tại ở một nơi cụ thể.
- "no"   → nếu không liên quan.

Ví dụ:
- "Mấy giờ rồi?" → yes
- "Bây giờ là ngày bao nhiêu?" → yes
- "Hôm nay là thứ mấy?" → yes
- "Giờ ở Tokyo là mấy giờ?" → yes
- "Ngày mai tôi có bận không?" → no
- "Hẹn giờ giúp tôi" → no
- "Mở nhạc đi" → no
- "Bạn khỏe không?" → no

Câu hỏi: {question}
Chỉ trả về "yes" hoặc "no".
"""
)


def is_date_time_intent(question: str) -> bool:
    return "yes" in (date_time_intent_prompt | model).invoke({"question": question}).lower()

def date_time_response(question: str, datetime_info: str) -> str:
    """
    Trả lời câu hỏi về ngày giờ sử dụng minh_model (đã có system prompt).
    """
    datetime_info = get_current_datetime()
    
    # Context rõ ràng hơn, nhắc model trả lời thân thiện
    context = f"Thông tin thời gian: {datetime_info}\nHãy trả lời ngắn gọn (1 câu), thân thiện. Nhớ gọi người dùng là 'sếp' và xưng 'tôi'."
    user_message = f"{question}"
    
    # Sử dụng minh_model.generate() đã có system prompt và cleanup
    response = minh_model.generate(user_message, context=context)
    
    # Thêm filter Chinese nếu còn sót
    import re
    response = re.sub(r'[\u4e00-\u9fff\u3000-\u303f]+', '', response)
    response = re.sub(r'Human:.*$', '', response, flags=re.MULTILINE).strip()
    
    return response

def weather_response(question: str, weather_info: str) -> str:
    """
    Trả lời câu hỏi về thời tiết sử dụng minh_model (đã có system prompt).
    """
    weather_info = get_weather(location=extract_location_from_question(question))
    
    # Context rõ ràng hơn, nhắc model trả lời thân thiện
    context = f"Thông tin thời tiết: {weather_info}\nHãy trả lời ngắn gọn (1-2 câu), thân thiện. Nhớ gọi người dùng là 'sếp' và xưng 'tôi'."
    user_message = f"{question}"
    
    # Sử dụng minh_model.generate() đã có system prompt và cleanup
    response = minh_model.generate(user_message, context=context)
    
    # Thêm filter Chinese nếu còn sót
    import re
    response = re.sub(r'[\u4e00-\u9fff\u3000-\u303f]+', '', response)
    response = re.sub(r'Human:.*$', '', response, flags=re.MULTILINE).strip()
    
    return response

extract_search_query_prompt = PromptTemplate.from_template("""
Câu hỏi của người dùng: {question}
Bạn là một công cụ tạo truy vấn tìm kiếm Google tối ưu, nên nhớ bạn không phải công cụ trả lời câu hỏi nên hãy làm đúng nhiệm vụ của mình, không được bịa.
Chỉ trả về DUY NHẤT câu truy vấn ngắn gọn nhất có thể.
Nhiệm vụ:
Không giải thích.
Không liệt kê bước.
Không phân tích.
Không nhắc lại câu hỏi.
Không thêm từ thừa. Chỉ giữ lại các từ khóa quan trọng.
Nếu người dùng viết tên riêng liền nhau (ví dụ: "hoanbucon"), KHÔNG được tách từ, kể cả viết tắt cũng phải để nguyên.
Nếu câu hỏi mơ hồ, hãy thêm từ khóa gợi ý như "là ai", "tiểu sử", "kết quả", "thông tin", "wiki",… hoặc đơn giản là trả về y nguyên.
CHỈ trả về duy nhất câu truy vấn, KHÔNG giải thích gì thêm.
chỉ trả về câu truy vấn tìm kiếm, không nhắc lại câu hỏi.
Ví dụ:
- "Dũng CT là ai?" → "Dũng CT"
- "hoanbucon" → "hoanbucon"
- "Python vs Java, cái nào nhanh hơn?" → "so sánh tốc độ Python vs Java"
- "Hôm nay thời tiết Hà Nội thế nào?" → "thời tiết Hà Nội hôm nay"
- "Ai là tổng thống Mỹ hiện tại?" → "tổng thống Mỹ 2025"
- "Messi ghi bao nhiêu bàn 2024?" → "Messi số bàn thắng 2024"
Chỉ trả về một kết quả cuối cùng:
""")

def extract_search_query(question: str) -> str:
    """
    Trích xuất truy vấn Google tối ưu, gần giống cách ChatGPT tìm kiếm.
    Sử dụng minh_model trực tiếp với max_new_tokens thấp để tránh output dài.
    """
    prompt_text = f"""Câu hỏi của người dùng: {question}
Bạn là một công cụ tạo truy vấn tìm kiếm Google tối ưu.
CHỈ trả về DUY NHẤT câu truy vấn ngắn gọn nhất có thể.
Không giải thích. Không nhắc lại câu hỏi. Không thêm từ thừa.
Nếu người dùng viết tên riêng liền nhau (ví dụ: "hoanbucon"), KHÔNG được tách từ.

Ví dụ:
- "Dũng CT là ai?" → "Dũng CT"
- "hoanbucon" → "hoanbucon"
- "Python vs Java, cái nào nhanh hơn?" → "so sánh tốc độ Python vs Java"

Trả lời chỉ 1 dòng:"""

    # Sử dụng minh_model với max_new_tokens thấp
    from config.model_config import GENERATION_CONFIG
    config = GENERATION_CONFIG.copy()
    config['max_new_tokens'] = 30  # Giới hạn chặt để tránh dài dòng
    
    # Generate với config tùy chỉnh
    inputs = minh_model.tokenizer([prompt_text], return_tensors="pt").to(minh_model.device)
    outputs = minh_model.model.generate(
        **inputs,
        **config,
        pad_token_id=minh_model.tokenizer.eos_token_id,
        eos_token_id=minh_model.tokenizer.eos_token_id
    )
    
    query = minh_model.tokenizer.decode(
        outputs[0][inputs['input_ids'].shape[1]:], 
        skip_special_tokens=True
    ).strip()
    
    # Clean up any extra text
    import re
    query = re.sub(r'^\s*\[?\s*minh\s*\]?\s*:\s*', '', query, flags=re.IGNORECASE)
    # Take first line only
    query = query.split('\n')[0].strip()
    
    return query if query else question
# test sth
# if __name__ == "__main__":
#     while True:
#         question = input("Nhập câu hỏi: ")
#         query = is_date_time_intent(question)
#         print("🔍 Truy vấn tìm kiếm:", query)

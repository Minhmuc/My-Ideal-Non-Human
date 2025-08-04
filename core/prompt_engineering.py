from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from core.prompts import get_prompt
from langchain_ollama import OllamaLLM
from data.realtime_data import get_current_datetime, get_weather

model = OllamaLLM(model="llama3.1:8b")

def clean_input(text: str) -> str:
    return text.strip()

# ===== Should search on web =====
_search_prompt = ChatPromptTemplate.from_template(
    "Câu sau có cần tìm kiếm thông tin trên web không? Trả lời chính xác 'có' hoặc 'không'.\nCâu hỏi: {question}"
)

def should_search(question: str) -> bool:
    result = (_search_prompt | model).invoke({"question": question})
    return "có" in result.lower()

exit_intent_confidence_prompt = PromptTemplate(
    input_variables=["user_input"],
    template="""
Bạn là một trợ lý AI. Dưới đây là một số ví dụ về mức độ người dùng có ý định kết thúc cuộc trò chuyện:

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
Câu hỏi trên có phải đang hỏi về thời tiết không?

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

extract_location_prompt = PromptTemplate.from_template(
    "Câu hỏi: {question}\n"
    "Địa điểm được nhắc tới trong câu hỏi là gì? chỉ trả lời chính xác tên địa điểm. Nếu không có thì trả lời chính xác 'không có' không trả lời thêm."
)

extract_location_chain = extract_location_prompt | model

def extract_location_from_question(question: str) -> str:
    location = extract_location_chain.invoke({"question": question}).strip()
    if location.lower() in ["không có", "none", ""]:
        return "Hanoi"
    return location

date_time_intent_prompt = PromptTemplate.from_template(
    """
Câu hỏi: {question}
Câu hỏi trên có phải đang hỏi về ngày, giờ hoặc thời gian hiện tại không?

Chỉ trả lời chính xác một từ: "có" hoặc "không".

Ví dụ:
- "Mấy giờ rồi?" → có
- "Bây giờ là ngày bao nhiêu?" → có
- "Mở nhạc đi" → không
- "Hôm nay là thứ mấy?" → có
- "Giờ ở Tokyo là mấy giờ?" → có
- "Bạn khỏe không?" → không
- "Hẹn giờ giúp tôi" → có
- "Ngày mai tôi có bận không?" → không
mặc định trả lời:"không" nếu câu hỏi liên quan đến thời tiết, nhiệt độ, nắng, mưa.
Trả lời:
"""
)

def is_date_time_intent(question: str) -> bool:
    return "có" in (date_time_intent_prompt | model).invoke({"question": question}).lower()

date_time_prompt = PromptTemplate.from_template("""
Hiện tại là {datetime_info}.
Hãy trả lời câu hỏi sau một cách tự nhiên, thân thiện như một trợ lý ảo cá tính vầ luôn gọi người dùng là 'sếp'. người dùng hỏi gì trả lời nấy, hỏi giờ trả lời giờ, ngày trả lời ngày,...

Câu hỏi: "{question}"
Trả lời:
"""
)

def date_time_response(question: str, datetime_info: str) -> str:
    datetime_info = get_current_datetime()
    return (date_time_prompt | model).invoke({"datetime_info": datetime_info, "question": question})

Weather_infor_prompt = PromptTemplate.from_template(
"""
Thưa sếp, em vừa tra cứu được thời tiết: {weather_info}.

Dựa trên thông tin trên, hãy trả lời câu hỏi sau theo phong cách tự nhiên, thân thiện, như cấp dưới trả lời sếp. Gọi người dùng là "sếp", và giữ chất riêng của một trợ lý ảo cá tính.

Câu hỏi: "{question}"
Trả lời:
""")


def weather_response(question: str, weather_info: str) -> str:
    weather_info= get_weather(location=extract_location_from_question(question))
    return (Weather_infor_prompt | model).invoke({"weather_info": weather_info, "question": question})


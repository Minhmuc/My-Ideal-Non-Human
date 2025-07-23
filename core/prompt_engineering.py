from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from core.prompts import get_prompt
from langchain_ollama import OllamaLLM

model = OllamaLLM(model="llama3.1:8b")

# ===== Rule-based detection =====
INTENT_KEYWORDS = {
    "exit": ["exit", "quit", "bye", "tạm biệt", "hẹn gặp lại", "dừng lại", "shutdown", "thoát", "đi ngủ", "ngủ đây", "tắt đi", "tắt minh", "off", "mệt quá"],
    "confirm": ["yes", "ok", "đồng ý", "được", "chắc chắn", "tôi đồng ý", "tôi muốn", "làm đi", "tiếp tục"],
    "reject": ["no", "không", "từ chối", "không đồng ý", "không muốn", "không làm", "dừng lại", "không cần"],
}

def clean_input(text: str) -> str:
    return text.strip()

def match_intent(user_input: str, intent: str) -> bool:
    return any(kw in user_input.lower() for kw in INTENT_KEYWORDS.get(intent, []))

def is_exit_input(user_input: str) -> bool:
    return match_intent(user_input, "exit")

def is_confirm_input(user_input: str) -> bool:
    return match_intent(user_input, "confirm")

def is_reject_input(user_input: str) -> bool:
    return match_intent(user_input, "reject")

# ===== LLM-based exit intent detection =====
_exit_prompt = ChatPromptTemplate.from_template(
    "Câu sau có phải là câu hỏi kết thúc cuộc trò chuyện không? Trả lời chỉ 'có' hoặc 'không'.\nCâu hỏi: {user_input}"
)

def exit_intent(user_input: str) -> bool:
    result = (_exit_prompt | model).invoke({"user_input": user_input}).lower()
    keywords = ["muốn thoát", "kết thúc", "dừng lại", "kết thúc cuộc trò chuyện", "đóng", "thoát"]
    return any(k in result for k in keywords) or is_exit_input(user_input)
# ===== Should search on web =====
_search_prompt = ChatPromptTemplate.from_template(
    "Câu sau có cần tìm kiếm thông tin trên web không? Trả lời chỉ 'có' hoặc 'không'.\nCâu hỏi: {question}"
)

def should_search(question: str) -> bool:
    result = (_search_prompt | model).invoke({"question": question})
    return "có" in result.lower()

# ===== Intent classification (multi-class) =====
CLASSIFY_PROMPT = ChatPromptTemplate.from_template(
    """Bạn là một AI phân loại mục đích của người dùng.
Hãy đọc câu sau và trả lời đúng một từ trong các nhãn sau: [thời tiết, giờ, tìm kiếm, trò chuyện, kể chuyện, tạm biệt].

Câu: "{user_input}"
Mục đích:"""
)

def classify_intent(user_input: str) -> str:
    return (CLASSIFY_PROMPT | model).invoke({"user_input": user_input}).strip().lower()

# ===== Greeting =====
def greeting() -> str:
    return get_prompt("greeting")

_exit_prompt = PromptTemplate(
    input_variables=["user_input"],
    template="""
    Câu sau có vẻ cho thấy người dùng muốn kết thúc cuộc trò chuyện: "{user_input}".
    Hãy tạo một câu hỏi xác nhận tự nhiên, đồng cảm, và không lặp lại như trước.
    Chỉ trả về một câu hỏi xác nhận.
    """
)
confirm_message = (_exit_prompt | model).invoke({"user_input": clean_input})

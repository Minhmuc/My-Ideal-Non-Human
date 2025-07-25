from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from core.prompts import get_prompt
from langchain_ollama import OllamaLLM

model = OllamaLLM(model="llama3.1:8b")

def clean_input(text: str) -> str:
    return text.strip()

# ===== Should search on web =====
_search_prompt = ChatPromptTemplate.from_template(
    "Câu sau có cần tìm kiếm thông tin trên web không? Trả lời chỉ 'có' hoặc 'không'.\nCâu hỏi: {question}"
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
    "Câu hỏi: {question}\n"
    "Câu hỏi trên có phải đang hỏi về thời tiết không? Trả lời chính xác 'có' hoặc 'không'."
)

def is_weather_intent(question: str) -> bool:
    return "có" in (weather_intent_prompt | model).invoke({"question": question}).lower()

extract_location_prompt = PromptTemplate.from_template(
    "Câu hỏi: {question}\n"
    "Địa điểm được nhắc tới trong câu hỏi là gì? chỉ trả lời chính xác tên địa điểm. Nếu không có thì trả lời chính xác 'không có'."
)

extract_location_chain = extract_location_prompt | model

def extract_location_from_question(question: str) -> str:
    location = extract_location_chain.invoke({"question": question}).strip()
    if location.lower() in ["không có", "none", ""]:
        return "Hanoi"
    return location


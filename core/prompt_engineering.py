from core.prompts import get_prompt

def clean_input(text: str) -> str:
    """
    Tiền xử lý câu hỏi đầu vào: loại bỏ ký tự thừa, chuẩn hóa.
    """
    return text.strip()


def is_exit_input(user_input):
    exit_phrases = [
        "exit", "quit", "bye", "tạm biệt", "hẹn gặp lại", "dừng lại", 
        "shutdown", "thoát", "đi ngủ", "mệt quá", "ngủ đây", "tắt đi", "tắt minh", "off"
    ]
    return any(phrase in user_input.lower() for phrase in exit_phrases)

def is_confirm_input(user_input):
    confirm_phrases = [
        "yes", "ok", "đồng ý", "được", "chắc chắn", "tôi đồng ý", 
        "tôi muốn", "làm đi", "tiếp tục"
    ]
    return any(phrase in user_input.lower() for phrase in confirm_phrases)

def is_reject_input(user_input):
    reject_phrases = [
        "no", "không", "từ chối", "không đồng ý", "không muốn", 
        "không làm", "dừng lại", "không cần"
    ]
    return any(phrase in user_input.lower() for phrase in reject_phrases)

def should_search(user_input: str) -> bool:
    get_search_phrases = [get_prompt("web_search")]
    return any(phrase in user_input.lower() for phrase in get_search_phrases)
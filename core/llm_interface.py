"""
MINH LLM Interface - Refactored to use True AI Agent
No more hardcode! Agent decides everything.
"""
from core.agents.minh_agent import minh_agent
from core.models import minh_model
from core.vectorstore import search_similar, add_texts_to_vectorstore
import re


def ask_llm_with_context(question: str, retrieved_info: str = "") -> str:
    """
    Hỏi LLM kèm ngữ cảnh từ vectorstore
    Kept for backward compatibility, but simplified
    """
    if retrieved_info:
        context = f"Thông tin tham khảo:\n{retrieved_info}\n\nHãy trả lời ngắn gọn (1-2 câu), thân thiện. Nhớ gọi người dùng là 'sếp' và xưng 'tôi'."
        user_message = f"{question}"
    else:
        context = "Hãy trả lời ngắn gọn (1-2 câu), thân thiện. Nhớ gọi người dùng là 'sếp' và xưng 'tôi'."
        user_message = question
    
    response = minh_model.generate(user_message, context=context)
    return response.strip()


async def ask_llm_with_memory(question: str) -> str:
    """
    Main entry point - Now uses AI Agent instead of hardcode!
    
    Agent tự quyết định:
    - Function nào cần gọi
    - Parameters là gì
    - Multi-step workflows
    - Self-verification
    
    No more if-else hardcode!
    """
    try:
        # Delegate to AI Agent
        response = await minh_agent.process(question)
        return response
    
    except Exception as e:
        print(f"[MINH Agent Error] {e}")
        import traceback
        traceback.print_exc()
        return "Xin lỗi sếp, có lỗi khi xử lý yêu cầu. Sếp thử hỏi lại được không?"

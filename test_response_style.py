"""
Quick test - Kiểm tra MINH trả lời ngắn gọn tự nhiên
"""
import asyncio
from core.llm_interface_simple import ask_llm_with_memory

async def test_responses():
    print("=" * 60)
    print("Testing MINH's Response Style")
    print("=" * 60)
    
    test_questions = [
        "Xin chào!",
        "Bạn là ai?",
        "Hôm nay thứ mấy?",
        "Thời tiết Hà Nội hôm nay thế nào?",
    ]
    
    for q in test_questions:
        print(f"\n👤 Sếp: {q}")
        response = await ask_llm_with_memory(q)
        print(f"🤖 MINH: {response}")
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(test_responses())

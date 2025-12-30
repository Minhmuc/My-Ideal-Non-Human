"""
Test MINH personality - Kiểm tra câu trả lời có giữ đúng tính cách không
"""
import asyncio
from core.llm_interface_simple import ask_llm_with_memory

async def test_personality():
    print("=" * 60)
    print("Testing MINH Personality & Knowledge")
    print("=" * 60)
    
    tests = [
        "Xin chào!",
        "Bạn là ai?",
        "Ai tạo ra bạn?",
        "Creator của bạn tên gì?",
        "Bạn ở đâu?",
        "Hôm nay thứ mấy?",
    ]
    
    for q in tests:
        print(f"\n👤 Sếp: {q}")
        response = await ask_llm_with_memory(q)
        print(f"🤖 MINH: {response}")
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(test_personality())

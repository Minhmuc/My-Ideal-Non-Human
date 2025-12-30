"""
Test function calling - ChatGPT style
"""
import asyncio
import sys
sys.path.insert(0, '.')

from core.llm_interface_simple import ask_llm_with_memory

async def test():
    print("=" * 60)
    print("TEST FUNCTION CALLING - ChatGPT Style")
    print("=" * 60)
    
    tests = [
        "Mấy giờ rồi?",
        "Hôm nay là thứ mấy?",
        "Thời tiết ở Hà Nội thế nào?",
        "Cho tôi biết thời tiết ở Sài Gòn",
        "Xin chào MINH",
        "Người tạo ra bạn là ai?"
    ]
    
    for i, question in enumerate(tests, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {question}")
        print("-" * 60)
        
        response = await ask_llm_with_memory(question)
        print(f"MINH: {response}")
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test())

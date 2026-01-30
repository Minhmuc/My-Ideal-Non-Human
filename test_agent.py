"""
Test MINH AI Agent - Refactored to use new agent architecture
"""
import asyncio
from core.agents import minh_agent


async def test_agent():
    """Test various queries với new agent"""
    
    test_cases = [
        # Simple queries (fast-path)
        "Mấy giờ rồi?",
        "Thời tiết Hà Nội?",
        "Python là gì?",
        
        # Complex queries (ReAct loop)
        "So sánh Python và JavaScript",
        "hoanbucon là ai?, hãy tra cứu trên google về họ(tên đầy đủ, đóng góp nổi bật).",
    ]
    
    print("=" * 60)
    print("🤖 Testing MINH AI Agent (Refactored)")
    print("=" * 60)
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}/{len(test_cases)}: {query}")
        print("-" * 60)
        
        try:
            response = await minh_agent.process(query)
            print(f"✅ Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("=" * 60)
    print("✅ Testing complete!")


if __name__ == "__main__":
    asyncio.run(test_agent())

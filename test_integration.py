"""
Quick test script - Backend + Frontend integration
"""
import asyncio
import sys

async def test_backend():
    print("=" * 60)
    print("MINH Backend Integration Test")
    print("=" * 60)
    
    print("\n[1/3] Testing LLM interface...")
    try:
        from core.llm_interface import ask_llm_with_memory
        response = await ask_llm_with_memory("Xin chào!")
        print(f"✅ LLM Response: {response[:100]}...")
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        return False
    
    print("\n[2/3] Testing vectorstore...")
    try:
        from core.vectorstore import search_similar, add_texts_to_vectorstore
        add_texts_to_vectorstore(["Test data from integration test"])
        results = search_similar("test", k=1)
        print(f"✅ Vectorstore: Found {len(results)} results")
    except Exception as e:
        print(f"❌ Vectorstore Error: {e}")
        return False
    
    print("\n[3/3] Testing web search...")
    try:
        from core.webSearch import search_web
        results = search_web("Python programming")
        print(f"✅ Web Search: Found {len(results)} results")
    except Exception as e:
        print(f"❌ Web Search Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Backend is ready.")
    print("=" * 60)
    print("\nTo start API server:")
    print("  python -m uvicorn api_server:app --host 127.0.0.1 --port 8000")
    print("\nTo start Desktop app:")
    print("  cd desktop")
    print("  npm run dev")
    return True

if __name__ == "__main__":
    asyncio.run(test_backend())

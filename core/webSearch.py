from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import requests
import asyncio
from typing import Optional, List, Tuple

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY") #  API key 
CX = os.getenv("CX") #  Custom Search Engine ID

def search_duckduckgo(query: str, num_results: int = 5) -> Optional[str]:
    """
    Tìm kiếm qua DuckDuckGo sử dụng thư viện ddgs
    Không cần API key, lấy kết quả thực từ web
    """
    try:
        from ddgs import DDGS
        
        results = []
        with DDGS() as ddgs:
            search_results = ddgs.text(query, max_results=num_results, region='vn-vi')
            
            for item in search_results:
                title = item.get('title', '')
                body = item.get('body', '')
                href = item.get('href', '')
                
                if title and body:
                    results.append(f"📌 {title}\n{body}\n🔗 {href}")
        
        print(f"[DuckDuckGo] Found {len(results)} results")
        return "\n\n".join(results) if results else None
        
    except Exception as e:
        print(f"[DuckDuckGo Search Error] {e}")
        import traceback
        traceback.print_exc()
        return None

def search_google(query: str, num_results: int = 5) -> Optional[str]:
    """
    Hàm tìm kiếm Google bằng Google Custom Search API
    Trả về kết quả tiếng Việt tối ưu
    """
    try:
        if not API_KEY or not CX:
            print("[Google Search] API_KEY or CX not configured")
            return None
        
        print(f"[Google Search] Searching for: {query}")
        service = build("customsearch", "v1", developerKey=API_KEY)
        results = service.cse().list(
            q=query,
            cx=CX,
            lr="lang_vi",      # Ưu tiên tiếng Việt
            hl="vi",           # Trả về kết quả tiếng Việt
            num=min(num_results, 10)  # Google API max 10
        ).execute()

        data = []
        if "items" in results:
            for item in results["items"]:
                title = item.get("title", "Không có tiêu đề")
                snippet = item.get("snippet", "Không có mô tả")
                link = item.get("link", "#")
                data.append(f"📌 {title}\n{snippet}\n🔗 Link: {link}")
            print(f"[Google Search] Found {len(data)} results")
        else:
            print(f"[Google Search] No items in response: {results}")
        
        return "\n\n".join(data) if data else None

    except Exception as e:
        print(f"[Google Search Error] Type: {type(e).__name__}")
        print(f"[Google Search Error] Message: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def search_web_async(query: str, num_results: int = 5) -> str:
    """
    Async version: Tìm kiếm web với multiple engines ĐỒNG THỜI
    Query cùng lúc: Google + DuckDuckGo
    """
    print(f"\n[WebSearch] Starting parallel search for: '{query}'")
    
    # Create tasks for parallel execution
    async def google_wrapper():
        # Run sync function in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, search_google, query, num_results)
        return ("Google", result)
    
    async def ddg_wrapper():
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, search_duckduckgo, query, num_results)
        return ("DuckDuckGo", result)
    
    # Wait for all searches to complete
    search_results = await asyncio.gather(
        google_wrapper(),
        ddg_wrapper(),
        return_exceptions=True
    )
    
    # Combine results from all sources
    combined_results = []
    successful_sources = []
    
    for result in search_results:
        if isinstance(result, Exception):
            print(f"[WebSearch] Search failed with exception: {result}")
            continue
        source, data = result
        if data:
            combined_results.append(f"### 🔍 Nguồn: {source}\n{data}")
            successful_sources.append(source)
            print(f"[WebSearch] ✅ {source} successful")
        else:
            print(f"[WebSearch] {source} returned no results")
    
    # Return combined results or fallback
    if combined_results:
        print(f"[WebSearch] ✅ Combined results from: {', '.join(successful_sources)}")
        return "\n\n" + "="*50 + "\n\n".join(combined_results)
    
    # Last resort
    print("[WebSearch] ❌ All search engines failed")
    return f"⚠️ Tôi không tìm thấy thông tin về '{query}' trên web. Sếp có thể thử hỏi theo cách khác hoặc cung cấp thêm chi tiết không?"


def search_web(query: str, num_results: int = 5) -> str:
    """
    Sync wrapper for search_web_async
    Tìm kiếm web với Google + DuckDuckGo ĐỒNG THỜI
    """
    try:
        # Try to get running loop
        loop = asyncio.get_running_loop()
        # We're already in async context - create a task
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                asyncio.run,
                search_web_async(query, num_results)
            )
            return future.result()
    except RuntimeError:
        # No running loop - safe to use asyncio.run()
        return asyncio.run(search_web_async(query, num_results))
    
# print(search_web("hoanbucon"))  #test ham tim kiem
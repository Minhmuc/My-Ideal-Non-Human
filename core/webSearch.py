from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import requests
from typing import Optional

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY") #  API key 
CX = os.getenv("CX") #  Custom Search Engine ID
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")  # Brave Search API (optional)

def search_brave(query: str, num_results: int = 5) -> Optional[str]:
    """
    Tìm kiếm qua Brave Search API (miễn phí 2000 queries/tháng)
    Đăng ký tại: https://brave.com/search/api/
    """
    try:
        if not BRAVE_API_KEY:
            print("[Brave Search] API key not configured")
            return None
            
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": BRAVE_API_KEY
        }
        params = {
            "q": query,
            "count": num_results,
            "country": "VN",
            "search_lang": "vi"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"[Brave Search] Status: {response.status_code}")
            return None
            
        data = response.json()
        results = []
        
        # Web results
        for item in data.get("web", {}).get("results", [])[:num_results]:
            title = item.get("title", "")
            description = item.get("description", "")
            url = item.get("url", "")
            if title and description:
                results.append(f"📌 {title}\n{description}\n🔗 {url}")
        
        print(f"[Brave Search] Found {len(results)} results")
        return "\n\n".join(results) if results else None
        
    except Exception as e:
        print(f"[Brave Search Error] {e}")
        return None

def search_duckduckgo(query: str, num_results: int = 5) -> Optional[str]:
    """
    Tìm kiếm qua DuckDuckGo API (miễn phí, không cần API key)
    """
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        results = []
        
        # Abstract (câu trả lời trực tiếp)
        if data.get("Abstract"):
            results.append(f"📌 {data.get('Heading', 'Thông tin')}\n{data['Abstract']}")
        
        # Related Topics
        for topic in data.get("RelatedTopics", [])[:num_results]:
            if isinstance(topic, dict) and "Text" in topic:
                text = topic.get("Text", "")
                url = topic.get("FirstURL", "")
                if text:
                    results.append(f"📌 {text}\n🔗 {url}")
        
        return "\n\n".join(results) if results else None
        
    except Exception as e:
        print(f"[DuckDuckGo Search Error] {e}")
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

def search_web(query: str, num_results: int = 5) -> str:
    """
    Tìm kiếm web với multiple engines và fallback
    Thử theo thứ tự: Google → Brave → DuckDuckGo → Fallback message
    """
    print(f"\n[WebSearch] Starting search for: '{query}'")
    
    # Try Google first (nếu có API key)
    google_result = search_google(query, num_results)
    if google_result:
        print("[WebSearch] ✅ Google successful")
        return google_result
    
    # Fallback to Brave Search
    print("[WebSearch] Google failed, trying Brave Search...")
    brave_result = search_brave(query, num_results)
    if brave_result:
        print("[WebSearch] ✅ Brave successful")
        return brave_result
    
    # Fallback to DuckDuckGo
    print("[WebSearch] Brave failed, trying DuckDuckGo...")
    ddg_result = search_duckduckgo(query, num_results)
    if ddg_result:
        print("[WebSearch] ✅ DuckDuckGo successful")
        return ddg_result
    
    # Last resort: simple web search message
    print("[WebSearch] ❌ All search engines failed")
    return f"⚠️ Tôi không tìm thấy thông tin về '{query}' trên web. Sếp có thể thử hỏi theo cách khác hoặc cung cấp thêm chi tiết không?"
    
# print(search_web("hoanbucon"))  #test ham tim kiem
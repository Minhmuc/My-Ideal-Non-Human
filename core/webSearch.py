from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY") #  API key 
CX = os.getenv("CX") #  Custom Search Engine ID

def search_web(query: str, num_results: int = 5) -> str:
    """
    Hàm tìm kiếm Google bằng Google Custom Search API
    Trả về kết quả tiếng Việt tối ưu
    """
    try:
        service = build("customsearch", "v1", developerKey=API_KEY)
        results = service.cse().list(
            q=query,
            cx=CX,
            lr="lang_vi",      # Ưu tiên tiếng Việt
            hl="vi",           # Trả về kết quả tiếng Việt
            num=num_results
        ).execute()

        data = []
        if "items" in results:
            for item in results["items"]:
                title = item.get("title", "Không có tiêu đề")
                snippet = item.get("snippet", "Không có mô tả")
                link = item.get("link", "#")
                data.append(f"📌 {title}\n{snippet}\n🔗 Link: {link}")
        else:
            data.append("⚠️ Không tìm thấy kết quả phù hợp.")

        return "\n\n".join(data)

    except Exception as e:
        return f"❌ Lỗi khi tìm kiếm: {e}"
    
# print(search_web("hoanbucon"))  #test ham tim kiem
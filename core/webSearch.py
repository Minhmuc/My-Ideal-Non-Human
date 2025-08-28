from ddgs import DDGS
import wikipedia

def search_web(query: str, num_results: int = 3) -> str:
    """
    Tìm kiếm trên DuckDuckGo và Wikipedia.
    Trả về chuỗi tổng hợp kết quả (dùng trong prompt LLM).
    """
    results = []

    # DuckDuckGo Search
    try:
        with DDGS() as ddgs:
            for result in ddgs.text(query, max_results=num_results):
                content = result.get("body") or result.get("title") or ""
                link = result.get("href") or ""
                if content:
                    results.append(f"{content}\nLink: {link}")
    except Exception as e:
        results.append(f"[DuckDuckGo Error] {str(e)}")

    # Wikipedia Summary
    try:
        summary = wikipedia.summary(query, sentences=3, auto_suggest=True)
        results.append(f"[Wikipedia] {summary}")
    except wikipedia.exceptions.DisambiguationError as e:
        results.append(f"[Wikipedia Warning] Nhiều kết quả: {e.options[:3]}")
    except wikipedia.exceptions.PageError:
        results.append("[Wikipedia Warning] Không tìm thấy trang phù hợp.")
    except Exception as e:
        results.append(f"[Wikipedia Error] {str(e)}")

    return "\n\n".join(results)

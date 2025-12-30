"""
Function calling definitions for MINH - ChatGPT style
"""
import json
from typing import List, Dict, Any
from data.realtime_data import get_current_datetime, get_weather
from core.webSearch import search_duckduckgo

# Define available functions
FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Lấy thông tin ngày giờ hiện tại. Sử dụng khi người dùng hỏi về thời gian, ngày tháng, thứ mấy, mấy giờ.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Lấy thông tin thời tiết của một địa điểm. Sử dụng khi người dùng hỏi về thời tiết, nhiệt độ, mưa nắng.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Tên thành phố hoặc địa điểm cần lấy thông tin thời tiết. Ví dụ: 'Hanoi', 'Ho Chi Minh', 'Da Nang'"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Tìm kiếm thông tin trên web khi không biết câu trả lời hoặc cần thông tin mới nhất. Sử dụng khi người dùng hỏi về người nổi tiếng, sự kiện, tin tức, hoặc thông tin bạn không chắc chắn.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Từ khóa tìm kiếm. Ví dụ: 'Đoàn Văn Sáng', 'World Cup 2026', 'ChatGPT là gì'"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def execute_function(function_name: str, arguments: Dict[str, Any]) -> str:
    """Execute function and return result"""
    try:
        if function_name == "get_current_datetime":
            return get_current_datetime()
        
        elif function_name == "get_weather":
            location = arguments.get("location", "Hanoi")
            return get_weather(location)
        
        elif function_name == "search_web":
            query = arguments.get("query", "")
            if not query:
                return "Error: Missing search query"
            results = search_duckduckgo(query, max_results=3)
            if results:
                return "\n\n".join([f"- {r}" for r in results])
            return "Không tìm thấy kết quả phù hợp."
        
        else:
            return f"Error: Unknown function {function_name}"
    
    except Exception as e:
        return f"Error executing {function_name}: {str(e)}"

def parse_function_call(text: str) -> tuple[str, Dict[str, Any]] | None:
    """Parse function call from model output"""
    # Qwen format: <tool_call>{"name": "func", "arguments": {...}}</tool_call>
    if "<tool_call>" in text and "</tool_call>" in text:
        try:
            start = text.index("<tool_call>") + len("<tool_call>")
            end = text.index("</tool_call>")
            json_str = text[start:end].strip()
            
            call_data = json.loads(json_str)
            function_name = call_data.get("name")
            arguments = call_data.get("arguments", {})
            
            return function_name, arguments
        except:
            pass
    
    return None

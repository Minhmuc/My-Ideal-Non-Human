"""
Quick Executor - Fast-path cho simple queries
Bypass ReAct loop cho performance
"""
import re
from typing import Optional
from core.functions import execute_function
from core.models import minh_model
from data.realtime_data import get_current_datetime


class QuickExecutor:
    """Execute simple single-function tasks nhanh (< 3s)"""
    
    def __init__(self):
        self.cities = ['hà nội', 'sài gòn', 'tp hcm', 'đà nẵng', 'huế', 
                      'cần thơ', 'hải phòng', 'nha trang', 'vũng tàu']
    
    async def execute(self, quick_action: dict) -> str:
        """
        Execute quick action và format response
        
        Args:
            quick_action: {"type": "datetime/weather/search", "function": "...", "args": {...}}
        
        Returns:
            Formatted response from MINH
        """
        action_type = quick_action['type']
        function_name = quick_action['function']
        args = quick_action.get('args', {})
        
        # Execute function
        result = execute_function(function_name, args)
        
        # Format response với personality
        if action_type == 'datetime':
            response = self._format_datetime_response(result)
        elif action_type == 'weather':
            response = self._format_weather_response(result, args.get('location', 'Hanoi'))
        elif action_type == 'search':
            # Search cần context từ model
            question = quick_action.get('original_question', '')
            response = await self._format_search_response(question, result)
        else:
            response = result
        
        return response
    
    def _format_datetime_response(self, datetime_info: str) -> str:
        """Quick format datetime without model call"""
        # Extract time
        time_match = re.search(r'(\d{1,2}:\d{2})', datetime_info)
        date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', datetime_info)
        
        if time_match:
            time = time_match.group(1)
            if date_match:
                return f"Bây giờ là {time} sếp ạ!"
            return f"Bây giờ là {time} sếp!"
        
        return f"Thời gian hiện tại: {datetime_info} sếp ạ!"
    
    def _format_weather_response(self, weather_info: str, location: str) -> str:
        """Quick format weather without model call"""
        # Extract key info
        temp_match = re.search(r'(\d+)°C', weather_info)
        
        if temp_match:
            temp = temp_match.group(1)
            return f"Thời tiết {location} hiện tại {temp}°C sếp ạ!"
        
        return f"Thời tiết {location}: {weather_info}"
    
    async def _format_search_response(self, question: str, search_result: str) -> str:
        """Format search result với AI (cần model)"""
        context = f"Kết quả tìm kiếm:\n{search_result}\n\nHãy trả lời ngắn gọn (2-3 câu), thân thiện. Nhớ gọi người dùng là 'sếp' và xưng 'tôi'."
        
        response = minh_model.generate(question, context=context, max_new_tokens=180)
        return response
    
    def extract_location_fast(self, text: str) -> str:
        """Extract location bằng regex, không dùng model"""
        t = text.lower()
        
        for city in self.cities:
            if city in t:
                return city.title()
        
        # Default
        return "Hanoi"


# Singleton instance
quick_executor = QuickExecutor()

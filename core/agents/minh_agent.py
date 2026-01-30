"""
MINH Agent - Main entry point
Smart routing between Fast-path và ReAct loop
"""
import re
from typing import Optional, Dict, Any
from core.agents.quick_executor import QuickExecutor
from core.agents.react_agent import ReActAgent
from core.vectorstore import add_texts_to_vectorstore


class MINHAgent:
    """
    Main MINH AI Agent
    
    Smart routing:
    - Simple queries → Fast-path (< 3s)
    - Complex tasks → ReAct loop (optimized)
    """
    
    def __init__(self):
        self.quick_executor = QuickExecutor()
        self.react_agent = ReActAgent()
    
    async def process(self, user_input: str) -> str:
        """
        Main processing pipeline
        
        Args:
            user_input: User's question or command
            
        Returns:
            MINH's response
        """
        # Check for data provision
        data_response = self._handle_data_provision(user_input)
        if data_response:
            return data_response
        
        # Try fast-path first
        quick_action = self._detect_quick_action(user_input)
        
        if quick_action:
            # Fast execution
            response = await self.quick_executor.execute(quick_action)
        else:
            # Complex task → ReAct loop
            response = await self.react_agent.process(user_input)
        
        # Save to memory
        self._save_to_memory(user_input, response)
        
        return response
    
    def _detect_quick_action(self, task: str) -> Optional[Dict[str, Any]]:
        """
        Detect simple single-function tasks
        
        Returns:
            Quick action dict hoặc None nếu complex
        """
        t = task.lower()
        
        # Datetime queries
        if re.search(r'(mấy giờ|bây giờ|hôm nay là|ngày bao nhiêu|thứ mấy)', t):
            return {
                "type": "datetime",
                "function": "get_current_datetime",
                "args": {}
            }
        
        # Weather queries
        if re.search(r'(thời tiết|nhiệt độ|mưa|nắng|độ c)', t):
            location = self.quick_executor.extract_location_fast(task)
            return {
                "type": "weather",
                "function": "get_weather",
                "args": {"location": location}
            }
        
        # Simple "X là ai?" or "X là gì?" queries
        match = re.search(r'^(.+?)\s+là\s+(ai|gì)\s*\??$', t)
        if match:
            query = match.group(1).strip()
            return {
                "type": "search",
                "function": "search_web",
                "args": {"query": query},
                "original_question": task
            }
        
        # Wiki/info queries
        if re.search(r'(wiki|thông tin về|giới thiệu về)\s+(.+)', t):
            match = re.search(r'(wiki|thông tin về|giới thiệu về)\s+(.+)', t)
            if match:
                query = match.group(2).strip()
                return {
                    "type": "search",
                    "function": "search_web",
                    "args": {"query": query},
                    "original_question": task
                }
        
        # None = Complex task, cần ReAct
        return None
    
    def _handle_data_provision(self, user_input: str) -> Optional[str]:
        """Handle data provision requests"""
        if user_input.lower().startswith(('dữ liệu:', 'data:')):
            data_content = user_input.split(':', 1)[-1].strip()
            if data_content:
                add_texts_to_vectorstore([f"{data_content}"])
                return "Đã lưu dữ liệu của sếp vào hệ thống. Sếp có thể hỏi lại bất cứ lúc nào!"
            else:
                return "Sếp cần nhập nội dung dữ liệu sau 'dữ liệu:' hoặc 'data:' nhé!"
        return None
    
    def _save_to_memory(self, question: str, response: str):
        """Save conversation to vectorstore"""
        try:
            add_texts_to_vectorstore([f"Người dùng: {question}\nMINH: {response}"])
        except Exception as e:
            # Silent fail, không ảnh hưởng main flow
            print(f"[Warning] Failed to save to vectorstore: {e}")


# Singleton instance
minh_agent = MINHAgent()

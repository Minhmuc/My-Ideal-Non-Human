"""
ReAct Agent - Reasoning + Acting Loop
True AI Agent với self-verification và planning
"""
import json
import asyncio
from typing import List, Dict, Any, Optional
from core.models import minh_model
from core.functions import FUNCTIONS, execute_function


class ReActAgent:
    """
    ReAct (Reasoning + Acting) Agent
    
    Loop: Think → Act → Observe → Repeat
    Không hardcode logic, AI tự quyết định actions
    """
    
    def __init__(self, max_iterations: int = 10, max_memory_tokens: int = 1500):
        self.model = minh_model
        self.max_iterations = max_iterations
        self.max_memory_tokens = max_memory_tokens
        self.memory: List[str] = []
        self.available_functions = FUNCTIONS
    
    async def process(self, task: str) -> str:
        """
        Main ReAct loop
        
        Args:
            task: User request
            
        Returns:
            Final answer
        """
        self.memory = [f"Task: {task}"]
        
        for iteration in range(self.max_iterations):
            # Parallel: Generate thought + action candidates
            thought, action = await self._iteration_optimized()
            
            self.memory.append(f"Thought {iteration + 1}: {thought}")
            
            # Check completion
            if self._is_task_complete(thought):
                answer = self._extract_answer(thought)
                return answer
            
            # Execute action
            self.memory.append(f"Action {iteration + 1}: {json.dumps(action, ensure_ascii=False)}")
            
            observation = await self._execute_action(action)
            self.memory.append(f"Observation {iteration + 1}: {observation}")
            
            # Check if observation indicates completion
            if self._is_success(observation):
                # Generate final response
                final_answer = await self._generate_final_response(task, observation)
                return final_answer
        
        # Max iterations reached
        return "Xin lỗi sếp, task này phức tạp quá, tôi cần nhiều thời gian hơn hoặc sếp có thể chia nhỏ task giúp tôi được không?"
    
    async def _iteration_optimized(self) -> tuple[str, dict]:
        """
        Optimized iteration với parallel processing
        
        Returns:
            (thought, selected_action)
        """
        # Parallel: Think + Generate candidates
        thought_task = self._generate_thought()
        candidates_task = self._generate_action_candidates()
        
        thought, candidates = await asyncio.gather(thought_task, candidates_task)
        
        # Select best action (fast, no model call)
        action = self._select_best_action(thought, candidates)
        
        return thought, action
    
    async def _generate_thought(self) -> str:
        """Generate reasoning about current state"""
        context = self._get_context()
        
        prompt = f"""Bạn là AI agent đang thực hiện task. 

{context}

Hãy suy nghĩ về tình trạng hiện tại và bước tiếp theo:
- Task đã hoàn thành chưa? Nếu rồi, trả lời: "TASK_COMPLETE. Answer: <câu trả lời cho user>"
- Nếu chưa: Bước tiếp theo cần làm gì? Tại sao?

Chỉ trả về suy nghĩ ngắn gọn (1-2 câu):"""
        
        thought = self.model.generate(prompt, context="", max_new_tokens=100)
        return thought.strip()
    
    async def _generate_action_candidates(self) -> List[Dict]:
        """Generate possible next actions"""
        context = self._get_context()
        
        functions_str = json.dumps(self.available_functions, indent=2, ensure_ascii=False)
        
        prompt = f"""Bạn là AI agent. Dựa vào context, đề xuất 2-3 actions có thể thực hiện tiếp theo.

{context}

Available functions:
{functions_str}

Trả về JSON array (không giải thích):
[
  {{"name": "function_name", "arguments": {{}}, "reason": "why this action"}},
  ...
]

Actions:"""
        
        response = self.model.generate(prompt, context="", max_new_tokens=120)
        
        try:
            # Extract JSON
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                candidates = json.loads(json_match.group(0))
                return candidates
        except:
            pass
        
        # Fallback: Empty candidates
        return []
    
    def _select_best_action(self, thought: str, candidates: List[Dict]) -> Dict:
        """
        Fast selection dựa trên keyword matching
        Không cần model call
        """
        if not candidates:
            # No candidates → Ask model to decide (fallback)
            return self._fallback_action_selection(thought)
        
        # Score each candidate based on relevance to thought
        scores = []
        for candidate in candidates:
            score = self._calculate_relevance(thought, candidate.get('reason', ''))
            scores.append(score)
        
        # Pick highest score
        best_idx = scores.index(max(scores))
        return candidates[best_idx]
    
    def _calculate_relevance(self, thought: str, reason: str) -> float:
        """Simple keyword overlap scoring"""
        thought_words = set(thought.lower().split())
        reason_words = set(reason.lower().split())
        
        overlap = len(thought_words & reason_words)
        total = len(thought_words | reason_words)
        
        return overlap / total if total > 0 else 0.0
    
    def _fallback_action_selection(self, thought: str) -> Dict:
        """Fallback khi không có candidates"""
        # Simple heuristic: Pick function based on keywords in thought
        t = thought.lower()
        
        if any(kw in t for kw in ['thời gian', 'giờ', 'ngày']):
            return {"name": "get_current_datetime", "arguments": {}}
        elif any(kw in t for kw in ['thời tiết', 'weather']):
            return {"name": "get_weather", "arguments": {"location": "Hanoi"}}
        elif any(kw in t for kw in ['tìm', 'search', 'tra cứu']):
            return {"name": "search_web", "arguments": {"query": thought}}
        
        # Default: Search
        return {"name": "search_web", "arguments": {"query": thought}}
    
    async def _execute_action(self, action: Dict) -> str:
        """Execute action and return observation"""
        try:
            function_name = action.get('name')
            arguments = action.get('arguments', {})
            
            result = execute_function(function_name, arguments)
            return f"SUCCESS: {result}"
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def _is_task_complete(self, thought: str) -> bool:
        """Check if thought indicates completion"""
        return "TASK_COMPLETE" in thought or "hoàn thành" in thought.lower()
    
    def _is_success(self, observation: str) -> bool:
        """Check if observation indicates success"""
        return "SUCCESS" in observation and "ERROR" not in observation
    
    def _extract_answer(self, thought: str) -> str:
        """Extract answer from completion thought"""
        if "Answer:" in thought:
            return thought.split("Answer:")[1].strip()
        return thought
    
    async def _generate_final_response(self, task: str, observation: str) -> str:
        """Generate natural final response"""
        # Extract result from observation
        result = observation.replace("SUCCESS:", "").strip()
        
        prompt = f"""User yêu cầu: {task}
Kết quả: {result}

Hãy trả lời user một cách đầy đủ, tự nhiên, thân thiện. Tổng hợp thông tin từ kết quả tìm kiếm. 
Nhớ gọi người dùng là 'sếp' và xưng 'tôi'.

Response:"""
        
        response = self.model.generate(prompt, context="", max_new_tokens=300)
        return response.strip()
    
    def _get_context(self) -> str:
        """Get truncated context (avoid token overflow)"""
        if len(self.memory) <= 5:
            return "\n".join(self.memory)
        
        # Keep: Task + Last 4 items
        important = [
            self.memory[0],   # Original task
            *self.memory[-4:] # Recent 4 steps
        ]
        
        return "\n".join(important)


# Singleton instance
react_agent = ReActAgent()


# Import re for json extraction
import re

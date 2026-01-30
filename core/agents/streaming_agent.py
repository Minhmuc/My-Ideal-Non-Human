"""
Streaming Agent - Real-time progress updates
Better UX: User thấy AI đang làm gì
"""
from typing import AsyncIterator
from core.agents.minh_agent import MINHAgent
from core.agents.react_agent import ReActAgent


class StreamingAgent(MINHAgent):
    """
    Extension của MINHAgent với streaming support
    Stream thoughts và actions real-time
    """
    
    async def process_stream(self, user_input: str) -> AsyncIterator[str]:
        """
        Process với streaming progress updates
        
        Yields:
            Progress messages + final response
        """
        # Check for data provision
        data_response = self._handle_data_provision(user_input)
        if data_response:
            yield data_response
            return
        
        # Check fast-path
        quick_action = self._detect_quick_action(user_input)
        
        if quick_action:
            yield "⚡ Đang xử lý nhanh..."
            response = await self.quick_executor.execute(quick_action)
            yield response
        else:
            # Complex task với ReAct streaming
            yield "🧠 Đang phân tích task..."
            
            async for update in self._react_stream(user_input):
                yield update
        
        # Save to memory (silent)
        # Will be saved by agent internally
    
    async def _react_stream(self, task: str) -> AsyncIterator[str]:
        """Stream ReAct loop progress"""
        agent = self.react_agent
        agent.memory = [f"Task: {task}"]
        
        for iteration in range(agent.max_iterations):
            # Thinking phase
            yield f"💭 Bước {iteration + 1}: Đang suy nghĩ..."
            
            thought, action = await agent._iteration_optimized()
            agent.memory.append(f"Thought {iteration + 1}: {thought}")
            
            # Check completion
            if agent._is_task_complete(thought):
                answer = agent._extract_answer(thought)
                yield f"✅ {answer}"
                return
            
            # Action phase
            action_name = action.get('name', 'unknown')
            yield f"🎯 Thực hiện: {action_name}..."
            
            agent.memory.append(f"Action {iteration + 1}: {action}")
            
            # Execute
            observation = await agent._execute_action(action)
            agent.memory.append(f"Observation {iteration + 1}: {observation}")
            
            # Check success
            if agent._is_success(observation):
                yield "📝 Đang tạo câu trả lời..."
                final_answer = await agent._generate_final_response(task, observation)
                yield f"✅ {final_answer}"
                return
        
        yield "⚠️ Task phức tạp quá, cần nhiều thời gian hơn."


# Singleton
streaming_agent = StreamingAgent()

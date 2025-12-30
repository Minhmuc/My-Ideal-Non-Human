"""
LLM interface with function calling - ChatGPT style
"""
from core.models import minh_model
from core.vectorstore import search_similar, add_texts_to_vectorstore
from core.functions import FUNCTIONS, execute_function, parse_function_call
import re

def simple_generate(user_message: str, context: str = "", use_tools: bool = True) -> str:
    """Generate response với function calling support"""
    if use_tools:
        return minh_model.generate(user_message, context, tools=FUNCTIONS)
    else:
        return minh_model.generate(user_message, context)

async def ask_llm_with_memory(question: str) -> str:
    """
    Main entry point - ChatGPT style với function calling
    Hybrid: Model quyết định + keyword fallback
    """
    # 1. Search vector store for context
    try:
        results = search_similar(question, k=3)
        context = ""
        if results:
            context = "\n".join([doc.page_content for doc, _ in results[:2]])
    except:
        context = ""
    
    # 2. Hybrid detection: Force search for unknown entities
    q_lower = question.lower()
    
    # Check if asking about someone/something unknown
    if any(pattern in q_lower for pattern in ["là ai", "là gì", "ai là", "gì là"]):
        # Extract entity name (simple approach)
        words = question.split()
        entity = " ".join(words[:3])  # First few words usually contain the name
        
        from core.webSearch import search_duckduckgo
        search_results = search_duckduckgo(entity, num_results=2)
        
        if search_results:
            search_context = "\n".join([f"- {r}" for r in search_results])
            follow_up = f"Thông tin tìm được:\n{search_context}\n\nDựa vào thông tin trên, trả lời ngắn gọn: {question}"
            response = simple_generate(follow_up, context, use_tools=False)
            
            try:
                add_texts_to_vectorstore([f"Người dùng: {question}\nMINH: {response}"])
            except:
                pass
            
            return response
    
    # 3. Normal flow - model decides
    response = simple_generate(question, context, use_tools=True)
    
    # 4. Check if model wants to call a function
    function_call = parse_function_call(response)
    
    if function_call:
        function_name, arguments = function_call
        
        # Execute function
        function_result = execute_function(function_name, arguments)
        
        # Send result back to model for final response
        follow_up = f"Kết quả từ {function_name}: {function_result}\n\nCâu hỏi ban đầu: {question}"
        final_response = simple_generate(follow_up, context, use_tools=False)
        
        response = final_response
    
    # 5. Store conversation
    try:
        add_texts_to_vectorstore([f"Người dùng: {question}\nMINH: {response}"])
    except:
        pass
    
    return response

def provide_data_via_chat(user_input: str) -> str:
    """Allow user to provide data"""
    if user_input.lower().startswith(('dữ liệu:', 'data:')):
        data_content = user_input.split(':', 1)[-1].strip()
        if data_content:
            add_texts_to_vectorstore([data_content])
            return "Đã lưu dữ liệu của sếp!"
    return None

def provide_data_via_chat(user_input: str) -> str:
    """Allow user to provide data"""
    if user_input.lower().startswith(('dữ liệu:', 'data:')):
        data_content = user_input.split(':', 1)[-1].strip()
        if data_content:
            add_texts_to_vectorstore([data_content])
            return "Đã lưu dữ liệu của sếp!"
    return None

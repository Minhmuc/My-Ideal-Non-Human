from core.models import hf_model, tokenizer
import json
import re

async def detect_intent(question: str):
    """Phân loại intent: datetime, weather, search, hoặc normal"""
    try:
        system_prompt = """Bạn là bộ phân loại intent. Chỉ trả về JSON format:
{"intent": "datetime"} - hỏi giờ, ngày, thứ
{"intent": "weather"} - hỏi thời tiết, nhiệt độ
{"intent": "search"} - cần tra cứu web
{"intent": "normal"} - còn lại

Ví dụ:
"Mấy giờ rồi?" → {"intent": "datetime"}
"Thời tiết HN?" → {"intent": "weather"}
"Elon Musk là ai?" → {"intent": "search"}
"Bạn khỏe không?" → {"intent": "normal"}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Phân loại: {question}"}
        ]
        
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = tokenizer([text], return_tensors="pt").to(hf_model.device)
        
        outputs = hf_model.generate(
            **inputs,
            max_new_tokens=50,
            temperature=0.3,  # Giảm cho consistent
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        
        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        
        # Extract JSON
        match = re.search(r'\{.*?"intent"\s*:\s*"(\w+)".*?\}', response)
        if match:
            intent = match.group(1).lower()
            if intent in ["datetime", "weather", "search", "normal"]:
                return intent
        
        # Fallback: simple keyword matching
        q_lower = question.lower()
        if any(w in q_lower for w in ["giờ", "ngày", "thứ", "tháng", "năm", "hôm nay", "ngày mai"]):
            if any(w in q_lower for w in ["thời tiết", "nắng", "mưa", "nhiệt độ", "nóng", "lạnh"]):
                return "weather"
            return "datetime"
        elif any(w in q_lower for w in ["thời tiết", "nắng", "mưa", "nhiệt độ", "nóng", "lạnh", "gió", "bão"]):
            return "weather"
        elif any(w in q_lower for w in ["là ai", "là gì", "tìm kiếm", "google", "tra cứu", "tìm"]):
            return "search"
        
        return "normal"
        
    except Exception as e:
        print(f"[Intent Detector] Error: {e}")
        return "normal"
# async def main():
#     while True:
#         test = input("Nhập câu hỏi: ")
#         intent = await detect_intent(test)
#         print(f"Câu hỏi: {test} => Intent: {intent}")


# if __name__ == "__main__":
#     asyncio.run(main())

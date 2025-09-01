from langchain.prompts import ChatPromptTemplate
from core.models import model
import json
import re
import asyncio

intent_prompt = ChatPromptTemplate.from_template("""
Bạn là một bộ phân loại intent chính xác cho trợ lý AI cá nhân.
Nhiệm vụ: Phân loại câu hỏi dưới đây thành đúng MỘT trong 4 loại: "datetime", "weather", "search" hoặc "normal".

**Luật phân loại:**
- "datetime" → hỏi giờ, ngày, thứ, thời gian hiện tại hoặc múi giờ.
- "weather" → hỏi về thời tiết, nhiệt độ, mưa, nắng, bão, dự báo.
- "search" → yêu cầu tra cứu thông tin trên Google hoặc web.
- "normal" → tất cả trường hợp còn lại.

Câu hỏi: "{question}"

**Ví dụ:**
- "Mấy giờ rồi?" → datetime
- "Hôm nay là thứ mấy?" → datetime
- "Ngày bao nhiêu rồi?" → datetime
- "Giờ ở Tokyo là mấy giờ?" → datetime
- "Hẹn giờ giúp tôi" → datetime
- "Thời tiết Hà Nội hôm nay thế nào?" → weather
- "Dự báo mưa ở TP.HCM ngày mai?" → weather
- "Nhiệt độ hôm nay bao nhiêu?" → weather
- "Elon Musk là ai?" → search
- "Tỷ giá USD hôm nay?" → search
- "Mở nhạc đi" → normal
- "Bạn khỏe không?" → normal
- "Ngày mai tôi có bận không?" → normal
- "bây giờ là mấy giờ?" → datetime
- "bây giờ có nắng không?" → weather
Chỉ trả về JSON hợp lệ theo định dạng:
{{"intent": "<datetime|weather|search|normal>"}}
""")

async def detect_intent(question: str):
    try:
        chain = intent_prompt | model
        result = await chain.ainvoke({"question": question})
        # Kết quả có thể là string hoặc AIMessage → chuẩn hóa thành string
        if isinstance(result, str):
            text = result.strip()
        else:
            text = result.content.strip() if hasattr(result, "content") else str(result)

        # Trích phần JSON
        match = re.search(r'\{.*\}', text)
        if match:
            try:
                data = json.loads(match.group(0))
                return data.get("intent", "normal")
            except json.JSONDecodeError:
                return "normal"

        return "normal"

    except Exception as e:
        print(f"[Intent Detector] Lỗi: {e}")
        return "normal"


# async def main():
#     while True:
#         test = input("Nhập câu hỏi: ")
#         intent = await detect_intent(test)
#         print(f"Câu hỏi: {test} => Intent: {intent}")


# if __name__ == "__main__":
#     asyncio.run(main())

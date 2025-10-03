import asyncio
import time
from core.llm_interface import ask_llm_with_memory, provide_data_via_chat
from utils.tools import ensure_ollama_running
from core.prompt_engineering import exit_intent_confidence
from utils.tools import ensure_ollama_running
from core.prompts import get_prompt, exit_prompt, get_greeting

async def main():
    print("🤖 M.I.N.H: Powering Up...")
    # Đảm bảo Ollama daemon chạy (nếu Ollama được cài đặt)
    ok = ensure_ollama_running()
    if not ok:
        print("⚠️ Ollama không sẵn sàng hoặc không được cài đặt. Một số tính năng embedding có thể không hoạt động.")
    # Đảm bảo Ollama đang chạy (khởi động nếu cần)
    ollama_ok = ensure_ollama_running()
    if ollama_ok:
        print("✅ Ollama: started successfully")
    else:
        print("⚠️ Ollama không khả dụng. Một số tính năng embedding có thể không hoạt động.")

    greeting_message = get_greeting()
    print(f"🤖 M.I.N.H: {greeting_message}")

    while True:
        user_input = input("👤 Bạn: ")
        confidence = exit_intent_confidence(user_input)

        if confidence in ("cao"):
            confirm_quit = input(f"🤖 M.I.N.H: {(exit_prompt())} (y/n): ").strip().lower()
            if confirm_quit in ["y", "yes", "có"]:
                print(f"🤖 M.I.N.H: {get_prompt('end')}")
                break

        # Kiểm tra nếu người dùng cung cấp dữ liệu
        data_response = provide_data_via_chat(user_input)
        if data_response:
            print(f"🤖 M.I.N.H: {data_response}")
            continue

        start = time.time()
        print("🤖 M.I.N.H đang suy nghĩ...")
        response = await ask_llm_with_memory(user_input)
        #time
        end = time.time()
        print(f"🤖 M.I.N.H: {response}")
        print(f"⏳Thời gian xử lý: {end - start:.2f} giây")

if __name__ == "__main__":
    asyncio.run(main())
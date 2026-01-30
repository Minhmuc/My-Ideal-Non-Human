import asyncio
import time
from core.llm_interface import ask_llm_with_memory, provide_data_via_chat
from core.prompts import get_prompt, exit_prompt, get_greeting

async def main():
    print("🤖 M.I.N.H: Powering Up...")
    print("✅ Function calling enabled (ChatGPT style)")

    greeting_message = get_greeting()
    print(f"🤖 M.I.N.H: {greeting_message}")

    while True:
        user_input = input("👤 Bạn: ")
        
        # Simple exit detection
        if user_input.lower() in ["thoát", "exit", "quit", "bye", "tạm biệt"]:
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
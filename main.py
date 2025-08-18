from core.llm_interface import ask_llm_with_memory, provide_data_via_chat
from core.memory import ConversationBufferMemory
from core.prompt_engineering import exit_intent_confidence
from core.prompts import get_prompt,exit_prompt, get_greeting

if __name__ == "__main__":
    print("🤖 M.I.N.H: Powering Up...")
    memory = ConversationBufferMemory()
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
        data_response = provide_data_via_chat(user_input, memory)
        if data_response:
            print(f"🤖 M.I.N.H: {data_response}")
            continue
        print("🤖M.I.N.H đang suy nghĩ...")
        response = ask_llm_with_memory(user_input, memory)
        print(f"🤖 M.I.N.H: {response}")
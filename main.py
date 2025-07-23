from core.llm_interface import ask_llm_with_memory
from core.memory import ConversationBufferMemory
from core.prompt_engineering import clean_input, exit_intent, confirm_message
from core.prompts import get_prompt

if __name__ == "__main__":
    memory = ConversationBufferMemory()
    greeting_message = get_prompt("greeting")
    print(f"🤖 M.I.N.H: {greeting_message}")
    while True:
        user_input = input("👤 Bạn: ")
        if exit_intent(user_input):
            confirm_quit = input(f"🤖 M.I.N.H: {confirm_message} (y/n): ").strip().lower()
            if confirm_quit in ["y", "yes", "có"]:
                print(f"🤖 M.I.N.H: {get_prompt('end')}")
                break
        user_input = clean_input(user_input)
        print("🤖M.I.N.H đang suy nghĩ...")
        response = ask_llm_with_memory(user_input,memory)
        print(f"🤖 M.I.N.H: {response}")
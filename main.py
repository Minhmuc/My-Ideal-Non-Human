from core.llm_interface import ask_llm_with_memory
from core.memory import ConversationBufferMemory
from core.prompt_engineering import clean_input, is_exit_input
from core.prompts import get_prompt

if __name__ == "__main__":
    memory = ConversationBufferMemory()
    while True:
        user_input = input("👤 Bạn: ")
        if is_exit_input(user_input):
            print(f"🤖 M.I.N.H: {get_prompt('end')}")
            break
        user_input = clean_input(user_input)
        print("🤖M.I.N.H đang suy nghĩ...")
        response = ask_llm_with_memory(user_input,memory)
        print(f"🤖 M.I.N.H: {response}")
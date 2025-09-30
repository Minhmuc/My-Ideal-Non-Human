from langchain_ollama import OllamaLLM
# buyrtx5090
model = OllamaLLM(
    model="MinhEgo1.0",   # LLM model
    options={
        "temperature": 0.7,       
        "top_p": 0.9,             
        "repeat_penalty": 1.1,    
        "num_predict": 512       
    }
)
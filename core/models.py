from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from langchain_huggingface import HuggingFacePipeline
import torch
import warnings
warnings.filterwarnings('ignore')

# Import system prompt từ config (giống Modelfile)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.model_config import MINH_SYSTEM_PROMPT, GENERATION_CONFIG

# star pls!
print("🤖 Loading Qwen2.5-7B-Instruct model (4-bit optimized for 6GB VRAM)...")
print("⏳ First load takes 3-5 minutes. Please wait...")

# Model 7B cho responses tốt hơn
model_name = "Qwen/Qwen2.5-7B-Instruct"

# Cấu hình 4-bit quantization tối ưu
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,  # Nested quantization để tiết kiệm thêm VRAM
)

# Load model with optimized settings
hf_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
    low_cpu_mem_usage=True,
    max_memory={0: "5.5GB", "cpu": "16GB"}  # Reserve 0.5GB cho system
)
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

# Wrapper class để "tiêm" system prompt vào model - giống Ollama Modelfile
class MINHModel:
    """
    Wrapper cho Qwen model với system prompt built-in
    Giống như Ollama's Modelfile: System prompt được 'bake' vào model
    """
    def __init__(self, base_model, tokenizer, system_prompt):
        self.model = base_model
        self.tokenizer = tokenizer
        self.system_prompt = system_prompt
        self.device = base_model.device
        
    def generate(self, user_message: str, context: str = "", tools: list = None) -> str:
        """Generate với system prompt tự động - hỗ trợ function calling"""
        if context:
            user_content = f"Thông tin: {context}\n\nCâu hỏi: {user_message}"
        else:
            user_content = user_message
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        # Apply chat template với tools nếu có
        if tools:
            text = self.tokenizer.apply_chat_template(
                messages, 
                tools=tools,
                tokenize=False, 
                add_generation_prompt=True
            )
        else:
            text = self.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
        
        inputs = self.tokenizer([text], return_tensors="pt").to(self.device)
        
        outputs = self.model.generate(
            **inputs,
            **GENERATION_CONFIG,
            pad_token_id=self.tokenizer.eos_token_id,
            eos_token_id=self.tokenizer.eos_token_id
        )
        
        response = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        
        # Post-process: Clean up response
        import re
        # Remove role prefixes like [minh]:, [MINH]:, minh:, etc.
        response = re.sub(r'^\s*\[?\s*minh\s*\]?\s*:\s*', '', response, flags=re.IGNORECASE)
        # Remove Chinese characters và các dấu ngoặc đơn/Chinese punctuation thừa
        response = re.sub(r'[\u4e00-\u9fff\u3000-\u303f]+', '', response)
        response = re.sub(r'[（）【】]+', '', response)  # Remove Chinese brackets
        response = response.replace('！', '!').replace('？', '?')  # Replace fullwidth to halfwidth
        
        return response.strip()

# Tạo MINH model instance với system prompt "baked in"
minh_model = MINHModel(hf_model, tokenizer, MINH_SYSTEM_PROMPT)

# Create text generation pipeline với parameters tối ưu cho chat ngắn gọn
pipe = pipeline(
    "text-generation",
    model=hf_model,
    tokenizer=tokenizer,
    max_new_tokens=256,  # Giảm để tránh responses quá dài
    temperature=0.8,  # Tăng một chút cho tự nhiên hơn
    top_p=0.85,
    repetition_penalty=1.15,  # Tăng để tránh lặp lại
    do_sample=True,
    pad_token_id=tokenizer.eos_token_id  # Fix padding warning
)


# Wrap in LangChain compatible interface
model = HuggingFacePipeline(pipeline=pipe)

print("✅ Model loaded successfully!")
print(f"📊 Model: {model_name}")
print(f"🎮 Device: {hf_model.device}")
print(f"💾 VRAM: ~4.5GB (4-bit quantized)")
print(f"🎭 System Prompt: Loaded from config/model_config.py (Modelfile-style)")

# Export để dùng trực tiếp
__all__ = ['model', 'hf_model', 'tokenizer', 'pipe', 'minh_model']
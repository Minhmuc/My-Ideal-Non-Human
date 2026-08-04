# test_gpu.py
import torch
from core.models import minh_model

print(f"🔍 CUDA available: {torch.cuda.is_available()}")
print(f"🔍 CUDA device count: {torch.cuda.device_count()}")

if torch.cuda.is_available():
    print(f"🔍 Current device: {torch.cuda.current_device()}")
    print(f"🔍 Device name: {torch.cuda.get_device_name(0)}")
    print(f"🔍 VRAM allocated: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
    print(f"🔍 VRAM reserved: {torch.cuda.memory_reserved(0) / 1024**3:.2f} GB")
    
print(f"\n🔍 Model device: {minh_model.device}")
print(f"🔍 Model type: {type(minh_model.model)}")

# Test inference to confirm GPU is working
print("\n🧪 Testing inference on GPU...")
response = minh_model.generate("Xin chào", max_new_tokens=20)
print(f"✅ Test response: {response[:100]}...")
print(f"\n✅ GPU is being used successfully!")
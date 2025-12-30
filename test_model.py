"""
Test script để verify Qwen2.5-7B-Instruct load thành công với 4-bit quantization
"""
import sys
print("🧪 Testing Hugging Face Transformers setup...")
print(f"Python: {sys.version}")

# Test CUDA
import torch
print(f"\n🎮 CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   Device: {torch.cuda.get_device_name(0)}")
    print(f"   VRAM Total: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

# Test load model
print("\n📦 Loading model from core.models...")
try:
    from core.models import model, hf_model
    print("✅ Model loaded successfully!")
    
    # Test inference
    print("\n💬 Testing inference...")
    test_prompt = "Xin chào! Bạn là ai?"
    response = model.invoke(test_prompt)
    print(f"\nPrompt: {test_prompt}")
    print(f"Response: {response}")
    
    # Check VRAM usage
    if torch.cuda.is_available():
        print(f"\n📊 VRAM usage: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
        print(f"   VRAM reserved: {torch.cuda.memory_reserved(0) / 1024**3:.2f} GB")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

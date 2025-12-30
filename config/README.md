# MINH Model Configuration

## 🎯 Cấu trúc giống Ollama Modelfile

Thay vì viết prompt trong code như trước, giờ MINH sử dụng **Modelfile-style configuration**:

```
Ollama Modelfile          →    MINH Config
─────────────────              ──────────────
FROM llama3.1:8b          →    models.py (Qwen2.5-3B)
PARAMETER temperature     →    config/model_config.py
PARAMETER top_p           →    config/model_config.py
SYSTEM "..."              →    config/model_config.py
```

## 📁 File Structure

```
config/
  └── model_config.py          # ← System prompt & parameters (như Modelfile)
      ├── MINH_SYSTEM_PROMPT   # Personality, rules, creator info
      └── GENERATION_CONFIG     # Temperature, top_p, max_tokens

core/
  └── models.py                # ← Model wrapper với prompt "baked in"
      └── MINHModel class      # Auto-inject system prompt mỗi lần generate
```

## 🔧 Cách hoạt động

### Trước (Prompt trong code):
```python
# ❌ Prompt bị scatter khắp nơi
def generate(msg):
    system = "Bạn là MINH..."  # Hardcoded trong function
    messages = [{"role": "system", "content": system}, ...]
```

### Sau (Prompt trong config - giống Ollama):
```python
# ✅ Prompt được "tiêm" vào model level
from core.models import minh_model

# System prompt tự động apply
response = minh_model.generate("Xin chào")  
```

## 📝 Để thay đổi personality

**Chỉ cần sửa 1 file:** `config/model_config.py`

```python
# config/model_config.py
MINH_SYSTEM_PROMPT = """
Bạn là MINH...
[Thay đổi personality ở đây]
Người tạo ra bạn là...
"""

GENERATION_CONFIG = {
    "temperature": 0.9,  # Điều chỉnh parameters
    "top_p": 0.9,
    ...
}
```

## 🎭 So sánh với Ollama

| Aspect | Ollama Modelfile | MINH Config |
|--------|------------------|-------------|
| **System Prompt** | `SYSTEM "..."` | `MINH_SYSTEM_PROMPT` |
| **Parameters** | `PARAMETER temperature` | `GENERATION_CONFIG` |
| **Location** | `Modelfile` | `config/model_config.py` |
| **Apply** | `ollama create` | Import `minh_model` |
| **Modify** | Edit Modelfile → recreate | Edit config → reload |

## ✅ Advantages

1. **Centralized**: Tất cả config ở 1 nơi
2. **Clean Code**: Không có prompt hardcoded
3. **Easy Modify**: Chỉ sửa config file
4. **Version Control**: Track prompt changes qua Git
5. **Consistent**: System prompt luôn đồng nhất

## 🚀 Usage

```python
# Trong code, chỉ cần:
from core.models import minh_model

# System prompt tự động inject
answer = minh_model.generate("Bạn là ai?")
# → "Tôi là MINH, được tạo bởi Nguyễn Quang Minh..."
```

---

**🎉 Giờ MINH hoạt động giống Ollama: Prompt được "bake" vào model level!**

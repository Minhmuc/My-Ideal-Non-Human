# M.I.N.H – My Ideal Non-Human  

[English](#english) | [Tiếng Việt](#tiếng-việt)

---

<a name="english"></a>
## 🇬🇧 English

M.I.N.H (My Ideal Non-Human) is a Vietnamese personal AI assistant running entirely offline on local hardware with GPU acceleration.  
A smart, confident, and witty AI that calls you "sếp" (boss), supports Vietnamese sovereignty, and helps with daily tasks like chatting, searching information, and remembering content.

---

### ✨ Features

- **Smart Chat**: Natural conversations with context awareness
- **Long-term Memory**: ChromaDB vectorstore for conversation history
- **Web Search**: Integrated DuckDuckGo search
- **Real-time Data**: Weather and datetime information
- **Desktop App**: Beautiful Copilot-like interface built with Electron
- **Offline**: Runs completely local, no cloud required

---

### 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| **LLM** | Qwen2.5-3B-Instruct (Hugging Face) |
| **Function Calling** | ChatGPT-style tool usage |
| **Framework** | Transformers + bitsandbytes |
| **Embeddings** | BGE-M3 (sentence-transformers) |
| **Vector DB** | ChromaDB |
| **Backend** | FastAPI + Uvicorn |
| **Frontend** | React + Vite + Tailwind CSS |
| **Desktop** | Electron |
| **Quantization** | 4-bit NF4 |
| **GPU** | CUDA 12.4 (PyTorch) |

---

### 📋 Prerequisites

#### Hardware
- **GPU**: NVIDIA GPU with 4-6GB VRAM (recommended)
  - Can run on CPU but **VERY SLOW**
  - RTX 3050/3060/4060 or equivalent AMD GPU
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: ~10GB for models and dependencies

#### Software
- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher (for Desktop app)
- **CUDA**: 12.1+ (auto-installed with PyTorch)
- **Git**: For cloning repository

---

### 🚀 Installation

#### 1. Clone Repository
```bash
git clone https://github.com/Minhmuc/My-Ideal-Non-Human.git
cd My-Ideal-Non-Human
```

#### 2. Setup Python Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

#### 3. Test Backend
```bash
# Test model load
python -c "from core.models import minh_model; print('Model OK!')"

# Test embeddings
python -c "from core.vectorstore import embedding_model; print('Embeddings OK!')"

# Start API server
python -m uvicorn api_server:app --host 127.0.0.1 --port 8000
```

Visit: http://127.0.0.1:8000/docs for API documentation

#### 4. Setup Desktop App (Optional)
```bash
cd desktop
npm install
npm run dev
```

---

### 🎮 Usage

#### Option 1: Console Mode
```bash
python main.py
```

#### Option 2: Desktop App (Recommended)
```bash
# Auto-launch
start_desktop.bat

# Or manual
# Terminal 1: Backend
start_backend_only.bat

# Terminal 2: Frontend
cd desktop
npm run dev
```

#### Option 3: API Mode
```bash
python -m uvicorn api_server:app --host 127.0.0.1 --port 8000 --reload
```

---

### ⚙️ Configuration

#### Change LLM Model
Edit [core/models.py](core/models.py):
```python
# Smaller model (for 4GB GPU)
model_name = "Qwen/Qwen2.5-1.5B-Instruct"

# Larger model (needs 8GB+ VRAM)
model_name = "Qwen/Qwen2.5-7B-Instruct"

# Vietnamese native
model_name = "Viet-Mistral/Vistral-7B-Chat"
```

#### Change Embedding Model
Edit [core/vectorstore.py](core/vectorstore.py):
```python
# Current: BGE-M3 (best multilingual)
model_name = "BAAI/bge-m3"

# Alternative: Lighter model
model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

#### Customize System Prompt
Edit [config/model_config.py](config/model_config.py) to change MINH's personality.

---

### 🎯 Roadmap

- [x] Smart AI chat interface
- [x] Long-term memory with vectorstore
- [x] Web search integration
- [x] Real-time data (weather, datetime)
- [x] Desktop application with Electron
- [x] FastAPI backend with WebSocket
- [ ] Voice input/output
- [ ] System tray integration
- [ ] File upload and analysis
- [ ] Plugin system

---

### 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

### 📜 License

MIT License - See [LICENSE](LICENSE)

---

### 💬 Contact

- GitHub: [@Minhmuc](https://github.com/Minhmuc)
- Issues: [GitHub Issues](https://github.com/Minhmuc/My-Ideal-Non-Human/issues)

---

**⭐ If you find this useful, please star the repo! ⭐**

---
---

<a name="tiếng-việt"></a>
## 🇻🇳 Tiếng Việt

M.I.N.H (My Ideal Non-Human) là trợ lý AI cá nhân của Việt Nam chạy hoàn toàn offline trên máy local với GPU.  
Một AI thông minh, tự tin và hài hước, xưng hô "sếp" với người dùng, bảo vệ chủ quyền Việt Nam, hỗ trợ các tác vụ hàng ngày như trò chuyện, tìm kiếm thông tin và ghi nhớ nội dung.

---

### ✨ Tính năng

- **Chat thông minh**: Trò chuyện tự nhiên với khả năng hiểu ngữ cảnh
- **Bộ nhớ dài hạn**: ChromaDB vectorstore lưu trữ lịch sử hội thoại
- **Tìm kiếm web**: Tích hợp DuckDuckGo search
- **Dữ liệu thời gian thực**: Thông tin thời tiết và ngày giờ
- **Desktop App**: Giao diện đẹp mắt giống Copilot với Electron
- **Offline**: Chạy hoàn toàn local, không cần cloud

---

### 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| **LLM** | Qwen2.5-3B-Instruct (Hugging Face) |
| **Function Calling** | ChatGPT-style tool usage |
| **Framework** | Transformers + bitsandbytes |
| **Embeddings** | BGE-M3 (sentence-transformers) |
| **Vector DB** | ChromaDB |
| **Backend** | FastAPI + Uvicorn |
| **Frontend** | React + Vite + Tailwind CSS |
| **Desktop** | Electron |
| **Quantization** | 4-bit NF4 |
| **GPU** | CUDA 12.4 (PyTorch) |

---

### 📋 Yêu cầu hệ thống

#### Hardware
- **GPU**: NVIDIA GPU với 4-6GB VRAM (khuyến nghị)
  - Model chạy được trên CPU nhưng **CỰC CHẬM**
  - RTX 3050/3060/4060 hoặc AMD GPU tương đương
- **RAM**: 8GB tối thiểu (16GB khuyến nghị)
- **Storage**: ~10GB cho models và dependencies

#### Software
- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.11 trở lên
- **Node.js**: 18.x trở lên (cho Desktop app)
- **CUDA**: 12.1+ (tự động cài với PyTorch)
- **Git**: Để clone repository

---

### 🚀 Cài đặt

#### 1. Clone Repository
```bash
git clone https://github.com/Minhmuc/My-Ideal-Non-Human.git
cd My-Ideal-Non-Human
```

#### 2. Setup Python Environment
```bash
# Tạo virtual environment
python -m venv .venv

# Activate
.venv\Scripts\activate  # Windows

# Cài dependencies
pip install -r requirements.txt

# Cài PyTorch với CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

#### 3. Test Backend
```bash
# Test model load
python -c "from core.models import minh_model; print('Model OK!')"

# Test embeddings
python -c "from core.vectorstore import embedding_model; print('Embeddings OK!')"

# Khởi động API server
python -m uvicorn api_server:app --host 127.0.0.1 --port 8000
```

Truy cập: http://127.0.0.1:8000/docs để xem API documentation

#### 4. Setup Desktop App (Optional)
```bash
cd desktop
npm install
npm run dev
```

---

### 🎮 Cách sử dụng

#### Option 1: Console Mode
```bash
python main.py
```

#### Option 2: Desktop App (Khuyến nghị)
```bash
# Tự động
start_desktop.bat

# Hoặc manual
# Terminal 1: Backend
start_backend_only.bat

# Terminal 2: Frontend
cd desktop
npm run dev
```

#### Option 3: API Mode
```bash
python -m uvicorn api_server:app --host 127.0.0.1 --port 8000 --reload
```

---

### ⚙️ Cấu hình

#### Đổi Model LLM
Edit [core/models.py](core/models.py):
```python
# Model nhỏ hơn (cho GPU 4GB)
model_name = "Qwen/Qwen2.5-1.5B-Instruct"

# Model to hơn (cần 8GB+ VRAM)
model_name = "Qwen/Qwen2.5-7B-Instruct"

# Tiếng Việt native
model_name = "Viet-Mistral/Vistral-7B-Chat"
```

#### Đổi Embedding Model
Edit [core/vectorstore.py](core/vectorstore.py):
```python
# Hiện tại: BGE-M3 (đa ngôn ngữ tốt nhất)
model_name = "BAAI/bge-m3"

# Alternative: Model nhẹ hơn
model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

#### Thay đổi System Prompt
Edit [config/model_config.py](config/model_config.py) để thay đổi tính cách của MINH.

---

### 🎯 Roadmap

- [x] Giao diện chat AI thông minh
- [x] Bộ nhớ dài hạn với vectorstore
- [x] Tích hợp tìm kiếm web
- [x] Dữ liệu thời gian thực (thời tiết, ngày giờ)
- [x] Desktop application với Electron
- [x] FastAPI backend với WebSocket
- [ ] Voice input/output
- [ ] System tray integration
- [ ] Upload và phân tích file
- [ ] Hệ thống plugin

---

### 🤝 Đóng góp

Pull requests luôn được chào đón! Với thay đổi lớn, vui lòng tạo issue trước.

---

### 📜 License

MIT License - Xem [LICENSE](LICENSE)

---

### 💬 Contact

- GitHub: [@Minhmuc](https://github.com/Minhmuc)
- Issues: [GitHub Issues](https://github.com/Minhmuc/My-Ideal-Non-Human/issues)

---

**⭐ Nếu thấy hữu ích, hãy star repo nhé! ⭐**

# M.I.N.H – My Ideal Non-Human  

M.I.N.H (My Ideal Non-Human) is a personal AI assistant designed to run locally.  
It combines natural conversation, real-time information, memory, and computer control to provide a personalized and extensible experience.  

## ✨ Features  
- **Conversational AI**: Natural, context-aware chat powered by local LLMs.  
- **Memory System**: Stores and recalls past interactions to maintain continuity.  
- **Real-Time Data**: Fetches current time, date, and weather with integrated APIs.  
- **Vector Search**: Retrieves relevant information from custom knowledge bases.  
- **Computer Autopilot (in progress)**: Real-time control over the computer environment.  
- **Custom Personality**: MINH learns and adapts to match the user’s style.  

## 🛠 Tech Stack  
- **LLM**: [Ollama](https://ollama.com) with models such as `LLaMA 3.1 8B` or custom fine-tuned versions.  
- **LangChain**: Orchestration, memory, and tool integration.  
- **Python**: Core logic and API handling.  
- **Vectorstore**: For semantic search and knowledge retrieval.  
- **APIs**: Open-Meteo, OpenStreetMap (real-time weather & location data).  

## 🚀 Getting Started  

### Prerequisites  
- Python 3.10+  
- [Ollama](https://ollama.com) installed and running  
- Virtual environment (recommended)  

### Installation  
```bash
# Clone repository
git clone https://github.com/Minhmuc/My-Ideal-Non-Human.git
cd My-Ideal-Non-Human

# Create virtual environment
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Run MINH  
```bash
python main.py
```

## ⚙️ Configuration  
- **Model Selection**: Update `core/models.py` to change Ollama LLM (e.g., `llama3.1:8b` or custom model).  
- **Thresholds**: Configure similarity thresholds in `vectorstore` for more precise retrieval.  
- **APIs**: Add or adjust API keys/settings in `data/realtime_data.py`.  

## 📌 Roadmap  
- ✔️ Conversational core with memory  
- ✔️ Real-time weather & datetime  
- ✔️ Vector search integration  
- [ ] Real-time computer autopilot  
- [ ] Speech-to-Text & Text-to-Speech  
- [ ] Graphical interface  

## 🤝 Contribution  
Pull requests and suggestions are welcome. Feel free to fork and extend MINH with your own personality and tools.  

## 📜 License  
This project is licensed under the MIT License.
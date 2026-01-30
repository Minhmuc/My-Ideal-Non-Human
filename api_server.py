from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import time
import sys
import io
from core.llm_interface import ask_llm_with_memory
from core.agents.streaming_agent import streaming_agent

# Enable UTF-8 for console output (supports emoji and Vietnamese)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

app = FastAPI()

# Enable CORS for Electron app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    processing_time: float

@app.on_event("startup")
async def startup_event():
    """Initialize on server startup"""
    print("🚀 Starting MINH API Server...")
    print("⏳ Model sẽ được load khi có request đầu tiên (lazy loading)")
    print("✅ Server ready at http://127.0.0.1:8000")
    # Note: Model loaded on first request to save startup time

@app.get("/")
async def root():
    return {"status": "MINH API Server is running", "version": "1.0"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Standard chat endpoint - returns full response"""
    start = time.time()
    
    # Use AI Agent (no more hardcode!)
    response = await ask_llm_with_memory(request.message)
    end = time.time()
    
    return ChatResponse(response=response, processing_time=end - start)

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for streaming responses - Now with real-time AI Agent progress!"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            if not message:
                continue
            
            # Stream AI Agent progress real-time
            start = time.time()
            
            async for update in streaming_agent.process_stream(message):
                # Send each progress update
                await websocket.send_json({
                    "type": "chunk",
                    "chunk": update + "\n"
                })
                await asyncio.sleep(0.01)  # Small delay for smooth streaming
            
            end = time.time()
            
            # Send completion signal
            await websocket.send_json({
                "type": "complete",
                "processing_time": end - start
            })
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        import traceback
        traceback.print_exc()
        await websocket.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MINH"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

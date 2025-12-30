from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import time
import sys
import io
from core.llm_interface_simple import ask_llm_with_memory, provide_data_via_chat

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
    
    # Check if user is providing data
    data_response = provide_data_via_chat(request.message)
    if data_response:
        end = time.time()
        return ChatResponse(response=data_response, processing_time=end - start)
    
    # Get LLM response
    response = await ask_llm_with_memory(request.message)
    end = time.time()
    
    return ChatResponse(response=response, processing_time=end - start)

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for streaming responses"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            if not message:
                continue
            
            # Send status: processing
            await websocket.send_json({"type": "status", "status": "processing"})
            
            # Check if user is providing data
            data_response = provide_data_via_chat(message)
            if data_response:
                # Send complete response for data provision
                await websocket.send_json({
                    "type": "complete",
                    "response": data_response
                })
                continue
            
            # Get LLM response
            start = time.time()
            response = await ask_llm_with_memory(message)
            end = time.time()
            
            # Stream response character by character
            for char in response:
                await websocket.send_json({
                    "type": "chunk",
                    "chunk": char
                })
                await asyncio.sleep(0.03)  # 30ms delay to match frontend
            
            # Send completion signal
            await websocket.send_json({
                "type": "complete",
                "processing_time": end - start
            })
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MINH"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

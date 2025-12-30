import React, { useState, useEffect, useRef } from 'react'

function Greeting() {
  const hour = new Date().getHours()
  let part = 'Chào'
  if (hour >= 18) part = 'Chào buổi tối'
  else if (hour >= 12) part = 'Chào buổi chiều'
  else if (hour >= 5) part = 'Chào buổi sáng'
  return (
    <div className="text-center">
      <h2 className="text-3xl md:text-4xl font-semibold">{part}, Sếp!</h2>
      <p className="text-gray-300 mt-2 text-lg">LiemDai.AI Here!</p>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-5 py-3">
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
    </div>
  )
}

function StreamingText({ text, speed = 30, onComplete, shouldStop, onStop }) {
  const [displayText, setDisplayText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)
  const stoppedRef = useRef(false)
  const timerRef = useRef(null)

  // Reset when text changes (new message)
  useEffect(() => {
    stoppedRef.current = false
    setDisplayText('')
    setCurrentIndex(0)
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }
  }, [text])

  // Handle stop signal - cancel timer immediately
  useEffect(() => {
    if (shouldStop && !stoppedRef.current) {
      stoppedRef.current = true
      if (timerRef.current) {
        clearTimeout(timerRef.current)
        timerRef.current = null
      }
      if (onStop) onStop(displayText) // Return partial text
      if (onComplete) onComplete()
    }
  }, [shouldStop, onComplete, onStop, displayText])

  // Streaming logic
  useEffect(() => {
    if (stoppedRef.current) return

    if (currentIndex < text.length) {
      timerRef.current = setTimeout(() => {
        if (!stoppedRef.current) {
          setDisplayText((prev) => prev + text[currentIndex])
          setCurrentIndex((prev) => prev + 1)
        }
      }, speed)
      
      return () => {
        if (timerRef.current) {
          clearTimeout(timerRef.current)
        }
      }
    } else if (currentIndex === text.length && onComplete) {
      onComplete()
    }
  }, [currentIndex, text, speed, onComplete])

  return <p className="text-sm leading-relaxed">{displayText}{currentIndex < text.length && !stoppedRef.current && <span className="animate-pulse">▋</span>}</p>
}

export default function App() {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [shouldStopStreaming, setShouldStopStreaming] = useState(false)
  const [isThinking, setIsThinking] = useState(false)
  const partialTextRef = useRef('')
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Auto-start backend when app loads
    startBackend()
  }, [])

  const startBackend = async () => {
    if (window.minh) {
      const res = await window.minh.startPython()
      console.log('Khởi động backend:', res)
    }
  }

  const onSend = async () => {
    if (!query.trim() || isStreaming) return
    const userMessage = query
    setMessages((prev) => [...prev, { role: 'user', text: userMessage, streaming: false }])
    setQuery('')
    setIsStreaming(true)
    setShouldStopStreaming(false)
    setIsThinking(true)
    
    try {
      // Connect to WebSocket
      const ws = new WebSocket('ws://127.0.0.1:8000/ws/chat')
      let responseText = ''
      
      ws.onopen = () => {
        // Send message to backend
        ws.send(JSON.stringify({ message: userMessage }))
      }
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        
        if (data.type === 'chunk') {
          // Tắt thinking indicator khi nhận chunk đầu tiên
          if (isThinking) {
            setIsThinking(false)
          }
          // Append character to response
          responseText += data.chunk
          // Update or create message
          setMessages((prev) => {
            const newMessages = [...prev]
            const lastMsg = newMessages[newMessages.length - 1]
            if (lastMsg && lastMsg.role === 'minh' && lastMsg.streaming) {
              lastMsg.text = responseText
            } else {
              newMessages.push({ role: 'minh', text: responseText, streaming: true })
            }
            return newMessages
          })
        } else if (data.type === 'complete') {
          // Streaming complete
          if (data.processing_time) {
            console.log(`⏳ Thời gian xử lý: ${data.processing_time.toFixed(2)} giây`)
            // Optionally add processing time to message
            setMessages((prev) => {
              const newMessages = [...prev]
              const lastMsg = newMessages[newMessages.length - 1]
              if (lastMsg && lastMsg.role === 'minh') {
                lastMsg.processingTime = data.processing_time
              }
              return newMessages
            })
          }
          ws.close()
          handleStreamComplete()
        } else if (data.type === 'status') {
          console.log('Status:', data.status)
        }
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsThinking(false)
        setMessages((prev) => [...prev, { 
          role: 'minh', 
          text: 'Lỗi kết nối với backend. Vui lòng kiểm tra lại.', 
          streaming: false 
        }])
        setIsStreaming(false)
      }
      
      ws.onclose = () => {
        console.log('WebSocket closed')
      }
      
      // Store ws for stop functionality
      window.currentWS = ws
      
    } catch (error) {
      console.error('Error:', error)
      setIsThinking(false)
      setMessages((prev) => [...prev, { 
        role: 'minh', 
        text: 'Đã xảy ra lỗi. Vui lòng thử lại.', 
        streaming: false 
      }])
      setIsStreaming(false)
    }
  }

  const onStopStreaming = (partialText) => {
    // This is called from StreamingText when stop is triggered
    // Just save the partial text, don't update messages yet
    partialTextRef.current = partialText || ''
  }

  const handleStopButton = () => {
    // Close WebSocket connection
    if (window.currentWS) {
      window.currentWS.close()
      window.currentWS = null
    }
    setShouldStopStreaming(true)
    setIsStreaming(false)
  }

  const handleStreamComplete = () => {
    setIsStreaming(false)
    setShouldStopStreaming(false)
    
    // Update message: if stopped, use partial text
    setMessages((prev) => {
      const newMessages = [...prev]
      const lastMsg = newMessages[newMessages.length - 1]
      if (lastMsg && lastMsg.streaming) {
        if (partialTextRef.current) {
          lastMsg.text = partialTextRef.current
          partialTextRef.current = ''
        }
        lastMsg.streaming = false
      }
      return newMessages
    })
  }

  return (
    <div className="h-screen bg-transparent text-white flex flex-col">
      <header className="flex items-center justify-between px-6 py-4 border-b border-white/5 backdrop-blur-md bg-black/20">
        <div className="flex items-center gap-3">
          <img src="/favicon.ico" alt="MINH" className="w-9 h-9 rounded" />
          <div className="text-lg font-medium">MINH</div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={startBackend} className="px-3 py-1 bg-cyan-500 text-white rounded text-sm hover:bg-cyan-600">
            🚀 Start Backend
          </button>
          <button className="px-3 py-1 bg-transparent border border-slate-700 rounded text-sm hover:bg-slate-800">
            ⚙️ Cài đặt
          </button>
        </div>
      </header>

      <main className="flex-1 overflow-auto px-6 py-8 flex flex-col">
        {messages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center max-w-3xl mx-auto w-full">
            <div className="text-center mb-8">
              <Greeting />
            </div>
            
            {/* Input ở giữa khi chưa chat */}
            <div className="w-full mb-6">
              <div className="relative">
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Hỏi gì đó..."
                  className="w-full rounded-3xl py-4 px-6 pr-16 text-base bg-white/10 text-white placeholder-slate-400 border border-white/20 focus:outline-none focus:border-cyan-400/50"
                  onKeyDown={(e) => e.key === 'Enter' && !isStreaming && onSend()}
                  disabled={isStreaming}
                />
                <button 
                  onClick={onSend}
                  disabled={isStreaming || !query.trim()}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-full bg-cyan-500 text-white hover:bg-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Quick action buttons */}
            <div className="flex flex-wrap gap-3 justify-center">
              <button 
                onClick={() => setQuery("Viết một đoạn văn về...")}
                className="px-4 py-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-sm text-white transition"
              >
                ✍️ Viết văn bản
              </button>
              <button 
                onClick={() => setQuery("Tôi cần lời khuyên về...")}
                className="px-4 py-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-sm text-white transition"
              >
                💡 Lời khuyên
              </button>
              <button 
                onClick={() => setQuery("Giải thích cho tôi về...")}
                className="px-4 py-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-sm text-white transition"
              >
                📚 Học hỏi
              </button>
              <button 
                onClick={() => setQuery("Lập kế hoạch cho...")}
                className="px-4 py-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-sm text-white transition"
              >
                📋 Lập kế hoạch
              </button>
            </div>
          </div>
        ) : (
          <div className="flex-1 max-w-4xl mx-auto w-full space-y-6 pb-4">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] ${msg.role === 'user' ? '' : 'w-full'}`}>
                  <div className={`rounded-2xl px-5 py-3 ${
                    msg.role === 'user' 
                      ? 'bg-cyan-500 text-white' 
                      : 'bg-white/5 text-white border border-white/10'
                  }`}>
                    {msg.streaming ? (
                      <p className="text-sm leading-relaxed">
                        {msg.text}
                        {i === messages.length - 1 && <span className="animate-pulse">▋</span>}
                      </p>
                    ) : (
                      <>
                        <p className="text-sm leading-relaxed">{msg.text}</p>
                        {msg.processingTime && msg.role === 'minh' && (
                          <p className="text-xs text-gray-400 mt-2">
                            ⏳ {msg.processingTime.toFixed(2)}s
                          </p>
                        )}
                      </>
                    )}
                  </div>
                  
                  {/* Action buttons chỉ cho message của MINH */}
                  {msg.role === 'minh' && !msg.streaming && (
                    <div className="flex items-center gap-2 mt-2 ml-2">
                      <button className="p-1.5 rounded hover:bg-white/5 text-gray-400 hover:text-white transition" title="Thích">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                        </svg>
                      </button>
                      <button className="p-1.5 rounded hover:bg-white/5 text-gray-400 hover:text-white transition" title="Không thích">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
                        </svg>
                      </button>
                      <button 
                        onClick={() => navigator.clipboard.writeText(msg.text)}
                        className="p-1.5 rounded hover:bg-white/5 text-gray-400 hover:text-white transition" 
                        title="Sao chép"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      </button>
                      <button className="p-1.5 rounded hover:bg-white/5 text-gray-400 hover:text-white transition" title="Chia sẻ">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                        </svg>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {/* Typing indicator khi đang suy nghĩ */}
            {isThinking && (
              <div className="flex justify-start">
                <div className="bg-white/5 border border-white/10 rounded-2xl">
                  <TypingIndicator />
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      {/* Chỉ hiển thị footer input khi đã có messages */}
      {messages.length > 0 && (
        <footer className="px-6 py-4 border-t border-white/5 backdrop-blur-md bg-black/20">
          <div className="max-w-4xl mx-auto">
            <div className="relative">
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={isStreaming ? "MINH đang trả lời..." : "Hỏi gì đó..."}
                className="w-full rounded-3xl py-4 px-6 pr-32 text-base bg-[rgba(255,255,255,0.04)] text-white placeholder-slate-400 border border-white/10 focus:outline-none focus:border-cyan-400/50 disabled:opacity-50 disabled:cursor-not-allowed"
                onKeyDown={(e) => e.key === 'Enter' && !isStreaming && onSend()}
                disabled={isStreaming}
              />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2">
              {!isStreaming ? (
                <>
                  <button className="p-2 rounded-full bg-white/6 hover:bg-white/10 text-sm" disabled={isStreaming}>📎</button>
                  <button className="p-2 rounded-full bg-white/6 hover:bg-white/10 text-sm" disabled={isStreaming}>🎤</button>
                  <button 
                    onClick={onSend}
                    disabled={isStreaming || !query.trim()}
                    className="px-4 py-2 rounded-full bg-cyan-500 text-white hover:bg-cyan-600 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Gửi
                  </button>
                </>
              ) : (
                <button 
                  onClick={handleStopButton}
                  className="px-4 py-2 rounded-full bg-red-500 text-white hover:bg-red-600 text-sm font-medium flex items-center gap-2"
                >
                  <span className="w-3 h-3 bg-white rounded-sm"></span>
                  Stop
                </button>
              )}
            </div>
          </div>
        </div>
        </footer>
      )}
    </div>
  )
}

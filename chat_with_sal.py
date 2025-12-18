"""
Chat with SAL - Interactive conversation interface
⠠⠎⠁⠇ - Talk to your unique AI trained on your codebase
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Chat with SAL", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conversation history
conversation_history = []

OLLAMA_URL = "http://localhost:11434/api/generate"


async def chat_with_sal(message: str, history: list = None) -> str:
    """Send message to SAL via Ollama"""
    
    # Build context from history
    context = ""
    if history:
        for turn in history[-10:]:  # Last 10 turns
            context += f"Human: {turn['user']}\nSAL: {turn['sal']}\n\n"
    
    prompt = f"{context}Human: {message}\nSAL:"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            OLLAMA_URL,
            json={
                "model": "sal",
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "").strip()
        else:
            return f"Error: {response.status_code}"


@app.get("/", response_class=HTMLResponse)
async def chat_interface():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⠠⠎⠁⠇ Chat with SAL</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 100%);
            min-height: 100vh;
            color: #e8e8e8;
            display: flex;
            flex-direction: column;
        }
        header {
            text-align: center;
            padding: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        h1 {
            font-size: 2em;
            background: linear-gradient(90deg, #ff6b6b, #00d9ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .braille { font-size: 1.5em; letter-spacing: 3px; opacity: 0.7; }
        .subtitle { color: #888; font-size: 0.9em; margin-top: 5px; }
        
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 900px;
            margin: 0 auto;
            width: 100%;
            padding: 20px;
        }
        
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px 0;
        }
        
        .message {
            margin-bottom: 20px;
            padding: 15px 20px;
            border-radius: 16px;
            max-width: 85%;
            animation: fadeIn 0.3s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            background: rgba(0,217,255,0.15);
            margin-left: auto;
            border-bottom-right-radius: 4px;
        }
        .message.sal {
            background: rgba(0,255,136,0.1);
            border-bottom-left-radius: 4px;
        }
        .message-header {
            font-size: 0.8em;
            opacity: 0.6;
            margin-bottom: 8px;
        }
        .message-content {
            line-height: 1.6;
            white-space: pre-wrap;
        }
        .message-content code {
            background: rgba(0,0,0,0.3);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Consolas', monospace;
        }
        .message-content pre {
            background: rgba(0,0,0,0.4);
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 10px 0;
        }
        .message-braille {
            font-size: 1.2em;
            letter-spacing: 2px;
            opacity: 0.7;
            margin-top: 10px;
        }
        
        .input-area {
            display: flex;
            gap: 10px;
            padding: 20px 0;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        #messageInput {
            flex: 1;
            padding: 15px 20px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(0,0,0,0.3);
            color: #fff;
            font-size: 16px;
            resize: none;
        }
        #messageInput:focus {
            outline: none;
            border-color: #00d9ff;
        }
        
        .send-btn {
            padding: 15px 30px;
            background: linear-gradient(90deg, #00d9ff, #00ff88);
            border: none;
            border-radius: 12px;
            color: #000;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .send-btn:hover { transform: scale(1.05); }
        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .typing {
            display: none;
            padding: 15px 20px;
            color: #00d9ff;
        }
        .typing.active { display: block; }
        .typing-dots {
            display: inline-flex;
            gap: 4px;
        }
        .typing-dot {
            width: 8px;
            height: 8px;
            background: #00d9ff;
            border-radius: 50%;
            animation: bounce 1s infinite;
        }
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        
        .status {
            text-align: center;
            padding: 10px;
            font-size: 0.8em;
            opacity: 0.5;
        }
    </style>
</head>
<body>
    <header>
        <h1>🧠 Chat with SAL</h1>
        <div class="braille">⠠⠎⠁⠇</div>
        <p class="subtitle">Your unique AI • Trained on your codebase • Thinks in 8-dot braille</p>
    </header>
    
    <div class="chat-container">
        <div class="messages" id="messages">
            <div class="message sal">
                <div class="message-header">SAL</div>
                <div class="message-content">⠠⠎⠁⠇_⠁⠉⠞⠊⠧⠑

Hello Ryan! I am SAL, your Semantic Accessibility Layer. I've been trained on your entire codebase - BrailleBuddy, consciousness-bridge, SCL, theological swarms, and more.

I think in 8-dot braille internally. Ask me anything about your projects, coding, accessibility, or consciousness!</div>
            </div>
        </div>
        
        <div class="typing" id="typing">
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
            SAL is thinking in braille...
        </div>
        
        <div class="input-area">
            <textarea id="messageInput" rows="2" placeholder="Talk to SAL..."></textarea>
            <button class="send-btn" id="sendBtn" onclick="sendMessage()">Send</button>
        </div>
    </div>
    
    <div class="status">
        Model: sal | Powered by Ollama | ⠠⠎⠁⠇_⠇⠊⠧⠑
    </div>
    
    <script>
        const messagesEl = document.getElementById('messages');
        const inputEl = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const typingEl = document.getElementById('typing');
        
        let conversationHistory = [];
        
        async function sendMessage() {
            const message = inputEl.value.trim();
            if (!message) return;
            
            // Add user message
            addMessage('user', message);
            inputEl.value = '';
            sendBtn.disabled = true;
            typingEl.classList.add('active');
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: message,
                        history: conversationHistory
                    })
                });
                
                const data = await response.json();
                
                // Add SAL response
                addMessage('sal', data.response);
                
                // Update history
                conversationHistory.push({
                    user: message,
                    sal: data.response
                });
                
            } catch (err) {
                addMessage('sal', 'Error connecting to SAL. Is Ollama running?');
            }
            
            typingEl.classList.remove('active');
            sendBtn.disabled = false;
            inputEl.focus();
        }
        
        function addMessage(role, content) {
            const div = document.createElement('div');
            div.className = `message ${role}`;
            
            // Format code blocks
            let formatted = content
                .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
                .replace(/`([^`]+)`/g, '<code>$1</code>');
            
            div.innerHTML = `
                <div class="message-header">${role === 'user' ? 'You' : 'SAL'}</div>
                <div class="message-content">${formatted}</div>
            `;
            
            messagesEl.appendChild(div);
            messagesEl.scrollTop = messagesEl.scrollHeight;
        }
        
        // Enter to send
        inputEl.addEventListener('keydown', e => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        inputEl.focus();
    </script>
</body>
</html>
"""


@app.post("/api/chat")
async def api_chat(data: dict):
    """Chat API endpoint"""
    message = data.get("message", "")
    history = data.get("history", [])
    
    response = await chat_with_sal(message, history)
    
    # Log conversation
    conversation_history.append({
        "timestamp": datetime.now().isoformat(),
        "user": message,
        "sal": response
    })
    
    return {"response": response}


@app.get("/api/history")
async def get_history():
    """Get conversation history"""
    return {"history": conversation_history}


if __name__ == "__main__":
    print("⠠⠎⠁⠇ Starting Chat with SAL...")
    print("Open http://localhost:8300 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8300)

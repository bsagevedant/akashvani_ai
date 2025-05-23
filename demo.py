#!/usr/bin/env python3
"""
Demo script for Akashvani AI - showcases functionality without API keys
"""

import asyncio
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Create a simple demo app
demo_app = FastAPI(
    title="@akashvani_ai - Demo Mode",
    description="Demo version of the voice news assistant",
    version="1.0.0-demo"
)

demo_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DemoTextInput(BaseModel):
    text: str

# Mock news data
MOCK_NEWS = {
    "technology": [
        {"title": "AI Breakthrough in Machine Learning", "description": "Researchers achieve new milestone in artificial intelligence.", "source": "Tech News"},
        {"title": "New Smartphone Innovation", "description": "Latest smartphone features revolutionary technology.", "source": "Mobile World"},
        {"title": "Quantum Computing Advances", "description": "Scientists make progress in quantum computing research.", "source": "Science Today"}
    ],
    "sports": [
        {"title": "Championship Finals Results", "description": "Exciting match concludes season championship.", "source": "Sports Central"},
        {"title": "New Stadium Opens", "description": "State-of-the-art sports facility welcomes fans.", "source": "Stadium News"},
        {"title": "Record-Breaking Performance", "description": "Athlete sets new world record in competition.", "source": "Athletic Times"}
    ],
    "entertainment": [
        {"title": "New Movie Release", "description": "Blockbuster film premieres to enthusiastic audiences.", "source": "Entertainment Weekly"},
        {"title": "Music Festival Announcement", "description": "Major artists to perform at summer festival.", "source": "Music News"},
        {"title": "Award Show Highlights", "description": "Celebrities gather for annual awards ceremony.", "source": "Celebrity Times"}
    ]
}

def generate_demo_response(user_input: str) -> str:
    """Generate demo responses based on user input"""
    user_input_lower = user_input.lower()
    
    if any(word in user_input_lower for word in ['hello', 'hi', 'hey']):
        return """Hello! I'm Akashvani AI, your voice news assistant! 

🎤 In the full version, I can:
• Listen to your voice commands using Deepgram
• Provide real-time news from NewsAPI
• Have intelligent conversations using OpenAI
• Speak responses back to you

Try asking for 'technology news' or 'sports updates' to see a demo!"""

    elif 'technology' in user_input_lower or 'tech' in user_input_lower:
        news = MOCK_NEWS['technology']
        response = "Here are the top technology news updates:\n\n"
        for i, article in enumerate(news, 1):
            response += f"{i}. {article['title']}\n   {article['description']}\n   Source: {article['source']}\n\n"
        return response

    elif 'sports' in user_input_lower:
        news = MOCK_NEWS['sports']
        response = "Here are the top sports news updates:\n\n"
        for i, article in enumerate(news, 1):
            response += f"{i}. {article['title']}\n   {article['description']}\n   Source: {article['source']}\n\n"
        return response

    elif 'entertainment' in user_input_lower:
        news = MOCK_NEWS['entertainment']
        response = "Here are the top entertainment news updates:\n\n"
        for i, article in enumerate(news, 1):
            response += f"{i}. {article['title']}\n   {article['description']}\n   Source: {article['source']}\n\n"
        return response

    elif 'news' in user_input_lower:
        return """I can provide news from these categories:
• Technology - Latest tech innovations
• Sports - Sports scores and updates  
• Entertainment - Celebrity and entertainment news
• Politics - Political developments
• Business - Financial and business news
• Health - Health and medical news
• Science - Scientific discoveries

Just ask for any category! For example: 'Give me technology news'"""

    else:
        return f"""Thanks for your message: "{user_input}"

🎙️ In demo mode, I can respond to:
• Greetings (hello, hi)
• News requests (technology news, sports news, entertainment news)
• General news inquiries

For full functionality with real-time news, voice interaction, and AI conversations, please set up the API keys as described in the README.md file."""

@demo_app.get("/", response_class=HTMLResponse)
async def demo_home():
    """Demo home page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>@akashvani_ai - Demo Mode</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                color: white;
                padding: 2rem;
            }
            .header {
                text-align: center;
                margin-bottom: 2rem;
            }
            .logo {
                font-size: 3rem;
                font-weight: bold;
                margin-bottom: 1rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .demo-badge {
                background: rgba(255,255,255,0.2);
                padding: 0.5rem 1rem;
                border-radius: 25px;
                font-size: 1rem;
                margin-bottom: 1rem;
                display: inline-block;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                padding: 2rem;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }
            .input-section {
                margin-bottom: 2rem;
            }
            .input-field {
                width: 100%;
                padding: 1rem;
                border: none;
                border-radius: 10px;
                background: rgba(255,255,255,0.9);
                color: #333;
                font-size: 1rem;
                margin-bottom: 1rem;
            }
            .send-btn {
                width: 100%;
                padding: 1rem;
                border: none;
                border-radius: 10px;
                background: linear-gradient(45deg, #4ecdc4, #44a08d);
                color: white;
                font-size: 1rem;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .send-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(68, 160, 141, 0.3);
            }
            .response-section {
                background: rgba(255,255,255,0.1);
                padding: 1.5rem;
                border-radius: 15px;
                min-height: 200px;
                white-space: pre-line;
                line-height: 1.6;
            }
            .suggestions {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin-top: 1rem;
            }
            .suggestion-btn {
                padding: 0.75rem;
                border: none;
                border-radius: 10px;
                background: rgba(255,255,255,0.2);
                color: white;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }
            .suggestion-btn:hover {
                background: rgba(255,255,255,0.3);
                transform: translateY(-1px);
            }
            .info-box {
                background: rgba(255,255,255,0.1);
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 1rem;
                border-left: 4px solid #ffd700;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">@akashvani_ai</div>
            <div class="demo-badge">🚀 DEMO MODE</div>
        </div>
        
        <div class="container">
            <div class="info-box">
                <strong>📢 Demo Version</strong><br>
                This is a demonstration of Akashvani AI. For full functionality with real-time news, voice interaction, and AI conversations, please set up API keys (see README.md).
            </div>
            
            <div class="input-section">
                <input type="text" id="textInput" class="input-field" placeholder="Try: 'Hello' or 'Give me technology news'">
                <button id="sendBtn" class="send-btn">Send Message</button>
            </div>
            
            <div class="response-section" id="responseText">
                Welcome to Akashvani AI Demo! 
                
Try asking for news or say hello to get started.

🎤 Full version features:
• Real-time voice interaction with Deepgram
• Live news from NewsAPI
• AI conversations with OpenAI GPT
• Multiple news categories
• Text-to-speech responses
            </div>
            
            <div class="suggestions">
                <button class="suggestion-btn" onclick="sendMessage('Hello')">👋 Say Hello</button>
                <button class="suggestion-btn" onclick="sendMessage('Give me technology news')">💻 Tech News</button>
                <button class="suggestion-btn" onclick="sendMessage('Sports updates')">⚽ Sports</button>
                <button class="suggestion-btn" onclick="sendMessage('Entertainment news')">🎬 Entertainment</button>
            </div>
        </div>
        
        <script>
            const textInput = document.getElementById('textInput');
            const sendBtn = document.getElementById('sendBtn');
            const responseText = document.getElementById('responseText');
            
            sendBtn.addEventListener('click', () => {
                const message = textInput.value.trim();
                if (message) {
                    sendMessage(message);
                    textInput.value = '';
                }
            });
            
            textInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendBtn.click();
                }
            });
            
            async function sendMessage(message) {
                try {
                    responseText.textContent = 'Processing...';
                    
                    const response = await fetch('/api/demo', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: message })
                    });
                    
                    const result = await response.json();
                    responseText.textContent = result.response;
                } catch (error) {
                    responseText.textContent = 'Error: Could not process your request.';
                    console.error('Error:', error);
                }
            }
        </script>
    </body>
    </html>
    """

@demo_app.post("/api/demo")
async def demo_chat(request: DemoTextInput):
    """Demo chat endpoint"""
    response = generate_demo_response(request.text)
    return {"response": response}

@demo_app.get("/health")
async def demo_health():
    """Demo health check"""
    return {"status": "healthy", "mode": "demo", "service": "@akashvani_ai"}

def main():
    print("🚀 Starting Akashvani AI in Demo Mode...")
    print("="*50)
    print("📱 Open your browser and go to: http://localhost:8001")
    print()
    print("🎯 Demo Features:")
    print("  • Text chat interface")
    print("  • Mock news responses")
    print("  • Basic conversation")
    print()
    print("🔧 For full features, set up API keys and use: python3 start.py")
    print("="*50)
    
    uvicorn.run(
        "demo:demo_app",
        host="localhost",
        port=8001,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main() 
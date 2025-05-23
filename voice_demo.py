#!/usr/bin/env python3
"""
Voice-only demo script for Akashvani AI - Voice input/output with headlines display
"""

import asyncio
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Create voice-focused demo app
voice_app = FastAPI(
    title="@akashvani_ai - Voice Mode",
    description="Voice-only version of the news assistant with headlines display",
    version="1.0.0-voice"
)

voice_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VoiceInput(BaseModel):
    text: str

# Mock news data with headlines
MOCK_HEADLINES = {
    "technology": [
        "AI Breakthrough in Machine Learning",
        "New Smartphone Innovation Unveiled",
        "Quantum Computing Advances Rapidly",
        "Tech Giants Report Record Earnings",
        "Revolutionary Battery Technology Announced"
    ],
    "sports": [
        "Championship Finals Complete",
        "New Stadium Opens This Weekend", 
        "Record-Breaking Performance Set",
        "Major Trade Announcement Made",
        "Olympic Preparations Underway"
    ],
    "entertainment": [
        "Blockbuster Movie Premieres",
        "Music Festival Lineup Revealed",
        "Award Show Highlights",
        "Celebrity Charity Event Success",
        "Streaming Service Launches"
    ],
    "general": [
        "Breaking: Major Economic Changes",
        "Weather Alert: Storm Approaching",
        "Health Update: New Study Results", 
        "Travel Advisory: Airport Delays",
        "Education: School Year Updates"
    ]
}

DETAILED_NEWS = {
    "technology": [
        {"title": "AI Breakthrough in Machine Learning", "summary": "Researchers achieve new milestone in artificial intelligence capabilities with 40% improvement in processing speed"},
        {"title": "New Smartphone Innovation Unveiled", "summary": "Latest smartphone features revolutionary battery technology lasting 5 days on single charge"},
        {"title": "Quantum Computing Advances Rapidly", "summary": "Scientists make breakthrough in quantum computing research with new 1000-qubit processor"}
    ],
    "sports": [
        {"title": "Championship Finals Complete", "summary": "Exciting championship match concludes with record-breaking attendance of 85,000 fans"},
        {"title": "New Stadium Opens This Weekend", "summary": "State-of-the-art sports facility featuring retractable roof welcomes first game"},
        {"title": "Record-Breaking Performance Set", "summary": "Athlete sets new world record in 100-meter dash with time of 9.58 seconds"}
    ],
    "entertainment": [
        {"title": "Blockbuster Movie Premieres", "summary": "Highly anticipated superhero film breaks opening weekend box office records"},
        {"title": "Music Festival Lineup Revealed", "summary": "Summer festival announces star-studded lineup with over 50 artists performing"},
        {"title": "Award Show Highlights", "summary": "Annual awards ceremony celebrates achievements in film and television"}
    ]
}

def generate_voice_response(user_input: str) -> dict:
    """Generate voice response with headlines"""
    user_input_lower = user_input.lower()
    
    if any(word in user_input_lower for word in ['hello', 'hi', 'hey', 'start']):
        return {
            "voice_text": "Hello! I'm Akashvani AI, your voice news assistant. I can provide you with the latest news updates. Just ask for technology, sports, entertainment, or general news.",
            "headlines": ["Welcome to Akashvani AI", "Voice News Assistant", "Ask for: Tech, Sports, Entertainment", "Or say 'news' for general updates"],
            "category": "greeting"
        }
    
    elif 'technology' in user_input_lower or 'tech' in user_input_lower:
        headlines = MOCK_HEADLINES['technology']
        news = DETAILED_NEWS['technology']
        voice_summary = f"Here are the top {len(news)} technology news stories. " + " ".join([f"{item['title']}. {item['summary']}." for item in news])
        return {
            "voice_text": voice_summary,
            "headlines": headlines,
            "category": "technology"
        }
    
    elif 'sports' in user_input_lower:
        headlines = MOCK_HEADLINES['sports']
        news = DETAILED_NEWS['sports']
        voice_summary = f"Here are the top {len(news)} sports news stories. " + " ".join([f"{item['title']}. {item['summary']}." for item in news])
        return {
            "voice_text": voice_summary,
            "headlines": headlines,
            "category": "sports"
        }
    
    elif 'entertainment' in user_input_lower:
        headlines = MOCK_HEADLINES['entertainment']
        news = DETAILED_NEWS['entertainment']
        voice_summary = f"Here are the top {len(news)} entertainment news stories. " + " ".join([f"{item['title']}. {item['summary']}." for item in news])
        return {
            "voice_text": voice_summary,
            "headlines": headlines,
            "category": "entertainment"
        }
    
    elif 'news' in user_input_lower or 'headlines' in user_input_lower:
        headlines = MOCK_HEADLINES['general']
        voice_summary = "Here are the top general news headlines. " + " ".join(headlines) + ". Ask for specific categories like technology, sports, or entertainment for detailed coverage."
        return {
            "voice_text": voice_summary,
            "headlines": headlines,
            "category": "general"
        }
    
    else:
        return {
            "voice_text": f"I heard you say '{user_input}'. I can provide news on technology, sports, entertainment, or general news. What would you like to hear about?",
            "headlines": ["Available Categories:", "• Technology News", "• Sports Updates", "• Entertainment News", "• General Headlines"],
            "category": "help"
        }

@voice_app.get("/", response_class=HTMLResponse)
async def voice_home():
    """Voice interface home page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>@akashvani_ai - Voice Mode</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                color: white;
                overflow: hidden;
            }
            
            .voice-container {
                display: flex;
                flex-direction: column;
                height: 100vh;
                justify-content: center;
                align-items: center;
                padding: 2rem;
            }
            
            .logo {
                font-size: 3.5rem;
                font-weight: bold;
                margin-bottom: 1rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                text-align: center;
            }
            
            .voice-badge {
                background: rgba(255,255,255,0.2);
                padding: 0.5rem 1.5rem;
                border-radius: 25px;
                font-size: 1.2rem;
                margin-bottom: 2rem;
                display: inline-block;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
            .headlines-screen {
                background: rgba(0,0,0,0.8);
                border: 3px solid #00ff88;
                border-radius: 15px;
                padding: 2rem;
                margin: 2rem 0;
                min-height: 200px;
                width: 100%;
                max-width: 800px;
                box-shadow: 0 0 30px rgba(0,255,136,0.3);
                position: relative;
                overflow: hidden;
            }
            
            .headlines-screen::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(0,255,136,0.1), transparent);
                animation: scan 3s infinite;
            }
            
            @keyframes scan {
                0% { left: -100%; }
                100% { left: 100%; }
            }
            
            .headlines-title {
                font-size: 1.5rem;
                color: #00ff88;
                margin-bottom: 1rem;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
            
            .headline-item {
                font-size: 1.1rem;
                padding: 0.5rem 0;
                border-bottom: 1px solid rgba(0,255,136,0.2);
                animation: fadeIn 0.5s ease-in;
                color: #ffffff;
            }
            
            .headline-item:last-child {
                border-bottom: none;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateX(-20px); }
                to { opacity: 1; transform: translateX(0); }
            }
            
            .voice-controls {
                display: flex;
                gap: 2rem;
                margin-top: 2rem;
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .voice-btn {
                padding: 1.5rem 2rem;
                border: none;
                border-radius: 50px;
                background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                color: white;
                font-size: 1.2rem;
                cursor: pointer;
                transition: all 0.3s ease;
                min-width: 180px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .voice-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 30px rgba(255,107,107,0.4);
            }
            
            .voice-btn.listening {
                background: linear-gradient(45deg, #00ff88, #00cc6a);
                animation: pulse 1.5s infinite;
            }
            
            .voice-btn.speaking {
                background: linear-gradient(45deg, #ffa726, #ff7043);
                animation: pulse 1.5s infinite;
            }
            
            .category-buttons {
                display: flex;
                gap: 1rem;
                margin-top: 1rem;
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .category-btn {
                padding: 0.75rem 1.5rem;
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 25px;
                background: rgba(255,255,255,0.1);
                color: white;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }
            
            .category-btn:hover {
                background: rgba(255,255,255,0.2);
                border-color: rgba(255,255,255,0.6);
                transform: translateY(-2px);
            }
            
            .status-indicator {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                background: rgba(0,0,0,0.7);
                font-size: 0.9rem;
                border: 1px solid rgba(255,255,255,0.3);
            }
            
            .hidden {
                display: none;
            }
            
            .dev-link {
                position: fixed;
                bottom: 20px;
                left: 20px;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                background: rgba(0,0,0,0.7);
                font-size: 0.9rem;
                border: 1px solid rgba(255,255,255,0.3);
                text-decoration: none;
                color: #00ff88;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .dev-link:hover {
                background: rgba(0,255,136,0.2);
                border-color: #00ff88;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,255,136,0.3);
            }
        </style>
    </head>
    <body>
        <div class="status-indicator" id="statusIndicator">Ready</div>
        <a href="https://x.com/sageadvik" target="_blank" class="dev-link">
            <span>🔗</span>
            <span>dev</span>
        </a>
        
        <div class="voice-container">
            <div class="logo">@akashvani_ai</div>
            <div class="voice-badge">🎤 VOICE MODE</div>
            
            <div class="headlines-screen" id="headlinesScreen">
                <div class="headlines-title" id="headlinesTitle">Voice News Assistant</div>
                <div id="headlinesList">
                    <div class="headline-item">🎤 Click "Start Listening" to begin</div>
                    <div class="headline-item">📰 Ask for: Technology, Sports, Entertainment, or General News</div>
                    <div class="headline-item">🔊 Voice responses will be spoken aloud</div>
                    <div class="headline-item">📺 Headlines will appear on this screen</div>
                </div>
            </div>
            
            <div class="voice-controls">
                <button id="startListeningBtn" class="voice-btn">🎤 Start Listening</button>
                <button id="stopBtn" class="voice-btn hidden">⏹️ Stop</button>
            </div>
            
            <div class="category-buttons">
                <button class="category-btn" onclick="askForNews('technology')">💻 Technology</button>
                <button class="category-btn" onclick="askForNews('sports')">⚽ Sports</button>
                <button class="category-btn" onclick="askForNews('entertainment')">🎬 Entertainment</button>
                <button class="category-btn" onclick="askForNews('general news')">📰 General</button>
            </div>
        </div>
        
        <script>
            let recognition;
            let synthesis = window.speechSynthesis;
            let isListening = false;
            let isSpeaking = false;
            
            const startBtn = document.getElementById('startListeningBtn');
            const stopBtn = document.getElementById('stopBtn');
            const statusIndicator = document.getElementById('statusIndicator');
            const headlinesTitle = document.getElementById('headlinesTitle');
            const headlinesList = document.getElementById('headlinesList');
            
            // Initialize speech recognition
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'en-US';
                
                recognition.onstart = function() {
                    isListening = true;
                    updateUI();
                    statusIndicator.textContent = 'Listening...';
                };
                
                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript;
                    console.log('Heard:', transcript);
                    processVoiceInput(transcript);
                };
                
                recognition.onerror = function(event) {
                    console.error('Speech recognition error:', event.error);
                    statusIndicator.textContent = 'Error: ' + event.error;
                    isListening = false;
                    updateUI();
                };
                
                recognition.onend = function() {
                    isListening = false;
                    updateUI();
                    if (!isSpeaking) {
                        statusIndicator.textContent = 'Ready';
                    }
                };
            } else {
                alert('Speech recognition not supported in this browser. Please use Chrome or Edge.');
            }
            
            startBtn.addEventListener('click', startListening);
            stopBtn.addEventListener('click', stopListening);
            
            function startListening() {
                if (recognition && !isListening) {
                    recognition.start();
                }
            }
            
            function stopListening() {
                if (recognition && isListening) {
                    recognition.stop();
                }
                if (synthesis.speaking) {
                    synthesis.cancel();
                    isSpeaking = false;
                    updateUI();
                    statusIndicator.textContent = 'Ready';
                }
            }
            
            function updateUI() {
                startBtn.classList.toggle('hidden', isListening);
                stopBtn.classList.toggle('hidden', !isListening && !isSpeaking);
                
                if (isListening) {
                    startBtn.classList.add('listening');
                } else {
                    startBtn.classList.remove('listening');
                }
                
                if (isSpeaking) {
                    stopBtn.classList.add('speaking');
                } else {
                    stopBtn.classList.remove('speaking');
                }
            }
            
            async function processVoiceInput(text) {
                try {
                    statusIndicator.textContent = 'Processing...';
                    
                    const response = await fetch('/api/voice', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    
                    const result = await response.json();
                    
                    // Update headlines display
                    updateHeadlines(result.category, result.headlines);
                    
                    // Speak the response
                    speakText(result.voice_text);
                    
                } catch (error) {
                    console.error('Error:', error);
                    statusIndicator.textContent = 'Error processing request';
                    speakText('Sorry, I could not process your request. Please try again.');
                }
            }
            
            function updateHeadlines(category, headlines) {
                const categoryTitles = {
                    'technology': '💻 Technology News',
                    'sports': '⚽ Sports Updates', 
                    'entertainment': '🎬 Entertainment News',
                    'general': '📰 General Headlines',
                    'greeting': '👋 Welcome',
                    'help': '❓ Available Options'
                };
                
                headlinesTitle.textContent = categoryTitles[category] || '📰 News Headlines';
                
                headlinesList.innerHTML = '';
                headlines.forEach((headline, index) => {
                    setTimeout(() => {
                        const item = document.createElement('div');
                        item.className = 'headline-item';
                        item.textContent = headline;
                        headlinesList.appendChild(item);
                    }, index * 200);
                });
            }
            
            function speakText(text) {
                if (synthesis.speaking) {
                    synthesis.cancel();
                }
                
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 0.9;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;
                
                utterance.onstart = function() {
                    isSpeaking = true;
                    updateUI();
                    statusIndicator.textContent = 'Speaking...';
                };
                
                utterance.onend = function() {
                    isSpeaking = false;
                    updateUI();
                    statusIndicator.textContent = 'Ready';
                };
                
                synthesis.speak(utterance);
            }
            
            function askForNews(category) {
                processVoiceInput(category);
            }
            
            // Auto-start with greeting
            window.addEventListener('load', function() {
                setTimeout(() => {
                    processVoiceInput('hello');
                }, 1000);
            });
        </script>
    </body>
    </html>
    """

@voice_app.post("/api/voice")
async def voice_chat(request: VoiceInput):
    """Voice chat endpoint"""
    response = generate_voice_response(request.text)
    return response

@voice_app.get("/health")
async def voice_health():
    """Voice demo health check"""
    return {"status": "healthy", "mode": "voice", "service": "@akashvani_ai"}

def main():
    print("🎤 Starting Akashvani AI in Voice Mode...")
    print("="*50)
    print("📱 Open your browser and go to: http://localhost:8002")
    print()
    print("🎯 Voice Features:")
    print("  • Voice input only (speech recognition)")
    print("  • Voice output only (text-to-speech)")
    print("  • Headlines display on screen")
    print("  • No text chat interface")
    print()
    print("🔧 Make sure to allow microphone access in your browser")
    print("="*50)
    
    uvicorn.run(
        "voice_demo:voice_app",
        host="localhost",
        port=8002,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main() 
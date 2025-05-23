import asyncio
import logging
import json
import base64
import uuid
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse, Response
from pydantic import BaseModel
import uvicorn
import tempfile
import os

from config import Config
from services.conversation_handler import ConversationHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Akashvani AI - Voice News Assistant",
    description="A two-way conversational voice AI for news updates",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global conversation handler
conversation_handler = ConversationHandler()

# Pydantic models
class TextInput(BaseModel):
    text: str
    voice_type: Optional[str] = "female"

class VoiceInput(BaseModel):
    voice_type: Optional[str] = "female"

class NewsRequest(BaseModel):
    category: Optional[str] = None
    search_query: Optional[str] = None
    voice_type: Optional[str] = "female"

class ConversationResponse(BaseModel):
    text_response: str
    audio_available: bool
    session_id: Optional[str] = None
    headlines_only: Optional[list] = None

# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            self.disconnect(websocket)

manager = ConnectionManager()

# Store audio files temporarily
audio_storage = {}

@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup"""
    try:
        Config.validate_config()
        logger.info("Akashvani AI started successfully!")
        logger.info("Available news categories: " + ", ".join(Config.NEWS_CATEGORIES))
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        logger.error("Please check your environment variables in .env file")

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main web interface with voice selection"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>@akashvani_ai - Voice News Assistant</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: white;
                padding: 20px;
            }
            
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                max-width: 800px;
                width: 100%;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                border: 1px solid rgba(255, 255, 255, 0.18);
                text-align: center;
            }
            
            .header {
                margin-bottom: 30px;
            }
            
            .logo {
                font-size: 2.5rem;
                font-weight: bold;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #fff, #f0f0f0);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .subtitle {
                font-size: 1.2rem;
                opacity: 0.9;
                margin-bottom: 20px;
            }
            
            .voice-selection {
                margin-bottom: 30px;
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 15px;
            }
            
            .voice-selection h3 {
                margin-bottom: 15px;
                font-size: 1.1rem;
            }
            
            .voice-buttons {
                display: flex;
                gap: 15px;
                justify-content: center;
            }
            
            .voice-btn {
                padding: 10px 20px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border-radius: 25px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 1rem;
            }
            
            .voice-btn.active {
                background: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.6);
                transform: scale(1.05);
            }
            
            .voice-btn:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: scale(1.02);
            }
            
            .controls {
                display: flex;
                flex-direction: column;
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .voice-controls {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 20px;
            }
            
            .mic-button {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                border: none;
                background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                color: white;
                font-size: 2rem;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .mic-button:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 20px rgba(255, 107, 107, 0.6);
            }
            
            .mic-button.recording {
                background: linear-gradient(45deg, #20bf6b, #01a3a4);
                animation: pulse 1.5s infinite;
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }
            
            .text-input-container {
                display: flex;
                gap: 10px;
                align-items: center;
            }
            
            .text-input {
                flex: 1;
                padding: 15px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                background: rgba(255, 255, 255, 0.1);
                border-radius: 25px;
                color: white;
                font-size: 1rem;
                outline: none;
                transition: all 0.3s ease;
            }
            
            .text-input::placeholder {
                color: rgba(255, 255, 255, 0.7);
            }
            
            .text-input:focus {
                border-color: rgba(255, 255, 255, 0.6);
                background: rgba(255, 255, 255, 0.15);
            }
            
            .send-button {
                padding: 15px 25px;
                background: linear-gradient(45deg, #4834d4, #686de0);
                border: none;
                border-radius: 25px;
                color: white;
                cursor: pointer;
                font-size: 1rem;
                transition: all 0.3s ease;
            }
            
            .send-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(72, 52, 212, 0.4);
            }
            
            .categories {
                margin-bottom: 30px;
            }
            
            .category-buttons {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                justify-content: center;
                margin-top: 15px;
            }
            
            .category-btn {
                padding: 10px 20px;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 20px;
                color: white;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }
            
            .category-btn:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: translateY(-2px);
            }
            
            .response-section {
                margin-top: 30px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                min-height: 120px;
            }
            
            .headlines-container {
                text-align: left;
                margin-bottom: 15px;
            }
            
            .headline-item {
                padding: 10px;
                margin-bottom: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                border-left: 4px solid #4834d4;
            }
            
            .headline-title {
                font-weight: bold;
                margin-bottom: 5px;
                font-size: 1rem;
            }
            
            .headline-source {
                font-size: 0.8rem;
                opacity: 0.7;
            }
            
            .response-text {
                font-size: 1.1rem;
                line-height: 1.6;
                margin-bottom: 15px;
                text-align: center;
            }
            
            .audio-player {
                width: 100%;
                margin-top: 15px;
                border-radius: 25px;
            }
            
            .status {
                margin-top: 15px;
                font-size: 0.9rem;
                opacity: 0.8;
            }
            
            @media (max-width: 600px) {
                .container {
                    padding: 20px;
                }
                
                .voice-controls {
                    flex-direction: column;
                    gap: 15px;
                }
                
                .text-input-container {
                    flex-direction: column;
                    gap: 15px;
                }
                
                .voice-buttons {
                    flex-direction: column;
                    align-items: center;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">@akashvani_ai</div>
                <div class="subtitle">Your AI-Powered Voice News Assistant</div>
            </div>
            
            <div class="voice-selection">
                <h3>🎙️ Choose Your Preferred Voice</h3>
                <div class="voice-buttons">
                    <button class="voice-btn active" data-voice="female">👩 Female Voice (Asteria)</button>
                    <button class="voice-btn" data-voice="male">👨 Male Voice (Orion)</button>
                </div>
            </div>
            
            <div class="controls">
                <div class="voice-controls">
                    <button class="mic-button" id="micButton">🎤</button>
                    <div class="status" id="status">Click microphone to start recording</div>
                </div>
                
                <div class="text-input-container">
                    <input type="text" class="text-input" id="textInput" placeholder="Or type your message here...">
                    <button class="send-button" id="sendButton">Send</button>
                </div>
            </div>
            
            <div class="categories">
                <h3>📰 Quick News Categories</h3>
                <div class="category-buttons">
                    <button class="category-btn" onclick="askForNews('technology')">Tech</button>
                    <button class="category-btn" onclick="askForNews('politics')">Politics</button>
                    <button class="category-btn" onclick="askForNews('sports')">Sports</button>
                    <button class="category-btn" onclick="askForNews('entertainment')">Entertainment</button>
                    <button class="category-btn" onclick="askForNews('business')">Business</button>
                    <button class="category-btn" onclick="askForNews('health')">Health</button>
                    <button class="category-btn" onclick="askForNews('science')">Science</button>
                </div>
            </div>
            
            <div class="response-section">
                <div class="headlines-container" id="headlinesContainer" style="display: none;"></div>
                <div class="response-text" id="responseText">👋 Welcome! Ask me for news updates or choose a category above.</div>
                <audio class="audio-player" id="audioPlayer" controls style="display: none;"></audio>
            </div>
        </div>
        
        <script>
            let isRecording = false;
            let mediaRecorder;
            let audioChunks = [];
            let selectedVoice = 'female';
            
            const micButton = document.getElementById('micButton');
            const textInput = document.getElementById('textInput');
            const sendButton = document.getElementById('sendButton');
            const responseText = document.getElementById('responseText');
            const audioPlayer = document.getElementById('audioPlayer');
            const status = document.getElementById('status');
            const headlinesContainer = document.getElementById('headlinesContainer');
            const voiceButtons = document.querySelectorAll('.voice-btn');
            
            // Voice selection
            voiceButtons.forEach(btn => {
                btn.addEventListener('click', () => {
                    voiceButtons.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    selectedVoice = btn.dataset.voice;
                    status.textContent = `Voice set to ${btn.textContent}`;
                });
            });
            
            // Microphone functionality
            micButton.addEventListener('click', toggleRecording);
            
            async function toggleRecording() {
                if (!isRecording) {
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        mediaRecorder = new MediaRecorder(stream);
                        audioChunks = [];
                        
                        mediaRecorder.ondataavailable = event => {
                            audioChunks.push(event.data);
                        };
                        
                        mediaRecorder.onstop = async () => {
                            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                            await sendVoiceMessage(audioBlob);
                            stream.getTracks().forEach(track => track.stop());
                        };
                        
                        mediaRecorder.start();
                        isRecording = true;
                        micButton.classList.add('recording');
                        micButton.textContent = '🛑';
                        status.textContent = 'Recording... Click again to stop';
                        
                    } catch (error) {
                        console.error('Error accessing microphone:', error);
                        status.textContent = 'Microphone access denied. Please enable microphone permissions.';
                    }
                } else {
                    mediaRecorder.stop();
                    isRecording = false;
                    micButton.classList.remove('recording');
                    micButton.textContent = '🎤';
                    status.textContent = 'Processing your voice message...';
                }
            }
            
            async function sendVoiceMessage(audioBlob) {
                try {
                    const formData = new FormData();
                    formData.append('audio', audioBlob, 'voice.wav');
                    formData.append('voice_type', selectedVoice);
                    
                    const response = await fetch('/api/voice', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    displayResponse(result.text_response, result.audio_url, result.headlines_only);
                    status.textContent = 'Click microphone to start recording';
                } catch (error) {
                    console.error('Error sending voice:', error);
                    responseText.textContent = 'Sorry, there was an error processing your voice message.';
                    status.textContent = 'Error occurred. Please try again.';
                }
            }
            
            // Text input functionality
            sendButton.addEventListener('click', sendTextMessage);
            textInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendTextMessage();
                }
            });
            
            async function sendTextMessage() {
                const text = textInput.value.trim();
                if (!text) return;
                
                try {
                    const response = await fetch('/api/text', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ 
                            text: text,
                            voice_type: selectedVoice 
                        })
                    });
                    
                    const result = await response.json();
                    displayResponse(result.text_response, result.audio_url, result.headlines_only);
                    textInput.value = '';
                } catch (error) {
                    console.error('Error sending text:', error);
                    responseText.textContent = 'Sorry, there was an error processing your message.';
                }
            }
            
            function displayResponse(text, audioUrl, headlines) {
                // Show headlines if available (for news responses)
                if (headlines && headlines.length > 0) {
                    displayHeadlines(headlines);
                    responseText.textContent = 'Reading news summaries... 🎧';
                } else {
                    headlinesContainer.style.display = 'none';
                    responseText.textContent = text;
                }
                
                if (audioUrl) {
                    audioPlayer.src = audioUrl;
                    audioPlayer.style.display = 'block';
                    audioPlayer.play().catch(e => console.log('Audio autoplay prevented'));
                } else {
                    audioPlayer.style.display = 'none';
                }
            }
            
            function displayHeadlines(headlines) {
                headlinesContainer.innerHTML = '';
                headlinesContainer.style.display = 'block';
                
                headlines.forEach((headline, index) => {
                    const headlineDiv = document.createElement('div');
                    headlineDiv.className = 'headline-item';
                    headlineDiv.innerHTML = `
                        <div class="headline-title">${index + 1}. ${headline.title}</div>
                        <div class="headline-source">Source: ${headline.source}</div>
                    `;
                    headlinesContainer.appendChild(headlineDiv);
                });
            }
            
            function askForNews(category) {
                textInput.value = `Give me ${category} news`;
                sendTextMessage();
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/voice")
async def handle_voice_input(audio: UploadFile = File(...), voice_type: str = Form("female")):
    """Handle voice input from the frontend with voice selection"""
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Process with conversation handler using selected voice
        text_response, audio_response = await conversation_handler.handle_voice_input(audio_data, voice_type)
        
        # Check if this is a news response and get headlines only
        headlines_only = None
        if "headline" in text_response.lower() or "news" in text_response.lower():
            # Extract category if possible and get headlines
            for category in Config.NEWS_CATEGORIES:
                if category in text_response.lower():
                    headlines_only = await conversation_handler.get_headlines_only(category)
                    break
        
        # Store audio response and generate URL
        audio_url = None
        if audio_response:
            audio_id = str(uuid.uuid4())
            audio_storage[audio_id] = audio_response
            audio_url = f"/api/audio/{audio_id}"
        
        return {
            "text_response": text_response,
            "audio_available": audio_response is not None,
            "audio_url": audio_url,
            "headlines_only": headlines_only
        }
        
    except Exception as e:
        logger.error(f"Error handling voice input: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing voice input")

@app.post("/api/text")
async def handle_text_input(request: TextInput):
    """Handle text input from the frontend with voice selection"""
    try:
        # Process with conversation handler using selected voice
        text_response, audio_response = await conversation_handler.handle_text_input(request.text, request.voice_type)
        
        # Check if this is a news response and get headlines only
        headlines_only = None
        if "headline" in text_response.lower() or "news" in text_response.lower():
            # Extract category if possible and get headlines
            for category in Config.NEWS_CATEGORIES:
                if category in request.text.lower():
                    headlines_only = await conversation_handler.get_headlines_only(category)
                    break
        
        # Store audio response and generate URL
        audio_url = None
        if audio_response:
            audio_id = str(uuid.uuid4())
            audio_storage[audio_id] = audio_response
            audio_url = f"/api/audio/{audio_id}"
        
        return {
            "text_response": text_response,
            "audio_available": audio_response is not None,
            "audio_url": audio_url,
            "headlines_only": headlines_only
        }
        
    except Exception as e:
        logger.error(f"Error handling text input: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing text input")

@app.get("/api/audio/{audio_id}")
async def serve_audio(audio_id: str):
    """Serve audio files"""
    try:
        if audio_id in audio_storage:
            audio_data = audio_storage[audio_id]
            # Clean up after serving
            del audio_storage[audio_id]
            
            return Response(
                content=audio_data,
                media_type="audio/wav",
                headers={
                    "Content-Disposition": "inline; filename=response.wav",
                    "Cache-Control": "no-cache"
                }
            )
        else:
            raise HTTPException(status_code=404, detail="Audio not found")
    except Exception as e:
        logger.error(f"Error serving audio: {str(e)}")
        raise HTTPException(status_code=500, detail="Error serving audio")

@app.get("/api/categories")
async def get_news_categories():
    """Get available news categories"""
    return {
        "categories": Config.NEWS_CATEGORIES,
        "description": await conversation_handler.get_available_categories()
    }

@app.post("/api/news")
async def get_news(request: NewsRequest):
    """Direct news endpoint for specific requests"""
    try:
        if request.category:
            # Get specific category news
            news = await conversation_handler.news_service.get_top_headlines(request.category)
            formatted_response = conversation_handler.news_service.format_news_for_speech(news, request.category)
        elif request.search_query:
            # Search for specific news
            news = await conversation_handler.news_service.search_news(request.search_query)
            formatted_response = f"Search results for '{request.search_query}':\n" + \
                               conversation_handler.news_service.format_news_for_speech(news, "search")
        else:
            # Get general news update
            all_news = await conversation_handler.news_service.get_all_categories_news()
            formatted_response = await conversation_handler._format_general_news_update(all_news)
        
        return {
            "response": formatted_response,
            "news_data": news if 'news' in locals() else all_news
        }
        
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching news")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "text":
                # Handle text message
                text_response, _ = await conversation_handler.handle_text_input(message_data["content"])
                await manager.send_personal_message(json.dumps({
                    "type": "response",
                    "content": text_response
                }), websocket)
            
            elif message_data["type"] == "voice":
                # Handle voice message (audio data would be base64 encoded)
                # This would require additional implementation for audio handling over WebSocket
                await manager.send_personal_message(json.dumps({
                    "type": "response", 
                    "content": "Voice message received (WebSocket voice processing not implemented in this demo)"
                }), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)

@app.get("/api/session")
async def get_session_info():
    """Get current session information"""
    try:
        session_info = await conversation_handler.get_session_info()
        return session_info
    except Exception as e:
        logger.error(f"Error getting session info: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving session information")

@app.post("/api/session/clear")
async def clear_session():
    """Clear current session"""
    try:
        conversation_handler.clear_session()
        return {"message": "Session cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(status_code=500, detail="Error clearing session")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "@akashvani_ai",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    try:
        Config.validate_config()
        uvicorn.run(
            "main:app",
            host=Config.HOST,
            port=Config.PORT,
            reload=True
        )
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set up your environment variables before running the application.")
        exit(1) 
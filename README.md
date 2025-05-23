# @akashvani_ai - Voice News Assistant

A sophisticated two-way conversational voice AI platform that reads out the top 5 news updates from various categories including technology, politics, sports, entertainment, business, health, and science.

## 🌟 Features

- **🎤 Voice Interaction**: Real-time speech-to-text and text-to-speech using Deepgram
- **🤖 AI Conversation**: Natural language processing powered by OpenAI GPT
- **📰 Live News**: Fresh news updates from NewsAPI across multiple categories
- **💬 Text Chat**: Alternative text-based interaction
- **🌐 Modern Web Interface**: Beautiful, responsive UI with voice controls
- **⚡ Real-time Updates**: WebSocket support for instant communication
- **📱 Mobile Friendly**: Responsive design that works on all devices

## 🏗 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────┐
│   Web Frontend  │◄──►│   FastAPI Backend │◄──►│  External APIs  │
│                 │    │                  │    │                │
│ • Voice UI      │    │ • Conversation   │    │ • Deepgram     │
│ • Text Chat     │    │   Handler        │    │ • OpenAI       │
│ • Audio Player  │    │ • Speech Service │    │ • NewsAPI      │
│                 │    │ • AI Service     │    │                │
└─────────────────┘    └──────────────────┘    └────────────────┘
```

## 🛠 Setup Instructions

### Prerequisites

- Python 3.8+
- API Keys for:
  - [Deepgram](https://deepgram.com/) (Speech-to-Text & Text-to-Speech)
  - [OpenAI](https://openai.com/) (GPT for conversations)
  - [NewsAPI](https://newsapi.org/) (News data)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd akashvani_ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file with your API keys:
   ```env
   DEEPGRAM_API_KEY=your_deepgram_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   NEWS_API_KEY=your_news_api_key_here
   HOST=localhost
   PORT=8000
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:8000`

## 🚀 Usage

### Voice Interaction
1. Click the **red microphone button** to start recording
2. Speak your request (e.g., "Give me technology news")
3. Click again to stop recording
4. Listen to Akashvani's response

### Text Chat
1. Type your message in the text area
2. Click "Send Message" or press Enter
3. Read the response and listen to the audio version

### Sample Commands
- "Hello" - Get a greeting and introduction
- "Give me technology news" - Latest tech news
- "What's happening in sports?" - Sports updates
- "Tell me about politics" - Political news
- "Search for artificial intelligence news" - Specific topic search

## 📁 Project Structure

```
akashvani_ai/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and environment variables
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── README.md             # This file
└── services/
    ├── __init__.py
    ├── conversation_handler.py  # Main conversation orchestrator
    ├── ai_service.py           # OpenAI integration
    ├── speech_service.py       # Deepgram STT/TTS
    └── news_service.py         # NewsAPI integration
```

## 🔧 API Endpoints

### Main Interface
- `GET /` - Web interface
- `GET /health` - Health check

### Voice & Text Interaction
- `POST /api/voice` - Process voice input
- `POST /api/text` - Process text input
- `WebSocket /ws` - Real-time communication

### News Services
- `GET /api/categories` - Available news categories
- `POST /api/news` - Direct news fetch

### Session Management
- `GET /api/session` - Session information
- `POST /api/session/clear` - Clear session

## 🎯 News Categories

- **Technology** - Latest tech innovations and updates
- **Politics** - Political news and developments
- **Sports** - Sports scores, news, and updates
- **Entertainment** - Celebrity news and entertainment
- **Business** - Financial and business news
- **Health** - Health and medical news
- **Science** - Scientific discoveries and research

## 🔊 Voice Features

### Supported Voice Commands
- News requests by category
- General greetings and conversations
- Specific news searches
- Follow-up questions

### Text-to-Speech
- Natural-sounding voice responses
- Multiple voice options available
- Optimized for news delivery

## 🛡 Security & Privacy

- API keys stored securely in environment variables
- No permanent storage of conversation data
- CORS enabled for web interface
- Input validation and error handling

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### Production Deployment
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

**Microphone not working**
- Check browser permissions for microphone access
- Ensure HTTPS is used for production deployments

**API Key errors**
- Verify all API keys are set correctly in `.env`
- Check API key validity and quotas

**News not loading**
- Verify NewsAPI key and quota
- Check internet connectivity

**Speech synthesis not working**
- Verify Deepgram API key
- Check browser audio support

### Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs for error messages
3. Create an issue in the repository

## 🚀 Future Enhancements

- [ ] Real-time streaming speech recognition
- [ ] Voice conversation memory
- [ ] Multiple language support
- [ ] Custom news sources
- [ ] Voice command shortcuts
- [ ] Mobile app version
- [ ] Podcast-style news summaries

---

**@akashvani_ai** - Your intelligent voice companion for staying informed! 🎙️📰 
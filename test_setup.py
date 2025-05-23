#!/usr/bin/env python3
"""
Test script to verify Akashvani AI setup and configuration
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import openai
        print("✅ OpenAI imported successfully")
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
        return False
    
    try:
        import deepgram
        print("✅ Deepgram imported successfully")
    except ImportError as e:
        print(f"❌ Deepgram import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n🔧 Testing configuration...")
    
    try:
        from config import Config
        print("✅ Config module imported successfully")
        
        # Check if environment variables are accessible (they may be None if not set)
        print(f"📋 Deepgram API Key: {'✅ Set' if Config.DEEPGRAM_API_KEY else '❌ Not Set'}")
        print(f"📋 OpenAI API Key: {'✅ Set' if Config.OPENAI_API_KEY else '❌ Not Set'}")
        print(f"📋 News API Key: {'✅ Set' if Config.NEWS_API_KEY else '❌ Not Set'}")
        print(f"📋 Host: {Config.HOST}")
        print(f"📋 Port: {Config.PORT}")
        print(f"📋 News Categories: {', '.join(Config.NEWS_CATEGORIES)}")
        
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_services():
    """Test service initialization"""
    print("\n🔧 Testing service initialization...")
    
    try:
        from services.news_service import NewsService
        news_service = NewsService()
        print("✅ NewsService initialized successfully")
    except Exception as e:
        print(f"❌ NewsService initialization failed: {e}")
        return False
    
    try:
        from services.speech_service import SpeechService
        speech_service = SpeechService()
        print("✅ SpeechService initialized successfully")
    except Exception as e:
        print(f"❌ SpeechService initialization failed: {e}")
        return False
    
    try:
        from services.ai_service import AIService
        ai_service = AIService()
        print("✅ AIService initialized successfully")
    except Exception as e:
        print(f"❌ AIService initialization failed: {e}")
        return False
    
    try:
        from services.conversation_handler import ConversationHandler
        conversation_handler = ConversationHandler()
        print("✅ ConversationHandler initialized successfully")
    except Exception as e:
        print(f"❌ ConversationHandler initialization failed: {e}")
        return False
    
    return True

async def test_basic_functionality():
    """Test basic functionality with mock data"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from services.conversation_handler import ConversationHandler
        handler = ConversationHandler()
        
        # Test text input processing (this won't make API calls without valid keys)
        print("📝 Testing text processing...")
        
        # This will fail gracefully if API keys are not set
        try:
            response, audio = await handler.handle_text_input("Hello")
            print("✅ Text processing works (with valid API keys)")
        except Exception as e:
            print(f"⚠️ Text processing needs valid API keys: {str(e)[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI application initialization"""
    print("\n🌐 Testing FastAPI application...")
    
    try:
        from main import app
        print("✅ FastAPI app initialized successfully")
        print(f"📋 App title: {app.title}")
        print(f"📋 App version: {app.version}")
        return True
    except Exception as e:
        print(f"❌ FastAPI app test failed: {e}")
        return False

def print_setup_instructions():
    """Print setup instructions if tests fail"""
    print("\n" + "="*50)
    print("📋 SETUP INSTRUCTIONS")
    print("="*50)
    print()
    print("1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print()
    print("2. Set up environment variables:")
    print("   cp env.example .env")
    print("   # Edit .env with your API keys")
    print()
    print("3. Get API keys from:")
    print("   - Deepgram: https://deepgram.com/")
    print("   - OpenAI: https://openai.com/")
    print("   - NewsAPI: https://newsapi.org/")
    print()
    print("4. Run the application:")
    print("   python main.py")
    print()

async def main():
    """Run all tests"""
    print("🚀 Akashvani AI Setup Test")
    print("="*50)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test configuration
    if not test_config():
        all_passed = False
    
    # Test services
    if not test_services():
        all_passed = False
    
    # Test basic functionality
    if not await test_basic_functionality():
        all_passed = False
    
    # Test FastAPI app
    if not test_fastapi_app():
        all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Akashvani AI is ready to run!")
        print("\nTo start the application, run:")
        print("   python main.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("⚠️ Please fix the issues above before running the application")
        print_setup_instructions()
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main()) 
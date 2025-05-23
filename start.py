#!/usr/bin/env python3
"""
Quick start script for Akashvani AI
"""

import sys
import uvicorn
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("🚀 Starting Akashvani AI...")
    print("="*50)
    
    try:
        from config import Config
        
        # Validate configuration
        print("🔧 Validating configuration...")
        Config.validate_config()
        print("✅ Configuration valid!")
        
        print(f"🌐 Starting server on {Config.HOST}:{Config.PORT}")
        print("📱 Open your browser and go to:")
        print(f"   http://{Config.HOST}:{Config.PORT}")
        print()
        print("🎤 Features available:")
        print("   • Voice interaction with microphone")
        print("   • Text chat interface") 
        print("   • Real-time news from multiple categories")
        print("   • AI-powered conversation")
        print()
        print("Press Ctrl+C to stop the server")
        print("="*50)
        
        # Start the server
        uvicorn.run(
            "main:app",
            host=Config.HOST,
            port=Config.PORT,
            reload=True,
            log_level="info"
        )
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print()
        print("📋 Please set up your API keys:")
        print("1. Copy env.example to .env")
        print("2. Edit .env with your API keys:")
        print("   - DEEPGRAM_API_KEY (from https://deepgram.com/)")
        print("   - OPENAI_API_KEY (from https://openai.com/)")
        print("   - NEWS_API_KEY (from https://newsapi.org/)")
        print()
        print("💡 Run 'python test_setup.py' to verify your setup")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n👋 Akashvani AI stopped. Thanks for using our voice assistant!")
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("💡 Run 'python test_setup.py' to diagnose issues")
        sys.exit(1)

if __name__ == "__main__":
    main() 
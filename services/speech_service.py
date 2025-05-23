import asyncio
import aiofiles
from deepgram import (
    DeepgramClient,
    SpeakOptions,
    PrerecordedOptions,
    FileSource,
)
from typing import Optional, AsyncGenerator
import tempfile
import os
import logging
from config import Config

logger = logging.getLogger(__name__)

class SpeechService:
    def __init__(self):
        self.deepgram = DeepgramClient(Config.DEEPGRAM_API_KEY)
        
        # Voice options for male and female voices
        self.voices = {
            "female": "aura-asteria-en",  # Female voice
            "male": "aura-orion-en"      # Male voice
        }
        
    async def transcribe_audio(self, audio_data: bytes, mimetype: str = "audio/wav") -> Optional[str]:
        """
        Transcribe audio data to text using Deepgram STT
        """
        try:
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Read the audio file
                async with aiofiles.open(temp_file_path, "rb") as audio_file:
                    buffer_data = await audio_file.read()
                
                payload: FileSource = {
                    "buffer": buffer_data,
                }
                
                # Configure transcription options
                options = PrerecordedOptions(
                    model=Config.DEEPGRAM_MODEL,
                    language=Config.DEEPGRAM_LANGUAGE,
                    smart_format=True,
                    punctuate=True,
                    diarize=False,
                )
                
                # Transcribe the audio using the new API - response is already resolved
                response = self.deepgram.listen.rest.v("1").transcribe_file(
                    payload, options
                )
                
                # Extract transcript from response
                if hasattr(response, 'results') and response.results and response.results.channels:
                    transcript = response.results.channels[0].alternatives[0].transcript
                else:
                    logger.error("No transcript data received from Deepgram")
                    return None
                
                logger.info(f"Transcribed audio: {transcript}")
                return transcript
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return None
    
    async def synthesize_speech(self, text: str, voice_type: str = "female") -> Optional[bytes]:
        """
        Convert text to speech using Deepgram TTS with voice selection
        """
        try:
            # Select voice based on type
            selected_voice = self.voices.get(voice_type, self.voices["female"])
            
            # Configure TTS options for new SDK 4.1.0
            options = SpeakOptions(
                model=selected_voice,
                encoding="linear16",
                sample_rate=24000
            )
            
            # Generate speech using the new API - response is already resolved
            response = self.deepgram.speak.rest.v("1").stream(
                {"text": text}, options
            )
            
            # Get the audio data from response stream
            # response.stream_memory returns a BytesIO object, we need to get the bytes
            if hasattr(response, 'stream_memory') and response.stream_memory:
                if hasattr(response.stream_memory, 'getvalue'):
                    # If it's a BytesIO object, get the bytes value
                    audio_data = response.stream_memory.getvalue()
                else:
                    # If it's already bytes
                    audio_data = response.stream_memory
            else:
                logger.error("No audio data received from Deepgram")
                return None
            
            logger.info(f"Generated {voice_type} speech for text: {text[:50]}...")
            return audio_data
            
        except Exception as e:
            logger.error(f"Error synthesizing speech: {str(e)}")
            return None
    
    async def transcribe_streaming(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        """
        Handle streaming transcription for real-time conversation
        """
        try:
            # Note: This would require WebSocket implementation with Deepgram
            # For now, we'll implement a simplified version
            async for audio_chunk in audio_stream:
                if audio_chunk:
                    transcript = await self.transcribe_audio(audio_chunk)
                    if transcript:
                        yield transcript
                        
        except Exception as e:
            logger.error(f"Error in streaming transcription: {str(e)}")
            yield ""
    
    def get_available_voices(self) -> dict:
        """
        Get list of available TTS voices with types
        """
        return {
            "female": {
                "name": "Asteria",
                "description": "Professional female voice",
                "model": "aura-asteria-en"
            },
            "male": {
                "name": "Orion", 
                "description": "Professional male voice",
                "model": "aura-orion-en"
            }
        }
    
    def validate_audio_format(self, audio_data: bytes) -> bool:
        """
        Validate if audio data is in a supported format
        """
        try:
            # Check for common audio file headers
            wav_header = b'RIFF'
            mp3_header = b'ID3'
            m4a_header = b'ftyp'
            
            return (
                audio_data.startswith(wav_header) or
                audio_data.startswith(mp3_header) or
                b'ftyp' in audio_data[:20]
            )
        except Exception:
            return False

    def format_news_for_speech(self, articles: list, category: str) -> str:
        """
        Format news articles specifically for voice reading with 2-line summaries
        """
        if not articles:
            return f"Sorry, I couldn't fetch any news for {category} at the moment."
        
        speech_text = f"Here are the top {category} news headlines:\n\n"
        
        for i, article in enumerate(articles, 1):
            title = article.get("title", "")
            description = article.get("description", "")
            
            # Create a 2-line summary for each headline
            speech_text += f"Headline {i}: {title}. "
            
            if description and description != title:
                # Create a concise 2-line summary (about 25-30 words)
                desc_words = description.split()[:25]
                summary = " ".join(desc_words)
                if len(desc_words) == 25:
                    summary += "..."
                speech_text += f"{summary} "
            
            speech_text += "\n\n"
        
        return speech_text 
import asyncio
import logging
from typing import Dict, Optional, Tuple
from services.ai_service import AIService
from services.speech_service import SpeechService
from services.news_service import NewsService

logger = logging.getLogger(__name__)

class ConversationHandler:
    def __init__(self):
        self.ai_service = AIService()
        self.speech_service = SpeechService()
        self.news_service = NewsService()
        self.current_session = {"voice_preference": "female"}  # Default to female voice
        
    async def handle_voice_input(self, audio_data: bytes, voice_type: str = "female") -> Tuple[str, Optional[bytes]]:
        """
        Complete pipeline: Audio -> Text -> AI Processing -> News (if needed) -> Response Text -> Audio
        """
        try:
            # Step 1: Transcribe audio to text
            transcript = await self.speech_service.transcribe_audio(audio_data)
            if not transcript:
                error_response = "I'm sorry, I couldn't understand what you said. Could you please try again?"
                audio_response = await self.speech_service.synthesize_speech(error_response, voice_type)
                return error_response, audio_response
            
            logger.info(f"User said: {transcript}")
            
            # Step 2: Process with AI to understand intent
            ai_response = await self.ai_service.process_user_input(transcript)
            
            # Step 3: Handle the request based on intent
            final_response = await self._handle_intent(ai_response)
            
            # Step 4: Convert response to speech with selected voice
            audio_response = await self.speech_service.synthesize_speech(final_response, voice_type)
            
            return final_response, audio_response
            
        except Exception as e:
            logger.error(f"Error in voice input handling: {str(e)}")
            error_response = "I'm experiencing some technical difficulties. Please try again in a moment."
            audio_response = await self.speech_service.synthesize_speech(error_response, voice_type)
            return error_response, audio_response
    
    async def handle_text_input(self, text_input: str, voice_type: str = "female") -> Tuple[str, Optional[bytes]]:
        """
        Handle text input (for chat interface) with voice selection
        """
        try:
            # Process with AI to understand intent
            ai_response = await self.ai_service.process_user_input(text_input)
            
            # Handle the request based on intent
            final_response = await self._handle_intent(ai_response)
            
            # Generate audio response with selected voice
            audio_response = await self.speech_service.synthesize_speech(final_response, voice_type)
            
            return final_response, audio_response
            
        except Exception as e:
            logger.error(f"Error in text input handling: {str(e)}")
            error_response = "I'm sorry, I encountered an error processing your request."
            return error_response, None
    
    async def _handle_intent(self, ai_response: Dict) -> str:
        """
        Handle different types of intents from AI service
        """
        intent = ai_response.get("intent", "general_conversation")
        action = ai_response.get("action", "respond_only")
        
        try:
            if action == "fetch_news":
                return await self._handle_news_request(ai_response)
            elif action == "search_news":
                return await self._handle_news_search(ai_response)
            else:
                # For greetings, general conversation, help
                return ai_response.get("response", "I'm here to help you with news updates!")
                
        except Exception as e:
            logger.error(f"Error handling intent {intent}: {str(e)}")
            return "I'm sorry, I encountered an issue while processing your request. Please try again."
    
    async def _handle_news_request(self, ai_response: Dict) -> str:
        """
        Handle news category requests with voice-optimized formatting
        """
        category = ai_response.get("category", "general")
        
        if category == "general":
            # Get news from multiple categories
            all_news = await self.news_service.get_all_categories_news(limit_per_category=3)
            response = await self._format_general_news_update(all_news)
        else:
            # Get specific category news and format for voice
            news_articles = await self.news_service.get_top_headlines(category, limit=5)
            if news_articles:
                # Use speech service's voice-optimized formatting
                response = self.speech_service.format_news_for_speech(news_articles, category)
            else:
                response = f"I'm sorry, I couldn't fetch {category} news at the moment. Would you like news from another category?"
        
        # Store session data for follow-up questions
        self.current_session.update({
            "last_category": category,
            "last_news_data": news_articles if category != "general" else all_news,
            "last_action": "news_fetch"
        })
        
        return response
    
    async def _handle_news_search(self, ai_response: Dict) -> str:
        """
        Handle news search requests with voice-optimized formatting
        """
        search_query = ai_response.get("search_query", "")
        
        if not search_query:
            return "I need a specific topic to search for. What news would you like me to find?"
        
        search_results = await self.news_service.search_news(search_query, limit=5)
        
        if search_results:
            # Use speech service's voice-optimized formatting
            response = self.speech_service.format_news_for_speech(search_results, f"search results for {search_query}")
        else:
            response = f"I couldn't find any recent news about '{search_query}'. Would you like me to search for something else?"
        
        # Store session data
        self.current_session.update({
            "last_search": search_query,
            "last_news_data": search_results,
            "last_action": "news_search"
        })
        
        return response

    async def _format_general_news_update(self, all_news: Dict) -> str:
        """
        Format general news update from multiple categories for voice reading
        """
        try:
            response = "Here's your news briefing from Akashvani AI.\n\n"
            
            for category, articles in all_news.items():
                if articles:
                    # Only include headlines for display, full summaries will be read
                    response += f"Top {category} headline: {articles[0].get('title', 'No title available')}.\n\n"
            
            response += "Which category would you like me to read in detail?"
            return response
            
        except Exception as e:
            logger.error(f"Error formatting general news: {str(e)}")
            return "Here's a quick news update. I have the latest stories from technology, politics, sports, and entertainment. Which category interests you most?"

    def set_voice_preference(self, voice_type: str):
        """
        Set the user's voice preference
        """
        if voice_type in ["male", "female"]:
            self.current_session["voice_preference"] = voice_type
            logger.info(f"Voice preference set to: {voice_type}")
    
    def get_voice_preference(self) -> str:
        """
        Get the current voice preference
        """
        return self.current_session.get("voice_preference", "female")

    async def get_headlines_only(self, category: str) -> list:
        """
        Get only headlines for display (not full text)
        """
        try:
            news_articles = await self.news_service.get_top_headlines(category, limit=5)
            headlines = []
            for article in news_articles:
                headlines.append({
                    "title": article.get("title", ""),
                    "source": article.get("source", ""),
                    "publishedAt": article.get("publishedAt", "")
                })
            return headlines
        except Exception as e:
            logger.error(f"Error getting headlines for {category}: {str(e)}")
            return []
    
    async def get_available_categories(self) -> str:
        """
        Get list of available news categories
        """
        from config import Config
        categories = ", ".join(Config.NEWS_CATEGORIES)
        return f"I can provide news updates from these categories: {categories}. Which would you like to hear about?"
    
    async def get_session_info(self) -> Dict:
        """
        Get current session information
        """
        return {
            "session_data": self.current_session,
            "conversation_summary": self.ai_service.get_conversation_summary(),
            "available_voices": await self.speech_service.get_available_voices()
        }
    
    def clear_session(self):
        """
        Clear current session and conversation history
        """
        self.current_session = {}
        self.ai_service.clear_conversation_history()
        logger.info("Session cleared")
    
    async def handle_followup(self, user_input: str) -> str:
        """
        Handle follow-up questions based on current session
        """
        if not self.current_session:
            return "What would you like to know about? I can provide news updates from various categories."
        
        response = await self.ai_service.handle_followup_question(user_input, self.current_session)
        return response
    
    async def get_detailed_article(self, article_number: int) -> str:
        """
        Get detailed information about a specific article
        """
        last_news_data = self.current_session.get("last_news_data", [])
        
        if not last_news_data or article_number < 1 or article_number > len(last_news_data):
            return "I don't have that article number. Please ask for a valid article number from the recent news."
        
        article = last_news_data[article_number - 1]
        title = article.get('title', 'No title')
        description = article.get('description', 'No description available')
        source = article.get('source', 'Unknown source')
        
        detailed_response = f"Here's more detail about article {article_number}: {title}. {description} This story is from {source}."
        
        return detailed_response 
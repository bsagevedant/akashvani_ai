import openai
from typing import Dict, List, Optional, Tuple
import json
import re
import logging
from config import Config

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.client = openai.OpenAI()
        self.conversation_history = []
        
    async def process_user_input(self, user_text: str) -> Dict:
        """
        Process user input and determine intent and extract relevant information
        """
        try:
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_text
            })
            
            # System prompt for Akashvani AI
            system_prompt = """
You are Akashvani AI, a helpful voice assistant that specializes in delivering news updates. 
Your primary functions are:
1. Provide top 5 news updates from different categories (technology, politics, sports, entertainment, business, health, science)
2. Search for specific news topics
3. Have natural conversations about current events

Analyze the user's request and respond with a JSON object containing:
{
    "intent": "news_category" | "news_search" | "general_conversation" | "greeting" | "help",
    "category": "technology|politics|sports|entertainment|business|health|science" (if intent is news_category),
    "search_query": "search terms" (if intent is news_search),
    "response": "Your conversational response",
    "action": "fetch_news" | "search_news" | "respond_only"
}

For news requests, be enthusiastic and professional. For greetings, introduce yourself as Akashvani AI.
"""
            
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": system_prompt},
                *self.conversation_history[-5:]  # Keep last 5 messages for context
            ]
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=messages,
                max_tokens=Config.OPENAI_MAX_TOKENS,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Add AI response to conversation history
            self.conversation_history.append({
                "role": "assistant", 
                "content": ai_response
            })
            
            # Parse JSON response
            try:
                result = json.loads(ai_response)
                return result
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return self._parse_fallback_response(ai_response, user_text)
                
        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}")
            return {
                "intent": "general_conversation",
                "response": "I'm sorry, I'm having trouble processing your request right now. Please try again.",
                "action": "respond_only"
            }
    
    def _parse_fallback_response(self, ai_response: str, user_text: str) -> Dict:
        """
        Fallback parsing when JSON response fails
        """
        user_text_lower = user_text.lower()
        
        # Check for news category requests
        for category in Config.NEWS_CATEGORIES:
            if category in user_text_lower or f"{category} news" in user_text_lower:
                return {
                    "intent": "news_category",
                    "category": category,
                    "response": f"Let me get the latest {category} news for you.",
                    "action": "fetch_news"
                }
        
        # Check for general news request
        if any(word in user_text_lower for word in ['news', 'headlines', 'updates']):
            return {
                "intent": "news_category", 
                "category": "general",
                "response": "Let me get the latest news updates for you.",
                "action": "fetch_news"
            }
        
        # Check for greetings
        if any(word in user_text_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
            return {
                "intent": "greeting",
                "response": "Hello! I'm Akashvani AI, your voice assistant for news updates. Ask me for news from any category like technology, politics, sports, or entertainment!",
                "action": "respond_only"
            }
        
        # Default to general conversation
        return {
            "intent": "general_conversation",
            "response": ai_response,
            "action": "respond_only"
        }
    
    async def generate_news_summary(self, news_data: Dict, category: str) -> str:
        """
        Generate a conversational summary of news articles
        """
        try:
            articles = news_data.get(category, [])
            if not articles:
                return f"I couldn't find any {category} news at the moment. Would you like news from another category?"
            
            # Create a prompt for summarizing news
            news_text = ""
            for article in articles[:5]:
                news_text += f"Title: {article['title']}\n"
                if article['description']:
                    news_text += f"Description: {article['description']}\n"
                news_text += f"Source: {article['source']}\n\n"
            
            summary_prompt = f"""
As Akashvani AI, create a natural, conversational summary of these {category} news articles. 
Keep it engaging and easy to listen to. Structure it as "Here are today's top {category} news updates:" 
followed by brief, clear summaries of each article.

News articles:
{news_text}

Make it sound natural for voice delivery, around 200-300 words total.
"""
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[{"role": "user", "content": summary_prompt}],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating news summary: {str(e)}")
            return f"Here are the top {category} news updates: " + self._format_basic_news_summary(news_data.get(category, []))
    
    def _format_basic_news_summary(self, articles: List[Dict]) -> str:
        """
        Basic fallback news formatting
        """
        if not articles:
            return "No news available at the moment."
        
        summary = ""
        for i, article in enumerate(articles[:5], 1):
            title = article.get('title', 'No title')
            source = article.get('source', 'Unknown source')
            summary += f"News {i}: {title} from {source}. "
        
        return summary
    
    async def handle_followup_question(self, question: str, context: Dict) -> str:
        """
        Handle follow-up questions about news articles
        """
        try:
            followup_prompt = f"""
The user asked a follow-up question about news: "{question}"
Context: {json.dumps(context, indent=2)}

Provide a helpful response as Akashvani AI. If they're asking for more details, 
news from another category, or want to search for specific topics, provide appropriate guidance.
"""
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[{"role": "user", "content": followup_prompt}],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error handling followup question: {str(e)}")
            return "I'm sorry, could you please repeat your question? I want to make sure I understand what you're looking for."
    
    def clear_conversation_history(self):
        """
        Clear conversation history for a fresh start
        """
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_conversation_summary(self) -> str:
        """
        Get a summary of the current conversation
        """
        if not self.conversation_history:
            return "No conversation history available."
        
        return f"Conversation has {len(self.conversation_history)} messages." 
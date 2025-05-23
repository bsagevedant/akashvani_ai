import requests
from typing import List, Dict, Optional
from config import Config
import logging

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.api_key = Config.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
        
    async def get_top_headlines(self, category: str, country: str = "us", limit: int = 5) -> List[Dict]:
        """
        Fetch top headlines for a specific category
        """
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                "apiKey": self.api_key,
                "category": category,
                "country": country,
                "pageSize": limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get("articles", [])
            
            # Format articles for voice output
            formatted_articles = []
            for i, article in enumerate(articles[:limit], 1):
                formatted_article = {
                    "number": i,
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "url": article.get("url", ""),
                    "publishedAt": article.get("publishedAt", "")
                }
                formatted_articles.append(formatted_article)
            
            return formatted_articles
            
        except Exception as e:
            logger.error(f"Error fetching news for category {category}: {str(e)}")
            return []
    
    async def get_all_categories_news(self, limit_per_category: int = 5) -> Dict[str, List[Dict]]:
        """
        Fetch news from all configured categories
        """
        all_news = {}
        
        for category in Config.NEWS_CATEGORIES:
            try:
                news = await self.get_top_headlines(category, limit=limit_per_category)
                all_news[category] = news
                logger.info(f"Fetched {len(news)} articles for {category}")
            except Exception as e:
                logger.error(f"Failed to fetch news for {category}: {str(e)}")
                all_news[category] = []
        
        return all_news
    
    def format_news_for_speech(self, articles: List[Dict], category: str) -> str:
        """
        Format news articles for text-to-speech output
        """
        if not articles:
            return f"Sorry, I couldn't fetch any news for {category} at the moment."
        
        speech_text = f"Here are the top {len(articles)} {category} news updates:\n\n"
        
        for article in articles:
            title = article["title"]
            description = article["description"] or "No description available"
            source = article["source"]
            
            # Clean up the text for better speech synthesis
            speech_text += f"News {article['number']}: {title}. "
            if description and description != title:
                # Limit description length for better speech flow
                desc_words = description.split()[:20]
                short_description = " ".join(desc_words)
                if len(desc_words) == 20:
                    short_description += "..."
                speech_text += f"{short_description} "
            speech_text += f"Source: {source}.\n\n"
        
        return speech_text
    
    async def search_news(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for specific news topics
        """
        try:
            url = f"{self.base_url}/everything"
            params = {
                "apiKey": self.api_key,
                "q": query,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get("articles", [])
            
            formatted_articles = []
            for i, article in enumerate(articles[:limit], 1):
                formatted_article = {
                    "number": i,
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "url": article.get("url", ""),
                    "publishedAt": article.get("publishedAt", "")
                }
                formatted_articles.append(formatted_article)
            
            return formatted_articles
            
        except Exception as e:
            logger.error(f"Error searching news for query '{query}': {str(e)}")
            return [] 
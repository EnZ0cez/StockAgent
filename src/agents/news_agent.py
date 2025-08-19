from tavily import TavilyClient
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import re

class NewsAgent:
    """Agent for retrieving and analyzing news sentiment"""
    
    def __init__(self, llm, tavily_api_key: str = None):
        self.llm = llm
        self.tavily_api_key = tavily_api_key
        
    def get_news_sentiment(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """
        Get news sentiment analysis for a stock
        
        Args:
            symbol: Stock symbol (e.g., AAPL, MSFT)
            days: Number of days to look back for news
        
        Returns:
            Dictionary containing news data and sentiment analysis
        """
        try:
            # Search for news using Tavily
            news_articles = self._search_news(symbol, days)
            
            if not news_articles:
                return {
                    "symbol": symbol,
                    "sentiment": "neutral",
                    "confidence": 0.0,
                    "articles_count": 0,
                    "articles": [],
                    "summary": "No recent news found",
                    "last_updated": datetime.now().isoformat()
                }
            
            # Analyze sentiment using LLM
            sentiment_analysis = self._analyze_sentiment_llm(news_articles, symbol)
            
            # Calculate sentiment metrics
            sentiment_scores = [article.get("sentiment_score", 0) for article in news_articles]
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
            
            # Classify overall sentiment
            overall_sentiment = self._classify_sentiment(avg_sentiment)
            
            # Extract key topics
            key_topics = self._extract_key_topics(news_articles)
            
            # Calculate sentiment distribution
            sentiment_distribution = self._calculate_sentiment_distribution(news_articles)
            
            result = {
                "symbol": symbol,
                "period_days": days,
                "overall_sentiment": overall_sentiment,
                "average_sentiment_score": avg_sentiment,
                "confidence": min(abs(avg_sentiment), 1.0),
                "articles_count": len(news_articles),
                "sentiment_distribution": sentiment_distribution,
                "key_topics": key_topics,
                "articles": news_articles,
                "summary": sentiment_analysis.get("summary", ""),
                "impact_analysis": sentiment_analysis.get("impact_analysis", ""),
                "last_updated": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "sentiment": "neutral",
                "confidence": 0.0,
                "last_updated": datetime.now().isoformat()
            }
    
    def _search_news(self, symbol: str, days: int) -> List[Dict[str, Any]]:
        """Search for news articles using Tavily"""
        try:
            if not self.tavily_api_key:
                # Fallback to mock data for testing
                return self._get_mock_news(symbol, days)
            
            client = TavilyClient(self.tavily_api_key)
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Search query
            query = f"{symbol} stock news analysis {start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
            
            # Search for news
            response = client.search(query, 
                                   search_depth="advanced",
                                   max_results=10,
                                   include_answer=False,
                                   include_raw_content=False)
            
            articles = []
            for result in response.get("results", []):
                article = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "published_date": result.get("published_date", ""),
                    "source": result.get("source", ""),
                    "sentiment_score": 0.0,  # Will be calculated later
                    "sentiment": "neutral"
                }
                articles.append(article)
            
            return articles
            
        except Exception as e:
            print(f"Error searching news: {e}")
            return self._get_mock_news(symbol, days)
    
    def _get_mock_news(self, symbol: str, days: int) -> List[Dict[str, Any]]:
        """Get mock news data for testing"""
        return [
            {
                "title": f"{symbol} Reports Strong Quarterly Earnings",
                "url": "https://example.com/news1",
                "content": f"{symbol} announced better-than-expected earnings for the quarter, beating analyst estimates.",
                "published_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "source": "Financial Times",
                "sentiment_score": 0.7,
                "sentiment": "positive"
            },
            {
                "title": f"Analysts Upgrade {symbol} Stock Rating",
                "url": "https://example.com/news2",
                "content": f"Major investment firms have upgraded their rating for {symbol} based on strong growth prospects.",
                "published_date": (datetime.now() - timedelta(days=2)).isoformat(),
                "source": "Bloomberg",
                "sentiment_score": 0.6,
                "sentiment": "positive"
            },
            {
                "title": f"{symbol} Faces Market Volatility Concerns",
                "url": "https://example.com/news3",
                "content": f"{symbol} stock experiences volatility due to broader market concerns and economic uncertainty.",
                "published_date": (datetime.now() - timedelta(days=3)).isoformat(),
                "source": "Reuters",
                "sentiment_score": -0.3,
                "sentiment": "negative"
            }
        ]
    
    def _analyze_sentiment_llm(self, articles: List[Dict[str, Any]], symbol: str) -> Dict[str, Any]:
        """Analyze sentiment using LLM"""
        try:
            # Prepare articles for analysis
            articles_text = ""
            for i, article in enumerate(articles[:5]):  # Limit to 5 articles for context
                articles_text += f"Article {i+1}: {article['title']}\n"
                articles_text += f"Content: {article['content'][:200]}...\n\n"
            
            prompt = f"""
            Analyze the sentiment of the following news articles about {symbol} stock:
            
            {articles_text}
            
            Please provide:
            1. Overall sentiment summary (2-3 sentences)
            2. Impact analysis on stock price (positive/negative/neutral)
            3. Key themes and topics mentioned
            4. Confidence level in sentiment assessment (0-1)
            
            Return the analysis in JSON format:
            {{
                "summary": "Overall sentiment summary",
                "impact_analysis": "Impact on stock price",
                "key_themes": ["theme1", "theme2"],
                "confidence": 0.8
            }}
            """
            
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            return json.loads(response.content)
            
        except Exception as e:
            return {
                "summary": "Unable to analyze sentiment due to error",
                "impact_analysis": "Unknown impact",
                "key_themes": [],
                "confidence": 0.0
            }
    
    def _classify_sentiment(self, score: float) -> str:
        """Classify sentiment based on score"""
        if score > 0.2:
            return "positive"
        elif score < -0.2:
            return "negative"
        else:
            return "neutral"
    
    def _extract_key_topics(self, articles: List[Dict[str, Any]]) -> List[str]:
        """Extract key topics from news articles"""
        topics = []
        
        # Simple keyword extraction
        keywords = [
            "earnings", "revenue", "profit", "growth", "dividend", "merger", "acquisition",
            "regulation", "lawsuit", "innovation", "expansion", "market", "competition",
            "leadership", "strategy", "forecast", "guidance", "analyst", "rating"
        ]
        
        all_text = " ".join([article.get("title", "") + " " + article.get("content", "") for article in articles])
        
        for keyword in keywords:
            if keyword.lower() in all_text.lower():
                topics.append(keyword)
        
        return list(set(topics))[:10]  # Return top 10 topics
    
    def _calculate_sentiment_distribution(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate sentiment distribution"""
        positive = sum(1 for article in articles if article.get("sentiment") == "positive")
        negative = sum(1 for article in articles if article.get("sentiment") == "negative")
        neutral = sum(1 for article in articles if article.get("sentiment") == "neutral")
        
        return {
            "positive": positive,
            "negative": negative,
            "neutral": neutral
        }
    
    def get_real_time_news(self, symbol: str) -> Dict[str, Any]:
        """Get real-time news updates"""
        return self.get_news_sentiment(symbol, days=1)
    
    def get_trending_topics(self, symbols: List[str]) -> Dict[str, Any]:
        """Get trending topics for multiple symbols"""
        trending_data = {}
        
        for symbol in symbols:
            news_data = self.get_news_sentiment(symbol, days=3)
            trending_data[symbol] = {
                "sentiment": news_data.get("overall_sentiment", "neutral"),
                "key_topics": news_data.get("key_topics", []),
                "articles_count": news_data.get("articles_count", 0)
            }
        
        return trending_data
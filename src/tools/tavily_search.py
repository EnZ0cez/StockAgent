from tavily import TavilyClient
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import re

class TavilySearchTool:
    """Enhanced Tavily search tool for market news and financial information"""
    
    def __init__(self, api_key: str):
        self.client = TavilyClient(api_key)
    
    def search_market_news(self, symbol: str, days: int = 7, max_results: int = 10) -> Dict[str, Any]:
        """Search for market news related to a stock symbol"""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Build search query
            query = f"{symbol} stock news analysis market {start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
            
            # Perform search
            response = self.client.search(
                query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=False,
                include_raw_content=False
            )
            
            # Process results
            articles = []
            for result in response.get("results", []):
                article = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "published_date": result.get("published_date", ""),
                    "source": result.get("source", ""),
                    "score": result.get("score", 0.0)
                }
                articles.append(article)
            
            return {
                "symbol": symbol,
                "query": query,
                "articles": articles,
                "total_results": len(articles),
                "search_period": f"{days} days",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def search_company_news(self, company_name: str, days: int = 7, max_results: int = 10) -> Dict[str, Any]:
        """Search for news about a specific company"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = f"{company_name} company news business {start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
            
            response = self.client.search(
                query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=False,
                include_raw_content=False
            )
            
            articles = []
            for result in response.get("results", []):
                article = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "published_date": result.get("published_date", ""),
                    "source": result.get("source", ""),
                    "score": result.get("score", 0.0)
                }
                articles.append(article)
            
            return {
                "company": company_name,
                "query": query,
                "articles": articles,
                "total_results": len(articles),
                "search_period": f"{days} days",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "company": company_name,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def search_sector_trends(self, sector: str, days: int = 30, max_results: int = 15) -> Dict[str, Any]:
        """Search for sector trends and industry news"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = f"{sector} industry trends market analysis {start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
            
            response = self.client.search(
                query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=False,
                include_raw_content=False
            )
            
            articles = []
            for result in response.get("results", []):
                article = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "published_date": result.get("published_date", ""),
                    "source": result.get("source", ""),
                    "score": result.get("score", 0.0)
                }
                articles.append(article)
            
            return {
                "sector": sector,
                "query": query,
                "articles": articles,
                "total_results": len(articles),
                "search_period": f"{days} days",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "sector": sector,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def search_earnings_reports(self, symbol: str, days: int = 30, max_results: int = 8) -> Dict[str, Any]:
        """Search for earnings reports and analysis"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = f"{symbol} earnings report Q4 Q3 Q2 Q1 results analysis {start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
            
            response = self.client.search(
                query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=False,
                include_raw_content=False
            )
            
            articles = []
            for result in response.get("results", []):
                article = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "published_date": result.get("published_date", ""),
                    "source": result.get("source", ""),
                    "score": result.get("score", 0.0)
                }
                articles.append(article)
            
            return {
                "symbol": symbol,
                "query": query,
                "articles": articles,
                "total_results": len(articles),
                "search_period": f"{days} days",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def search_market_sentiment(self, symbol: str, days: int = 7, max_results: int = 12) -> Dict[str, Any]:
        """Search for market sentiment and analyst opinions"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = f"{symbol} analyst rating buy hold sell recommendation sentiment {start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
            
            response = self.client.search(
                query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=False,
                include_raw_content=False
            )
            
            articles = []
            for result in response.get("results", []):
                article = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "published_date": result.get("published_date", ""),
                    "source": result.get("source", ""),
                    "score": result.get("score", 0.0)
                }
                articles.append(article)
            
            return {
                "symbol": symbol,
                "query": query,
                "articles": articles,
                "total_results": len(articles),
                "search_period": f"{days} days",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def comprehensive_news_search(self, symbol: str, company_name: str = None, days: int = 7) -> Dict[str, Any]:
        """Perform comprehensive news search combining multiple search types"""
        try:
            # Initialize results
            all_results = {
                "symbol": symbol,
                "company_name": company_name,
                "search_period": f"{days} days",
                "market_news": None,
                "company_news": None,
                "earnings_reports": None,
                "market_sentiment": None,
                "combined_articles": [],
                "last_updated": datetime.now().isoformat()
            }
            
            # Search market news
            market_news = self.search_market_news(symbol, days, max_results=8)
            all_results["market_news"] = market_news
            if "articles" in market_news:
                all_results["combined_articles"].extend(market_news["articles"])
            
            # Search company news if company name provided
            if company_name:
                company_news = self.search_company_news(company_name, days, max_results=6)
                all_results["company_news"] = company_news
                if "articles" in company_news:
                    all_results["combined_articles"].extend(company_news["articles"])
            
            # Search earnings reports
            earnings_reports = self.search_earnings_reports(symbol, days, max_results=5)
            all_results["earnings_reports"] = earnings_reports
            if "articles" in earnings_reports:
                all_results["combined_articles"].extend(earnings_reports["articles"])
            
            # Search market sentiment
            market_sentiment = self.search_market_sentiment(symbol, days, max_results=6)
            all_results["market_sentiment"] = market_sentiment
            if "articles" in market_sentiment:
                all_results["combined_articles"].extend(market_sentiment["articles"])
            
            # Remove duplicates based on URL
            seen_urls = set()
            unique_articles = []
            for article in all_results["combined_articles"]:
                if article.get("url") not in seen_urls:
                    unique_articles.append(article)
                    seen_urls.add(article.get("url"))
            
            all_results["combined_articles"] = unique_articles
            all_results["total_unique_articles"] = len(unique_articles)
            
            return all_results
            
        except Exception as e:
            return {
                "symbol": symbol,
                "company_name": company_name,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def get_news_summary(self, articles: List[Dict[str, Any]], llm) -> Dict[str, Any]:
        """Generate a summary of news articles using LLM"""
        try:
            if not articles:
                return {
                    "summary": "No articles to summarize",
                    "key_points": [],
                    "sentiment": "neutral"
                }
            
            # Prepare articles text
            articles_text = ""
            for i, article in enumerate(articles[:8]):  # Limit to 8 articles
                articles_text += f"Article {i+1}: {article.get('title', 'No title')}\n"
                articles_text += f"Source: {article.get('source', 'Unknown')}\n"
                articles_text += f"Content: {article.get('content', 'No content')[:300]}...\n\n"
            
            prompt = f"""
            Analyze the following news articles and provide:
            1. A comprehensive summary (3-4 sentences)
            2. Key points mentioned (3-5 bullet points)
            3. Overall sentiment (positive/negative/neutral)
            4. Confidence level in sentiment (0-1)
            
            Articles:
            {articles_text}
            
            Return the analysis in JSON format:
            {{
                "summary": "Comprehensive summary",
                "key_points": ["point1", "point2", "point3"],
                "sentiment": "positive/negative/neutral",
                "confidence": 0.8
            }}
            """
            
            response = llm.invoke([{"role": "user", "content": prompt}])
            return json.loads(response.content)
            
        except Exception as e:
            return {
                "summary": f"Error generating summary: {str(e)}",
                "key_points": [],
                "sentiment": "neutral",
                "confidence": 0.0
            }
    
    def extract_topics(self, articles: List[Dict[str, Any]]) -> List[str]:
        """Extract key topics from articles"""
        try:
            all_text = " ".join([article.get("title", "") + " " + article.get("content", "") for article in articles])
            
            # Define relevant financial topics
            topics = [
                "earnings", "revenue", "profit", "growth", "dividend", "merger", "acquisition",
                "regulation", "lawsuit", "innovation", "expansion", "market", "competition",
                "leadership", "strategy", "forecast", "guidance", "analyst", "rating",
                "buy", "sell", "hold", "upgrade", "downgrade", "target", "price",
                "quarterly", "annual", "report", "results", "outlook", "guidance"
            ]
            
            found_topics = []
            for topic in topics:
                if topic.lower() in all_text.lower():
                    found_topics.append(topic)
            
            return list(set(found_topics))[:15]  # Return top 15 unique topics
            
        except Exception as e:
            return []
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Tavily API connection"""
        try:
            response = self.client.search("test", max_results=1)
            return {
                "status": "connected",
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
import asyncio
import os
import sys
import json
from datetime import datetime, timedelta

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.stock_data_agent import StockDataAgent
from agents.news_agent import NewsAgent
from agents.financial_agent import FinancialAgent
from tools.tavily_search import TavilySearchTool
from tools.financial_datasets_api import FinancialDatasetsAPI
from utils.llm import get_llm
from config import settings, validate_settings

async def test_stock_data_agent():
    """Test the Stock Data Agent"""
    print("📊 Testing Stock Data Agent...")
    
    try:
        llm = get_llm()
        agent = StockDataAgent(llm)
        
        # Test single stock
        result = agent.get_stock_data("AAPL", "6mo")
        print(f"✅ AAPL data retrieved successfully")
        print(f"   Current price: ${result['current_data']['price']:.2f}")
        print(f"   Daily change: {result['current_data']['change_percent']:.2f}%")
        print(f"   Period return: {result['performance']['period_return']:.2f}%")
        
        # Test multiple stocks
        stocks = ["AAPL", "MSFT", "GOOGL"]
        multi_result = agent.get_multiple_stocks(stocks)
        print(f"✅ Multiple stocks data retrieved: {len(multi_result)} stocks")
        
        return True
        
    except Exception as e:
        print(f"❌ Stock Data Agent test failed: {e}")
        return False

async def test_news_agent():
    """Test the News Agent"""
    print("📰 Testing News Agent...")
    
    try:
        llm = get_llm()
        agent = NewsAgent(llm, settings.tavily_api_key)
        
        # Test news sentiment analysis
        result = agent.get_news_sentiment("AAPL", 7)
        print(f"✅ News sentiment analysis completed")
        print(f"   Overall sentiment: {result['overall_sentiment']}")
        print(f"   Articles analyzed: {result['articles_count']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        
        # Test trending topics
        trending = agent.get_trending_topics(["AAPL", "MSFT"])
        print(f"✅ Trending topics retrieved: {len(trending)} stocks")
        
        return True
        
    except Exception as e:
        print(f"❌ News Agent test failed: {e}")
        return False

async def test_financial_agent():
    """Test the Financial Agent"""
    print("💰 Testing Financial Agent...")
    
    try:
        llm = get_llm()
        agent = FinancialAgent(llm)
        
        # Test financial data retrieval
        result = agent.get_financial_data("AAPL")
        print(f"✅ Financial data retrieved successfully")
        
        # Check key metrics
        key_metrics = result.get("key_metrics", {})
        print(f"   Market cap: ${key_metrics.get('market_cap', 0):,.0f}")
        print(f"   P/E ratio: {key_metrics.get('trailing_pe', 0):.2f}")
        print(f"   Revenue growth: {key_metrics.get('revenue_growth', 0):.2%}")
        
        # Check financial health
        financial_health = result.get("financial_health", {})
        print(f"   Health score: {financial_health.get('health_score', 0)}/100")
        print(f"   Overall health: {financial_health.get('overall_health', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Financial Agent test failed: {e}")
        return False

async def test_tavily_search():
    """Test Tavily Search Tool"""
    print("🔍 Testing Tavily Search Tool...")
    
    try:
        if not settings.tavily_api_key:
            print("⚠️  Tavily API key not set, skipping test")
            return True
        
        search_tool = TavilySearchTool(settings.tavily_api_key)
        
        # Test market news search
        result = search_tool.search_market_news("AAPL", 7, 5)
        print(f"✅ Market news search completed")
        print(f"   Articles found: {result['total_results']}")
        
        # Test comprehensive search
        comprehensive = search_tool.comprehensive_news_search("AAPL", "Apple Inc.", 7)
        print(f"✅ Comprehensive search completed")
        print(f"   Unique articles: {comprehensive['total_unique_articles']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tavily Search test failed: {e}")
        return False

async def test_financial_datasets_api():
    """Test Financial Datasets API"""
    print("📈 Testing Financial Datasets API...")
    
    try:
        if not settings.financial_datasets_api_key:
            print("⚠️  Financial Datasets API key not set, skipping test")
            return True
        
        api = FinancialDatasetsAPI(settings.financial_datasets_api_key)
        
        # Test API connection
        connection = api.test_connection()
        if connection['status'] == 'connected':
            print(f"✅ API connection successful")
            print(f"   Response time: {connection['response_time']:.2f}s")
        else:
            print(f"❌ API connection failed: {connection.get('error', 'Unknown error')}")
            return False
        
        # Test company fundamentals
        fundamentals = api.get_company_fundamentals("AAPL")
        if "error" not in fundamentals:
            print(f"✅ Company fundamentals retrieved")
        else:
            print(f"⚠️  Fundamentals test failed: {fundamentals['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Financial Datasets API test failed: {e}")
        return False

async def test_report_generation():
    """Test Report Generation"""
    print("📄 Testing Report Generation...")
    
    try:
        from utils.report_generator import ReportGenerator
        
        generator = ReportGenerator()
        
        # Create test data
        test_data = {
            "stock_symbol": "AAPL",
            "analysis_date": datetime.now().isoformat(),
            "analysis_result": {
                "summary": "Test analysis summary",
                "recommendation": "Buy",
                "confidence_score": 0.85,
                "sentiment_analysis": "Positive",
                "risk_factors": ["Market volatility", "Competition"]
            },
            "raw_data": {
                "stock_data": {
                    "current_data": {"price": 150.00, "change_percent": 1.5},
                    "performance": {"period_return": 12.5, "volatility": 18.2}
                },
                "news_data": {
                    "overall_sentiment": "positive",
                    "confidence": 0.75,
                    "articles_count": 15
                },
                "financial_data": {
                    "financial_health": {
                        "health_score": 85,
                        "overall_health": "Excellent"
                    }
                }
            }
        }
        
        # Test JSON report generation
        json_path = generator.generate_json_report(test_data)
        if json_path and os.path.exists(json_path):
            print(f"✅ JSON report generated: {json_path}")
        else:
            print(f"❌ JSON report generation failed")
            return False
        
        # Test PDF report generation
        pdf_path = generator.generate_pdf_report(test_data)
        if pdf_path and os.path.exists(pdf_path):
            print(f"✅ PDF report generated: {pdf_path}")
        else:
            print(f"❌ PDF report generation failed")
            return False
        
        # Test summary report
        summary = generator.generate_summary_report(test_data)
        if "error" not in summary:
            print(f"✅ Summary report generated")
        else:
            print(f"❌ Summary report generation failed: {summary['error']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Report generation test failed: {e}")
        return False

async def test_llm_connection():
    """Test LLM connection"""
    print("🤖 Testing LLM Connection...")
    
    try:
        llm = get_llm()
        
        # Simple test prompt
        response = llm.invoke([{"role": "user", "content": "Hello! Please respond with 'LLM connection successful'"}])
        
        if "successful" in response.content.lower():
            print(f"✅ LLM connection successful")
            print(f"   Model: {settings.deepseek_model}")
            print(f"   Response: {response.content}")
            return True
        else:
            print(f"❌ LLM connection test failed")
            return False
            
    except Exception as e:
        print(f"❌ LLM connection test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🧪 Running Comprehensive Tests")
    print("=" * 60)
    
    # Test configuration
    print("🔧 Testing Configuration...")
    try:
        validate_settings()
        print("✅ Configuration validated successfully")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Run all tests
    tests = [
        ("LLM Connection", test_llm_connection),
        ("Stock Data Agent", test_stock_data_agent),
        ("News Agent", test_news_agent),
        ("Financial Agent", test_financial_agent),
        ("Tavily Search", test_tavily_search),
        ("Financial Datasets API", test_financial_datasets_api),
        ("Report Generation", test_report_generation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'-' * 40}")
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'=' * 60}")
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please check the configuration and try again.")
    
    return passed == total

async def main():
    """Main function"""
    print("🚀 Stock Analysis Agent - Test Suite")
    print("=" * 60)
    
    # Run all tests
    success = await run_all_tests()
    
    if success:
        print(f"\n✅ System is ready! You can now run the interactive demo:")
        print(f"   python examples/interactive_demo.py")
    else:
        print(f"\n❌ Some tests failed. Please check the configuration and try again.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
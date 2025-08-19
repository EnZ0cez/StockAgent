from typing import Dict, Any, Optional, List
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
import asyncio
import json

from ..utils.llm import get_llm
from ..config import settings

class StockAnalysisState:
    """State management for stock analysis workflow"""
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.stock_symbol: str = ""
        self.time_period: str = ""
        self.news_days: int = 0
        self.stock_data: Optional[Dict[str, Any]] = None
        self.news_data: Optional[Dict[str, Any]] = None
        self.financial_data: Optional[Dict[str, Any]] = None
        self.analysis_result: Optional[Dict[str, Any]] = None
        self.current_agent: str = ""
        self.error: Optional[str] = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization"""
        return {
            "messages": self.messages,
            "stock_symbol": self.stock_symbol,
            "time_period": self.time_period,
            "news_days": self.news_days,
            "stock_data": self.stock_data,
            "news_data": self.news_data,
            "financial_data": self.financial_data,
            "analysis_result": self.analysis_result,
            "current_agent": self.current_agent,
            "error": self.error
        }

class StockAnalysisCoordinator:
    """Main coordinator for stock analysis agents"""
    
    def __init__(self):
        self.llm = get_llm()
        self.state = StockAnalysisState()
        self.graph = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for agent coordination"""
        workflow = StateGraph(StockAnalysisState)
        
        # Add nodes for each agent
        workflow.add_node("coordinator", self._coordinate_task)
        workflow.add_node("stock_data_agent", self._get_stock_data)
        workflow.add_node("news_agent", self._get_news_data)
        workflow.add_node("financial_agent", self._get_financial_data)
        workflow.add_node("analysis_agent", self._analyze_data)
        workflow.add_node("report_agent", self._generate_report)
        
        # Define the workflow
        workflow.set_entry_point("coordinator")
        
        workflow.add_edge("coordinator", "stock_data_agent")
        workflow.add_edge("stock_data_agent", "news_agent")
        workflow.add_edge("news_agent", "financial_agent")
        workflow.add_edge("financial_agent", "analysis_agent")
        workflow.add_edge("analysis_agent", "report_agent")
        workflow.add_edge("report_agent", END)
        
        return workflow.compile()
    
    def _coordinate_task(self, state: StockAnalysisState, config: RunnableConfig) -> StockAnalysisState:
        """Coordinate the initial task and route to appropriate agents"""
        state.current_agent = "coordinator"
        
        # Extract user query from messages
        if state.messages:
            user_message = state.messages[-1]["content"]
            
            # Parse query for stock symbol and parameters
            parsed_query = self._parse_user_query(user_message)
            state.stock_symbol = parsed_query.get("symbol", settings.default_stock_symbol)
            state.time_period = parsed_query.get("time_period", settings.default_time_period)
            state.news_days = parsed_query.get("news_days", settings.default_news_days)
        
        return state
    
    def _parse_user_query(self, query: str) -> Dict[str, Any]:
        """Parse user query to extract stock symbol and parameters"""
        # Simple parsing logic - can be enhanced with LLM
        import re
        
        # Extract stock symbol (e.g., AAPL, MSFT, GOOGL)
        symbol_match = re.search(r'\b[A-Z]{1,5}\b', query.upper())
        symbol = symbol_match.group(0) if symbol_match else settings.default_stock_symbol
        
        # Extract time period
        period_match = re.search(r'\b(\d+[ymwd])\b', query.lower())
        time_period = period_match.group(1) if period_match else settings.default_time_period
        
        # Extract news days
        days_match = re.search(r'\b(\d+)\s*(?:days?|news)\b', query.lower())
        news_days = int(days_match.group(1)) if days_match else settings.default_news_days
        
        return {
            "symbol": symbol,
            "time_period": time_period,
            "news_days": news_days
        }
    
    def _get_stock_data(self, state: StockAnalysisState, config: RunnableConfig) -> StockAnalysisState:
        """Get real-time stock price data"""
        state.current_agent = "stock_data_agent"
        
        try:
            from ..agents.stock_data_agent import StockDataAgent
            stock_agent = StockDataAgent(self.llm)
            
            stock_data = stock_agent.get_stock_data(
                state.stock_symbol, 
                state.time_period
            )
            
            state.stock_data = stock_data
            state.messages.append({
                "role": "assistant",
                "content": f"Retrieved stock data for {state.stock_symbol}",
                "agent": "stock_data_agent"
            })
            
        except Exception as e:
            state.error = f"Stock data error: {str(e)}"
            state.messages.append({
                "role": "assistant",
                "content": f"Error retrieving stock data: {str(e)}",
                "agent": "stock_data_agent"
            })
        
        return state
    
    def _get_news_data(self, state: StockAnalysisState, config: RunnableConfig) -> StockAnalysisState:
        """Get news sentiment data"""
        state.current_agent = "news_agent"
        
        try:
            from ..agents.news_agent import NewsAgent
            news_agent = NewsAgent(self.llm)
            
            news_data = news_agent.get_news_sentiment(
                state.stock_symbol,
                state.news_days
            )
            
            state.news_data = news_data
            state.messages.append({
                "role": "assistant",
                "content": f"Retrieved news sentiment for {state.stock_symbol}",
                "agent": "news_agent"
            })
            
        except Exception as e:
            state.error = f"News data error: {str(e)}"
            state.messages.append({
                "role": "assistant",
                "content": f"Error retrieving news data: {str(e)}",
                "agent": "news_agent"
            })
        
        return state
    
    def _get_financial_data(self, state: StockAnalysisState, config: RunnableConfig) -> StockAnalysisState:
        """Get historical financial data"""
        state.current_agent = "financial_agent"
        
        try:
            from ..agents.financial_agent import FinancialAgent
            financial_agent = FinancialAgent(self.llm)
            
            financial_data = financial_agent.get_financial_data(
                state.stock_symbol
            )
            
            state.financial_data = financial_data
            state.messages.append({
                "role": "assistant",
                "content": f"Retrieved financial data for {state.stock_symbol}",
                "agent": "financial_agent"
            })
            
        except Exception as e:
            state.error = f"Financial data error: {str(e)}"
            state.messages.append({
                "role": "assistant",
                "content": f"Error retrieving financial data: {str(e)}",
                "agent": "financial_agent"
            })
        
        return state
    
    def _analyze_data(self, state: StockAnalysisState, config: RunnableConfig) -> StockAnalysisState:
        """Analyze all collected data"""
        state.current_agent = "analysis_agent"
        
        try:
            analysis_prompt = f"""
            Analyze the following stock data for {state.stock_symbol}:
            
            Stock Data: {json.dumps(state.stock_data, indent=2) if state.stock_data else 'Not available'}
            News Sentiment: {json.dumps(state.news_data, indent=2) if state.news_data else 'Not available'}
            Financial Data: {json.dumps(state.financial_data, indent=2) if state.financial_data else 'Not available'}
            
            Provide a comprehensive analysis including:
            1. Current stock performance
            2. News sentiment impact
            3. Financial health assessment
            4. Risk factors
            5. Investment recommendation (Buy/Hold/Sell)
            
            Return the analysis in JSON format with the following structure:
            {{
                "summary": "Brief overview",
                "performance_analysis": "Detailed performance analysis",
                "sentiment_analysis": "News sentiment impact",
                "financial_health": "Financial health assessment",
                "risk_factors": ["List of risk factors"],
                "recommendation": "Buy/Hold/Sell with reasoning",
                "confidence_score": 0.8,
                "timestamp": "2024-01-01T00:00:00Z"
            }}
            """
            
            response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
            analysis_result = json.loads(response.content)
            
            state.analysis_result = analysis_result
            state.messages.append({
                "role": "assistant",
                "content": f"Completed analysis for {state.stock_symbol}",
                "agent": "analysis_agent"
            })
            
        except Exception as e:
            state.error = f"Analysis error: {str(e)}"
            state.messages.append({
                "role": "assistant",
                "content": f"Error analyzing data: {str(e)}",
                "agent": "analysis_agent"
            })
        
        return state
    
    def _generate_report(self, state: StockAnalysisState, config: RunnableConfig) -> StockAnalysisState:
        """Generate final report"""
        state.current_agent = "report_agent"
        
        try:
            from ..utils.report_generator import ReportGenerator
            report_generator = ReportGenerator()
            
            report_data = {
                "stock_symbol": state.stock_symbol,
                "analysis_date": datetime.now().isoformat(),
                "analysis_result": state.analysis_result,
                "raw_data": {
                    "stock_data": state.stock_data,
                    "news_data": state.news_data,
                    "financial_data": state.financial_data
                },
                "conversation_history": state.messages
            }
            
            # Generate both PDF and JSON reports
            pdf_report = report_generator.generate_pdf_report(report_data)
            json_report = report_generator.generate_json_report(report_data)
            
            state.analysis_result["reports"] = {
                "pdf_path": pdf_report,
                "json_path": json_report
            }
            
            state.messages.append({
                "role": "assistant",
                "content": f"Generated investment report for {state.stock_symbol}",
                "agent": "report_agent"
            })
            
        except Exception as e:
            state.error = f"Report generation error: {str(e)}"
            state.messages.append({
                "role": "assistant",
                "content": f"Error generating report: {str(e)}",
                "agent": "report_agent"
            })
        
        return state
    
    async def analyze_stock(self, query: str) -> Dict[str, Any]:
        """Main method to analyze a stock"""
        # Initialize state
        self.state = StockAnalysisState()
        self.state.messages.append({
            "role": "user",
            "content": query,
            "timestamp": datetime.now().isoformat()
        })
        
        # Run the workflow
        try:
            result = await self.graph.ainvoke(self.state)
            return {
                "success": True,
                "state": result.to_dict(),
                "analysis_result": result.analysis_result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "state": self.state.to_dict()
            }
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation"""
        return {
            "stock_symbol": self.state.stock_symbol,
            "current_agent": self.state.current_agent,
            "message_count": len(self.state.messages),
            "has_error": self.state.error is not None,
            "has_analysis": self.state.analysis_result is not None
        }
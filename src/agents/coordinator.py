from typing import Dict, Any, Optional, List, TypedDict
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
import asyncio
import json

from src.utils.llm import get_llm
from src.config import settings

class StockAnalysisState(TypedDict):
    """State management for stock analysis workflow"""
    messages: List[Dict[str, Any]]
    stock_symbol: str
    time_period: str
    news_days: int
    stock_data: Optional[Dict[str, Any]]
    news_data: Optional[Dict[str, Any]]
    financial_data: Optional[Dict[str, Any]]
    analysis_result: Optional[Dict[str, Any]]
    current_agent: str
    error: Optional[str]

class StockAnalysisCoordinator:
    """Main coordinator for stock analysis agents"""
    
    def __init__(self):
        self.llm = get_llm()
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
    
    def _coordinate_task(self, state: StockAnalysisState, config: RunnableConfig) -> Dict[str, Any]:
        """Coordinate the initial task and route to appropriate agents"""
        updates = {"current_agent": "coordinator"}
        
        # Extract user query from messages
        if state.get("messages"):
            user_message = state["messages"][-1]["content"]
            
            # Parse query for stock symbol and parameters
            parsed_query = self._parse_user_query(user_message)
            updates.update({
                "stock_symbol": parsed_query.get("symbol", settings.default_stock_symbol),
                "time_period": parsed_query.get("time_period", settings.default_time_period),
                "news_days": parsed_query.get("news_days", settings.default_news_days)
            })
        
        return updates
    
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
    
    def _get_stock_data(self, state: StockAnalysisState, config: RunnableConfig) -> Dict[str, Any]:
        """Get real-time stock price data"""
        updates = {"current_agent": "stock_data_agent"}
        
        try:
            from src.agents.stock_data_agent import StockDataAgent
            stock_agent = StockDataAgent(self.llm)
            
            stock_data = stock_agent.get_stock_data(
                state.get("stock_symbol", settings.default_stock_symbol), 
                state.get("time_period", settings.default_time_period)
            )
            
            updates["stock_data"] = stock_data
            
            # Update messages
            new_messages = list(state.get("messages", []))
            new_messages.append({
                "role": "assistant",
                "content": f"Retrieved stock data for {state.get('stock_symbol')}",
                "agent": "stock_data_agent"
            })
            updates["messages"] = new_messages
            
        except Exception as e:
            updates["error"] = f"Stock data error: {str(e)}"
            new_messages = list(state.get("messages", []))
            new_messages.append({
                "role": "assistant",
                "content": f"Error retrieving stock data: {str(e)}",
                "agent": "stock_data_agent"
            })
            updates["messages"] = new_messages
        
        return updates
    
    def _get_news_data(self, state: StockAnalysisState, config: RunnableConfig) -> Dict[str, Any]:
        """Get news sentiment data"""
        return {"current_agent": "news_agent", "news_data": {"status": "skipped"}}
    
    def _get_financial_data(self, state: StockAnalysisState, config: RunnableConfig) -> Dict[str, Any]:
        """Get financial data"""
        return {"current_agent": "financial_agent", "financial_data": {"status": "skipped"}}
    
    def _analyze_data(self, state: StockAnalysisState, config: RunnableConfig) -> Dict[str, Any]:
        """Analyze collected data"""
        updates = {"current_agent": "analysis_agent"}
        
        try:
            stock_data = state.get("stock_data")
            stock_symbol = state.get("stock_symbol", "UNKNOWN")
            
            if not stock_data or "error" in stock_data:
                # If stock data failed, provide basic analysis
                updates["analysis_result"] = {
                    "summary": f"Unable to analyze {stock_symbol} due to data issues",
                    "recommendation": "N/A",
                    "confidence_score": 0.0,
                    "analysis": "Data retrieval failed",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Create analysis prompt with real data
                current_data = stock_data.get("current_data", {}) or {}
                performance = stock_data.get("performance", {}) or {}
                technical = stock_data.get("technical_indicators", {}) or {}
                company_info = stock_data.get("company_info", {}) or {}
                
                analysis_prompt = f"""
                Analyze the following stock data for {stock_symbol} and provide investment recommendations:
                
                **Current Market Data:**
                - Price: ${current_data.get('price', 0):.2f}
                - Change: {current_data.get('change', 0):+.2f} ({current_data.get('change_percent', 0):+.2f}%)
                - Volume: {current_data.get('volume', 0):,}
                - Market Cap: ${current_data.get('market_cap', 0):,}
                - P/E Ratio: {current_data.get('pe_ratio', 'N/A')}
                
                **Company Information:**
                - Name: {company_info.get('name', 'N/A')}
                - Sector: {company_info.get('sector', 'N/A')}
                - Industry: {company_info.get('industry', 'N/A')}
                
                **Technical Analysis:**
                - RSI: {technical.get('rsi') or 'N/A'}
                - 50-day MA: {'${:.2f}'.format(performance.get('ma_50')) if performance.get('ma_50') else 'N/A'}
                - 200-day MA: {'${:.2f}'.format(performance.get('ma_200')) if performance.get('ma_200') else 'N/A'}
                - Volatility: {'{:.2f}%'.format(performance.get('volatility')) if performance.get('volatility') else 'N/A'}
                
                **Performance:**
                - Period Return: {'{:.2f}%'.format(performance.get('period_return')) if performance.get('period_return') else 'N/A'}
                - 52-week High: {'${:.2f}'.format(performance.get('high_52w')) if performance.get('high_52w') else 'N/A'}
                - 52-week Low: {'${:.2f}'.format(performance.get('low_52w')) if performance.get('low_52w') else 'N/A'}
                
                Based on this data, provide:
                1. Investment recommendation (Buy/Hold/Sell)
                2. Confidence score (0.0-1.0)
                3. Key reasons for the recommendation
                4. Risk factors to consider
                5. Price targets if applicable
                
                Be concise but thorough in your analysis.
                """
                
                response = self.llm.invoke([{"role": "user", "content": analysis_prompt}])
                
                # Parse the LLM response (simplified - could be enhanced)
                analysis_text = response.content
                
                # Extract recommendation (basic parsing)
                recommendation = "Hold"  # Default
                confidence_score = 0.7   # Default
                
                if "buy" in analysis_text.lower() and "don't buy" not in analysis_text.lower():
                    recommendation = "Buy"
                    confidence_score = 0.8
                elif "sell" in analysis_text.lower():
                    recommendation = "Sell"
                    confidence_score = 0.75
                
                updates["analysis_result"] = {
                    "summary": f"Analysis completed for {stock_symbol}",
                    "recommendation": recommendation,
                    "confidence_score": confidence_score,
                    "analysis": analysis_text,
                    "stock_price": current_data.get('price', 0),
                    "change_percent": current_data.get('change_percent', 0),
                    "company_name": company_info.get('name', stock_symbol),
                    "timestamp": datetime.now().isoformat()
                }
            
            # Update messages
            new_messages = list(state.get("messages", []))
            new_messages.append({
                "role": "assistant",
                "content": f"Completed analysis for {stock_symbol}",
                "agent": "analysis_agent"
            })
            updates["messages"] = new_messages
            
        except Exception as e:
            updates["error"] = f"Analysis error: {str(e)}"
            new_messages = list(state.get("messages", []))
            new_messages.append({
                "role": "assistant",
                "content": f"Error during analysis: {str(e)}",
                "agent": "analysis_agent"
            })
            updates["messages"] = new_messages
        
        return updates
    
    def _generate_report(self, state: StockAnalysisState, config: RunnableConfig) -> Dict[str, Any]:
        """Generate final report"""
        return {"current_agent": "report_agent"}
    
    async def analyze_stock(self, query: str) -> Dict[str, Any]:
        """Main method to analyze a stock"""
        # Initialize state
        initial_state: StockAnalysisState = {
            "messages": [{
                "role": "user",
                "content": query,
                "timestamp": datetime.now().isoformat()
            }],
            "stock_symbol": "",
            "time_period": "1y",
            "news_days": 7,
            "stock_data": None,
            "news_data": None,
            "financial_data": None,
            "analysis_result": None,
            "current_agent": "",
            "error": None
        }
        
        # Run the workflow
        try:
            result = await self.graph.ainvoke(initial_state)
            return {
                "success": True,
                "state": result,
                "analysis_result": result.get("analysis_result")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "state": initial_state
            }
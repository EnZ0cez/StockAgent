import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re

from src.agents.coordinator import StockAnalysisCoordinator
from src.config import settings
from src.utils.llm import get_llm

class ConversationManager:
    """Manages multi-turn conversations with the stock analysis agent"""
    
    def __init__(self):
        self.coordinator = StockAnalysisCoordinator()
        self.llm = get_llm()
        self.conversation_history = []
        self.current_context = {
            "symbol": None,
            "analysis_complete": False,
            "last_analysis": None,
            "follow_up_questions": []
        }
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process a user message and return response"""
        try:
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Analyze user intent
            intent = self._analyze_intent(message)
            
            # Process based on intent
            if intent["type"] == "new_analysis":
                response = await self._handle_new_analysis(message)
            elif intent["type"] == "follow_up":
                response = await self._handle_follow_up(message)
            elif intent["type"] == "clarification":
                response = await self._handle_clarification(message)
            elif intent["type"] == "comparison":
                response = await self._handle_comparison(message)
            elif intent["type"] == "general_question":
                response = await self._handle_general_question(message)
            else:
                response = await self._handle_unknown_intent(message)
            
            # Add response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response["message"],
                "timestamp": datetime.now().isoformat(),
                "data": response.get("data", {})
            })
            
            return response
            
        except Exception as e:
            error_response = {
                "success": False,
                "message": f"I apologize, but I encountered an error: {str(e)}",
                "data": {"error": str(e)}
            }
            
            self.conversation_history.append({
                "role": "assistant",
                "content": error_response["message"],
                "timestamp": datetime.now().isoformat(),
                "data": error_response.get("data", {})
            })
            
            return error_response
    
    def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user intent using LLM"""
        try:
            prompt = f"""
            Analyze the user's message to determine their intent. The user is interacting with a stock analysis AI agent.
            
            User message: "{message}"
            
            Current context:
            - Previous analysis symbol: {self.current_context.get('symbol')}
            - Analysis complete: {self.current_context.get('analysis_complete')}
            
            Classify the intent as one of the following:
            1. "new_analysis" - User wants to analyze a new stock
            2. "follow_up" - User is asking follow-up questions about previous analysis
            3. "clarification" - User is asking for clarification about previous analysis
            4. "comparison" - User wants to compare stocks
            5. "general_question" - User is asking general questions about investing/markets
            6. "unknown" - Cannot determine intent
            
            Extract relevant information:
            - Stock symbols mentioned
            - Time periods mentioned
            - Specific questions asked
            - Comparison parameters
            
            Return the analysis in JSON format:
            {{
                "type": "intent_type",
                "confidence": 0.8,
                "symbols": ["AAPL", "MSFT"],
                "time_period": "1y",
                "specific_questions": ["What if interest rates rise?"],
                "comparison_parameters": ["performance", "financial_health"]
            }}
            """
            
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            return json.loads(response.content)
            
        except Exception as e:
            return {
                "type": "unknown",
                "confidence": 0.0,
                "symbols": [],
                "time_period": None,
                "specific_questions": [],
                "comparison_parameters": []
            }
    
    async def _handle_new_analysis(self, message: str) -> Dict[str, Any]:
        """Handle new stock analysis request"""
        try:
            # Extract stock symbol from message
            symbol_match = re.search(r'\b[A-Z]{1,5}\b', message.upper())
            symbol = symbol_match.group(0) if symbol_match else settings.default_stock_symbol
            
            # Update context
            self.current_context["symbol"] = symbol
            self.current_context["analysis_complete"] = False
            
            # Perform analysis
            result = await self.coordinator.analyze_stock(message)
            
            if result["success"]:
                self.current_context["analysis_complete"] = True
                self.current_context["last_analysis"] = result
                
                # Generate follow-up questions
                follow_up_questions = self._generate_follow_up_questions(result)
                self.current_context["follow_up_questions"] = follow_up_questions
                
                analysis_result = result.get("analysis_result", {})
                response_message = f"""
                I've completed the analysis for {symbol}.
                
                **Key Findings:**
                - Recommendation: {analysis_result.get('recommendation', 'N/A')}
                - Confidence Score: {analysis_result.get('confidence_score', 0):.2f}
                - Overall Sentiment: {analysis_result.get('sentiment_analysis', 'N/A')}
                
                **Reports Generated:**
                - PDF Report: {analysis_result.get('reports', {}).get('pdf_path', 'Not available')}
                - JSON Report: {analysis_result.get('reports', {}).get('json_path', 'Not available')}
                
                **You can ask me follow-up questions like:**
                {self._format_follow_up_questions(follow_up_questions)}
                """
            else:
                response_message = f"I apologize, but I couldn't complete the analysis for {symbol}. Error: {result.get('error', 'Unknown error')}"
            
            return {
                "success": result["success"],
                "message": response_message,
                "data": {
                    "type": "new_analysis",
                    "symbol": symbol,
                    "analysis_result": result.get("analysis_result"),
                    "follow_up_questions": self.current_context.get("follow_up_questions", [])
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error analyzing stock: {str(e)}",
                "data": {"error": str(e)}
            }
    
    async def _handle_follow_up(self, message: str) -> Dict[str, Any]:
        """Handle follow-up questions about previous analysis"""
        try:
            if not self.current_context.get("analysis_complete"):
                return {
                    "success": False,
                    "message": "I don't have a previous analysis to refer to. Please ask me to analyze a stock first.",
                    "data": {"type": "follow_up", "error": "No previous analysis"}
                }
            
            # Get previous analysis
            previous_analysis = self.current_context.get("last_analysis")
            symbol = self.current_context.get("symbol")
            
            # Generate follow-up response
            follow_up_response = await self._generate_follow_up_response(message, previous_analysis)
            
            return {
                "success": True,
                "message": follow_up_response["message"],
                "data": {
                    "type": "follow_up",
                    "symbol": symbol,
                    "question": message,
                    "answer": follow_up_response.get("answer", ""),
                    "additional_data": follow_up_response.get("additional_data", {})
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error handling follow-up question: {str(e)}",
                "data": {"error": str(e)}
            }
    
    async def _handle_clarification(self, message: str) -> Dict[str, Any]:
        """Handle clarification requests"""
        try:
            if not self.current_context.get("analysis_complete"):
                return {
                    "success": False,
                    "message": "I don't have a previous analysis to clarify. Please ask me to analyze a stock first.",
                    "data": {"type": "clarification", "error": "No previous analysis"}
                }
            
            # Generate clarification response
            clarification_response = await self._generate_clarification_response(message)
            
            return {
                "success": True,
                "message": clarification_response["message"],
                "data": {
                    "type": "clarification",
                    "question": message,
                    "answer": clarification_response.get("answer", "")
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error handling clarification: {str(e)}",
                "data": {"error": str(e)}
            }
    
    async def _handle_comparison(self, message: str) -> Dict[str, Any]:
        """Handle stock comparison requests"""
        try:
            # Extract symbols from message
            symbols = re.findall(r'\b[A-Z]{1,5}\b', message.upper())
            
            if len(symbols) < 2:
                return {
                    "success": False,
                    "message": "I need at least 2 stock symbols to compare. Please provide symbols like 'Compare AAPL and MSFT'",
                    "data": {"type": "comparison", "error": "Insufficient symbols"}
                }
            
            # Generate comparison
            comparison_response = await self._generate_comparison(symbols[:5])  # Limit to 5 symbols
            
            return {
                "success": True,
                "message": comparison_response["message"],
                "data": {
                    "type": "comparison",
                    "symbols": symbols[:5],
                    "comparison_data": comparison_response.get("comparison_data", {})
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error handling comparison: {str(e)}",
                "data": {"error": str(e)}
            }
    
    async def _handle_general_question(self, message: str) -> Dict[str, Any]:
        """Handle general investment questions"""
        try:
            prompt = f"""
            The user is asking a general question about investing or the stock market:
            
            Question: "{message}"
            
            Provide a helpful, educational response about investing principles, market concepts, or general financial advice.
            Remember to:
            - Be educational and informative
            - Provide balanced perspectives
            - Mention that this is not financial advice
            - Keep responses concise but helpful
            
            Return the response in JSON format:
            {{
                "answer": "Your educational response",
                "topics_covered": ["topic1", "topic2"],
                "disclaimer_needed": true
            }}
            """
            
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            result = json.loads(response.content)
            
            answer = result.get("answer", "")
            if result.get("disclaimer_needed", False):
                answer += "\n\n*Note: This information is for educational purposes only and should not be considered as financial advice.*"
            
            return {
                "success": True,
                "message": answer,
                "data": {
                    "type": "general_question",
                    "question": message,
                    "topics_covered": result.get("topics_covered", [])
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error handling general question: {str(e)}",
                "data": {"error": str(e)}
            }
    
    async def _handle_unknown_intent(self, message: str) -> Dict[str, Any]:
        """Handle unknown or unclear intent"""
        return {
            "success": False,
            "message": "I'm not sure what you're asking for. You can:\n• Ask me to analyze a stock (e.g., 'Analyze AAPL')\n• Ask follow-up questions about previous analysis\n• Compare multiple stocks\n• Ask general investing questions\n\nWhat would you like to know?",
            "data": {"type": "unknown_intent", "message": message}
        }
    
    def _generate_follow_up_questions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate relevant follow-up questions"""
        return [
            "What are the main risk factors for this stock?",
            "How might this stock perform if interest rates rise?",
            "What are the key growth drivers?",
            "How does this compare to its industry peers?",
            "What's the long-term investment potential?",
            "Should I consider buying, holding, or selling?",
            "What are the catalysts that could affect the stock price?",
            "How does the financial health look compared to last year?"
        ]
    
    def _format_follow_up_questions(self, questions: List[str]) -> str:
        """Format follow-up questions for display"""
        return "\n".join([f"• {q}" for q in questions[:5]])  # Show top 5 questions
    
    async def _generate_follow_up_response(self, question: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response to follow-up question"""
        try:
            analysis_data = analysis_result.get("analysis_result", {})
            raw_data = analysis_result.get("state", {}).get("to_dict", lambda: {})()
            
            prompt = f"""
            The user is asking a follow-up question about a stock analysis:
            
            Question: "{question}"
            
            Previous analysis results:
            - Symbol: {self.current_context.get('symbol')}
            - Recommendation: {analysis_data.get('recommendation', 'N/A')}
            - Summary: {analysis_data.get('summary', 'N/A')}
            - Risk factors: {analysis_data.get('risk_factors', [])}
            
            Available data includes stock performance, news sentiment, and financial information.
            
            Provide a specific, helpful response to their question based on the available analysis data.
            If you need to make assumptions, state them clearly.
            
            Return the response in JSON format:
            {{
                "answer": "Your specific answer to the question",
                "additional_data": {{"key": "value"}},
                "confidence": 0.8
            }}
            """
            
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            return json.loads(response.content)
            
        except Exception as e:
            return {
                "answer": f"I apologize, but I couldn't generate a response to your follow-up question: {str(e)}",
                "additional_data": {},
                "confidence": 0.0
            }
    
    async def _generate_clarification_response(self, question: str) -> Dict[str, Any]:
        """Generate response to clarification request"""
        try:
            prompt = f"""
            The user is asking for clarification about a previous stock analysis:
            
            Question: "{question}"
            
            Symbol: {self.current_context.get('symbol')}
            Analysis complete: {self.current_context.get('analysis_complete')}
            
            Provide a clear, helpful explanation to clarify their question about the analysis.
            Use simple language and provide context where helpful.
            
            Return the response in JSON format:
            {{
                "answer": "Your clarification response",
                "additional_data": {{"key": "value"}}
            }}
            """
            
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            return json.loads(response.content)
            
        except Exception as e:
            return {
                "answer": f"I apologize, but I couldn't provide clarification: {str(e)}",
                "additional_data": {}
            }
    
    async def _generate_comparison(self, symbols: List[str]) -> Dict[str, Any]:
        """Generate comparison between multiple stocks"""
        try:
            comparison_data = {}
            
            for symbol in symbols:
                # Get quick comparison data for each symbol
                try:
                    from src.agents.stock_data_agent import StockDataAgent
                    stock_agent = StockDataAgent(self.llm)
                    stock_data = stock_agent.get_stock_data(symbol, period="1y")
                    
                    comparison_data[symbol] = {
                        "current_price": stock_data.get("current_data", {}).get("price", 0),
                        "daily_change": stock_data.get("current_data", {}).get("change_percent", 0),
                        "period_return": stock_data.get("performance", {}).get("period_return", 0),
                        "market_cap": stock_data.get("current_data", {}).get("market_cap", 0),
                        "pe_ratio": stock_data.get("current_data", {}).get("pe_ratio", 0)
                    }
                except Exception as e:
                    comparison_data[symbol] = {"error": str(e)}
            
            # Generate comparison summary
            prompt = f"""
            Generate a comparison summary for these stocks: {', '.join(symbols)}
            
            Comparison data: {json.dumps(comparison_data, indent=2)}
            
            Provide a concise comparison highlighting key differences and similarities.
            Focus on performance, valuation, and relative strengths/weaknesses.
            
            Return the response in JSON format:
            {{
                "summary": "Comparison summary",
                "key_differences": ["difference1", "difference2"],
                "recommendation": "Brief comparison recommendation"
            }}
            """
            
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            summary_result = json.loads(response.content)
            
            message = f"""
            **Stock Comparison: {', '.join(symbols)}**
            
            {summary_result.get('summary', '')}
            
            **Key Differences:**
            {self._format_list(summary_result.get('key_differences', []))}
            
            **Data Comparison:**
            """
            
            for symbol, data in comparison_data.items():
                if "error" not in data:
                    message += f"\n**{symbol}:** ${data.get('current_price', 0):.2f} ({data.get('daily_change', 0):.2f}%) | Return: {data.get('period_return', 0):.2f}% | P/E: {data.get('pe_ratio', 0):.2f}"
            
            message += f"\n\n{summary_result.get('recommendation', '')}"
            
            return {
                "message": message,
                "comparison_data": comparison_data
            }
            
        except Exception as e:
            return {
                "message": f"Error generating comparison: {str(e)}",
                "comparison_data": {}
            }
    
    def _format_list(self, items: List[str]) -> str:
        """Format list items for display"""
        return "\n".join([f"• {item}" for item in items])
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation"""
        return {
            "total_messages": len(self.conversation_history),
            "current_symbol": self.current_context.get("symbol"),
            "analysis_complete": self.current_context.get("analysis_complete"),
            "follow_up_questions": self.current_context.get("follow_up_questions", []),
            "conversation_start": self.conversation_history[0]["timestamp"] if self.conversation_history else None
        }
    
    def reset_conversation(self) -> Dict[str, Any]:
        """Reset the conversation"""
        self.conversation_history = []
        self.current_context = {
            "symbol": None,
            "analysis_complete": False,
            "last_analysis": None,
            "follow_up_questions": []
        }
        
        return {
            "success": True,
            "message": "Conversation reset. You can start a new analysis.",
            "data": {"action": "reset_conversation"}
        }
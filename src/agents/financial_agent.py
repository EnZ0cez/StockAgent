import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

class FinancialAgent:
    """Agent for retrieving and analyzing historical financial data"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def get_financial_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive financial data for a company
        
        Args:
            symbol: Stock symbol (e.g., AAPL, MSFT)
        
        Returns:
            Dictionary containing financial data and analysis
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get financial statements
            financial_statements = self._get_financial_statements(ticker)
            
            # Get key financial metrics
            key_metrics = self._get_key_metrics(ticker)
            
            # Get historical financial data
            historical_financials = self._get_historical_financials(ticker)
            
            # Calculate financial ratios
            financial_ratios = self._calculate_financial_ratios(financial_statements)
            
            # Analyze financial health
            financial_health = self._analyze_financial_health(financial_statements, key_metrics)
            
            # Get earnings data
            earnings_data = self._get_earnings_data(ticker)
            
            result = {
                "symbol": symbol,
                "company_info": self._get_company_info(ticker),
                "financial_statements": financial_statements,
                "key_metrics": key_metrics,
                "financial_ratios": financial_ratios,
                "historical_financials": historical_financials,
                "earnings_data": earnings_data,
                "financial_health": financial_health,
                "last_updated": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def _get_financial_statements(self, ticker: yf.Ticker) -> Dict[str, Any]:
        """Get financial statements (Income Statement, Balance Sheet, Cash Flow)"""
        try:
            # Income Statement
            income_statement = ticker.financials
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow
            
            return {
                "income_statement": self._format_financial_statement(income_statement),
                "balance_sheet": self._format_financial_statement(balance_sheet),
                "cash_flow": self._format_financial_statement(cash_flow)
            }
        except Exception as e:
            return {
                "income_statement": {},
                "balance_sheet": {},
                "cash_flow": {},
                "error": str(e)
            }
    
    def _format_financial_statement(self, statement: pd.DataFrame) -> Dict[str, Any]:
        """Format financial statement data"""
        if statement is None or statement.empty:
            return {}
        
        result = {}
        for column in statement.columns:
            result[str(column.year)] = {}
            for index, value in statement[column].items():
                result[str(column.year)][index] = value if pd.notna(value) else None
        
        return result
    
    def _get_key_metrics(self, ticker: yf.Ticker) -> Dict[str, Any]:
        """Get key financial metrics"""
        try:
            info = ticker.info
            
            return {
                "market_cap": info.get("marketCap"),
                "enterprise_value": info.get("enterpriseValue"),
                "trailing_pe": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_sales": info.get("priceToSalesTrailing12Months"),
                "price_to_book": info.get("priceToBook"),
                "enterprise_to_revenue": info.get("enterpriseToRevenue"),
                "enterprise_to_ebitda": info.get("enterpriseToEbitda"),
                "profit_margins": info.get("profitMargins"),
                "operating_margins": info.get("operatingMargins"),
                "gross_margins": info.get("grossMargins"),
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "return_on_equity": info.get("returnOnEquity"),
                "return_on_assets": info.get("returnOnAssets"),
                "debt_to_equity": info.get("debtToEquity"),
                "current_ratio": info.get("currentRatio"),
                "quick_ratio": info.get("quickRatio"),
                "beta": info.get("beta"),
                "dividend_rate": info.get("dividendRate"),
                "dividend_yield": info.get("dividendYield"),
                "payout_ratio": info.get("payoutRatio")
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_historical_financials(self, ticker: yf.Ticker) -> Dict[str, Any]:
        """Get historical financial data"""
        try:
            # Get quarterly financials
            quarterly_financials = ticker.quarterly_financials
            quarterly_balance_sheet = ticker.quarterly_balance_sheet
            quarterly_cashflow = ticker.quarterly_cashflow
            
            return {
                "quarterly_income_statement": self._format_financial_statement(quarterly_financials),
                "quarterly_balance_sheet": self._format_financial_statement(quarterly_balance_sheet),
                "quarterly_cash_flow": self._format_financial_statement(quarterly_cashflow)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_financial_ratios(self, financial_statements: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate financial ratios from financial statements"""
        try:
            ratios = {}
            
            # Get most recent year data
            income_stmt = financial_statements.get("income_statement", {})
            balance_sheet = financial_statements.get("balance_sheet", {})
            
            if income_stmt and balance_sheet:
                # Get most recent year
                years = sorted([year for year in income_stmt.keys() if year != "error"], reverse=True)
                if years:
                    latest_year = years[0]
                    
                    # Extract values
                    revenue = income_stmt[latest_year].get("Total Revenue")
                    net_income = income_stmt[latest_year].get("Net Income")
                    total_assets = balance_sheet[latest_year].get("Total Assets")
                    total_equity = balance_sheet[latest_year].get("Total Stockholder Equity")
                    total_debt = balance_sheet[latest_year].get("Total Debt")
                    current_assets = balance_sheet[latest_year].get("Total Current Assets")
                    current_liabilities = balance_sheet[latest_year].get("Total Current Liabilities")
                    
                    # Calculate ratios
                    ratios = {
                        "net_profit_margin": (net_income / revenue * 100) if revenue and net_income else None,
                        "return_on_assets": (net_income / total_assets * 100) if total_assets and net_income else None,
                        "return_on_equity": (net_income / total_equity * 100) if total_equity and net_income else None,
                        "debt_to_equity_ratio": (total_debt / total_equity) if total_equity and total_debt else None,
                        "current_ratio": (current_assets / current_liabilities) if current_liabilities and current_assets else None,
                        "asset_turnover": (revenue / total_assets) if total_assets and revenue else None
                    }
            
            return ratios
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_financial_health(self, financial_statements: Dict[str, Any], key_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall financial health"""
        try:
            health_score = 0
            health_factors = []
            
            # Profitability analysis
            profit_margins = key_metrics.get("profit_margins")
            if profit_margins:
                if profit_margins > 0.15:
                    health_score += 25
                    health_factors.append("Strong profitability")
                elif profit_margins > 0.05:
                    health_score += 15
                    health_factors.append("Moderate profitability")
                else:
                    health_factors.append("Low profitability")
            
            # Growth analysis
            revenue_growth = key_metrics.get("revenue_growth")
            if revenue_growth:
                if revenue_growth > 0.1:
                    health_score += 25
                    health_factors.append("Strong revenue growth")
                elif revenue_growth > 0.05:
                    health_score += 15
                    health_factors.append("Moderate revenue growth")
                else:
                    health_factors.append("Low revenue growth")
            
            # Debt analysis
            debt_to_equity = key_metrics.get("debt_to_equity")
            if debt_to_equity:
                if debt_to_equity < 0.5:
                    health_score += 25
                    health_factors.append("Low debt levels")
                elif debt_to_equity < 1.0:
                    health_score += 15
                    health_factors.append("Moderate debt levels")
                else:
                    health_factors.append("High debt levels")
            
            # Liquidity analysis
            current_ratio = key_metrics.get("current_ratio")
            if current_ratio:
                if current_ratio > 2.0:
                    health_score += 25
                    health_factors.append("Strong liquidity")
                elif current_ratio > 1.0:
                    health_score += 15
                    health_factors.append("Adequate liquidity")
                else:
                    health_factors.append("Low liquidity")
            
            # Determine overall health
            if health_score >= 80:
                overall_health = "Excellent"
            elif health_score >= 60:
                overall_health = "Good"
            elif health_score >= 40:
                overall_health = "Fair"
            else:
                overall_health = "Poor"
            
            return {
                "health_score": health_score,
                "overall_health": overall_health,
                "health_factors": health_factors,
                "key_strengths": [factor for factor in health_factors if "Strong" in factor or "Low" in factor],
                "key_weaknesses": [factor for factor in health_factors if "Low" in factor or "High" in factor]
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_earnings_data(self, ticker: yf.Ticker) -> Dict[str, Any]:
        """Get earnings data"""
        try:
            earnings_dates = ticker.earnings_dates
            earnings_history = ticker.earnings_history
            
            return {
                "upcoming_earnings": self._format_earnings_dates(earnings_dates),
                "earnings_history": self._format_earnings_history(earnings_history)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _format_earnings_dates(self, earnings_dates: pd.DataFrame) -> List[Dict[str, Any]]:
        """Format earnings dates data"""
        if earnings_dates is None or earnings_dates.empty:
            return []
        
        result = []
        for date, row in earnings_dates.iterrows():
            result.append({
                "date": date.strftime('%Y-%m-%d'),
                "eps_estimate": row.get("EPS Estimate"),
                "eps_actual": row.get("Reported EPS"),
                "surprise_percent": row.get("Surprise(%)")
            })
        
        return result
    
    def _format_earnings_history(self, earnings_history: pd.DataFrame) -> List[Dict[str, Any]]:
        """Format earnings history data"""
        if earnings_history is None or earnings_history.empty:
            return []
        
        result = []
        for date, row in earnings_history.iterrows():
            result.append({
                "quarter": row.get("Quarter"),
                "year": row.get("Year"),
                "eps_estimate": row.get("EPS Estimate"),
                "eps_actual": row.get("Reported EPS"),
                "revenue_estimate": row.get("Revenue Estimate"),
                "revenue_actual": row.get("Revenue Actual")
            })
        
        return result
    
    def _get_company_info(self, ticker: yf.Ticker) -> Dict[str, Any]:
        """Get basic company information"""
        try:
            info = ticker.info
            
            return {
                "name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "description": info.get("longBusinessSummary"),
                "employees": info.get("fullTimeEmployees"),
                "founded": info.get("foundedYear"),
                "headquarters": info.get("city") + ", " + info.get("state") if info.get("city") else None,
                "website": info.get("website"),
                "business_summary": info.get("longBusinessSummary")
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_financial_comparison(self, symbols: List[str]) -> Dict[str, Any]:
        """Compare financial metrics across multiple companies"""
        comparison = {}
        
        for symbol in symbols:
            financial_data = self.get_financial_data(symbol)
            if "error" not in financial_data:
                comparison[symbol] = {
                    "market_cap": financial_data.get("key_metrics", {}).get("market_cap"),
                    "revenue_growth": financial_data.get("key_metrics", {}).get("revenue_growth"),
                    "profit_margins": financial_data.get("key_metrics", {}).get("profit_margins"),
                    "debt_to_equity": financial_data.get("key_metrics", {}).get("debt_to_equity"),
                    "health_score": financial_data.get("financial_health", {}).get("health_score")
                }
        
        return comparison
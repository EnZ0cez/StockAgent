import requests
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

class FinancialDatasetsAPI:
    """Integration with FinancialDatasets API for comprehensive financial data"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.financialdatasets.ai"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_historical_stock_data(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get historical stock price data"""
        try:
            url = f"{self.base_url}/stocks/{symbol}/history"
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "interval": "1d"
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "data": data.get("data", []),
                "metadata": data.get("metadata", {}),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def get_financial_statements(self, symbol: str, statement_type: str = "annual") -> Dict[str, Any]:
        """Get financial statements (income, balance sheet, cash flow)"""
        try:
            url = f"{self.base_url}/stocks/{symbol}/financials"
            params = {
                "type": statement_type  # "annual" or "quarterly"
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "symbol": symbol,
                "statement_type": statement_type,
                "data": data.get("data", {}),
                "metadata": data.get("metadata", {}),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def get_company_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get company fundamental data"""
        try:
            url = f"{self.base_url}/stocks/{symbol}/fundamentals"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "symbol": symbol,
                "fundamentals": data.get("data", {}),
                "metadata": data.get("metadata", {}),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def get_earnings_data(self, symbol: str) -> Dict[str, Any]:
        """Get earnings data"""
        try:
            url = f"{self.base_url}/stocks/{symbol}/earnings"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "symbol": symbol,
                "earnings": data.get("data", {}),
                "metadata": data.get("metadata", {}),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def get_analyst_ratings(self, symbol: str) -> Dict[str, Any]:
        """Get analyst ratings and price targets"""
        try:
            url = f"{self.base_url}/stocks/{symbol}/analyst-ratings"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "symbol": symbol,
                "analyst_ratings": data.get("data", {}),
                "metadata": data.get("metadata", {}),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def get_insider_trading(self, symbol: str) -> Dict[str, Any]:
        """Get insider trading data"""
        try:
            url = f"{self.base_url}/stocks/{symbol}/insider-trading"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "symbol": symbol,
                "insider_trading": data.get("data", []),
                "metadata": data.get("metadata", {}),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get real-time market data"""
        try:
            url = f"{self.base_url}/stocks/{symbol}/market-data"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "symbol": symbol,
                "market_data": data.get("data", {}),
                "metadata": data.get("metadata", {}),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def get_comprehensive_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive data for a symbol"""
        try:
            # Get all data types
            fundamentals = self.get_company_fundamentals(symbol)
            financial_statements = self.get_financial_statements(symbol)
            earnings = self.get_earnings_data(symbol)
            analyst_ratings = self.get_analyst_ratings(symbol)
            insider_trading = self.get_insider_trading(symbol)
            market_data = self.get_market_data(symbol)
            
            # Get historical data for the past year
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            historical_data = self.get_historical_stock_data(symbol, start_date, end_date)
            
            return {
                "symbol": symbol,
                "fundamentals": fundamentals,
                "financial_statements": financial_statements,
                "earnings": earnings,
                "analyst_ratings": analyst_ratings,
                "insider_trading": insider_trading,
                "market_data": market_data,
                "historical_data": historical_data,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def get_multiple_symbols_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Get data for multiple symbols"""
        results = {}
        
        for symbol in symbols:
            results[symbol] = self.get_comprehensive_data(symbol)
        
        return {
            "symbols": symbols,
            "data": results,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_sector_analysis(self, sector: str) -> Dict[str, Any]:
        """Get sector-level analysis"""
        try:
            url = f"{self.base_url}/sectors/{sector}/analysis"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "sector": sector,
                "analysis": data.get("data", {}),
                "metadata": data.get("metadata", {}),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "sector": sector,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test API connection"""
        try:
            url = f"{self.base_url}/health"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return {
                "status": "connected",
                "response_time": response.elapsed.total_seconds(),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
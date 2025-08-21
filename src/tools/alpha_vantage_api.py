#!/usr/bin/env python3

"""
Alpha Vantage API Integration
Primary data provider replacing Yahoo Finance
"""

import requests
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import time
import logging
import httpx
from src.config import settings

logger = logging.getLogger(__name__)

class AlphaVantageAPI:
    """Alpha Vantage API client for stock data"""
    
    def __init__(self, api_key: str = None):
        """Initialize with API key"""
        self.api_key = api_key or settings.alpha_vantage_api_key
        self.base_url = 'https://www.alphavantage.co/query'
        self.rate_limit = {'requests_per_minute': 5, 'last_request': 0, 'request_count': 0}
        
        # Create HTTP client with no proxy to avoid proxy issues
        self.client = httpx.Client(
            timeout=30.0,
            trust_env=False  # Disable proxy environment variables
        )
    
    def _check_rate_limit(self) -> bool:
        """Check if we can make a request (5 requests per minute limit)"""
        current_time = time.time()
        
        # Reset counter if a minute has passed
        if current_time - self.rate_limit['last_request'] > 60:
            self.rate_limit['request_count'] = 0
            
        # Check if we're under the limit
        if self.rate_limit['request_count'] < self.rate_limit['requests_per_minute']:
            self.rate_limit['request_count'] += 1
            self.rate_limit['last_request'] = current_time
            return True
            
        # Calculate wait time
        wait_time = 60 - (current_time - self.rate_limit['last_request'])
        logger.warning(f"Alpha Vantage rate limit reached. Waiting {wait_time:.1f} seconds...")
        return False
    
    def _make_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Make API request with rate limiting and proxy bypass"""
        if not self._check_rate_limit():
            # Calculate exact wait time and wait
            current_time = time.time()
            wait_time = 60 - (current_time - self.rate_limit['last_request'])
            if wait_time > 0:
                time.sleep(wait_time + 1)  # Add 1 second buffer
            
            # Reset rate limit after waiting
            self.rate_limit['request_count'] = 1
            self.rate_limit['last_request'] = time.time()
            
        params['apikey'] = self.api_key
        
        try:
            response = self.client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                raise Exception(f"Alpha Vantage API Error: {data['Error Message']}")
            if 'Note' in data:
                raise Exception(f"Alpha Vantage Rate Limit: {data['Note']}")
            if 'Information' in data and 'premium' in data['Information'].lower():
                logger.warning(f"Premium endpoint accessed: {data['Information']}")
                # For premium endpoints, still return what we can
                return {}
                
            return data
            
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"Failed to fetch data from Alpha Vantage: {e}")
    
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get current stock quote"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol
        }
        
        data = self._make_request(params)
        
        if 'Global Quote' not in data:
            raise Exception(f"No quote data available for {symbol}")
        
        quote = data['Global Quote']
        
        return {
            'symbol': symbol,
            'current_price': float(quote['05. price']),
            'change': float(quote['09. change']),
            'change_percent': float(quote['10. change percent'].rstrip('%')),
            'volume': int(quote['06. volume']),
            'high': float(quote['03. high']),
            'low': float(quote['04. low']),
            'open': float(quote['02. open']),
            'previous_close': float(quote['08. previous close']),
            'latest_trading_day': quote['07. latest trading day'],
            'provider': 'alpha_vantage'
        }
    
    def get_historical_data(self, symbol: str, period: str = "1y", outputsize: str = "compact") -> pd.DataFrame:
        """
        Get historical stock data
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: Time period ('1y', '3mo', '1mo', etc.)
            outputsize: 'compact' (100 data points) or 'full' (20+ years)
        """
        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': symbol,
            'outputsize': outputsize
        }
        
        data = self._make_request(params)
        
        if 'Time Series (Daily)' not in data:
            raise Exception(f"No historical data available for {symbol}")
        
        # Convert to pandas DataFrame
        df_data = []
        for date_str, values in data['Time Series (Daily)'].items():
            df_data.append({
                'Date': pd.to_datetime(date_str),
                'Open': float(values['1. open']),
                'High': float(values['2. high']),
                'Low': float(values['3. low']),
                'Close': float(values['4. close']),
                'Adj Close': float(values['5. adjusted close']),
                'Volume': int(values['6. volume']),
                'Dividend': float(values['7. dividend amount']),
                'Split': float(values['8. split coefficient'])
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        # Filter by period
        if period and period != "max":
            days_map = {
                '1d': 1, '5d': 5, '1mo': 30, '3mo': 90,
                '6mo': 180, '1y': 365, '2y': 730, '5y': 1825
            }
            
            if period in days_map:
                cutoff_date = datetime.now() - timedelta(days=days_map[period])
                df = df[df.index >= cutoff_date]
        
        return df
    
    def get_intraday_data(self, symbol: str, interval: str = "5min") -> pd.DataFrame:
        """
        Get intraday stock data
        
        Args:
            symbol: Stock symbol
            interval: '1min', '5min', '15min', '30min', '60min'
        """
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': interval,
            'outputsize': 'compact'
        }
        
        data = self._make_request(params)
        
        time_series_key = f'Time Series ({interval})'
        if time_series_key not in data:
            raise Exception(f"No intraday data available for {symbol}")
        
        # Convert to pandas DataFrame
        df_data = []
        for datetime_str, values in data[time_series_key].items():
            df_data.append({
                'DateTime': pd.to_datetime(datetime_str),
                'Open': float(values['1. open']),
                'High': float(values['2. high']),
                'Low': float(values['3. low']),
                'Close': float(values['4. close']),
                'Volume': int(values['5. volume'])
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('DateTime', inplace=True)
        df.sort_index(inplace=True)
        
        return df
    
    def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """Get company overview and fundamental data"""
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol
        }
        
        data = self._make_request(params)
        
        if not data or 'Symbol' not in data:
            raise Exception(f"No company overview available for {symbol}")
        
        # Convert numeric fields
        numeric_fields = [
            'MarketCapitalization', 'EBITDA', 'PERatio', 'PEGRatio',
            'BookValue', 'DividendPerShare', 'DividendYield', 'EPS',
            'RevenuePerShareTTM', 'ProfitMargin', 'OperatingMarginTTM',
            'ReturnOnAssetsTTM', 'ReturnOnEquityTTM', 'RevenueTTM',
            'GrossProfitTTM', 'DilutedEPSTTM', 'QuarterlyEarningsGrowthYOY',
            'QuarterlyRevenueGrowthYOY', 'AnalystTargetPrice', 'TrailingPE',
            'ForwardPE', 'PriceToSalesRatioTTM', 'PriceToBookRatio',
            'EVToRevenue', 'EVToEBITDA', 'Beta', '52WeekHigh', '52WeekLow',
            '50DayMovingAverage', '200DayMovingAverage'
        ]
        
        for field in numeric_fields:
            if field in data and data[field] != 'None' and data[field] != '-':
                try:
                    data[field] = float(data[field])
                except (ValueError, TypeError):
                    data[field] = None
            else:
                data[field] = None
        
        return data
    
    def get_technical_indicators(self, symbol: str, indicator: str = "SMA", 
                               interval: str = "daily", time_period: int = 20) -> pd.DataFrame:
        """
        Get technical indicators
        
        Args:
            symbol: Stock symbol
            indicator: Technical indicator (SMA, EMA, RSI, MACD, etc.)
            interval: daily, weekly, monthly
            time_period: Number of periods for calculation
        """
        params = {
            'function': indicator,
            'symbol': symbol,
            'interval': interval,
            'time_period': str(time_period),
            'series_type': 'close'
        }
        
        data = self._make_request(params)
        
        # Find the technical analysis data key
        data_key = None
        for key in data.keys():
            if 'Technical Analysis' in key:
                data_key = key
                break
        
        if not data_key:
            raise Exception(f"No technical indicator data available for {symbol}")
        
        # Convert to pandas DataFrame
        df_data = []
        for date_str, values in data[data_key].items():
            row = {'Date': pd.to_datetime(date_str)}
            for value_key, value in values.items():
                row[value_key] = float(value)
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        return df
    
    def search_symbol(self, keywords: str) -> List[Dict[str, str]]:
        """Search for stock symbols by company name or keywords"""
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': keywords
        }
        
        data = self._make_request(params)
        
        if 'bestMatches' not in data:
            return []
        
        return [
            {
                'symbol': match['1. symbol'],
                'name': match['2. name'],
                'type': match['3. type'],
                'region': match['4. region'],
                'market_open': match['5. marketOpen'],
                'market_close': match['6. marketClose'],
                'timezone': match['7. timezone'],
                'currency': match['8. currency'],
                'match_score': float(match['9. matchScore'])
            }
            for match in data['bestMatches']
        ]

# Usage example and test function
if __name__ == "__main__":
    # Test the Alpha Vantage API
    print("🧪 Testing Alpha Vantage API...")
    
    try:
        api = AlphaVantageAPI()
        
        # Test quote
        print("\n📈 Getting AAPL quote...")
        quote = api.get_stock_quote('AAPL')
        print(f"   {quote['symbol']}: ${quote['current_price']:.2f}")
        print(f"   Change: {quote['change']:+.2f} ({quote['change_percent']:+.2f}%)")
        
        # Test historical data
        print("\n📊 Getting historical data...")
        historical = api.get_historical_data('AAPL', '1mo')
        print(f"   Retrieved {len(historical)} days of data")
        print(f"   Latest close: ${historical['Close'].iloc[-1]:.2f}")
        
        # Test company overview
        print("\n🏢 Getting company overview...")
        overview = api.get_company_overview('AAPL')
        print(f"   Company: {overview.get('Name', 'N/A')}")
        print(f"   Sector: {overview.get('Sector', 'N/A')}")
        print(f"   Market Cap: ${overview.get('MarketCapitalization', 0):,}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("Please check your Alpha Vantage API key in the .env file")

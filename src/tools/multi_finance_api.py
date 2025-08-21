#!/usr/bin/env python3

"""
Multi-Finance API Integration
Supports multiple finance data providers with automatic fallback
"""

import requests
import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)

class MultiFinanceAPI:
    """Multi-provider finance data API with automatic fallback"""
    
    def __init__(self, config: Dict[str, str] = None):
        """
        Initialize with API keys
        
        Args:
            config: Dictionary with API keys
                - alpha_vantage_key
                - finnhub_key
                - iex_cloud_token
                - polygon_key
                - fmp_key
        """
        self.config = config or {}
        self.rate_limits = {
            'alpha_vantage': {'requests_per_minute': 5, 'last_request': 0},
            'finnhub': {'requests_per_minute': 60, 'last_request': 0},
            'iex_cloud': {'requests_per_minute': 100, 'last_request': 0},
            'polygon': {'requests_per_minute': 5, 'last_request': 0},
            'fmp': {'requests_per_minute': 300, 'last_request': 0}
        }
    
    def _check_rate_limit(self, provider: str) -> bool:
        """Check if we can make a request to the provider"""
        if provider not in self.rate_limits:
            return True
            
        limit_info = self.rate_limits[provider]
        current_time = time.time()
        
        # Reset counter if a minute has passed
        if current_time - limit_info['last_request'] > 60:
            limit_info['request_count'] = 0
            
        # Check if we're under the limit
        request_count = limit_info.get('request_count', 0)
        if request_count < limit_info['requests_per_minute']:
            limit_info['request_count'] = request_count + 1
            limit_info['last_request'] = current_time
            return True
            
        return False
    
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get current stock quote with provider fallback"""
        
        # Try Alpha Vantage first (most reliable)
        if self._check_rate_limit('alpha_vantage') and 'alpha_vantage_key' in self.config:
            try:
                return self._get_alpha_vantage_quote(symbol)
            except Exception as e:
                logger.warning(f"Alpha Vantage failed: {e}")
        
        # Fallback to Finnhub
        if self._check_rate_limit('finnhub') and 'finnhub_key' in self.config:
            try:
                return self._get_finnhub_quote(symbol)
            except Exception as e:
                logger.warning(f"Finnhub failed: {e}")
        
        # Fallback to IEX Cloud
        if self._check_rate_limit('iex_cloud') and 'iex_cloud_token' in self.config:
            try:
                return self._get_iex_quote(symbol)
            except Exception as e:
                logger.warning(f"IEX Cloud failed: {e}")
        
        # Last resort: Yahoo Finance
        try:
            return self._get_yahoo_quote(symbol)
        except Exception as e:
            logger.error(f"All providers failed for {symbol}: {e}")
            raise Exception(f"Unable to fetch quote for {symbol}")
    
    def _get_alpha_vantage_quote(self, symbol: str) -> Dict[str, Any]:
        """Get quote from Alpha Vantage"""
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.config['alpha_vantage_key']
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'Global Quote' not in data:
            raise Exception("Alpha Vantage API limit reached")
        
        quote = data['Global Quote']
        return {
            'symbol': symbol,
            'current_price': float(quote['05. price']),
            'change': float(quote['09. change']),
            'change_percent': quote['10. change percent'].rstrip('%'),
            'volume': int(quote['06. volume']),
            'high': float(quote['03. high']),
            'low': float(quote['04. low']),
            'open': float(quote['02. open']),
            'previous_close': float(quote['08. previous close']),
            'provider': 'alpha_vantage'
        }
    
    def _get_finnhub_quote(self, symbol: str) -> Dict[str, Any]:
        """Get quote from Finnhub"""
        url = f'https://finnhub.io/api/v1/quote'
        params = {
            'symbol': symbol,
            'token': self.config['finnhub_key']
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'c' not in data:
            raise Exception("Finnhub API error")
        
        return {
            'symbol': symbol,
            'current_price': data['c'],
            'change': data['d'],
            'change_percent': data['dp'],
            'high': data['h'],
            'low': data['l'],
            'open': data['o'],
            'previous_close': data['pc'],
            'provider': 'finnhub'
        }
    
    def _get_iex_quote(self, symbol: str) -> Dict[str, Any]:
        """Get quote from IEX Cloud"""
        url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote"
        params = {'token': self.config['iex_cloud_token']}
        
        response = requests.get(url, params=params)
        data = response.json()
        
        return {
            'symbol': symbol,
            'current_price': data['latestPrice'],
            'change': data['change'],
            'change_percent': data['changePercent'] * 100,
            'volume': data['latestVolume'],
            'high': data['high'],
            'low': data['low'],
            'open': data['open'],
            'previous_close': data['previousClose'],
            'provider': 'iex_cloud'
        }
    
    def _get_yahoo_quote(self, symbol: str) -> Dict[str, Any]:
        """Get quote from Yahoo Finance (fallback)"""
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'symbol': symbol,
            'current_price': info.get('currentPrice', 0),
            'change': info.get('regularMarketChange', 0),
            'change_percent': info.get('regularMarketChangePercent', 0),
            'volume': info.get('volume', 0),
            'high': info.get('dayHigh', 0),
            'low': info.get('dayLow', 0),
            'open': info.get('open', 0),
            'previous_close': info.get('previousClose', 0),
            'provider': 'yahoo_finance'
        }
    
    def get_historical_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Get historical data with provider fallback"""
        
        # Try Alpha Vantage for historical data
        if 'alpha_vantage_key' in self.config:
            try:
                return self._get_alpha_vantage_historical(symbol, period)
            except Exception as e:
                logger.warning(f"Alpha Vantage historical data failed: {e}")
        
        # Fallback to Yahoo Finance
        try:
            ticker = yf.Ticker(symbol)
            return ticker.history(period=period)
        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {e}")
            raise
    
    def _get_alpha_vantage_historical(self, symbol: str, period: str) -> pd.DataFrame:
        """Get historical data from Alpha Vantage"""
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': symbol,
            'outputsize': 'full',
            'apikey': self.config['alpha_vantage_key']
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'Time Series (Daily)' not in data:
            raise Exception("Alpha Vantage historical data not available")
        
        # Convert to pandas DataFrame
        df_data = []
        for date, values in data['Time Series (Daily)'].items():
            df_data.append({
                'Date': pd.to_datetime(date),
                'Open': float(values['1. open']),
                'High': float(values['2. high']),
                'Low': float(values['3. low']),
                'Close': float(values['4. close']),
                'Volume': int(values['6. volume'])
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        # Filter by period
        if period == "1y":
            cutoff_date = datetime.now() - timedelta(days=365)
            df = df[df.index >= cutoff_date]
        
        return df
    
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get company information"""
        
        # Try Financial Modeling Prep first
        if 'fmp_key' in self.config:
            try:
                return self._get_fmp_company_info(symbol)
            except Exception as e:
                logger.warning(f"FMP company info failed: {e}")
        
        # Fallback to Yahoo Finance
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                'symbol': symbol,
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'provider': 'yahoo_finance'
            }
        except Exception as e:
            logger.error(f"Failed to get company info for {symbol}: {e}")
            raise
    
    def _get_fmp_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get company info from Financial Modeling Prep"""
        url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}"
        params = {'apikey': self.config['fmp_key']}
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if not data:
            raise Exception("FMP company info not available")
        
        company = data[0]
        return {
            'symbol': symbol,
            'name': company.get('companyName', ''),
            'sector': company.get('sector', ''),
            'industry': company.get('industry', ''),
            'market_cap': company.get('mktCap', 0),
            'pe_ratio': company.get('pe', 0),
            'description': company.get('description', ''),
            'website': company.get('website', ''),
            'provider': 'fmp'
        }

# 使用示例
if __name__ == "__main__":
    # 配置 API 密钥
    config = {
        'alpha_vantage_key': 'YOUR_ALPHA_VANTAGE_KEY',
        'finnhub_key': 'YOUR_FINNHUB_KEY',
        'iex_cloud_token': 'YOUR_IEX_TOKEN',
        'fmp_key': 'YOUR_FMP_KEY'
    }
    
    api = MultiFinanceAPI(config)
    
    try:
        # 获取股票报价
        quote = api.get_stock_quote('AAPL')
        print(f"📈 {quote['symbol']}: ${quote['current_price']:.2f}")
        print(f"   Change: {quote['change']:+.2f} ({quote['change_percent']:+}%)")
        print(f"   Provider: {quote['provider']}")
        
        # 获取历史数据
        historical = api.get_historical_data('AAPL', '3mo')
        print(f"\n📊 Historical data shape: {historical.shape}")
        
        # 获取公司信息
        company = api.get_company_info('AAPL')
        print(f"\n🏢 {company['name']} ({company['symbol']})")
        print(f"   Sector: {company['sector']}")
        print(f"   Market Cap: ${company['market_cap']:,}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

from src.tools.alpha_vantage_api import AlphaVantageAPI
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
import time
import random
import logging

logger = logging.getLogger(__name__)

class StockDataAgent:
    """Agent for retrieving real-time stock price data using Alpha Vantage"""
    
    def __init__(self, llm):
        self.llm = llm
        self.alpha_vantage = AlphaVantageAPI()
    
    def get_stock_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """
        Get stock data for a given symbol and time period using Alpha Vantage
        
        Args:
            symbol: Stock symbol (e.g., AAPL, MSFT)
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
        
        Returns:
            Dictionary containing stock data and analysis
        """
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Add delay between retries
                if attempt > 0:
                    delay = random.uniform(2, 5)
                    time.sleep(delay)
                
                logger.info(f"Fetching stock data for {symbol} (attempt {attempt + 1})")
                
                # Get current quote
                quote = self.alpha_vantage.get_stock_quote(symbol)
                
                # Get historical data (gracefully handle premium limitations)
                try:
                    hist_data = self.alpha_vantage.get_historical_data(symbol, period)
                    has_historical = True
                except Exception as e:
                    logger.warning(f"Historical data not available (likely premium): {e}")
                    # Create minimal historical data using current quote
                    hist_data = pd.DataFrame({
                        'Open': [quote['open']],
                        'High': [quote['high']],
                        'Low': [quote['low']],
                        'Close': [quote['current_price']],
                        'Volume': [quote['volume']]
                    }, index=[pd.Timestamp.now().date()])
                    has_historical = False
                
                # Get company overview
                try:
                    company_info = self.alpha_vantage.get_company_overview(symbol)
                except Exception as e:
                    logger.warning(f"Could not fetch company overview: {e}")
                    company_info = {}
                
                # Calculate key metrics
                current_price = quote['current_price']
                previous_close = quote['previous_close']
                
                # Calculate returns (handle limited data gracefully)
                if has_historical and len(hist_data) > 1:
                    period_return = ((hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[0]) / hist_data['Close'].iloc[0] * 100)
                    volatility = hist_data['Close'].pct_change().std() * np.sqrt(252) * 100
                else:
                    period_return = quote['change_percent']  # Use daily change as proxy
                    volatility = None
                
                # Moving averages (only if we have sufficient data)
                ma_50 = hist_data['Close'].rolling(window=50).mean().iloc[-1] if len(hist_data) >= 50 else None
                ma_200 = hist_data['Close'].rolling(window=200).mean().iloc[-1] if len(hist_data) >= 200 else None
                
                # Technical indicators (only if we have sufficient data)
                rsi = self._calculate_rsi(hist_data['Close']) if len(hist_data) > 14 else None
                macd = self._calculate_macd(hist_data['Close']) if len(hist_data) > 26 else None
                
                # Volume analysis
                if has_historical:
                    avg_volume = hist_data['Volume'].mean()
                    current_volume = hist_data['Volume'].iloc[-1]
                    volume_ratio = current_volume / avg_volume if avg_volume > 0 else None
                else:
                    avg_volume = quote['volume']
                    current_volume = quote['volume']
                    volume_ratio = 1.0
                
                # Prepare result
                result = {
                    "symbol": symbol,
                    "period": period,
                    "current_data": {
                        "price": current_price,
                        "previous_close": previous_close,
                        "change": quote['change'],
                        "change_percent": quote['change_percent'],
                        "volume": quote['volume'],
                        "avg_volume": avg_volume,
                        "volume_ratio": volume_ratio,
                        "market_cap": company_info.get("MarketCapitalization"),
                        "pe_ratio": company_info.get("PERatio"),
                        "dividend_yield": company_info.get("DividendYield"),
                        "beta": company_info.get("Beta"),
                        "high": quote['high'],
                        "low": quote['low'],
                        "open": quote['open'],
                        "has_historical_data": has_historical,
                        "last_updated": datetime.now().isoformat()
                    },
                    "performance": {
                        "period_return": period_return,
                        "volatility": volatility,
                        "high_52w": company_info.get("52WeekHigh"),
                        "low_52w": company_info.get("52WeekLow"),
                        "ma_50": ma_50,
                        "ma_200": ma_200,
                        "price_above_ma_50": current_price > ma_50 if ma_50 else None,
                        "price_above_ma_200": current_price > ma_200 if ma_200 else None
                    },
                    "technical_indicators": {
                        "rsi": rsi,
                        "macd": macd,
                        "rsi_signal": self._get_rsi_signal(rsi) if rsi else None,
                        "macd_signal": self._get_macd_signal(macd) if macd else None
                    },
                    "historical_data": {
                        "dates": [date.strftime('%Y-%m-%d') for date in hist_data.index],
                        "prices": hist_data['Close'].tolist(),
                        "volumes": hist_data['Volume'].tolist(),
                        "highs": hist_data['High'].tolist(),
                        "lows": hist_data['Low'].tolist(),
                        "data_source": "alpha_vantage_current" if not has_historical else "alpha_vantage_historical",
                        "note": "Limited to current day data (premium required for historical)" if not has_historical else "Full historical data available"
                    },
                    "company_info": {
                        "name": company_info.get("Name"),
                        "sector": company_info.get("Sector"),
                        "industry": company_info.get("Industry"),
                        "description": company_info.get("Description")
                    }
                }
                
                return result
                
            except Exception as e:
                last_error = e
                if attempt == max_retries - 1:
                    # This was the last attempt
                    break
                # Continue to next attempt
                continue
        
        # If we get here, all attempts failed
        return {
            "symbol": symbol,
            "error": str(last_error),
            "last_updated": datetime.now().isoformat()
        }
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            "macd": macd_line.iloc[-1],
            "signal": signal_line.iloc[-1],
            "histogram": histogram.iloc[-1]
        }
    
    def _get_rsi_signal(self, rsi: float) -> str:
        """Get RSI trading signal"""
        if rsi > 70:
            return "Overbought"
        elif rsi < 30:
            return "Oversold"
        else:
            return "Neutral"
    
    def _get_macd_signal(self, macd: Dict[str, float]) -> str:
        """Get MACD trading signal"""
        if macd["histogram"] > 0:
            return "Bullish"
        elif macd["histogram"] < 0:
            return "Bearish"
        else:
            return "Neutral"
    
    def get_real_time_price(self, symbol: str) -> Dict[str, Any]:
        """Get real-time price data using Alpha Vantage"""
        try:
            quote = self.alpha_vantage.get_stock_quote(symbol)
            
            return {
                "symbol": symbol,
                "price": quote['current_price'],
                "change": quote['change'],
                "change_percent": quote['change_percent'],
                "volume": quote['volume'],
                "high": quote['high'],
                "low": quote['low'],
                "open": quote['open'],
                "previous_close": quote['previous_close'],
                "timestamp": datetime.now().isoformat(),
                "provider": "alpha_vantage"
            }
            
        except Exception as e:
            logger.error(f"Failed to get real-time price for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def get_multiple_stocks(self, symbols: list, period: str = "1y") -> Dict[str, Any]:
        """Get data for multiple stocks"""
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_stock_data(symbol, period)
        return results
import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np

class StockDataAgent:
    """Agent for retrieving real-time stock price data"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def get_stock_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """
        Get stock data for a given symbol and time period
        
        Args:
            symbol: Stock symbol (e.g., AAPL, MSFT)
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
        Returns:
            Dictionary containing stock data and analysis
        """
        try:
            # Get stock data using yfinance
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            hist_data = ticker.history(period=period)
            
            # Get current stock info
            info = ticker.info
            
            # Calculate key metrics
            current_price = hist_data['Close'].iloc[-1] if not hist_data.empty else None
            previous_close = hist_data['Close'].iloc[-2] if len(hist_data) > 1 else None
            
            # Calculate returns
            daily_return = ((current_price - previous_close) / previous_close * 100) if previous_close else None
            period_return = ((hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[0]) / hist_data['Close'].iloc[0] * 100) if len(hist_data) > 1 else None
            
            # Calculate volatility
            volatility = hist_data['Close'].pct_change().std() * np.sqrt(252) * 100 if len(hist_data) > 1 else None
            
            # Moving averages
            ma_50 = hist_data['Close'].rolling(window=50).mean().iloc[-1] if len(hist_data) >= 50 else None
            ma_200 = hist_data['Close'].rolling(window=200).mean().iloc[-1] if len(hist_data) >= 200 else None
            
            # Technical indicators
            rsi = self._calculate_rsi(hist_data['Close']) if len(hist_data) > 14 else None
            macd = self._calculate_macd(hist_data['Close']) if len(hist_data) > 26 else None
            
            # Volume analysis
            avg_volume = hist_data['Volume'].mean()
            current_volume = hist_data['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else None
            
            # Prepare result
            result = {
                "symbol": symbol,
                "period": period,
                "current_data": {
                    "price": current_price,
                    "previous_close": previous_close,
                    "change": current_price - previous_close if previous_close else None,
                    "change_percent": daily_return,
                    "volume": current_volume,
                    "avg_volume": avg_volume,
                    "volume_ratio": volume_ratio,
                    "market_cap": info.get("marketCap"),
                    "pe_ratio": info.get("trailingPE"),
                    "dividend_yield": info.get("dividendYield"),
                    "beta": info.get("beta"),
                    "last_updated": datetime.now().isoformat()
                },
                "performance": {
                    "period_return": period_return,
                    "volatility": volatility,
                    "high_52w": info.get("fiftyTwoWeekHigh"),
                    "low_52w": info.get("fiftyTwoWeekLow"),
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
                    "dates": hist_data.index.strftime('%Y-%m-%d').tolist(),
                    "prices": hist_data['Close'].tolist(),
                    "volumes": hist_data['Volume'].tolist(),
                    "highs": hist_data['High'].tolist(),
                    "lows": hist_data['Low'].tolist()
                },
                "company_info": {
                    "name": info.get("longName"),
                    "sector": info.get("sector"),
                    "industry": info.get("industry"),
                    "description": info.get("longBusinessSummary")
                }
            }
            
            return result
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
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
        """Get real-time price data"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get latest price
            hist = ticker.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else None
            
            return {
                "symbol": symbol,
                "current_price": current_price,
                "previous_close": info.get("previousClose"),
                "open": info.get("open"),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "volume": info.get("volume"),
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
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
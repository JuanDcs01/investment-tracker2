import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class MarketService:
    """Service for fetching market data from Yahoo Finance."""
    
    # Cache for market data (symbol: {data, timestamp})
    _cache = {}
    _cache_duration = timedelta(minutes=5)
    
    @classmethod
    def verify_symbol(cls, symbol: str, instrument_type: str) -> bool:
        """
        Verify if a symbol exists in Yahoo Finance.
        
        Args:
            symbol: The instrument symbol
            instrument_type: Type of instrument (stock, etf, crypto)
            
        Returns:
            bool: True if symbol exists, False otherwise
        """
        try:
            # Format symbol for crypto
            formatted_symbol = cls._format_symbol(symbol, instrument_type)
            
            # Try to fetch data
            ticker = yf.Ticker(formatted_symbol)
            info = ticker.info
            
            # Verify the ticker has valid data
            if not info or 'symbol' not in info:
                logger.warning(f"Symbol {formatted_symbol} not found or invalid")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying symbol {symbol}: {str(e)}")
            return False
    
    @classmethod
    def get_current_price(cls, symbol: str, instrument_type: str) -> Optional[float]:
        """
        Get current price for a symbol.
        
        Args:
            symbol: The instrument symbol
            instrument_type: Type of instrument
            
        Returns:
            float: Current price or None if not available
        """
        try:
            formatted_symbol = cls._format_symbol(symbol, instrument_type)
            
            # Check cache
            if cls._is_cached(formatted_symbol):
                return cls._cache[formatted_symbol]['data']['current_price']
            
            # Fetch new data
            ticker = yf.Ticker(formatted_symbol)
            
            # Try different price sources
            current_price = None
            
            # Try current price
            if hasattr(ticker, 'info') and ticker.info:
                current_price = ticker.info.get('currentPrice') or \
                               ticker.info.get('regularMarketPrice') or \
                               ticker.info.get('previousClose')
            
            # If info doesn't work, try history
            if current_price is None:
                hist = ticker.history(period='1d')
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
            
            if current_price is None:
                logger.warning(f"Could not fetch price for {formatted_symbol}")
                return None
            
            # Cache the result
            cls._cache_data(formatted_symbol, {
                'current_price': float(current_price),
                'symbol': formatted_symbol
            })
            
            return float(current_price)
            
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {str(e)}")
            return None
    
    @classmethod
    def get_previous_close(cls, symbol: str, instrument_type: str) -> Optional[float]:
        """
        Get previous close price for a symbol.
        
        Args:
            symbol: The instrument symbol
            instrument_type: Type of instrument
            
        Returns:
            float: Previous close price or None if not available
        """
        try:
            formatted_symbol = cls._format_symbol(symbol, instrument_type)
            
            ticker = yf.Ticker(formatted_symbol)
            
            # Try to get previous close from info
            if hasattr(ticker, 'info') and ticker.info:
                prev_close = ticker.info.get('previousClose') or \
                            ticker.info.get('regularMarketPreviousClose')
                if prev_close:
                    return float(prev_close)
            
            # Try from history
            hist = ticker.history(period='5d')
            if len(hist) >= 2:
                return float(hist['Close'].iloc[-2])
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching previous close for {symbol}: {str(e)}")
            return None
    
    @classmethod
    def get_instrument_info(cls, symbol: str, instrument_type: str) -> Optional[Dict]:
        """
        Get detailed information about an instrument.
        
        Args:
            symbol: The instrument symbol
            instrument_type: Type of instrument
            
        Returns:
            dict: Instrument information or None
        """
        try:
            formatted_symbol = cls._format_symbol(symbol, instrument_type)
            ticker = yf.Ticker(formatted_symbol)
            
            info = ticker.info
            if not info:
                return None
            
            return {
                'symbol': symbol,
                'name': info.get('longName') or info.get('shortName', symbol),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'N/A'),
                'type': instrument_type
            }
            
        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {str(e)}")
            return None
    
    @classmethod
    def get_batch_prices(cls, symbols_data: List[Dict]) -> Dict[str, float]:
        """
        Get current prices for multiple symbols at once.
        
        Args:
            symbols_data: List of dicts with 'symbol' and 'instrument_type'
            
        Returns:
            dict: Dictionary mapping symbols to prices
        """
        prices = {}
        
        for item in symbols_data:
            symbol = item['symbol']
            instrument_type = item['instrument_type']
            
            price = cls.get_current_price(symbol, instrument_type)
            if price is not None:
                prices[symbol] = price
        
        return prices
    
    @classmethod
    def _format_symbol(cls, symbol: str, instrument_type: str) -> str:
        """
        Format symbol for Yahoo Finance.
        Automatically adds -USD for crypto if not present.
        
        Args:
            symbol: The instrument symbol
            instrument_type: Type of instrument
            
        Returns:
            str: Formatted symbol
        """
        symbol = symbol.upper().strip()
        
        if instrument_type == 'crypto':
            # Add -USD suffix if not present
            if not symbol.endswith('-USD'):
                symbol = f"{symbol}-USD"
        
        return symbol
    
    @classmethod
    def _is_cached(cls, symbol: str) -> bool:
        """Check if symbol data is cached and still valid."""
        if symbol not in cls._cache:
            return False
        
        cache_entry = cls._cache[symbol]
        time_diff = datetime.now() - cache_entry['timestamp']
        
        return time_diff < cls._cache_duration
    
    @classmethod
    def _cache_data(cls, symbol: str, data: Dict):
        """Cache market data for a symbol."""
        cls._cache[symbol] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    @classmethod
    def clear_cache(cls):
        """Clear all cached data."""
        cls._cache.clear()
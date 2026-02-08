from typing import Dict, List, Optional
from decimal import Decimal
from app.models import Instrument
from app.services.market_service import MarketService
import logging

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service for portfolio calculations and metrics."""
    
    @staticmethod
    def calculate_portfolio_metrics(instruments: List[Instrument]) -> Dict:
        """
        Calculate overall portfolio metrics.
        
        Args:
            instruments: List of Instrument objects
            
        Returns:
            dict: Portfolio metrics including totals and gains
        """
        if not instruments:
                return {
                    'total_invested': 0.0,
                    'current_market_value': 0.0,
                    'today_gain': 0.0,
                    'today_gain_percentage': 0.0,      # Añade esto
                    'total_market_gain': 0.0,          # Añade esto
                    'market_gain_percentage': 0.0,      # Añade esto
                    'net_return': 0.0,
                    'net_return_percentage': 0.0
                }
                
        # Fetch current prices for all instruments
        symbols_data = [
            {'symbol': inst.symbol, 'instrument_type': inst.instrument_type}
            for inst in instruments
        ]
        current_prices = MarketService.get_batch_prices(symbols_data)
        
        # Fetch previous close prices for today's gain
        previous_prices = {}
        for inst in instruments:
            prev_price = MarketService.get_previous_close(
                inst.symbol,
                inst.instrument_type
            )
            if prev_price:
                previous_prices[inst.symbol] = prev_price
        
        total_invested = 0.0
        current_market_value = 0.0
        previous_market_value = 0.0
        total_market_gain = 0.0
        
        for inst in instruments:
            total_invested += float(inst.total_cost)
            
            current_price = current_prices.get(inst.symbol)
            if current_price:
                current_value = float(inst.quantity) * current_price
                current_market_value += current_value
                
                # Calcula y suma la ganancia de mercado individual
                avg_price = float(inst.average_purchase_price)
                total_market_gain += (current_price - avg_price) * float(inst.quantity)
                # Previous market value for today's gain
                prev_price = previous_prices.get(inst.symbol)
                if prev_price:
                    previous_market_value += float(inst.quantity) * prev_price
        
        # Calculate metrics
        today_gain = current_market_value - previous_market_value
        net_return = current_market_value - total_invested
        net_return_percentage = (
            (net_return / total_invested * 100) if total_invested > 0 else 0
        )
        market_gain_percentage = (total_market_gain / total_invested * 100) if total_invested > 0 else 0
        today_gain_percentage = (today_gain / previous_market_value * 100) if previous_market_value > 0 else 0
        
        return {
            'total_invested': round(total_invested, 2),
            'current_market_value': round(current_market_value, 2),
            'today_gain': round(today_gain, 2),
            'today_gain_percentage': round(today_gain_percentage, 2), # <--- Nuevo
            'total_market_gain': round(total_market_gain, 2),         # <--- Nuevo
            'market_gain_percentage': round(market_gain_percentage, 2), # <--- Nuevo
            'net_return': round(net_return, 2),
            'net_return_percentage': round(net_return_percentage, 2)
        }
    
    @staticmethod
    def calculate_instrument_metrics(instrument: Instrument) -> Dict:
        """
        Calculate metrics for a single instrument.
        
        Args:
            instrument: Instrument object
            
        Returns:
            dict: Instrument metrics with percentages
        """
        current_price = MarketService.get_current_price(
            instrument.symbol,
            instrument.instrument_type
        )
        
        previous_price = MarketService.get_previous_close(
            instrument.symbol,
            instrument.instrument_type
        )
        
        quantity = float(instrument.quantity)
        avg_price = float(instrument.average_purchase_price)
        total_cost = float(instrument.total_cost)
        total_comission = float(instrument.total_commission)
        
        # Current market value
        current_value = quantity * current_price if current_price else 0.0
        
        # Market gain (without considering commissions)
        market_gain = (current_price - avg_price) * quantity if current_price else 0.0
        
        # Market gain percentage (based on average purchase price)
        market_gain_percentage = (
            (market_gain / (total_cost - total_comission) * 100) if current_price and avg_price > 0 else 0.0
        )
        
        # Today's gain
        if current_price and previous_price:
            today_gain = (current_price - previous_price) * quantity
            # Today's gain percentage (based on previous close)
            today_gain_percentage = (
                ((current_price - previous_price) / previous_price * 100) if previous_price > 0 else 0.0
            )
        else:
            today_gain = 0.0
            today_gain_percentage = 0.0
        
        # Net return (considering commissions)
        net_return = current_value - total_cost
        net_return_percentage = (
            (net_return / total_cost * 100) if total_cost > 0 else 0
        )
        
        return {
            'symbol': instrument.symbol,
            'type': instrument.instrument_type,
            'quantity': quantity,
            'average_purchase_price': avg_price,
            'current_price': current_price if current_price else 0.0,
            'total_cost': total_cost,
            'current_value': round(current_value, 2),
            'market_gain': round(market_gain, 2),
            'market_gain_percentage': round(market_gain_percentage, 2),  # NUEVO - PORCENTAJE POR INSTRUMENTO
            'today_gain': round(today_gain, 2),
            'today_gain_percentage': round(today_gain_percentage, 2),  # NUEVO - PORCENTAJE POR INSTRUMENTO
            'net_return': round(net_return, 2),
            'net_return_percentage': round(net_return_percentage, 2),
            'instrument_id': instrument.id
        }
    
    @staticmethod
    def get_portfolio_distribution(instruments: List[Instrument]) -> Dict:
        """
        Calculate portfolio distribution by type and risk.
        
        Args:
            instruments: List of Instrument objects
            
        Returns:
            dict: Distribution data for charts
        """
        if not instruments:
            return {
                'by_type': [],
                'by_risk': [],
                'by_instrument': []
            }
        
        # Fetch current prices
        symbols_data = [
            {'symbol': inst.symbol, 'instrument_type': inst.instrument_type}
            for inst in instruments
        ]
        current_prices = MarketService.get_batch_prices(symbols_data)
        
        # Calculate current values
        type_distribution = {'stock': 0, 'etf': 0, 'crypto': 0}
        risk_distribution = {'medium': 0, 'high': 0}
        instrument_values = []
        total_value = 0.0
        
        for inst in instruments:
            current_price = current_prices.get(inst.symbol, 0)
            current_value = float(inst.quantity) * current_price
            total_value += current_value
            
            # By type
            type_distribution[inst.instrument_type] += current_value
            
            # By risk (ETF = medium, Stock and Crypto = high)
            risk_level = 'medium' if inst.instrument_type == 'etf' else 'high'
            risk_distribution[risk_level] += current_value
            
            # By instrument
            instrument_values.append({
                'symbol': inst.symbol,
                'value': current_value
            })
        
        # Convert to percentages and amounts
        by_type = [
            {
                'label': key.upper(),
                'value': value,
                'percentage': round((value / total_value * 100) if total_value > 0 else 0, 2)
            }
            for key, value in type_distribution.items()
            if value > 0
        ]
        
        by_risk = [
            {
                'label': 'Riesgo Medio (ETF)' if key == 'medium' else 'Riesgo Alto (Stock/Crypto)',
                'value': value,
                'percentage': round((value / total_value * 100) if total_value > 0 else 0, 2)
            }
            for key, value in risk_distribution.items()
            if value > 0
        ]
        
        by_instrument = [
            {
                'label': item['symbol'],
                'value': item['value'],
                'percentage': round((item['value'] / total_value * 100) if total_value > 0 else 0, 2)
            }
            for item in sorted(instrument_values, key=lambda x: x['value'], reverse=True)
            if item['value'] > 0
        ]
        
        return {
            'by_type': by_type,
            'by_risk': by_risk,
            'by_instrument': by_instrument[:10]  # Top 10 instruments
        }
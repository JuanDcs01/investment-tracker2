from typing import Dict, List
from app.models import Instrument
from app.models import Transaction
from app.services.market_service import MarketService
from app.services.fifo import FIFOService
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
                'unrealized_gain': 0.0,
                'unrealized_gain_percentage': 0.0,
                'realized_gain': 0.0,
                'realized_gain_percentage': 0.0,
                'total_gain': 0.0,
                'total_gain_percentage': 0.0
            }
        
        # Fetch current prices
        symbols_data = [
            {'symbol': inst.symbol, 'instrument_type': inst.instrument_type}
            for inst in instruments
        ]
        current_prices = MarketService.get_batch_prices(symbols_data)
        
        # Acumuladores
        total_invested = 0.0
        current_market_value = 0.0
        total_realized_gain = 0.0
        total_unrealized_gain = 0.0
        total_cost_basis_sold = 0.0
        
        for inst in instruments:
            current_price = current_prices.get(inst.symbol, 0)
            
            # Si el precio es 0 o None, el cálculo de ganancia no realizada fallará
            # o devolverá valores inconsistentes.
            if current_price is None:
                current_price = 0.0
            
            transactions = inst.transactions.order_by('transaction_date').all()
            
            # Si acabas de añadir el instrumento y NO tiene transacciones:
            if not transactions:
                continue # Saltarlo es seguro, pero no debe anular el diccionario
            
            # Calcular métricas con FIFO
            metrics = FIFOService.calculate_instrument_totals(transactions, current_price)
            
            # Acumular valores
            total_invested += metrics['total_investment']
            current_market_value += metrics['current_value']
            total_realized_gain += metrics['realized_gain']
            total_unrealized_gain += metrics['unrealized_gain']
            total_cost_basis_sold += metrics['cost_basis_sold']
        
        # Calcular porcentajes globales
        total_gain = total_realized_gain + total_unrealized_gain
        
        unrealized_gain_percentage = (
            (total_unrealized_gain / (total_invested - total_cost_basis_sold) * 100)
            if (total_invested - total_cost_basis_sold) > 0 else 0.0
        )
        
        realized_gain_percentage = (
            (total_realized_gain / total_cost_basis_sold * 100)
            if total_cost_basis_sold > 0 else 0.0
        )
        
        total_gain_percentage = (
            (total_gain / total_invested * 100)
            if total_invested > 0 else 0.0
        )
        
        return {
            'total_invested': round(total_invested, 2),
            'current_market_value': round(current_market_value, 2),
            'unrealized_gain': round(total_unrealized_gain, 2),
            'unrealized_gain_percentage': round(unrealized_gain_percentage, 2),
            'realized_gain': round(total_realized_gain, 2),
            'realized_gain_percentage': round(realized_gain_percentage, 2),
            'total_gain': round(total_gain, 2),
            'total_gain_percentage': round(total_gain_percentage, 2)
        }
    
    @staticmethod
    def calculate_instrument_metrics(instrument: Instrument) -> Dict:
        """
        Calculate metrics for a single instrument using FIFO.
        
        Args:
            instrument: Instrument object
            
        Returns:
            dict: Instrument metrics
        """
        current_price = MarketService.get_current_price(
            instrument.symbol,
            instrument.instrument_type
        )
        
        if not current_price:
            current_price = 0.0
        
        # Obtener transacciones ordenadas
        transactions = instrument.transactions.order_by('transaction_date').all()
        
        if not transactions:
            return {
                'symbol': instrument.symbol,
                'type': instrument.instrument_type,
                'current_quantity': 0.0,
                'average_price': 0.0,
                'current_price': 0.0,
                'current_value': 0.0,
                'cost_basis': 0.0,
                'unrealized_gain': 0.0,
                'unrealized_gain_percentage': 0.0,
                'realized_gain': 0.0,
                'realized_gain_percentage': 0.0,
                'total_gain': 0.0,
                'total_gain_percentage': 0.0,
                'total_investment': 0.0,
                'instrument_id': instrument.id
            }
        
        # Calcular usando FIFO
        metrics = FIFOService.calculate_instrument_totals(transactions, current_price)
        
        return {
            'symbol': instrument.symbol,
            'type': instrument.instrument_type,
            'current_quantity': metrics['current_quantity'],
            'average_price': metrics['average_price'],
            'current_price': current_price,
            'current_value': metrics['current_value'],
            'cost_basis': metrics['cost_basis'],
            'unrealized_gain': metrics['unrealized_gain'],
            'unrealized_gain_percentage': metrics['unrealized_gain_percentage'],
            'realized_gain': metrics['realized_gain'],
            'realized_gain_percentage': metrics['realized_gain_percentage'],
            'total_gain': metrics['total_gain'],
            'total_gain_percentage': metrics['total_gain_percentage'],
            'total_investment': metrics['total_investment'],
            'total_commissions': metrics['total_commissions'],
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
            transactions = inst.transactions.order_by('transaction_date').all()
            
            if not transactions or not current_price:
                continue
            
            unrealized = FIFOService.calculate_unrealized_gain(transactions, current_price)
            current_value = unrealized['current_value']
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
from typing import Dict, List
from app.models import Instrument, Wallet
from app.services.market_service import MarketService
from app.services.fifo import FIFOService
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service for portfolio calculations and metrics."""
    
    @staticmethod
    def calculate_portfolio_metrics(instruments: List[Instrument], user: int) -> Dict:
        """
        Calculate overall portfolio metrics.
        
        Args:
            instruments: List of Instrument objects
            
        Returns:
            dict: Portfolio metrics including totals and gains
        """
        if not instruments:
            return {
                'current_investment': 0.0,  # Inversión actual (no total histórico)
                'current_market_value': 0.0,
                'current_market_value_dop': 0.0,
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
        current_investment = Decimal('0.0')
        current_market_value = Decimal('0.0')
        total_realized_gain = Decimal('0.0')
        total_unrealized_gain = Decimal('0.0')
        total_cost_basis_sold = Decimal('0.0')

        dop = MarketService.get_usd_to_dop_rate()
        
        for inst in instruments:
            current_price = current_prices.get(inst.symbol, 0)
            
            if current_price is None:
                current_price = 0.0
            
            # Obtener transacciones ordenadas
            transactions = inst.transactions.order_by('transaction_date').all()
            
            if not transactions:
                continue
            
            # Calcular métricas con FIFO
            metrics = FIFOService.calculate_instrument_totals(transactions, current_price)   
            
            # Acumular valores
            # current_investment = solo el costo de lo que AÚN tienes
            current_investment += Decimal(str(metrics['cost_basis']))
            current_market_value += Decimal(str(metrics['current_value']))
            total_realized_gain += Decimal(str(metrics['realized_gain']))
            total_unrealized_gain += Decimal(str(metrics['unrealized_gain']))
            total_cost_basis_sold += Decimal(str(metrics['cost_basis_sold']))

        current_market_value_dop = current_market_value * dop

        wallet = Wallet.query.filter_by(user_id=user).first()

        try:
            total_realized_gain -= Decimal(wallet.commissions)
            total_realized_gain += Decimal(wallet.dividend)
        except Exception as e:
            logger.error(f"Error registering transaction: {e}")
            total_realized_gain = 0

        # Calcular porcentajes globales
        total_gain = total_realized_gain + total_unrealized_gain
        
        # % de ganancia no realizada sobre la inversión actual
        unrealized_gain_percentage = (
            (total_unrealized_gain / current_investment * 100)
            if current_investment > 0 else 0.0
        )
        
        # % de ganancia realizada sobre lo vendido
        realized_gain_percentage = (
            (total_realized_gain / total_cost_basis_sold * 100)
            if total_cost_basis_sold > 0 else 0.0
        )
        
        # % de ganancia total sobre inversión actual + lo vendido
        total_investment_historical = current_investment + total_cost_basis_sold
        total_gain_percentage = (
            (total_gain / total_investment_historical * 100)
            if total_investment_historical > 0 else 0.0
        )
        
        return {
            'current_investment': round(current_investment, 2),  # ✅ NUEVO NOMBRE
            'current_market_value': round(current_market_value, 2),
            'current_market_value_dop': round(current_market_value_dop, 2),
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
        change_info = MarketService.get_intraday_change(
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
                'current_price': current_price,
                'current_value': 0.0,
                'current_investment': 0.0,  # ✅ Inversión actual por instrumento
                'unrealized_gain': 0.0,
                'unrealized_gain_percentage': 0.0,
                'realized_gain': 0.0,
                'realized_gain_percentage': 0.0,
                'total_gain': 0.0,
                'total_gain_percentage': 0.0,
                'change': change_info['change'],
                'change_percentage': change_info['change_percent'],
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
            'current_investment': metrics['cost_basis'],  # ✅ Solo lo que tienes ahora
            'unrealized_gain': metrics['unrealized_gain'],
            'unrealized_gain_percentage': metrics['unrealized_gain_percentage'],
            'realized_gain': metrics['realized_gain'],
            'realized_gain_percentage': metrics['realized_gain_percentage'],
            'total_gain': metrics['total_gain'],
            'total_gain_percentage': metrics.get('total_gain_percentage', 0.0),
            'total_commissions': metrics['total_commissions'],
            'change': change_info['change'],
            'change_percentage': change_info['change_percent'],
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
        total_value = Decimal(str('0.0'))
        
        for inst in instruments:
            current_price = current_prices.get(inst.symbol, 0)
            transactions = inst.transactions.order_by('transaction_date').all()
            
            if not transactions or not current_price:
                continue
            
            unrealized = FIFOService.calculate_unrealized_gain(transactions, current_price)
            current_value = Decimal(unrealized['current_value'])
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
                'percentage': float(round((value / total_value * 100) if total_value > 0 else 0, 2))
            }
            for key, value in type_distribution.items()
            if value > 0
        ]

        
        by_risk = [
            {
                'label': 'Riesgo Medio (ETF)' if key == 'medium' else 'Riesgo Alto (Stock/Crypto)',
                'value': value,
                'percentage': float(round((value / total_value * 100) if total_value > 0 else 0, 2))
            }
            for key, value in risk_distribution.items()
            if value > 0
        ]
        
        by_instrument = [
            {
                'label': item['symbol'],
                'value': item['value'],
                'percentage': float(round((item['value'] / total_value * 100) if total_value > 0 else 0, 2))
            }
            for item in sorted(instrument_values, key=lambda x: x['value'], reverse=True)
            if item['value'] > 0
        ]
        
        return {
            'by_type': by_type,
            'by_risk': by_risk,
            'by_instrument': by_instrument[:10]  # Top 10 instruments
        }
    
    @staticmethod
    def create_wallet_default(user):
        try:
            # Asegúrate de pasar user.id si user es el objeto del usuario
            new_wallet = Wallet(user_id=user.id, balance=0.0, commissions=0.0, dividend=0.0)
            return new_wallet
        except Exception as e:
            logger.error(f"Error creando wallet: {e}")
            return None # Retorna None explícitamente si falla
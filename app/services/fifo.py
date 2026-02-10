"""
FIFO Service - Cálculo de Ganancias Realizadas
First In, First Out method for calculating realized gains/losses
"""

from typing import List, Dict
from decimal import Decimal, ROUND_HALF_UP
import logging

logger = logging.getLogger(__name__)


class FIFOService:
    """Service for calculating realized gains using FIFO method."""
    
    @staticmethod
    def calculate_realized_gain(transactions: List) -> Dict:
        """
        Calcula la ganancia realizada usando FIFO, incluyendo comisiones 
        en el costo base para obtener la ganancia neta real.
        """
        # Separar y ordenar transacciones
        buys = sorted([t for t in transactions if t.transaction_type == 'buy'], 
                      key=lambda x: x.transaction_date)
        sells = sorted([t for t in transactions if t.transaction_type == 'sell'], 
                       key=lambda x: x.transaction_date)
        
        if not sells:
            # No hay ventas, retornar ceros
            total_buy_commissions = sum(float(t.commission) for t in buys) if buys else 0.0
            return {
                'realized_gain': 0.0,
                'realized_gain_percentage': 0.0,
                'total_sold': 0.0,
                'cost_basis_sold': 0.0,
                'commissions_paid': total_buy_commissions  # ✅ CLAVE CORRECTA
            }

        # Cola de compras con Decimal para precisión
        buy_queue = []
        for buy in buys:
            buy_queue.append({
                'quantity': Decimal(str(buy.quantity)),
                'price': Decimal(str(buy.price)),
                'commission': Decimal(str(buy.commission))
            })

        total_sold_neto = Decimal('0.0')   # (Precio * Q) - Comisión de venta
        cost_basis_total = Decimal('0.0')  # (Precio * Q) + Comisión de compra proporcional
        total_commissions = Decimal('0.0')

        for sell in sells:
            quantity_to_sell = Decimal(str(sell.quantity))
            sell_price = Decimal(str(sell.price))
            sell_commission = Decimal(str(sell.commission))

            # Dinero que realmente entra al bolsillo
            total_sold_neto += (quantity_to_sell * sell_price) - sell_commission
            total_commissions += sell_commission
            
            remaining_to_sell = quantity_to_sell
            
            while remaining_to_sell > 0 and buy_queue:
                oldest_buy = buy_queue[0]
                
                if oldest_buy['quantity'] <= remaining_to_sell:
                    # Caso: Venta completa del lote
                    actual_qty = oldest_buy['quantity']
                    # Costo = (Precio * Q) + Su comisión total
                    cost = (actual_qty * oldest_buy['price']) + oldest_buy['commission']
                    
                    cost_basis_total += cost
                    total_commissions += oldest_buy['commission']
                    remaining_to_sell -= actual_qty
                    buy_queue.pop(0)
                else:
                    # Caso: Venta parcial del lote
                    actual_qty = remaining_to_sell
                    # Proporción de la comisión de compra
                    commission_portion = (actual_qty / oldest_buy['quantity']) * oldest_buy['commission']
                    
                    # Costo = (Precio * Q_parcial) + Comisión_proporcional
                    cost = (actual_qty * oldest_buy['price']) + commission_portion
                    
                    cost_basis_total += cost
                    total_commissions += commission_portion
                    
                    # Actualizar el lote para la siguiente venta
                    oldest_buy['quantity'] -= actual_qty
                    oldest_buy['commission'] -= commission_portion
                    remaining_to_sell = Decimal('0')

        # Ganancia realizada neta (ya incluye todas las comisiones)
        realized_gain = total_sold_neto - cost_basis_total
        
        # Porcentaje de ganancia sobre el costo total (incluyendo comisiones)
        gain_pct = (realized_gain / cost_basis_total * 100) if cost_basis_total > 0 else Decimal('0')

        return {
            'realized_gain': float(realized_gain.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'realized_gain_percentage': float(gain_pct.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'total_sold': float(total_sold_neto.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'cost_basis_sold': float(cost_basis_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'commissions_paid': float(total_commissions.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))  # ✅ CLAVE CORRECTA
        }
    
    @staticmethod
    def calculate_unrealized_gain(
        transactions: List,
        current_price: float
    ) -> Dict:
        """
        Calcula la ganancia no realizada de la posición actual.
        
        Args:
            transactions: Lista de transacciones ordenadas por fecha
            current_price: Precio actual del instrumento
            
        Returns:
            dict: Métricas de la posición actual
        """
        buys = [t for t in transactions if t.transaction_type == 'buy']
        sells = [t for t in transactions if t.transaction_type == 'sell']
        
        # Calcular cantidad actual
        total_bought = sum(float(t.quantity) for t in buys)
        total_sold = sum(float(t.quantity) for t in sells)
        current_quantity = total_bought - total_sold
        
        if current_quantity <= 0:
            return {
                'unrealized_gain': 0.0,
                'unrealized_gain_percentage': 0.0,
                'current_quantity': 0.0,
                'cost_basis': 0.0,
                'current_value': 0.0,
                'average_price': 0.0,
                'commissions_paid': 0.0  # ✅ CLAVE CORRECTA
            }
        
        # Calcular costo base de lo que aún se tiene (usando FIFO)
        buys_sorted = sorted(buys, key=lambda x: x.transaction_date)
        
        buy_queue = []
        for buy in buys_sorted:
            buy_queue.append({
                'quantity': float(buy.quantity),
                'price': float(buy.price),
                'commission': float(buy.commission)
            })
        
        # Remover lo vendido (FIFO)
        quantity_to_remove = total_sold
        while quantity_to_remove > 0 and buy_queue:
            oldest_buy = buy_queue[0]
            
            if oldest_buy['quantity'] <= quantity_to_remove:
                quantity_to_remove -= oldest_buy['quantity']
                buy_queue.pop(0)
            else:
                oldest_buy['quantity'] -= quantity_to_remove
                quantity_to_remove = 0
        
        # Calcular costo base de lo que queda
        cost_basis = 0.0
        total_commissions = 0.0
        
        for buy in buy_queue:
            cost_basis += buy['quantity'] * buy['price']
            total_commissions += buy['commission']
        
        # Precio promedio (sin comisiones)
        average_price = cost_basis / current_quantity if current_quantity > 0 else 0.0
        
        # Valor actual
        current_value = current_quantity * current_price
        
        # Ganancia no realizada (sin considerar comisiones en el %)
        unrealized_gain = current_value - cost_basis
        unrealized_gain_percentage = (
            (unrealized_gain / cost_basis * 100) if cost_basis > 0 else 0.0
        )
        
        return {
            'unrealized_gain': round(unrealized_gain, 2),
            'unrealized_gain_percentage': round(unrealized_gain_percentage, 2),
            'current_quantity': round(current_quantity, 12),
            'cost_basis': round(cost_basis, 2),
            'current_value': round(current_value, 2),
            'average_price': round(average_price, 2),
            'commissions_paid': round(total_commissions, 2)  # ✅ CLAVE CORRECTA
        }
    
    @staticmethod
    def calculate_instrument_totals(
        transactions: List,
        current_price: float
    ) -> Dict:
        """
        Calcula todas las métricas para un instrumento.
        
        Args:
            transactions: Lista de transacciones
            current_price: Precio actual
            
        Returns:
            dict: Todas las métricas combinadas
        """
        # Calcular ganancias realizadas y no realizadas
        realized = FIFOService.calculate_realized_gain(transactions)
        unrealized = FIFOService.calculate_unrealized_gain(transactions, current_price)
        
        # Ganancia total = Realizada + No Realizada
        total_gain = realized['realized_gain'] + unrealized['unrealized_gain']
        
        # Cálculo de inversión actual
        # = Costo de lo que tienes + Lo que ya recuperaste con ventas
        total_investment = unrealized['cost_basis'] + realized['cost_basis_sold']

        total_gain_percentage = (
            (total_gain / total_investment * 100)
            if total_investment > 0 else 0.0
        )
        
        # Total de comisiones pagadas (de compras que aún tienes + de ventas)
        # Nota: Las comisiones de compras vendidas ya están en realized['commissions_paid']
        total_commissions = realized['commissions_paid'] + unrealized['commissions_paid']
        
        return {
            # Ganancias
            'realized_gain': realized['realized_gain'],
            'realized_gain_percentage': realized['realized_gain_percentage'],
            'unrealized_gain': unrealized['unrealized_gain'],
            'unrealized_gain_percentage': unrealized['unrealized_gain_percentage'],
            'total_gain': round(total_gain, 2),
            'total_gain_percentage': round(total_gain_percentage, 2),
            
            # Posición actual
            'current_quantity': unrealized['current_quantity'],
            'average_price': unrealized['average_price'],
            'current_value': unrealized['current_value'],
            'cost_basis': unrealized['cost_basis'],
            
            # Histórico
            'total_sold': realized['total_sold'],
            'cost_basis_sold': realized['cost_basis_sold'],
            'total_investment': round(total_investment, 2),
            'total_commissions': round(total_commissions, 2)
        }
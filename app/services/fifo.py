"""
FIFO Service - Cálculo de Ganancias Realizadas
First In, First Out method for calculating realized gains/losses
"""

from typing import List, Dict
from decimal import Decimal, ROUND_HALF_UP
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class FIFOService:
    """Service for calculating realized gains using FIFO method."""
    
    @staticmethod
    def calculate_realized_gain(transactions: List) -> Dict:
        """
        Calcula la ganancia realizada usando FIFO, incluyendo comisiones 
        en el costo base para obtener la ganancia neta real.
        """
        def _to_date(d):
            from datetime import datetime
            return d.date() if isinstance(d, datetime) else d

        # Separar y ordenar transacciones
        buys = sorted([t for t in transactions if t.transaction_type == 'buy'], 
                      key=lambda x: _to_date(x.transaction_date))
        sells = sorted([t for t in transactions if t.transaction_type == 'sell'], 
                       key=lambda x: _to_date(x.transaction_date))
        
        if not sells:
            # No hay ventas, retornar ceros
            total_buy_commissions = sum(Decimal(t.commission) for t in buys) if buys else 0.0
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
            'realized_gain': Decimal(realized_gain.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'realized_gain_percentage': Decimal(gain_pct.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'total_sold': Decimal(total_sold_neto.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'cost_basis_sold': Decimal(cost_basis_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'commissions_paid': Decimal(total_commissions.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))  # ✅ CLAVE CORRECTA
        }
    
    @staticmethod
    def calculate_unrealized_gain(
        transactions: List,
        current_price: Decimal
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
        total_bought = sum(Decimal(t.quantity) for t in buys)
        total_sold = sum(Decimal(t.quantity) for t in sells)
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
        
        def _to_date(d):
            from datetime import datetime
            return d.date() if isinstance(d, datetime) else d

        # Calcular costo base de lo que aún se tiene (usando FIFO)
        buys_sorted = sorted(buys, key=lambda x: _to_date(x.transaction_date))
        
        buy_queue = []
        for buy in buys_sorted:
            buy_queue.append({
                'quantity': Decimal(buy.quantity),
                'price': Decimal(buy.price),
                'commission': Decimal(buy.commission)
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
        cost_basis = Decimal('0.0')
        total_commissions = Decimal('0.0')
        
        for buy in buy_queue:
            cost_basis += buy['quantity'] * buy['price']
            total_commissions += buy['commission']
        
        # Precio promedio (sin comisiones)
        average_price = cost_basis / current_quantity if current_quantity > 0 else 0.0
        
        # Valor actual
        current_value = current_quantity * Decimal(current_price)
        
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
        current_price: Decimal
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
        total_gain = Decimal(realized['realized_gain']) + Decimal(unrealized['unrealized_gain'])
        
        # Cálculo de inversión actual
        # = Costo de lo que tienes + Lo que ya recuperaste con ventas

        total_investment = Decimal(unrealized['cost_basis']) + Decimal(realized['cost_basis_sold'])


        total_gain_percentage = (
            (total_gain / total_investment * 100)
            if total_investment > 0 else 0.0
        )
        
        # Total de comisiones pagadas (de compras que aún tienes + de ventas)
        # Nota: Las comisiones de compras vendidas ya están en realized['commissions_paid']
        total_commissions = Decimal(realized['commissions_paid']) + Decimal(unrealized['commissions_paid'])
        
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

    @staticmethod
    def _validate_fifo_integrity(all_transactions, exclude_id=None):
        """
        Simula el orden cronológico de las transacciones y verifica que nunca
        se vendan más unidades de las disponibles en ese momento.

        Args:
            all_transactions: iterable de objetos Transaction del instrumento.
            exclude_id: id de la transacción a ignorar (usada al eliminar/editar).

        Returns:
            (True, None)              → FIFO válido
            (False, "mensaje error")  → FIFO roto, con descripción del problema
        """
        def _to_date(d):
            from datetime import datetime
            return d.date() if isinstance(d, datetime) else d

        txs = [t for t in all_transactions if t.id != exclude_id]
        txs_sorted = sorted(txs, key=lambda t: (_to_date(t.transaction_date), 0 if t.transaction_type == 'buy' else 1, t.id))

        running_qty = Decimal('0')
        for tx in txs_sorted:
            qty = Decimal(str(tx.quantity))
            if tx.transaction_type == 'buy':
                running_qty += qty
            else:
                running_qty -= qty
                if running_qty < Decimal('0'):
                    date_str = tx.transaction_date.strftime('%d/%m/%Y')
                    return False, (
                        f"La venta del {date_str} requiere más unidades "
                        f"de las disponibles en esa fecha. "
                        f"Ajusta o elimina primero las transacciones posteriores."
                    )
        return True, None
    
    @staticmethod
    def _simulate_fifo_with_new(all_transactions, new_tx_data, replace_id=None):
        """
        Simula el FIFO incluyendo una transacción nueva (o editada) sin guardarla.

        Args:
            all_transactions: transacciones actuales del instrumento.
            new_tx_data: dict con keys: transaction_type, quantity, transaction_date, id=None
            replace_id: si es edición, id de la transacción que se reemplaza.

        Returns:
            (True, None) o (False, "mensaje")
        """
        class FakeTx:
            def __init__(self, d):
                self.id = d.get('id')
                self.transaction_type = d['transaction_type']
                self.quantity = d['quantity']
                self.transaction_date = _to_date(d['transaction_date'])

        def _to_date(d):
            from datetime import datetime
            return d.date() if isinstance(d, datetime) else d

        # Filtrar la que se reemplaza (edición)
        txs = [t for t in all_transactions if t.id != replace_id]
        txs.append(FakeTx(new_tx_data))
        txs_sorted = sorted(txs, key=lambda t: (_to_date(t.transaction_date), 0 if t.transaction_type == 'buy' else 1, t.id or 0))

        running_qty = Decimal('0')
        for tx in txs_sorted:
            qty = Decimal(str(tx.quantity))
            if tx.transaction_type == 'buy':
                running_qty += qty
            else:
                running_qty -= qty
                if running_qty < Decimal('0'):
                    date_str = tx.transaction_date.strftime('%d/%m/%Y')
                    return False, (
                        f"La venta del {date_str} requiere más unidades "
                        f"de las disponibles en esa fecha."
                    )
        return True, None
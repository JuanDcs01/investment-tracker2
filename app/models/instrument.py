from app import db
from datetime import datetime
from sqlalchemy import Index


class Instrument(db.Model):
    """Model representing a financial instrument (stock, ETF, or crypto)."""
    
    __tablename__ = 'instruments'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, unique=True, index=True)
    instrument_type = db.Column(
        db.Enum('stock', 'etf', 'crypto', name='instrument_type_enum'),
        nullable=False
    )
    quantity = db.Column(db.Numeric(20, 12), nullable=False, default=0)
    average_purchase_price = db.Column(db.Numeric(20, 8), nullable=False, default=0)
    total_cost = db.Column(db.Numeric(20, 2), nullable=False, default=0)
    total_commission = db.Column(db.Numeric(20, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    transactions = db.relationship(
        'Transaction',
        backref='instrument',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_symbol_type', 'symbol', 'instrument_type'),
    )
    
    def __repr__(self):
        return f'<Instrument {self.symbol} ({self.instrument_type})>'
    
    def to_dict(self):
        """Convert instrument to dictionary."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'instrument_type': self.instrument_type,
            'quantity': float(self.quantity),
            'average_purchase_price': float(self.average_purchase_price),
            'total_cost': float(self.total_cost),
            'total_commission': float(self.total_commission),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_metrics(self):
        """
        Update average purchase price and total cost based on transactions.
        """
        # Obtener todas las transacciones de compra y venta
        buy_transactions = self.transactions.filter_by(transaction_type='buy').all()
        sell_transactions = self.transactions.filter_by(transaction_type='sell').all()
        
        # Si no hay transacciones de compra, resetear todo
        if not buy_transactions:
            self.quantity = 0
            self.average_purchase_price = 0
            self.total_cost = 0
            self.total_commission = 0
            self.updated_at = datetime.utcnow()
            return
        
        # Calcular cantidad total comprada
        total_bought = sum(float(t.quantity) for t in buy_transactions)
        
        # Calcular cantidad total vendida
        total_sold = sum(float(t.quantity) for t in sell_transactions)
        
        # Cantidad actual en posesión
        current_quantity = total_bought - total_sold
        self.quantity = current_quantity
        
        # Si la cantidad actual es 0 o negativa, resetear
        if current_quantity <= 0:
            self.quantity = 0
            self.average_purchase_price = 0
            self.total_cost = 0
            self.total_commission = sum(
                float(t.commission) for t in buy_transactions + sell_transactions
            )
            self.updated_at = datetime.utcnow()
            return
        
        # Calcular precio promedio ponderado de compra
        # Solo basado en las compras que aún están en posesión
        total_cost_of_purchases = sum(
            float(t.quantity) * float(t.price) 
            for t in buy_transactions
        )
        
        # El precio promedio es el costo total dividido por la cantidad total comprada
        self.average_purchase_price = total_cost_of_purchases / total_bought
        
        # Calcular costo total (inversión actual)
        # Esto es: costo de compras - ingresos de ventas
        total_paid_in_buys = sum(float(t.total_paid) for t in buy_transactions)
        total_received_in_sells = sum(float(t.total_paid) for t in sell_transactions)
        
        # El costo total es lo que pagaste menos lo que recibiste
        # Ajustado proporcionalmente a la cantidad actual
        if total_bought > 0:
            # Costo proporcional a la cantidad que aún posees
            proportion_held = current_quantity / total_bought
            self.total_cost = total_paid_in_buys * proportion_held
        else:
            self.total_cost = 0
        
        # Calcular comisiones totales
        self.total_commission = sum(
            float(t.commission) for t in buy_transactions + sell_transactions
        )
        
        # Actualizar timestamp
        self.updated_at = datetime.utcnow()
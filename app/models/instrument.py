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
    cost_base = db.Column(db.Numeric(20, 2), nullable=False, default=0)
    commission = db.Column(db.Numeric(20, 2), nullable=False, default=0)
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
            'cost_base': float(self.cost_base),
            'commission': float(self.commission),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_metrics(self):
        """
        Update quantity, average purchase price, cost_base (without commissions),
        and total commission based on transactions. Handles purchases, partial
        sales, and total sales correctly.
        """
        # Obtener transacciones de compra y venta
        buy_transactions = self.transactions.filter_by(transaction_type='buy').all()
        sell_transactions = self.transactions.filter_by(transaction_type='sell').all()

        # Si no hay compras, resetear todo
        if not buy_transactions:
            self.quantity = 0
            self.average_purchase_price = 0
            self.cost_base = 0
            self.commission = sum(float(t.commission) for t in sell_transactions)
            self.updated_at = datetime.utcnow()
            return

        # Cantidad total comprada y vendida
        total_bought = sum(float(t.quantity) for t in buy_transactions)
        total_sold = sum(float(t.quantity) for t in sell_transactions)
        current_quantity = total_bought - total_sold
        self.quantity = max(current_quantity, 0)

        # Si no queda cantidad en cartera, resetear cost_base y avg price
        if current_quantity <= 0:
            self.average_purchase_price = 0
            self.cost_base = 0
            self.commission = sum(float(t.commission) for t in buy_transactions + sell_transactions)
            self.updated_at = datetime.utcnow()
            return

        # --- CALCULAR COSTE DE LA POSICIÓN ACTUAL ---
        # Solo el costo de compra sin comisiones
        total_cost_of_buys = sum(float(t.price) * float(t.quantity) for t in buy_transactions)

        # Proporción de la posición que aún se mantiene
        proportion_held = current_quantity / total_bought
        self.cost_base = total_cost_of_buys * proportion_held

        # --- CALCULAR PRECIO PROMEDIO PONDERADO ---
        self.average_purchase_price = self.cost_base / current_quantity

        # --- CALCULAR COMISION TOTAL HISTÓRICA ---
        self.commission = sum(float(t.commission) for t in buy_transactions + sell_transactions)

        # Actualizar timestamp
        self.updated_at = datetime.utcnow()


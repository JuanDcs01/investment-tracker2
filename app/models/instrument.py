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
        """Update average purchase price and total cost based on transactions."""
        buy_transactions = self.transactions.filter_by(transaction_type='buy').all()
        
        if not buy_transactions:
            self.quantity = 0
            self.average_purchase_price = 0
            self.total_cost = 0
            self.total_commission = 0
            return
        
        # Calculate total quantity
        total_quantity = sum(t.quantity for t in buy_transactions)
        total_quantity -= sum(
            t.quantity for t in self.transactions.filter_by(transaction_type='sell').all()
        )
        
        self.quantity = total_quantity
        
        # Calculate weighted average purchase price
        if total_quantity > 0:
            total_cost_without_commission = sum(
                t.quantity * t.price for t in buy_transactions
            )
            self.average_purchase_price = total_cost_without_commission / sum(
                t.quantity for t in buy_transactions
            )
        else:
            self.average_purchase_price = 0
        
        # Calculate total cost including commissions
        self.total_commission = sum(t.commission for t in self.transactions.all())
        self.total_cost = sum(
            t.total_paid for t in buy_transactions
        ) - sum(
            t.total_paid for t in self.transactions.filter_by(transaction_type='sell').all()
        )
        
        self.updated_at = datetime.utcnow()
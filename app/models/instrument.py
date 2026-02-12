from app import db
from datetime import datetime
from sqlalchemy import Index
from decimal import Decimal


class Instrument(db.Model):
    """Model representing a financial instrument (stock, ETF, or crypto)."""
    
    __tablename__ = 'instruments'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, unique=True, index=True)
    instrument_type = db.Column(
        db.Enum('stock', 'etf', 'crypto', name='instrument_type_enum'),
        nullable=False
    )
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
            'quantity': Decimal(self.quantity),
            'cost_base': Decimal(self.cost_base),
            'commission': Decimal(self.commission),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
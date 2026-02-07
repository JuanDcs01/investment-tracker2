from app import db
from datetime import datetime


class Transaction(db.Model):
    """Model representing a buy or sell transaction for an instrument."""
    
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    instrument_id = db.Column(
        db.Integer,
        db.ForeignKey('instruments.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    transaction_type = db.Column(
        db.Enum('buy', 'sell', name='transaction_type_enum'),
        nullable=False
    )
    quantity = db.Column(db.Numeric(20, 12), nullable=False)
    price = db.Column(db.Numeric(20, 8), nullable=False)
    commission = db.Column(db.Numeric(20, 2), nullable=False, default=0)
    total_paid = db.Column(db.Numeric(20, 2), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return (
            f'<Transaction {self.transaction_type} '
            f'{self.quantity} @ {self.price}>'
        )
    
    def to_dict(self):
        """Convert transaction to dictionary."""
        return {
            'id': self.id,
            'instrument_id': self.instrument_id,
            'transaction_type': self.transaction_type,
            'quantity': float(self.quantity),
            'price': float(self.price),
            'commission': float(self.commission),
            'total_paid': float(self.total_paid),
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def calculate_total(self):
        """Calculate total paid for the transaction."""
        base_amount = float(self.quantity) * float(self.price)
        
        if self.transaction_type == 'buy':
            self.total_paid = base_amount + float(self.commission)
        else:  # sell
            self.total_paid = base_amount - float(self.commission)
        
        return self.total_paid
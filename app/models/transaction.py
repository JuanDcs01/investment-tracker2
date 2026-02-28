from app import db
from datetime import datetime
from decimal import Decimal


class Transaction(db.Model):
    """Model representing a buy or sell transaction for an instrument."""

    # Tabla
    __tablename__ = 'transactions'
    
    # Atributos (columnas)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # Añadido
    instrument_id = db.Column(db.Integer, db.ForeignKey('instruments.id', ondelete='CASCADE'), nullable=False, index=True)
    transaction_type = db.Column(db.Enum('buy', 'sell', name='transaction_type_enum'), nullable=False)
    quantity = db.Column(db.Numeric(20, 12), nullable=False)
    price = db.Column(db.Numeric(20, 8), nullable=False)
    commission = db.Column(db.Numeric(20, 2), nullable=False, default=0)
    base_amount = db.Column(db.Numeric(20, 2), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Representacion del objeto
    def __repr__(self):
        return (
            f'<Transaction {self.transaction_type} '
            f'{self.quantity} @ {self.base_amount}>'
        )
    
    # Diccionario del objeto
    def to_dict(self):
        """Convierte la transaccion a un diccionario."""
        return {
            'id': self.id,
            'instrument_id': self.instrument_id,
            'transaction_type': self.transaction_type,
            'quantity': Decimal(self.quantity),
            'price': Decimal(self.price),
            'commission': Decimal(self.commission),
            'base_amount': Decimal(self.base_amount),
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_id': self.user_id
        }

        
    # Calculo de la columna del monto base
    def calculate_base_amount(self):
        """invertido sin comisiones"""
        base_amount = Decimal(self.quantity) * Decimal(self.price)
        self.base_amount = base_amount

        return self.base_amount

    # Total pagado como atributo
    @property
    def total_paid(self):
        """Calculata el total pagado potr transaccion."""
        base_amount = Decimal(self.quantity) * Decimal(self.price)
        
        if self.transaction_type == 'buy':
            return base_amount + Decimal(self.commission)
        else:  # sell
            return base_amount - Decimal(self.commission)
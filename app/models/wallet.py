from app import db
from decimal import Decimal

class Wallet(db.Model):
    __tablename__ = 'wallet'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, default='Hapi')
    quantity = db.Column(db.Numeric(20, 2), nullable=False, default=0)
    commissions = db.Column(db.Numeric(20, 2), nullable=False, default=0)
    dividend = db.Column(db.Numeric(20, 2), nullable=False, default=0)

    def __repr__(self):
        return (
            f'''<wallet {self.id} 
            name {self.name}>'''
        )
    
    def to_dict(self):
        """Convert transaction to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'quantity': Decimal(self.quantity),
            'commissions': Decimal(self.commissions),
            'dividend': Decimal(self.dividend),
        }
from app import db
from decimal import Decimal

class Wallet(db.Model):
    __tablename__ = 'wallet'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Numeric(20, 2), nullable=False, default=0)
    commissions = db.Column(db.Numeric(20, 2), nullable=False, default=0)
    dividend = db.Column(db.Numeric(20, 2), nullable=False, default=0)

    user = db.relationship('User', backref=db.backref('wallet', lazy=True))

    def __repr__(self):
        return (
            f'''<wallet {self.id} 
            user_id {self.user_id}>'''
        )
    
    def to_dict(self):
        """Convert transaction to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'balance': Decimal(self.balance),
            'commissions': Decimal(self.commissions),
            'dividend': Decimal(self.dividend),
        }
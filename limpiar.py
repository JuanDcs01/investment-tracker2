"""
Script para limpiar datos
"""

from app import create_app, db
from app.models import Instrument, Transaction, Wallet

app = create_app('development')

def clean_data():
    
    with app.app_context():
        # 1. Limpieza total
        print("Borrando datos antiguos...")
        Transaction.query.delete()
        Instrument.query.delete()
        Wallet.query.delete()
        db.session.commit()

if __name__ == '__main__':
    clean_data()
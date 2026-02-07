"""
Sample data script for testing Investment Tracker
Run this to populate the database with test data
"""

from datetime import datetime, timedelta
from app import create_app, db
from app.models import Instrument, Transaction
from decimal import Decimal

app = create_app('development')


def create_sample_data():
    """Create sample instruments and transactions."""
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        Transaction.query.delete()
        Instrument.query.delete()
        db.session.commit()
        
        # Sample instruments
        instruments_data = [
            {'symbol': 'AAPL', 'type': 'stock'},
            {'symbol': 'MSFT', 'type': 'stock'},
            {'symbol': 'SPY', 'type': 'etf'},
            {'symbol': 'QQQ', 'type': 'etf'},
            {'symbol': 'BTC', 'type': 'crypto'},
            {'symbol': 'ETH', 'type': 'crypto'},
        ]
        
        print("\nCreating sample instruments...")
        instruments = {}
        
        for data in instruments_data:
            instrument = Instrument(
                symbol=data['symbol'],
                instrument_type=data['type'],
                quantity=0,
                average_purchase_price=0,
                total_cost=0,
                total_commission=0
            )
            db.session.add(instrument)
            instruments[data['symbol']] = instrument
            print(f"  ✓ Created {data['symbol']} ({data['type']})")
        
        db.session.commit()
        
        # Sample transactions
        print("\nCreating sample transactions...")
        
        # AAPL transactions
        transactions = [
            # AAPL
            Transaction(
                instrument_id=instruments['AAPL'].id,
                transaction_type='buy',
                quantity=Decimal('10'),
                price=Decimal('150.00'),
                commission=Decimal('5.00'),
                transaction_date=datetime.now().date() - timedelta(days=30)
            ),
            Transaction(
                instrument_id=instruments['AAPL'].id,
                transaction_type='buy',
                quantity=Decimal('5'),
                price=Decimal('155.00'),
                commission=Decimal('2.50'),
                transaction_date=datetime.now().date() - timedelta(days=15)
            ),
            
            # MSFT
            Transaction(
                instrument_id=instruments['MSFT'].id,
                transaction_type='buy',
                quantity=Decimal('8'),
                price=Decimal('380.00'),
                commission=Decimal('4.00'),
                transaction_date=datetime.now().date() - timedelta(days=25)
            ),
            
            # SPY ETF
            Transaction(
                instrument_id=instruments['SPY'].id,
                transaction_type='buy',
                quantity=Decimal('20'),
                price=Decimal('450.00'),
                commission=Decimal('10.00'),
                transaction_date=datetime.now().date() - timedelta(days=20)
            ),
            
            # QQQ ETF
            Transaction(
                instrument_id=instruments['QQQ'].id,
                transaction_type='buy',
                quantity=Decimal('15'),
                price=Decimal('380.00'),
                commission=Decimal('7.50'),
                transaction_date=datetime.now().date() - timedelta(days=18)
            ),
            
            # BTC
            Transaction(
                instrument_id=instruments['BTC'].id,
                transaction_type='buy',
                quantity=Decimal('0.5'),
                price=Decimal('45000.00'),
                commission=Decimal('50.00'),
                transaction_date=datetime.now().date() - timedelta(days=40)
            ),
            Transaction(
                instrument_id=instruments['BTC'].id,
                transaction_type='buy',
                quantity=Decimal('0.3'),
                price=Decimal('48000.00'),
                commission=Decimal('30.00'),
                transaction_date=datetime.now().date() - timedelta(days=10)
            ),
            
            # ETH
            Transaction(
                instrument_id=instruments['ETH'].id,
                transaction_type='buy',
                quantity=Decimal('5'),
                price=Decimal('2500.00'),
                commission=Decimal('20.00'),
                transaction_date=datetime.now().date() - timedelta(days=35)
            ),
        ]
        
        for trans in transactions:
            trans.calculate_total()
            db.session.add(trans)
            print(f"  ✓ Created transaction: {trans.transaction_type.upper()} "
                  f"{trans.quantity} @ ${trans.price}")
        
        db.session.commit()
        
        # Update instrument metrics
        print("\nUpdating instrument metrics...")
        for symbol, instrument in instruments.items():
            instrument.update_metrics()
            print(f"  ✓ Updated {symbol}: "
                  f"Qty={instrument.quantity}, "
                  f"Avg Price=${instrument.average_purchase_price:.2f}, "
                  f"Total Cost=${instrument.total_cost:.2f}")
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("Sample data created successfully!")
        print("="*50)
        print("\nYou can now start the application and view the dashboard.")


if __name__ == '__main__':
    try:
        create_sample_data()
    except Exception as e:
        print(f"\n❌ Error creating sample data: {str(e)}")
        print("Make sure the database is initialized and configured correctly.")
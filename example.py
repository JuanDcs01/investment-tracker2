"""
Script de carga de datos corregido basado en el modelo Instrument.
Se eliminan los argumentos que causaban el TypeError.
"""

from datetime import datetime
from app import create_app, db
from app.models import Instrument, Transaction, Wallet
from decimal import Decimal

app = create_app('development')

def create_sample_data():
    """Puebla la base de datos con los datos del archivo example.txt."""
    
    with app.app_context():
        # 1. Limpieza total
        print("Borrando datos antiguos...")
        Transaction.query.delete()
        Instrument.query.delete()
        Wallet.query.delete()
        db.session.commit()

        wallet_data = [ 
            {'name': 'Hapi',
                'quantity': 135.62,
                'commissions': 35.43,
                'dividend': 0.27
            },
        ]

        for data in wallet_data:
            wallet = Wallet(
                name=data['name'],
                quantity=data['quantity'],
                commissions=data['commissions'],
                dividend=data['dividend'],
            )
            db.session.add(wallet)

        db.session.commit()
        
        # 2. Creación de Instrumentos
        # Solo usamos campos definidos en tu modelo: symbol, instrument_type, commission
        instruments_data = [
            {'symbol': 'SHLD', 'type': 'etf'},
            {'symbol': 'AMD', 'type': 'stock'},
            {'symbol': 'GOOGL', 'type': 'stock'},
            {'symbol': 'MU', 'type': 'stock'},
            {'symbol': 'QQQ', 'type': 'etf'},
            {'symbol': 'VOO', 'type': 'etf'},
            {'symbol': 'SPY', 'type': 'etf'},
            {'symbol': 'BTC', 'type': 'crypto'},
            {'symbol': 'AAPL', 'type': 'stock'},
            {'symbol': 'PWR', 'type': 'stock'},
        ]
        
        instruments = {}
        for data in instruments_data:
            instrument = Instrument(
                symbol=data['symbol'],
                instrument_type=data['type'],
                commission=0  # Valor inicial por defecto
            )
            db.session.add(instrument)
            instruments[data['symbol']] = instrument
        
        db.session.commit()
        
        # 3. Datos de Transacciones extraídos de example.txt
        raw_transactions = [
            # SHLD [cite: 1]
            {'sym': 'SHLD', 'type': 'buy', 'qty': '0.64838', 'px': '77.11', 'comm': '0.15', 'dt': '2026-01-28'},
            # AMD [cite: 1]
            {'sym': 'AMD', 'type': 'buy', 'qty': '0.24581', 'px': '203.40', 'comm': '0.15', 'dt': '2026-02-06'},
            # AAPL
            {'sym': 'AAPL', 'type': 'buy', 'qty': '0.07217', 'px': '277.11', 'comm': '0.15', 'dt': '2026-11-26'},
            {'sym': 'AAPL', 'type': 'sell', 'qty': '0.07217', 'px': '271.44', 'comm': '0.16', 'dt': '2026-12-23'},
            # GOOGL [cite: 1]
            {'sym': 'GOOGL', 'type': 'buy', 'qty': '0.02739', 'px': '317.59', 'comm': '0.15', 'dt': '2025-11-24'},
            {'sym': 'GOOGL', 'type': 'buy', 'qty': '0.03513', 'px': '321.91', 'comm': '0.15', 'dt': '2025-11-25'},
            {'sym': 'GOOGL', 'type': 'buy', 'qty': '0.14853', 'px': '336.61', 'comm': '0.15', 'dt': '2026-01-27'},
            {'sym': 'GOOGL', 'type': 'buy', 'qty': '0.23963', 'px': '333.84', 'comm': '0.15', 'dt': '2026-02-04'},
            {'sym': 'GOOGL', 'type': 'buy', 'qty': '0.16186', 'px': '308.89', 'comm': '0.15', 'dt': '2026-02-20'},
            # MU [cite: 1, 2]
            {'sym': 'MU', 'type': 'buy', 'qty': '0.07285', 'px': '274.52', 'comm': '0.15', 'dt': '2025-12-22'},
            {'sym': 'MU', 'type': 'buy', 'qty': '0.07151', 'px': '279.65', 'comm': '0.15', 'dt': '2025-12-24'},
            {'sym': 'MU', 'type': 'buy', 'qty': '0.07247', 'px': '344.93', 'comm': '0.15', 'dt': '2026-01-12'},
            {'sym': 'MU', 'type': 'buy', 'qty': '0.1227', 'px': '407.48', 'comm': '0.15', 'dt': '2026-01-27'},
            {'sym': 'MU', 'type': 'buy', 'qty': '0.46029', 'px': '434.50', 'comm': '0.15', 'dt': '2026-01-28'},
            {'sym': 'MU', 'type': 'sell', 'qty': '0.79982', 'px': '424.72', 'comm': '0.16', 'dt': '2026-01-28'},
            {'sym': 'MU', 'type': 'buy', 'qty': '0.11795', 'px': '423.88', 'comm': '0.15', 'dt': '2026-01-28'},
            {'sym': 'MU', 'type': 'buy', 'qty': '0.47086', 'px': '424.75', 'comm': '0.15', 'dt': '2026-02-02'},
            {'sym': 'MU', 'type': 'sell', 'qty': '0.58881', 'px': '440.57', 'comm': '0.16', 'dt': '2026-02-02'},
            {'sym': 'MU', 'type': 'buy', 'qty': '0.12976', 'px': '385.31', 'comm': '0.15', 'dt': '2026-02-05'},
            {'sym': 'MU', 'type': 'sell', 'qty': '0.12976', 'px': '419.88', 'comm': '0.16', 'dt': '2026-02-12'},
            # QQQ [cite: 1]
            {'sym': 'QQQ', 'type': 'buy', 'qty': '0.15862', 'px': '630.43', 'comm': '0.15', 'dt': '2026-01-27'},
            {'sym': 'QQQ', 'type': 'buy', 'qty': '0.16558', 'px': '603.92', 'comm': '0.15', 'dt': '2026-02-04'},
            # VOO [cite: 1, 3]
            {'sym': 'VOO', 'type': 'buy', 'qty': '0.09204', 'px': '630.16', 'comm': '0.15', 'dt': '2025-12-11'},
            {'sym': 'VOO', 'type': 'buy', 'qty': '0.05324', 'px': '638.56', 'comm': '0.15', 'dt': '2026-01-12'},
            {'sym': 'VOO', 'type': 'buy', 'qty': '0.15647', 'px': '639.06', 'comm': '0.15', 'dt': '2026-01-27'},
            {'sym': 'VOO', 'type': 'buy', 'qty': '0.09481', 'px': '632.83', 'comm': '0.15', 'dt': '2026-02-04'},
            # SPY [cite: 3]
            {'sym': 'SPY', 'type': 'buy', 'qty': '0.02393', 'px': '668.34', 'comm': '0.15', 'dt': '2025-11-24'},
            {'sym': 'SPY', 'type': 'buy', 'qty': '0.05187', 'px': '674.69', 'comm': '0.15', 'dt': '2025-11-25'},
            {'sym': 'SPY', 'type': 'buy', 'qty': '0.02774', 'px': '685.44', 'comm': '0.15', 'dt': '2025-12-11'},
            {'sym': 'SPY', 'type': 'buy', 'qty': '0.0432', 'px': '694.33', 'comm': '0.15', 'dt': '2026-01-12'},
            {'sym': 'SPY', 'type': 'buy', 'qty': '0.14392', 'px': '694.79', 'comm': '0.15', 'dt': '2026-01-27'},
            # BTC [cite: 4]
            {'sym': 'BTC', 'type': 'buy', 'qty': '0.00153515', 'px': '65140.21', 'comm': '1.00', 'dt': '2026-02-05'},
            # PWR [cite: 4]
            {'sym': 'PWR', 'type': 'buy', 'qty': '0.136355', 'px': '550.02', 'comm': '0.15', 'dt': '2026-02-24'},
        ]

        for t in raw_transactions:
            trans = Transaction(
                instrument_id=instruments[t['sym']].id,
                transaction_type=t['type'],
                quantity=Decimal(t['qty']),
                price=Decimal(t['px']),
                commission=Decimal(t['comm']),
                transaction_date=datetime.strptime(t['dt'], '%Y-%m-%d').date()
            )
            # Poblamos el campo base_amount usando tu método del modelo
            trans.calculate_base_amount()
            db.session.add(trans)
            print(f"  ✓ Transacción añadida: {t['sym']} ({t['type']})")

        db.session.commit()
        print("\n¡Carga de datos finalizada con éxito!")

if __name__ == '__main__':
    create_sample_data()
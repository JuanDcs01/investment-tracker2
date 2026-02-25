from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app import db
from app.models import Instrument, Transaction, Wallet
from app.services import MarketService, PortfolioService, FIFOService
from app.utils import Validator
from datetime import datetime
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Dashboard home page."""
    try:
        instruments = Instrument.query.all()
        wallet = Wallet.query.first()

        if not wallet:
            wallet = PortfolioService.create_wallet_default()
            db.session.add(wallet)
            db.session.commit()

        portfolio_metrics = PortfolioService.calculate_portfolio_metrics(instruments)

        instrument_data = []
        for inst in instruments:
            metrics = PortfolioService.calculate_instrument_metrics(inst)
            instrument_data.append(metrics)

        distribution = PortfolioService.get_portfolio_distribution(instruments)
        usd_to_dop = MarketService.get_usd_to_dop_rate()

        return render_template(
            'dashboard.html',
            portfolio=portfolio_metrics,
            instruments=instrument_data,
            distribution=distribution,
            wallet=wallet,
            usd_to_dop=f'{usd_to_dop:.2f}'
        )

    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        flash('Error al cargar el dashboard', 'danger')
        return render_template(
            'dashboard.html',
            portfolio={},
            instruments=[],
            distribution={},
            wallet=[]
        )


@bp.route('/add-instrument', methods=['POST'])
def add_instrument():
    """Add a new instrument to the portfolio."""
    try:
        symbol = request.form.get('symbol', '').strip().upper()
        instrument_type = request.form.get('instrument_type', '').lower()

        is_valid, error = Validator.validate_symbol(symbol)
        if not is_valid:
            return jsonify({'success': False, 'message': error}), 400

        is_valid, error = Validator.validate_instrument_type(instrument_type)
        if not is_valid:
            return jsonify({'success': False, 'message': error}), 400

        existing = Instrument.query.filter_by(symbol=symbol).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'Este instrumento ya existe en el portafolio'
            }), 400

        if not MarketService.verify_symbol(symbol, instrument_type):
            return jsonify({
                'success': False,
                'message': f'El símbolo {symbol} no existe en Yahoo Finance'
            }), 400

        instrument = Instrument(symbol=symbol, instrument_type=instrument_type)
        db.session.add(instrument)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Instrumento {symbol} agregado exitosamente',
            'instrument_id': instrument.id
        })

    except Exception as e:
        logger.error(f"Error adding instrument: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al agregar el instrumento'}), 500


@bp.route('/delete-instrument/<int:instrument_id>', methods=['POST'])
def delete_instrument(instrument_id):
    """Delete an instrument from the portfolio."""
    try:
        instrument = Instrument.query.get_or_404(instrument_id)
        db.session.delete(instrument)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Instrumento {instrument.symbol} eliminado exitosamente'
        })

    except Exception as e:
        logger.error(f"Error deleting instrument: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al eliminar el instrumento'}), 500


@bp.route('/delete-transaction/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    """
    Elimina una transacción del portafolio.

    Validaciones FIFO:
    - Si es una COMPRA: verificar que eliminarla no deje ventas posteriores
      sin suficientes unidades disponibles.
    - Si es una VENTA: simplemente se puede eliminar (solo devuelve dinero
      a la wallet si esa venta ya se había cobrado).
    """
    try:
        transaction = Transaction.query.get_or_404(transaction_id)
        wallet = Wallet.query.first()
        instrument = transaction.instrument
        all_transactions = instrument.transactions.all()

        # ── Validación FIFO (solo aplica al eliminar compras) ──────────────
        if transaction.transaction_type == 'buy':
            valid, error_msg = FIFOService._validate_fifo_integrity(
                all_transactions, exclude_id=transaction_id
            )
            if not valid:
                return jsonify({'success': False, 'message': error_msg}), 400

        # ── Validación de wallet (solo aplica al eliminar ventas) ───────────
        # Si eliminamos una venta, la wallet pierde el dinero que esa venta
        # había aportado; verificar que no quede negativa.
        if transaction.transaction_type == 'sell':
            wallet_after = wallet.quantity - Decimal(str(transaction.total_paid))
            if wallet_after < Decimal('0'):
                return jsonify({
                    'success': False,
                    'message': (
                        f'No se puede eliminar esta venta: la billetera quedaría en '
                        f'${wallet_after:.2f}. Ajusta tu saldo primero.'
                    )
                }), 400

        # ── Revertir efecto en wallet ───────────────────────────────────────
        if transaction.transaction_type == 'buy':
            wallet.quantity += Decimal(str(transaction.total_paid))
        else:
            wallet.quantity -= Decimal(str(transaction.total_paid))

        db.session.delete(transaction)
        db.session.add(wallet)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Transacción eliminada exitosamente'})

    except Exception as e:
        logger.error(f"Error deleting transaction: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al eliminar la transacción'}), 500


@bp.route('/transaction/<int:instrument_id>', methods=['GET', 'POST'])
def register_transaction(instrument_id):
    """Register a buy or sell transaction."""
    instrument = Instrument.query.get_or_404(instrument_id)
    wallet = Wallet.query.first()

    if request.method == 'GET':
        transactions = Transaction.query.filter_by(
            instrument_id=instrument_id
        ).order_by(Transaction.transaction_date.desc(), Transaction.id.desc())

        metrics = PortfolioService.calculate_instrument_metrics(instrument)

        return render_template(
            'transaction.html',
            instrument=instrument,
            transactions=transactions,
            metrics=metrics
        )

    # ── POST ────────────────────────────────────────────────────────────────
    try:
        transaction_type   = request.form.get('transaction_type', '').lower()
        quantity_str       = request.form.get('quantity', '')
        price_str          = request.form.get('price', '')
        commission_str     = request.form.get('commission', '0')
        date_str           = request.form.get('transaction_date', '')
        edit_transaction_id = request.form.get('edit_transaction_id', '').strip()

        # ── Validaciones básicas de campos ──────────────────────────────────
        is_valid, error = Validator.validate_transaction_type(transaction_type)
        if not is_valid:
            flash(error, 'danger')
            return redirect(url_for('main.register_transaction', instrument_id=instrument_id))

        is_valid, error, quantity = Validator.validate_quantity(quantity_str)
        if not is_valid:
            flash(error, 'danger')
            return redirect(url_for('main.register_transaction', instrument_id=instrument_id))

        is_valid, error, price = Validator.validate_price(price_str)
        if not is_valid:
            flash(error, 'danger')
            return redirect(url_for('main.register_transaction', instrument_id=instrument_id))

        is_valid, error, commission = Validator.validate_commission(commission_str)
        if not is_valid:
            flash(error, 'danger')
            return redirect(url_for('main.register_transaction', instrument_id=instrument_id))

        is_valid, error, transaction_date = Validator.validate_date(date_str)
        if not is_valid:
            flash(error, 'danger')
            return redirect(url_for('main.register_transaction', instrument_id=instrument_id))

        # Normalizar a date puro — los registros de DB usan date, el Validator retorna datetime
        if isinstance(transaction_date, datetime):
            transaction_date = transaction_date.date()

        all_transactions = instrument.transactions.all()

        # ── EDICIÓN de transacción existente ────────────────────────────────
        if edit_transaction_id:
            transaction = Transaction.query.get_or_404(int(edit_transaction_id))

            # 1. Validar integridad FIFO con la nueva versión de la transacción
            #    antes de tocar nada en la base de datos.
            valid, fifo_error = FIFOService._simulate_fifo_with_new(
                all_transactions,
                {
                    'id': None,  # se trata como nueva dentro del simulador
                    'transaction_type': transaction_type,
                    'quantity': quantity,
                    'transaction_date': transaction_date,
                },
                replace_id=transaction.id
            )
            if not valid:
                flash(fifo_error, 'danger')
                return redirect(url_for('main.register_transaction', instrument_id=instrument_id))

            # 2. Calcular wallet temporal (revirtiendo la transacción vieja)
            if transaction.transaction_type == 'buy':
                wallet_temp = wallet.quantity + Decimal(str(transaction.total_paid))
            else:
                wallet_temp = wallet.quantity - Decimal(str(transaction.total_paid))

            # 3. Calcular el total de la nueva versión para la validación
            new_total = (quantity * price) + commission if transaction_type == 'buy' \
                        else (quantity * price) - commission

            # 4. Validar poder de compra si la nueva versión es una compra
            if transaction_type == 'buy' and wallet_temp < new_total:
                flash(
                    f'Poder de compra insuficiente. Disponible (billetera + transacción original): '
                    f'${wallet_temp:.2f}',
                    'danger'
                )
                return redirect(url_for('main.register_transaction', instrument_id=instrument_id))

            # 5. Todo OK → aplicar cambios
            # Revertir efecto viejo en wallet
            if transaction.transaction_type == 'buy':
                wallet.quantity += Decimal(str(transaction.total_paid))
            else:
                wallet.quantity -= Decimal(str(transaction.total_paid))

            # Actualizar transacción
            transaction.transaction_type  = transaction_type
            transaction.quantity          = quantity
            transaction.price             = price
            transaction.commission        = commission
            transaction.transaction_date  = transaction_date
            transaction.calculate_base_amount()

            # Aplicar efecto nuevo en wallet
            if transaction.transaction_type == 'buy':
                wallet.quantity -= Decimal(str(transaction.total_paid))
            else:
                wallet.quantity += Decimal(str(transaction.total_paid))

            db.session.add(wallet)
            db.session.commit()

            flash('Transacción actualizada exitosamente', 'success')
            return redirect(url_for('main.register_transaction', instrument_id=instrument_id))

        # ── NUEVA transacción ───────────────────────────────────────────────

        # 1. Validar integridad FIFO incluyendo la nueva transacción
        valid, fifo_error = FIFOService._simulate_fifo_with_new(
            all_transactions,
            {
                'id': None,
                'transaction_type': transaction_type,
                'quantity': quantity,
                'transaction_date': transaction_date,
            }
        )
        if not valid:
            flash(fifo_error, 'danger')
            return redirect(url_for('main.register_transaction', instrument_id=instrument_id))

        # 2. Crear objeto para poder calcular total_paid
        transaction = Transaction(
            instrument_id=instrument_id,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price,
            commission=commission,
            transaction_date=transaction_date
        )
        transaction.calculate_base_amount()

        # 3. Validar poder de compra
        if transaction_type == 'buy':
            if wallet.quantity - Decimal(str(transaction.total_paid)) < Decimal('0'):
                flash(
                    f'Poder de compra insuficiente. Solo posee ${wallet.quantity:.2f}',
                    'danger'
                )
                return redirect(url_for('main.register_transaction', instrument_id=instrument_id))
            wallet.quantity -= Decimal(str(transaction.total_paid))
        else:
            wallet.quantity += Decimal(str(transaction.total_paid))

        db.session.add(transaction)
        db.session.add(wallet)
        db.session.commit()

        tipo_texto = 'compra' if transaction_type == 'buy' else 'venta'
        flash(f'Transacción de {tipo_texto} registrada exitosamente', 'success')
        return redirect(url_for('main.register_transaction', instrument_id=instrument_id))

    except Exception as e:
        logger.error(f"Error registering transaction: {str(e)}")
        db.session.rollback()
        flash('Error al registrar la transacción', 'danger')
        return redirect(url_for('main.register_transaction', instrument_id=instrument_id))


@bp.route('/api/refresh-prices', methods=['POST'])
def refresh_prices():
    """API endpoint to refresh all market prices."""
    try:
        MarketService.clear_cache()
        return jsonify({'success': True, 'message': 'Precios actualizados'})
    except Exception as e:
        logger.error(f"Error refreshing prices: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al actualizar precios'}), 500


@bp.route('/glosario')
def glosario_web():
    return render_template('glosario.html')


@bp.route('/update-wallet', methods=['POST'])
def update_wallet():
    """Update wallet balances."""
    try:
        wallet = Wallet.query.first()

        new_quantity    = Decimal(request.form.get('quantity'))    if request.form.get('quantity')    else Decimal('0')
        new_commissions = Decimal(request.form.get('commissions')) if request.form.get('commissions') else Decimal('0')
        new_dividend    = Decimal(request.form.get('dividend'))    if request.form.get('dividend')    else Decimal('0')

        wallet.quantity     += new_quantity
        wallet.commissions  += new_commissions
        wallet.dividend     += new_dividend

        if wallet.commissions < 0 or wallet.dividend < 0 or wallet.quantity < 0:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Cantidad resultante negativa'})

        db.session.commit()
        return jsonify({'success': True, 'message': 'Billetera actualizada correctamente'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
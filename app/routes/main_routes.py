from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app import db
from app.models import Instrument, Transaction, Wallet
from app.services import MarketService, PortfolioService
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
        # Get all instruments
        instruments = Instrument.query.all()
        wallet = Wallet.query.first()
        
        # Calculate portfolio metrics
        portfolio_metrics = PortfolioService.calculate_portfolio_metrics(instruments)
        
        # Get instrument metrics
        instrument_data = []
        for inst in instruments:
            metrics = PortfolioService.calculate_instrument_metrics(inst)
            instrument_data.append(metrics)
        
        # Get portfolio distribution for charts
        distribution = PortfolioService.get_portfolio_distribution(instruments)
        
        return render_template(
            'dashboard.html',
            portfolio=portfolio_metrics,
            instruments=instrument_data,
            distribution=distribution,
            wallet=wallet
        )
        
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        flash('Error al cargar el dashboard', 'danger')
        return render_template(
            'dashboard.html',
            portfolio={},
            instruments=[],
            distribution={},

        )


@bp.route('/add-instrument', methods=['POST'])
def add_instrument():
    """Add a new instrument to the portfolio."""
    try:
        # Get form data
        symbol = request.form.get('symbol', '').strip().upper()
        instrument_type = request.form.get('instrument_type', '').lower()
        
        # Validate inputs
        is_valid, error = Validator.validate_symbol(symbol)
        if not is_valid:
            return jsonify({'success': False, 'message': error}), 400
        
        is_valid, error = Validator.validate_instrument_type(instrument_type)
        if not is_valid:
            return jsonify({'success': False, 'message': error}), 400
        
        # Check if instrument already exists
        existing = Instrument.query.filter_by(symbol=symbol).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'Este instrumento ya existe en el portafolio'
            }), 400
        
        # Verify symbol exists in Yahoo Finance
        if not MarketService.verify_symbol(symbol, instrument_type):
            return jsonify({
                'success': False,
                'message': f'El símbolo {symbol} no existe en Yahoo Finance'
            }), 400
        
        # Create new instrument (sin campos obsoletos)
        instrument = Instrument(
            symbol=symbol,
            instrument_type=instrument_type
        )
        
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
        return jsonify({
            'success': False,
            'message': 'Error al agregar el instrumento'
        }), 500


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
        return jsonify({
            'success': False,
            'message': 'Error al eliminar el instrumento'
        }), 500


@bp.route('/transaction/<int:instrument_id>', methods=['GET', 'POST'])
def register_transaction(instrument_id):
    """Register a buy or sell transaction."""
    instrument = Instrument.query.get_or_404(instrument_id)
    
    if request.method == 'GET':
        # Get transaction history
        transactions = Transaction.query.filter_by(
            instrument_id=instrument_id
        ).order_by(Transaction.transaction_date.desc()).all()
        
        # Get current metrics for display
        metrics = PortfolioService.calculate_instrument_metrics(instrument)
        
        return render_template(
            'transaction.html',
            instrument=instrument,
            transactions=transactions,
            metrics=metrics
        )
    
    # POST - Register new transaction
    try:
        # Get form data
        transaction_type = request.form.get('transaction_type', '').lower()
        quantity_str = request.form.get('quantity', '')
        price_str = request.form.get('price', '')
        commission_str = request.form.get('commission', '0')
        date_str = request.form.get('transaction_date', '')
        
        # Validate transaction type
        is_valid, error = Validator.validate_transaction_type(transaction_type)
        if not is_valid:
            flash(error, 'danger')
            return redirect(url_for('main.register_transaction', instrument_id=instrument_id))
        
        # Validate quantity
        is_valid, error, quantity = Validator.validate_quantity(quantity_str)
        if not is_valid:
            flash(error, 'danger')
            return redirect(url_for('main.register_transaction', instrument_id=instrument_id))
        
        # Validate price
        is_valid, error, price = Validator.validate_price(price_str)
        if not is_valid:
            flash(error, 'danger')
            return redirect(url_for('main.register_transaction', instrument_id=instrument_id))
        
        # Validate commission
        is_valid, error, commission = Validator.validate_commission(commission_str)
        if not is_valid:
            flash(error, 'danger')
            return redirect(url_for('main.register_transaction', instrument_id=instrument_id))
        
        # Validate date
        is_valid, error, transaction_date = Validator.validate_date(date_str)
        if not is_valid:
            flash(error, 'danger')
            return redirect(url_for('main.register_transaction', instrument_id=instrument_id))
        
        # Check if selling more than owned (using FIFO calculation)
        if transaction_type == 'sell':
            metrics = PortfolioService.calculate_instrument_metrics(instrument)
            current_quantity = Decimal(str(metrics['current_quantity']))
            
            if quantity > current_quantity:
                flash(
                    f'No puede vender {quantity} unidades. Solo posee {current_quantity}',
                    'danger'
                )
                return redirect(url_for('main.register_transaction', instrument_id=instrument_id))
        
        # Create transaction
        transaction = Transaction(
            instrument_id=instrument_id,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price,
            commission=commission,
            transaction_date=transaction_date
        )
        
        # Calculate total
        transaction.calculate_base_amount()
        
        db.session.add(transaction)
        db.session.commit()
        
        flash(
            f'Transacción de {transaction_type.upper()} registrada exitosamente',
            'success'
        )
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
        return jsonify({
            'success': True,
            'message': 'Precios actualizados'
        })
    except Exception as e:
        logger.error(f"Error refreshing prices: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error al actualizar precios'
        }), 500
    
@bp.route('/glosario')
def glosario_web():
    return render_template('glosario.html')

@bp.route('/update-wallet', methods=['POST'])
def update_wallet():
    # Buscamos la única wallet que existe
    wallet = Wallet.query.first()
    
    if not wallet:
        return jsonify({'success': False, 'message': 'No se encontró la billetera'}), 404

    try:
        # Obtenemos los datos del formulario
        new_quantitty = Decimal(request.form.get('quantity'))
        new_commisions = Decimal(request.form.get('commissions'))

        # Actualizamos los valores
        wallet.quantity += new_quantitty
        wallet.commissions += new_commisions

        if wallet.quantity < 0 or wallet.commissions < 0:
            return jsonify({'success': False, 'message': 'Cantida resultante negativa'})

        db.session.commit()
        return jsonify({'success': True, 'message': 'Billetera actualizada correctamente'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
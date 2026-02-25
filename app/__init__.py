from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config
import logging
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

# Configura el registro en un archivo llamado 'errores.log'
logging.basicConfig(
    filename='errores.log', 
    level=logging.ERROR,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()

login_manager.login_message = "Debe inicia sesión para acceder a la página."
login_manager.login_message_category = "danger"

def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions with app
    db.init_app(app)

    # csrf
    csrf.init_app(app)
    

    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Nombre de la ruta de login

    with app.app_context():
        from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.routes import main_routes
    app.register_blueprint(main_routes.bp)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register template filters
    register_template_filters(app)
    
    return app


def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('500.html'), 500


def register_template_filters(app):
    """Register custom template filters."""
    
    @app.template_filter('currency')
    def currency_filter(value):
        """Format value as currency."""
        try:
            return f"${float(value):,.2f}"
        except (ValueError, TypeError):
            return "$0.00"
    
    @app.template_filter('percentage')
    def percentage_filter(value):
        """Format value as percentage."""
        try:
            return f"{float(value):,.2f}%"
        except (ValueError, TypeError):
            return "0.00%"
    
    @app.template_filter('number')
    def number_filter(value, decimals=2):
        """Format number with specified decimals."""
        try:
            return f"{float(value):,.{decimals}f}"
        except (ValueError, TypeError):
            return "0.00"
        
    @app.template_filter('format_smart_decimal')
    def format_smart_decimal(value):
        if not value:
            return "0.00"
        
        # Formatea a 12 decimales
        formatted = f"{value:.12f}".rstrip('0').rstrip('.')
        
        # Si es un entero o no tiene suficientes decimales, asegura el .00
        if '.' not in formatted:
            return f"{formatted}.00"
        if len(formatted.split('.')[1]) < 2:
            return f"{value:.2f}"
            
        return formatted
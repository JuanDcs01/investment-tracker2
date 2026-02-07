from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from app.routes import main_routes
    app.register_blueprint(main_routes.bp)
    
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
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500


def register_template_filters(app):
    """Register custom template filters."""
    
    @app.template_filter('currency')
    def currency_filter(value):
        """Format value as currency."""
        if value is None:
            return "$0.00"
        return f"${value:,.2f}"
    
    @app.template_filter('percentage')
    def percentage_filter(value):
        """Format value as percentage."""
        if value is None:
            return "0.00%"
        return f"{value:,.2f}%"
    
    @app.template_filter('number')
    def number_filter(value, decimals=2):
        """Format number with specified decimals."""
        if value is None:
            return "0.00"
        return f"{value:,.{decimals}f}"
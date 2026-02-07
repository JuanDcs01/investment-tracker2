#!/usr/bin/env python3
"""
Investment Tracker Application
Main entry point for running the Flask application
"""

import os
import logging
from app import create_app, db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Get configuration from environment
config_name = os.getenv('FLASK_ENV', 'development')

# Create application
app = create_app(config_name)


@app.shell_context_processor
def make_shell_context():
    """Create shell context for flask shell command."""
    from app.models import Instrument, Transaction
    from app.services import MarketService, PortfolioService
    
    return {
        'db': db,
        'Instrument': Instrument,
        'Transaction': Transaction,
        'MarketService': MarketService,
        'PortfolioService': PortfolioService
    }


@app.cli.command()
def init_db():
    """Initialize the database."""
    try:
        db.create_all()
        logger.info("Database tables created successfully")
        print("✓ Database initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        print(f"✗ Error initializing database: {str(e)}")


@app.cli.command()
def reset_db():
    """Drop all tables and recreate them."""
    try:
        response = input("This will delete all data. Are you sure? (yes/no): ")
        if response.lower() == 'yes':
            db.drop_all()
            db.create_all()
            logger.info("Database reset successfully")
            print("✓ Database reset successfully!")
        else:
            print("Operation cancelled")
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        print(f"✗ Error resetting database: {str(e)}")


if __name__ == '__main__':
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=(config_name == 'development')
    )
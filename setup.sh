#!/bin/bash

# Investment Tracker Setup Script
# This script automates the setup process

echo "=========================================="
echo "Investment Tracker - Setup Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo "⚠️  MySQL client not found. Make sure MySQL server is installed and running."
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your database credentials"
fi

# Create database (optional)
echo ""
read -p "Do you want to create the MySQL database now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter MySQL root password: " -s mysql_password
    echo ""
    read -p "Enter database name (default: investment_tracker): " db_name
    db_name=${db_name:-investment_tracker}
    
    mysql -u root -p"$mysql_password" -e "CREATE DATABASE IF NOT EXISTS $db_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    
    if [ $? -eq 0 ]; then
        echo "✓ Database created successfully"
    else
        echo "❌ Failed to create database"
    fi
fi

# Initialize database tables
echo ""
read -p "Do you want to initialize database tables? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python run.py init-db
    if [ $? -eq 0 ]; then
        echo "✓ Database tables initialized"
    else
        echo "❌ Failed to initialize database tables"
    fi
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your database credentials"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python run.py"
echo "4. Open: http://localhost:5000"
echo ""
echo "For more information, see README.md"
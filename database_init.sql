-- Investment Tracker Database Initialization Script
-- This script creates the database and necessary tables

-- Create database
CREATE DATABASE IF NOT EXISTS investment_tracker2 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE investment_tracker;

-- Instruments table
CREATE TABLE IF NOT EXISTS instruments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    instrument_type ENUM('stock', 'etf', 'crypto') NOT NULL,
    quantity DECIMAL(20, 12) NOT NULL DEFAULT 0,
    average_purchase_price DECIMAL(20, 8) NOT NULL DEFAULT 0,
    total_cost DECIMAL(20, 2) NOT NULL DEFAULT 0,
    total_commission DECIMAL(20, 2) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_symbol_type (symbol, instrument_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    instrument_id INT NOT NULL,
    transaction_type ENUM('buy', 'sell') NOT NULL,
    quantity DECIMAL(20, 12) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    commission DECIMAL(20, 2) NOT NULL DEFAULT 0,
    total_paid DECIMAL(20, 2) NOT NULL,
    transaction_date DATE NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_instrument_id (instrument_id),
    INDEX idx_transaction_date (transaction_date),
    FOREIGN KEY (instrument_id) REFERENCES instruments(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Display success message
SELECT 'Database and tables created successfully!' AS Status;
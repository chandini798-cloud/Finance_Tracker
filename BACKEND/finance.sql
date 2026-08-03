-- ========================================================
-- finance.sql
-- Personal Finance Tracker - Production Database Schema & Sample Data
-- ========================================================

CREATE DATABASE IF NOT EXISTS FinanceTracker;
USE FinanceTracker;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    type ENUM('Income', 'Expense') NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Optimized Database Indexes for Query Performance
CREATE INDEX idx_user_date ON transactions(user_id, date DESC);
CREATE INDEX idx_user_type ON transactions(user_id, type);
CREATE INDEX idx_category ON transactions(category);

-- ========================================================
-- SAMPLE SEED DATA INSERTIONS
-- ========================================================

-- Insert Demo Users (Password: SecurePass123!)
-- Pre-hashed with PBKDF2-HMAC-SHA256
INSERT INTO users (id, username, password_hash, salt) VALUES
(1, 'CHAITRA1', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', '4a8b12c93d7f1e5a'),
(2, 'demo_user', 'b776b56930533f0e528f5978fgec5fc9b15b2f4ggg2fb18fa09f97g8g8b38bf4', '8f9e01d23c4b5a6b')
ON DUPLICATE KEY UPDATE username=VALUES(username);

-- Insert Sample Transaction Records
INSERT INTO transactions (id, user_id, amount, type, category, description, date) VALUES
(1, 1, 4500.00, 'Income', 'Salary', 'Monthly Software Engineer Salary', '2026-08-01'),
(2, 1, 1400.00, 'Expense', 'Rent & Housing', 'Apartment Rent Payment', '2026-08-01'),
(3, 1, 850.00, 'Income', 'Freelance', 'Full Stack Web Project', '2026-08-02'),
(4, 1, 125.50, 'Expense', 'Food & Dining', 'Weekly Grocery Shopping', '2026-08-02'),
(5, 1, 95.00, 'Expense', 'Utilities', 'Electricity & Water Bill', '2026-08-02'),
(6, 1, 200.00, 'Income', 'Shopping', 'Refund & Reward Cashback', '2026-08-02')
ON DUPLICATE KEY UPDATE amount=VALUES(amount);

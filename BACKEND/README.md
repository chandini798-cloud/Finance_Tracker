# 💰 Personal Finance Tracker - Production Backend Architecture

A modular, enterprise-grade Python backend system for the **Personal Finance Tracker** application. Built adhering to Object-Oriented Programming (OOP) principles, PEP8 coding standards, secure PBKDF2/bcrypt hashing, optimized MySQL queries, and automated financial analytics with Matplotlib and pandas.

---

## 🌟 Key Architecture & Features

1. **🔐 Authentication & Security Subsystem ([auth_manager.py](auth_manager.py))**:
   - Password hashing using PBKDF2-HMAC-SHA256 (100,000 iterations + unique per-user 16-byte salt).
   - Duplicate username prevention and input validation (regex checks, minimum security lengths).
   - Session authentication & constant-time password verification.

2. **📊 Transaction & Dashboard Subsystem ([transaction_manager.py](transaction_manager.py))**:
   - Full CRUD Operations (Add Income, Add Expense, Edit Transaction, Delete Transaction, Fetch History).
   - Automated real-time metric calculations (Total Income, Total Expense, Net Balance, Estimated Savings).
   - Field validations (positive non-zero amounts, `YYYY-MM-DD` date validation, non-empty categories).

3. **📈 Analytics & Visualization Subsystem ([analytics_manager.py](analytics_manager.py))**:
   - Calculates **Highest Expense**, **Highest Income**, **Monthly Spending**, and **Savings Trends**.
   - Server-side Matplotlib chart rendering for Expense Pie Charts, Income vs Expense Bar Charts, and Monthly Line Graphs.

4. **📥 Reports & Data Export Subsystem ([reports_manager.py](reports_manager.py))**:
   - Multi-criteria search and filter engine (Search, Month, Year, Category, Type).
   - Monthly Summaries & Category Breakdown aggregations.
   - One-click CSV export engine powered by **pandas**.

5. **🗄️ Database Management Subsystem ([db_manager.py](db_manager.py))**:
   - Connection pooling and auto-schema initialization (`finance.sql`).
   - Graceful offline fallback engine for zero-downtime demonstration.

---

## 📁 Repository Directory Structure

```text
backend/
├── config.py               # Database configuration settings
├── schema.sql              # Clean DDL database creation script
├── finance.sql             # Full schema DDL + sample seed data
├── db_manager.py           # MySQL connection manager & auto-init
├── auth_manager.py         # Authentication & security subsystem
├── transaction_manager.py  # Dashboard CRUD & metrics subsystem
├── reports_manager.py      # Search, filter, pandas CSV export subsystem
├── analytics_manager.py    # Analytics calculations & Matplotlib engine
├── main_backend.py         # Complete system execution & test suite
├── requirements.txt        # Production dependency specifications
└── README.md               # Production documentation
```

---

## 🚀 Quick Setup & Installation Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure MySQL Database
Import `finance.sql` into your MySQL server:
```bash
mysql -u root -p < finance.sql
```

### 3. Run Backend Demonstration Suite
```bash
python main_backend.py
```

---

## 📄 License & Author
Developed following strict PEP8 standards for production deployment and resume portfolio presentation.

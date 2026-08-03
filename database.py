"""
database.py
-----------
Module for handling MySQL database connections, database auto-creation,
and table initialization for the Personal Finance Tracker application.
"""

import sys
try:
    import mysql.connector
    from mysql.connector import Error
    HAS_MYSQL_CONNECTOR = True
except ImportError:
    HAS_MYSQL_CONNECTOR = False
    class Error(Exception):
        pass

from config import DB_CONFIG, DB_NAME


def get_db_connection(include_db=True):
    """
    Establishes and returns a MySQL database connection.
    
    :param include_db: If True, connects directly to FinanceTracker database.
                       If False, connects to the MySQL server root.
    :return: mysql.connector.CMySQLConnection instance or None.
    """
    if not HAS_MYSQL_CONNECTOR:
        return None

    try:
        connection_params = DB_CONFIG.copy()
        if include_db:
            connection_params["database"] = DB_NAME

        connection = mysql.connector.connect(**connection_params)
        return connection
    except Error:
        # Silently failover to Offline Mode without dumping error logs
        return None


def init_database():
    """
    Initializes the MySQL environment by creating the FinanceTracker database
    and creating the required 'users' and 'transactions' tables if they do not exist.
    """
    # Step 1: Connect to MySQL server (without selecting a specific database)
    conn = get_db_connection(include_db=False)
    if conn is None:
        print("[INFO] MySQL Server not detected on localhost:3306. Starting in Offline Mode.")
        return False

    try:
        cursor = conn.cursor()

        # Step 2: Create FinanceTracker database if it does not exist
        create_db_query = f"CREATE DATABASE IF NOT EXISTS {DB_NAME};"
        cursor.execute(create_db_query)
        print(f"[INFO] Database '{DB_NAME}' checked/created successfully.")

        cursor.close()
        conn.close()

        # Step 3: Connect directly to the FinanceTracker database
        conn = get_db_connection(include_db=True)
        if conn is None:
            return False

        cursor = conn.cursor()

        # Step 4: Create 'users' table
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(256) NOT NULL,
            salt VARCHAR(64) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(create_users_table)
        print("[INFO] Table 'users' checked/created successfully.")

        # Step 5: Create 'transactions' table
        create_transactions_table = """
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
        """
        cursor.execute(create_transactions_table)
        print("[INFO] Table 'transactions' checked/created successfully.")

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Error as e:
        print(f"[ERROR] Database initialization failed: {e}")
        return False

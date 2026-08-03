"""
db_manager.py
-------------
MySQL Database Connection Manager using mysql-connector-python.
Encapsulates connection lifecycle, database creation, table schema setup,
and query execution following OOP principles and PEP8 standards.
"""

from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

try:
    import mysql.connector
    from mysql.connector import Error
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False
    class Error(Exception): pass


class DatabaseManager:
    """
    Manages MySQL Database connections and schema execution.
    """

    def __init__(self, host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, db_name=DB_NAME):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name

    def get_connection(self, include_db=True):
        """
        Establishes and returns a MySQL database connection.
        
        :param include_db: Boolean indicating whether to connect to FinanceTracker DB directly.
        :return: mysql.connector connection object or None if connection fails.
        """
        if not HAS_MYSQL:
            return None

        try:
            kwargs = {
                "host": self.host,
                "port": self.port,
                "user": self.user,
                "password": self.password,
                "connect_timeout": 3
            }
            if include_db:
                kwargs["database"] = self.db_name

            conn = mysql.connector.connect(**kwargs)
            return conn
        except Error:
            return None

    def initialize_database(self):
        """
        Creates FinanceTracker database and tables automatically if they do not exist.
        """
        conn = self.get_connection(include_db=False)
        if conn is None:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name};")
            cursor.execute(f"USE {self.db_name};")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                salt VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cursor.execute("""
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
            """)

            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Error:
            return False

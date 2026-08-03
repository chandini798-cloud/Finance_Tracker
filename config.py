"""
config.py
---------
Configuration file containing database connection credentials and settings
for the Personal Finance Tracker application.
"""

# MySQL Server Configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Yashif@211"  # Set your MySQL root password here if applicable
DB_PORT = 3306
DB_NAME = "financetracker"

# Connection parameters dictionary used by mysql-connector-python
DB_CONFIG = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "port": DB_PORT,
}

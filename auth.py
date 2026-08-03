"""
auth.py
-------
Authentication and security module handling password hashing (PBKDF2-HMAC-SHA256),
input validation, user registration, and login logic for Finance Tracker.
Includes an in-memory Mock Database fallback for offline GUI testing.
"""

import hashlib
import hmac
import re
import secrets
from database import get_db_connection

# Graceful import handling for mysql.connector
try:
    from mysql.connector import Error, IntegrityError
    HAS_MYSQL_CONNECTOR = True
except ImportError:
    HAS_MYSQL_CONNECTOR = False
    class Error(Exception): pass
    class IntegrityError(Exception): pass

# In-Memory Mock Database for Offline GUI Testing (used when MySQL is unavailable)
MOCK_USERS_DB = {}


def generate_salt():
    """Generates a cryptographically strong 32-character hexadecimal salt string."""
    return secrets.token_hex(16)


def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hashes a plaintext password using PBKDF2-HMAC-SHA256 with 100,000 iterations."""
    if salt is None:
        salt = generate_salt()

    iterations = 100_000
    hash_bytes = hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=password.encode('utf-8'),
        salt=salt.encode('utf-8'),
        iterations=iterations
    )
    password_hash = hash_bytes.hex()
    return password_hash, salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verifies plaintext password against stored hash using constant-time comparison."""
    computed_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(computed_hash, stored_hash)


def validate_registration_input(username: str, password: str, confirm_password: str) -> tuple[bool, str]:
    """Validates registration rules: length, allowed chars, matching passwords."""
    username = username.strip()

    if not username or not password or not confirm_password:
        return False, "All fields are required. Please fill in all entries."

    if len(username) < 3 or len(username) > 30:
        return False, "Username must be between 3 and 30 characters long."

    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores (_)."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    if password != confirm_password:
        return False, "Passwords do not match. Please re-enter passwords."

    return True, ""


def validate_login_input(username: str, password: str) -> tuple[bool, str]:
    """Validates user input during login."""
    if not username.strip() or not password:
        return False, "Username and password cannot be empty."
    return True, ""


def register_user(username: str, password: str) -> tuple[bool, str]:
    """Registers a new user into MySQL (or Mock DB if MySQL is offline)."""
    username_clean = username.strip()
    conn = get_db_connection(include_db=True)

    # Fallback to In-Memory Mock Database if MySQL is not connected/installed
    if conn is None:
        if username_clean in MOCK_USERS_DB:
            return False, f"Username '{username_clean}' is already registered (Offline Mode)."
        
        password_hash, salt = hash_password(password)
        MOCK_USERS_DB[username_clean] = {
            "id": len(MOCK_USERS_DB) + 1,
            "username": username_clean,
            "password_hash": password_hash,
            "salt": salt
        }
        return True, "Registration successful (Offline Mode)! You can now log in."

    try:
        cursor = conn.cursor()

        # Step 1: Check duplicate username in MySQL
        check_query = "SELECT id FROM users WHERE username = %s;"
        cursor.execute(check_query, (username_clean,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False, f"Username '{username_clean}' is already taken. Please choose another."

        # Step 2: Hash password securely
        password_hash, salt = hash_password(password)

        # Step 3: Insert record into MySQL
        insert_query = "INSERT INTO users (username, password_hash, salt) VALUES (%s, %s, %s);"
        cursor.execute(insert_query, (username_clean, password_hash, salt))
        conn.commit()

        cursor.close()
        conn.close()
        return True, "Registration successful! You can now log in."

    except IntegrityError:
        return False, f"Username '{username_clean}' is already registered."
    except Error as e:
        return False, f"Database error during registration: {e}"


def login_user(username: str, password: str) -> tuple[bool, str, dict | None]:
    """Authenticates user against MySQL (or Mock DB if offline)."""
    username_clean = username.strip()
    conn = get_db_connection(include_db=True)

    # Fallback to In-Memory Mock Database if MySQL is not connected/installed
    if conn is None:
        if username_clean not in MOCK_USERS_DB:
            return False, "Invalid username or password (Offline Mode).", None

        user = MOCK_USERS_DB[username_clean]
        if verify_password(password, user["password_hash"], user["salt"]):
            user_info = {"id": user["id"], "username": user["username"]}
            return True, "Login successful (Offline Mode)!", user_info
        else:
            return False, "Invalid username or password (Offline Mode).", None

    try:
        cursor = conn.cursor(dictionary=True)

        query = "SELECT id, username, password_hash, salt FROM users WHERE username = %s;"
        cursor.execute(query, (username_clean,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user is None:
            return False, "Invalid username or password.", None

        if verify_password(password, user["password_hash"], user["salt"]):
            user_info = {"id": user["id"], "username": user["username"]}
            return True, "Login successful!", user_info
        else:
            return False, "Invalid username or password.", None

    except Error as e:
        return False, f"Database error during login: {e}", None

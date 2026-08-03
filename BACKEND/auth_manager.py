"""
auth_manager.py
----------------
Authentication and Security Manager for FinanceTracker.
Handles password hashing (PBKDF2-HMAC-SHA256 with unique salts),
input validation, duplicate username checking, registration, and login authentication.
"""

import hashlib
import hmac
import re
import secrets
from db_manager import DatabaseManager


class AuthManager:
    """
    Handles User Registration, Login, Hashing, and Security Validations.
    """

    MOCK_USERS_DB = {}

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_mgr = db_manager or DatabaseManager()

    @staticmethod
    def hash_password(password: str, salt: str = None) -> tuple[str, str]:
        """
        Hashes password using PBKDF2-HMAC-SHA256 with 100,000 iterations and unique salt.
        """
        if salt is None:
            salt = secrets.token_hex(16)

        hash_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations=100000
        )
        return hash_bytes.hex(), salt

    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """Verifies raw password against stored hash and salt."""
        new_hash, _ = AuthManager.hash_password(password, salt)
        return hmac.compare_digest(new_hash, password_hash)

    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """Validates username format and length."""
        username_clean = username.strip()
        if len(username_clean) < 3:
            return False, "Username must be at least 3 characters long."
        if len(username_clean) > 30:
            return False, "Username cannot exceed 30 characters."
        if not re.match(r"^[a-zA-Z0-9_]+$", username_clean):
            return False, "Username can only contain alphanumeric characters and underscores."
        return True, "Valid username."

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validates password strength."""
        if len(password) < 6:
            return False, "Password must be at least 6 characters long."
        return True, "Valid password."

    def register_user(self, username: str, password: str) -> tuple[bool, str]:
        """Registers a new user into MySQL (or Mock DB if offline)."""
        val_u_ok, val_u_msg = self.validate_username(username)
        if not val_u_ok:
            return False, val_u_msg

        val_p_ok, val_p_msg = self.validate_password(password)
        if not val_p_ok:
            return False, val_p_msg

        username_clean = username.strip()
        password_hash, salt = self.hash_password(password)

        conn = self.db_mgr.get_connection(include_db=True)

        if conn is None:
            if username_clean.lower() in [u.lower() for u in self.MOCK_USERS_DB]:
                return False, f"Username '{username_clean}' is already registered (Offline Mode)."
            
            user_id = len(self.MOCK_USERS_DB) + 1
            self.MOCK_USERS_DB[username_clean] = {
                "id": user_id,
                "username": username_clean,
                "password_hash": password_hash,
                "salt": salt
            }
            return True, "Registration successful (Offline Session Mode)!"

        try:
            cursor = conn.cursor()
            check_sql = "SELECT id FROM users WHERE LOWER(username) = LOWER(%s);"
            cursor.execute(check_sql, (username_clean,))
            if cursor.fetchone() is not None:
                cursor.close()
                conn.close()
                return False, f"Username '{username_clean}' is already registered."

            insert_sql = "INSERT INTO users (username, password_hash, salt) VALUES (%s, %s, %s);"
            cursor.execute(insert_sql, (username_clean, password_hash, salt))
            conn.commit()

            cursor.close()
            conn.close()
            return True, "Registration successful! You can now log in."

        except Exception as e:
            return False, f"Database error during registration: {e}"

    def login_user(self, username: str, password: str) -> tuple[bool, str, dict | None]:
        """Authenticates user against MySQL (or Mock DB if offline)."""
        username_clean = username.strip()
        conn = self.db_mgr.get_connection(include_db=True)

        if conn is None:
            if username_clean not in self.MOCK_USERS_DB:
                return False, "Invalid username or password (Offline Mode).", None

            user = self.MOCK_USERS_DB[username_clean]
            if self.verify_password(password, user["password_hash"], user["salt"]):
                return True, "Login successful (Offline Mode)!", {"id": user["id"], "username": user["username"]}
            else:
                return False, "Invalid username or password (Offline Mode).", None

        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT id, username, password_hash, salt FROM users WHERE username = %s;"
            cursor.execute(sql, (username_clean,))
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if user is None:
                return False, "Invalid username or password.", None

            if self.verify_password(password, user["password_hash"], user["salt"]):
                user_info = {"id": user["id"], "username": user["username"]}
                return True, "Login successful!", user_info
            else:
                return False, "Invalid username or password.", None

        except Exception as e:
            return False, f"Database error during login: {e}", None

    def reset_password(self, username: str, new_password: str) -> tuple[bool, str]:
        """
        Resets password for a user given username and new password.
        """
        val_u_ok, val_u_msg = self.validate_username(username)
        if not val_u_ok:
            return False, val_u_msg

        val_p_ok, val_p_msg = self.validate_password(new_password)
        if not val_p_ok:
            return False, val_p_msg

        username_clean = username.strip()
        new_hash, new_salt = self.hash_password(new_password)

        conn = self.db_mgr.get_connection(include_db=True)
        if conn is None:
            found_key = None
            for key in self.MOCK_USERS_DB:
                if key.lower() == username_clean.lower():
                    found_key = key
                    break
            if not found_key:
                return False, f"Username '{username_clean}' not found (Offline Mode)."
            self.MOCK_USERS_DB[found_key]["password_hash"] = new_hash
            self.MOCK_USERS_DB[found_key]["salt"] = new_salt
            return True, "Password reset successful! Please log in with your new password."

        try:
            cursor = conn.cursor()
            check_sql = "SELECT id FROM users WHERE LOWER(username) = LOWER(%s);"
            cursor.execute(check_sql, (username_clean,))
            user_rec = cursor.fetchone()
            if user_rec is None:
                cursor.close()
                conn.close()
                return False, f"Username '{username_clean}' not found."

            update_sql = "UPDATE users SET password_hash = %s, salt = %s WHERE id = %s;"
            cursor.execute(update_sql, (new_hash, new_salt, user_rec[0]))
            conn.commit()
            cursor.close()
            conn.close()
            return True, "Password reset successful! Please log in with your new password."

        except Exception as e:
            return False, f"Database error during password reset: {e}"

    def change_password(self, user_id: int, current_password: str, new_password: str) -> tuple[bool, str]:
        """
        Changes password for an authenticated user by verifying current password first.
        """
        val_p_ok, val_p_msg = self.validate_password(new_password)
        if not val_p_ok:
            return False, val_p_msg

        conn = self.db_mgr.get_connection(include_db=True)
        new_hash, new_salt = self.hash_password(new_password)

        if conn is None:
            user_item = None
            for u in self.MOCK_USERS_DB.values():
                if u["id"] == user_id:
                    user_item = u
                    break
            if not user_item:
                return False, "User account not found (Offline Mode)."
            if not self.verify_password(current_password, user_item["password_hash"], user_item["salt"]):
                return False, "Incorrect current password."
            user_item["password_hash"] = new_hash
            user_item["salt"] = new_salt
            return True, "Password updated successfully!"

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, password_hash, salt FROM users WHERE id = %s;", (user_id,))
            user = cursor.fetchone()
            if not user:
                cursor.close()
                conn.close()
                return False, "User account not found."

            if not self.verify_password(current_password, user["password_hash"], user["salt"]):
                cursor.close()
                conn.close()
                return False, "Incorrect current password."

            update_sql = "UPDATE users SET password_hash = %s, salt = %s WHERE id = %s;"
            cursor.execute(update_sql, (new_hash, new_salt, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            return True, "Password updated successfully!"

        except Exception as e:
            return False, f"Database error updating password: {e}"


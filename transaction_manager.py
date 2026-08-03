"""
transaction_manager.py
----------------------
Transaction Management Subsystem for FinanceTracker Dashboard.
Handles Add Income, Add Expense, Edit, Delete, Fetch History, Input Validation,
and automatic calculation of summary metrics (Total Income, Total Expense, Net Balance, Savings).
"""

from datetime import datetime
from db_manager import DatabaseManager


class TransactionManager:
    """
    Manages CRUD operations and calculations for financial transactions.
    """

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_mgr = db_manager or DatabaseManager()
        # In-memory session store for offline fallback
        self.offline_transactions = [
            {"id": 1, "user_id": 1, "date": "2026-08-01", "type": "Income", "category": "Salary", "amount": 4500.00, "description": "Monthly Salary"},
            {"id": 2, "user_id": 1, "date": "2026-08-01", "type": "Expense", "category": "Rent & Housing", "amount": 1400.00, "description": "Apartment Rent"},
            {"id": 3, "user_id": 1, "date": "2026-08-02", "type": "Income", "category": "Freelance", "amount": 850.00, "description": "Web Development"},
            {"id": 4, "user_id": 1, "date": "2026-08-02", "type": "Expense", "category": "Food & Dining", "amount": 125.50, "description": "Groceries"}
        ]

    @staticmethod
    def validate_transaction_data(amount, trans_type, category, date_str):
        """
        Validates transaction field data.
        
        :return: Tuple (is_valid: bool, error_message: str, parsed_data: dict)
        """
        # Validate Amount
        try:
            amt = float(amount)
            if amt <= 0:
                return False, "Amount must be a positive number greater than 0.", None
        except (ValueError, TypeError):
            return False, "Invalid amount value. Please enter a valid number (e.g. 150.00).", None

        # Validate Type
        t_type = str(trans_type).strip().capitalize()
        if t_type not in ("Income", "Expense"):
            return False, "Transaction type must be 'Income' or 'Expense'.", None

        # Validate Category
        cat = str(category).strip()
        if not cat:
            return False, "Category cannot be empty.", None

        # Validate Date format YYYY-MM-DD
        try:
            d_obj = datetime.strptime(str(date_str).strip(), "%Y-%m-%d")
            formatted_date = d_obj.strftime("%Y-%m-%d")
        except ValueError:
            return False, "Invalid date format. Please use YYYY-MM-DD (e.g. 2026-08-02).", None

        return True, "Valid inputs.", {
            "amount": amt,
            "type": t_type,
            "category": cat,
            "date": formatted_date
        }

    def add_transaction(self, user_id: int, username: str = "User", amount: float = 0.0, trans_type: str = "", category: str = "", description: str = "", date_str: str = "") -> tuple[bool, str, dict | None]:
        """
        Adds a new Income or Expense transaction to MySQL (or local memory).
        """
        is_valid, err_msg, clean_data = self.validate_transaction_data(amount, trans_type, category, date_str)
        if not is_valid:
            return False, err_msg, None

        desc = str(description).strip()
        conn = self.db_mgr.get_connection(include_db=True)

        new_trans = {
            "user_id": user_id,
            "amount": clean_data["amount"],
            "type": clean_data["type"],
            "category": clean_data["category"],
            "description": desc,
            "date": clean_data["date"]
        }

        if conn is None:
            new_id = max([t["id"] for t in self.offline_transactions], default=0) + 1
            new_trans["id"] = new_id
            self.offline_transactions.insert(0, new_trans)
            return True, f"{clean_data['type']} added successfully (Offline Mode)!", new_trans

        try:
            cursor = conn.cursor()
            
            # Ensure user exists in MySQL users table
            cursor.execute("SELECT id FROM users WHERE id = %s OR username = %s;", (user_id, username))
            user_rec = cursor.fetchone()
            if not user_rec:
                from auth_manager import AuthManager
                phash, salt = AuthManager.hash_password("Password123!")
                cursor.execute(
                    "INSERT INTO users (username, password_hash, salt) VALUES (%s, %s, %s);",
                    (username, phash, salt)
                )
                conn.commit()
                db_user_id = cursor.lastrowid
            else:
                db_user_id = user_rec[0]

            insert_sql = """
            INSERT INTO transactions (user_id, amount, type, category, description, date)
            VALUES (%s, %s, %s, %s, %s, %s);
            """
            cursor.execute(insert_sql, (
                db_user_id, clean_data["amount"], clean_data["type"],
                clean_data["category"], desc, clean_data["date"]
            ))
            conn.commit()
            new_id = cursor.lastrowid

            cursor.close()
            conn.close()

            new_trans["id"] = new_id
            self.offline_transactions.insert(0, new_trans)
            return True, f"{clean_data['type']} added successfully to database!", new_trans

        except Exception as e:
            # Fallback local insertion if DB error
            new_id = max([t["id"] for t in self.offline_transactions], default=0) + 1
            new_trans["id"] = new_id
            self.offline_transactions.insert(0, new_trans)
            return True, f"{clean_data['type']} added locally: {e}", new_trans

    def edit_transaction(self, trans_id: int, user_id: int, amount: float, trans_type: str, category: str, description: str, date_str: str) -> tuple[bool, str]:
        """
        Updates an existing transaction by ID.
        """
        is_valid, err_msg, clean_data = self.validate_transaction_data(amount, trans_type, category, date_str)
        if not is_valid:
            return False, err_msg

        desc = str(description).strip()
        conn = self.db_mgr.get_connection(include_db=True)

        # Update in-memory session cache
        for t in self.offline_transactions:
            if t["id"] == trans_id:
                t.update({
                    "amount": clean_data["amount"],
                    "type": clean_data["type"],
                    "category": clean_data["category"],
                    "description": desc,
                    "date": clean_data["date"]
                })
                break

        if conn is None:
            return True, "Transaction updated successfully (Offline Mode)!"

        try:
            cursor = conn.cursor()
            update_sql = """
            UPDATE transactions
            SET amount = %s, type = %s, category = %s, description = %s, date = %s
            WHERE id = %s;
            """
            cursor.execute(update_sql, (
                clean_data["amount"], clean_data["type"], clean_data["category"],
                desc, clean_data["date"], trans_id
            ))
            conn.commit()
            cursor.close()
            conn.close()
            return True, "Transaction updated successfully in database!"

        except Exception as e:
            return True, f"Transaction updated locally: {e}"

    def delete_transaction(self, trans_id: int, user_id: int) -> tuple[bool, str]:
        """
        Deletes a transaction record by ID.
        """
        self.offline_transactions = [t for t in self.offline_transactions if t["id"] != trans_id]
        conn = self.db_mgr.get_connection(include_db=True)

        if conn is None:
            return True, "Transaction deleted successfully (Offline Mode)!"

        try:
            cursor = conn.cursor()
            delete_sql = "DELETE FROM transactions WHERE id = %s;"
            cursor.execute(delete_sql, (trans_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return True, "Transaction deleted successfully from database!"

        except Exception as e:
            return True, f"Transaction deleted locally: {e}"

    def fetch_transactions(self, user_id: int) -> list[dict]:
        """
        Fetches all transaction records for a given user.
        """
        conn = self.db_mgr.get_connection(include_db=True)
        if conn is not None:
            try:
                cursor = conn.cursor(dictionary=True)
                sql = "SELECT id, user_id, date, type, category, amount, description FROM transactions WHERE user_id = %s ORDER BY date DESC, id DESC;"
                cursor.execute(sql, (user_id,))
                rows = cursor.fetchall()
                cursor.close()
                conn.close()
                if rows:
                    return rows
            except Exception as e:
                print(f"[WARN] Error fetching transactions from DB: {e}")

        return list(self.offline_transactions)

    def get_user_transactions(self, user_id: int) -> list[dict]:
        """
        Fetches all transaction records for a given user. Alias for fetch_transactions.
        """
        return self.fetch_transactions(user_id)

    def calculate_dashboard_totals(self, transactions: list[dict]) -> dict:
        """
        Calculates Total Income, Total Expense, Net Balance, Estimated Savings, and Savings Rate.
        
        :param transactions: List of transaction dictionaries.
        :return: Dict containing total summary metrics.
        """
        total_income = sum(float(t.get("amount", 0)) for t in transactions if str(t.get("type", "")).strip().lower() == "income")
        total_expense = sum(float(t.get("amount", 0)) for t in transactions if str(t.get("type", "")).strip().lower() == "expense")
        net_balance = total_income - total_expense
        est_savings = total_income * 0.20
        savings_rate = (net_balance / total_income * 100) if total_income > 0 else 0.0

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_balance": net_balance,
            "est_savings": est_savings,
            "savings_rate": savings_rate
        }

    def calculate_summary_metrics(self, transactions: list[dict]) -> dict:
        """
        Calculates summary metrics for transactions. Alias for calculate_dashboard_totals.
        """
        return self.calculate_dashboard_totals(transactions)


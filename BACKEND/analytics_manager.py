"""
analytics_manager.py
--------------------
Analytics & Data Visualization Subsystem for FinanceTracker.
Queries transaction data from MySQL, calculates key financial metrics
(Highest Expense, Highest Income, Monthly Spending, Savings Trend),
and generates dynamic charts using Matplotlib.
"""

from datetime import datetime
from db_manager import DatabaseManager

try:
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend for server-side chart generation
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class AnalyticsManager:
    """
    Manages Financial Analytics, Trend Calculations, and Matplotlib Chart Generation.
    """

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_mgr = db_manager or DatabaseManager()

    def fetch_transaction_data(self, user_id: int) -> list[dict]:
        """
        Reads raw transaction records from MySQL (or returns default dataset if offline).
        """
        conn = self.db_mgr.get_connection(include_db=True)
        if conn is not None:
            try:
                cursor = conn.cursor(dictionary=True)
                sql = """
                SELECT id, user_id, amount, type, category, description, date
                FROM transactions
                WHERE user_id = %s
                ORDER BY date ASC;
                """
                cursor.execute(sql, (user_id,))
                rows = cursor.fetchall()
                cursor.close()
                conn.close()
                if rows:
                    return rows
            except Exception as e:
                print(f"[WARN] Error querying MySQL for analytics: {e}")

        # Fallback session dataset
        return [
            {"id": 1, "user_id": user_id, "date": "2026-08-01", "type": "Income", "category": "Salary", "amount": 4500.00, "description": "Monthly Salary"},
            {"id": 2, "user_id": user_id, "date": "2026-08-01", "type": "Expense", "category": "Rent & Housing", "amount": 1400.00, "description": "Apartment Rent"},
            {"id": 3, "user_id": user_id, "date": "2026-08-02", "type": "Income", "category": "Freelance", "amount": 850.00, "description": "Web Development"},
            {"id": 4, "user_id": user_id, "date": "2026-08-02", "type": "Expense", "category": "Food & Dining", "amount": 125.50, "description": "Groceries"},
            {"id": 5, "user_id": user_id, "date": "2026-08-02", "type": "Expense", "category": "Utilities", "amount": 95.00, "description": "Electricity"}
        ]

    def calculate_analytics_metrics(self, user_id: int) -> dict:
        """
        Calculates:
        - Highest Expense
        - Highest Income
        - Monthly Spending
        - Savings Trend
        
        :param user_id: Authenticated user ID.
        :return: Dict containing computed analytics metrics.
        """
        transactions = self.fetch_transaction_data(user_id)

        highest_expense = {"amount": 0.0, "category": "N/A", "date": "N/A", "description": "N/A"}
        highest_income = {"amount": 0.0, "category": "N/A", "date": "N/A", "description": "N/A"}

        monthly_income = {}
        monthly_spending = {}
        savings_trend = {}

        for t in transactions:
            amt = float(t.get("amount", 0.0))
            ttype = str(t.get("type", "")).strip().lower()
            cat = str(t.get("category", "Other")).strip()
            date_str = str(t.get("date", ""))

            try:
                d_obj = datetime.strptime(date_str, "%Y-%m-%d")
                period = d_obj.strftime("%Y-%m")
            except ValueError:
                period = "Unknown"

            # Track Highest Income
            if ttype == "income":
                if amt > highest_income["amount"]:
                    highest_income = {
                        "amount": amt,
                        "category": cat,
                        "date": date_str,
                        "description": t.get("description", "")
                    }
                monthly_income[period] = monthly_income.get(period, 0.0) + amt

            # Track Highest Expense
            elif ttype == "expense":
                if amt > highest_expense["amount"]:
                    highest_expense = {
                        "amount": amt,
                        "category": cat,
                        "date": date_str,
                        "description": t.get("description", "")
                    }
                monthly_spending[period] = monthly_spending.get(period, 0.0) + amt

        # Compute Savings Trend (Income - Expense per month)
        all_periods = sorted(set(list(monthly_income.keys()) + list(monthly_spending.keys())))
        for period in all_periods:
            inc = monthly_income.get(period, 0.0)
            exp = monthly_spending.get(period, 0.0)
            savings_trend[period] = inc - exp

        return {
            "highest_expense": highest_expense,
            "highest_income": highest_income,
            "monthly_spending": monthly_spending,
            "savings_trend": savings_trend
        }

    # ----------------------------------------------------
    # Matplotlib Chart Generator Subsystem
    # ----------------------------------------------------
    def generate_expense_pie_chart(self, user_id: int, output_filepath: str = "expense_pie_chart.png") -> tuple[bool, str]:
        """
        Generates Expense Category Pie Chart using Matplotlib.
        """
        if not HAS_MATPLOTLIB:
            return False, "Matplotlib is not installed."

        transactions = self.fetch_transaction_data(user_id)
        expenses = [t for t in transactions if str(t.get("type", "")).strip().lower() == "expense"]

        if not expenses:
            return False, "No expense data available to plot pie chart."

        cat_totals = {}
        for t in expenses:
            cat = str(t.get("category", "Other")).strip()
            cat_totals[cat] = cat_totals.get(cat, 0.0) + float(t.get("amount", 0))

        categories = list(cat_totals.keys())
        amounts = list(cat_totals.values())
        colors = ["#EF4444", "#6366F1", "#F97316", "#F59E0B", "#8B5CF6", "#EC4899", "#3B82F6"]

        plt.figure(figsize=(7, 4.5), dpi=100)
        plt.pie(
            amounts,
            labels=categories,
            autopct='%1.1f%%',
            startangle=90,
            shadow=True,
            colors=colors[:len(categories)]
        )
        plt.axis("equal")
        plt.title("Expense Breakdown by Category", fontsize=12, fontweight="bold")
        plt.tight_layout()

        if output_filepath:
            plt.savefig(output_filepath, dpi=100)
            plt.close()
            return True, f"Expense Pie Chart saved to {output_filepath}"

        plt.close()
        return True, "Expense Pie Chart generated successfully."

    def generate_income_vs_expense_bar_chart(self, user_id: int, output_filepath: str = "income_vs_expense_bar.png") -> tuple[bool, str]:
        """
        Generates Income vs Expense Comparative Bar Chart using Matplotlib.
        """
        if not HAS_MATPLOTLIB:
            return False, "Matplotlib is not installed."

        transactions = self.fetch_transaction_data(user_id)
        total_income = sum(float(t.get("amount", 0)) for t in transactions if str(t.get("type", "")).strip().lower() == "income")
        total_expense = sum(float(t.get("amount", 0)) for t in transactions if str(t.get("type", "")).strip().lower() == "expense")

        plt.figure(figsize=(6, 4), dpi=100)
        bars = plt.bar(["Total Income", "Total Expense"], [total_income, total_expense], color=["#10B981", "#EF4444"], width=0.45)

        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2.0, yval + (max(total_income, total_expense)*0.02), f"${yval:,.2f}", ha='center', va='bottom', fontweight='bold')

        plt.ylabel("Amount ($)", fontsize=10, fontweight="bold")
        plt.title("Total Income vs Total Expense Comparison", fontsize=12, fontweight="bold")
        plt.tight_layout()

        if output_filepath:
            plt.savefig(output_filepath, dpi=100)
            plt.close()
            return True, f"Bar Chart saved to {output_filepath}"

        plt.close()
        return True, "Bar Chart generated successfully."

    def generate_monthly_spending_line_chart(self, user_id: int, output_filepath: str = "monthly_spending_line.png") -> tuple[bool, str]:
        """
        Generates Monthly Spending Trend Line Graph using Matplotlib.
        """
        if not HAS_MATPLOTLIB:
            return False, "Matplotlib is not installed."

        metrics = self.calculate_analytics_metrics(user_id)
        monthly_spending = metrics["monthly_spending"]

        if not monthly_spending:
            return False, "No monthly spending data available to plot."

        periods = sorted(monthly_spending.keys())
        amounts = [monthly_spending[p] for p in periods]

        plt.figure(figsize=(7, 4), dpi=100)
        plt.plot(periods, amounts, marker='o', color="#6366F1", linewidth=2.5, markersize=8)

        for x, y in zip(periods, amounts):
            plt.text(x, y + (max(amounts)*0.03), f"${y:,.2f}", ha='center', fontweight='bold')

        plt.xlabel("Month", fontsize=10, fontweight="bold")
        plt.ylabel("Spending ($)", fontsize=10, fontweight="bold")
        plt.title("Monthly Spending Trend", fontsize=12, fontweight="bold")
        plt.grid(True, linestyle="--", alpha=0.4)
        plt.tight_layout()

        if output_filepath:
            plt.savefig(output_filepath, dpi=100)
            plt.close()
            return True, f"Line Chart saved to {output_filepath}"

        plt.close()
        return True, "Line Chart generated successfully."

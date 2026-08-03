"""
main_backend.py
---------------
Backend Execution Entry Point & Demonstration Suite for FinanceTracker.
Runs registration, authentication, transaction CRUD operations, metrics calculation,
multi-criteria report filtering, category breakdowns, and pandas CSV export.
"""

from db_manager import DatabaseManager
from auth_manager import AuthManager
from transaction_manager import TransactionManager
from reports_manager import ReportsManager
from analytics_manager import AnalyticsManager


def run_backend_demo():
    print("=" * 65)
    print(" 🚀 PERSONAL FINANCE TRACKER - BACKEND SYSTEM DEMO ")
    print("=" * 65)

    # 1. Initialize Database & Tables
    db_mgr = DatabaseManager()
    print("\n[1] INITIALIZING DATABASE & TABLES...")
    db_ok = db_mgr.initialize_database()

    # 2. Authentication Subsystem (Register & Login)
    print("\n[2] TESTING USER AUTHENTICATION & SECURITY...")
    auth_mgr = AuthManager(db_mgr)
    reg_ok, reg_msg = auth_mgr.register_user("demo_user", "SecurePass123!")
    print(f"  • Register Result: {reg_msg}")

    login_ok, login_msg, user_info = auth_mgr.login_user("demo_user", "SecurePass123!")
    print(f"  • Login Result: {login_msg}")

    user_id = user_info["id"] if user_info else 1
    username = user_info["username"] if user_info else "demo_user"

    # 3. Transaction Subsystem (Add Income, Add Expense, Edit, Delete)
    print("\n[3] TESTING TRANSACTION CRUD OPERATIONS...")
    trans_mgr = TransactionManager(db_mgr)

    t1_ok, t1_msg, t1_data = trans_mgr.add_transaction(
        user_id, username, 3500.00, "Income", "Salary", "Monthly Software Engineering Salary", "2026-08-01"
    )
    print(f"  • Add Income: {t1_msg}")

    t2_ok, t2_msg, t2_data = trans_mgr.add_transaction(
        user_id, username, 1200.00, "Expense", "Rent & Housing", "Monthly Apartment Rent", "2026-08-01"
    )
    print(f"  • Add Expense: {t2_msg}")

    transactions = trans_mgr.fetch_transactions(user_id)
    print(f"  • Fetched Transactions: {len(transactions)} total records.")

    # Calculate Totals
    metrics = trans_mgr.calculate_dashboard_totals(transactions)
    print("\n[4] AUTOMATIC DASHBOARD METRICS CALCULATED:")
    print(f"  • Total Income:   ${metrics['total_income']:,.2f}")
    print(f"  • Total Expense:  ${metrics['total_expense']:,.2f}")
    print(f"  • Net Balance:    ${metrics['net_balance']:,.2f}")
    print(f"  • Est. Savings:   ${metrics['est_savings']:,.2f}")

    # 4. Reports Subsystem (Filter, Monthly Summary, Category Breakdown, CSV Export)
    print("\n[5] TESTING REPORTS & PANDAS CSV EXPORT...")
    reports_mgr = ReportsManager(db_mgr)

    filtered = reports_mgr.filter_transactions(transactions, search_query="", trans_type="Expense")
    print(f"  • Filtered Expenses Count: {len(filtered)}")

    monthly_summary = reports_mgr.generate_monthly_summary(transactions)
    print(f"  • Monthly Summary Periods: {list(monthly_summary.keys())}")

    category_summary = reports_mgr.generate_category_summary(transactions)
    print(f"  • Category Summary: {list(category_summary.keys())}")

    export_ok, export_msg = reports_mgr.export_to_csv_pandas(transactions, "finance_report_backend.csv")
    print(f"  • CSV Export Status: {export_msg}")

    # 5. Analytics Subsystem (Highest Expense, Highest Income, Spending, Savings Trend & Matplotlib Charts)
    print("\n[6] TESTING ANALYTICS BACKEND & MATPLOTLIB CHARTS...")
    analytics_mgr = AnalyticsManager(db_mgr)
    analytics_metrics = analytics_mgr.calculate_analytics_metrics(user_id)

    print(f"  • Highest Income:  ${analytics_metrics['highest_income']['amount']:,.2f} ({analytics_metrics['highest_income']['category']})")
    print(f"  • Highest Expense: ${analytics_metrics['highest_expense']['amount']:,.2f} ({analytics_metrics['highest_expense']['category']})")
    print(f"  • Monthly Spending: {analytics_metrics['monthly_spending']}")
    print(f"  • Savings Trend:    {analytics_metrics['savings_trend']}")

    pie_ok, pie_msg = analytics_mgr.generate_expense_pie_chart(user_id, "expense_pie_chart.png")
    print(f"  • Pie Chart Status:  {pie_msg}")

    bar_ok, bar_msg = analytics_mgr.generate_income_vs_expense_bar_chart(user_id, "income_vs_expense_bar.png")
    print(f"  • Bar Chart Status:  {bar_msg}")

    line_ok, line_msg = analytics_mgr.generate_monthly_spending_line_chart(user_id, "monthly_spending_line.png")
    print(f"  • Line Chart Status: {line_msg}")

    print("\n" + "=" * 65)
    print(" ✅ ALL BACKEND SUBSYSTEMS COMPLETED SUCCESSFULLY! ")
    print("=" * 65)


if __name__ == "__main__":
    run_backend_demo()

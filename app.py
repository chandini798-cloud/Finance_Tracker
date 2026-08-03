"""
app.py
------
Streamlit Web Application Entry Point for Personal Finance Tracker.
Provides a modern, interactive web interface powered by Streamlit, Plotly, and Pandas.
Reuses existing Python backend business logic (AuthManager, TransactionManager, DatabaseManager).
Includes session persistence on refresh, currency selector ($ EUR £ ₹ ¥ CA$ A$), and reset/change password features.
"""

import os
import sys
import json
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add current directory to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from auth_manager import AuthManager
from transaction_manager import TransactionManager
from db_manager import DatabaseManager

SETTINGS_FILE = os.path.join(CURRENT_DIR, "settings.json")


def load_settings():
    """Loads application settings from settings.json."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"currency_symbol": "$", "currency_name": "USD ($) - US Dollar"}


def save_settings(settings_dict):
    """Saves application settings to settings.json."""
    try:
        existing = load_settings()
        existing.update(settings_dict)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=4)
    except Exception as e:
        print(f"[WARN] Failed to save settings.json: {e}")


# Page Configuration
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Glassmorphism Styling
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Cards & Containers */
    div.metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }
    
    /* Metrics headers */
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 5px;
    }
    .income-val { color: #10b981; }
    .expense-val { color: #f43f5e; }
    .balance-val { color: #6366f1; }
    
    /* Custom Headers */
    h1, h2, h3 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Backend Services in Streamlit Session State
@st.cache_resource
def get_backend_services():
    db_mgr = DatabaseManager()
    db_mgr.initialize_database()
    auth_mgr = AuthManager(db_mgr)
    trans_mgr = TransactionManager(db_mgr)
    return auth_mgr, trans_mgr

auth_mgr, trans_mgr = get_backend_services()

# Session State & Persistence Initialization
settings_data = load_settings()

if "currency" not in st.session_state:
    qp = st.query_params
    if "currency" in qp:
        st.session_state.currency = qp["currency"]
    else:
        st.session_state.currency = settings_data.get("currency_symbol", "$")

if "user" not in st.session_state or st.session_state.user is None:
    qp = st.query_params
    if "user_id" in qp and "username" in qp:
        try:
            st.session_state.user = {"id": int(qp["user_id"]), "username": qp["username"]}
        except ValueError:
            st.session_state.user = None
    else:
        st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# ==========================================
# AUTHENTICATION MODULE (LOGIN / REGISTER / RESET)
# ==========================================
def render_auth_screen():
    st.markdown("<h1 style='text-align: center;'>💰 Personal Finance Tracker</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Manage income, expenses, analytics, and reports effortlessly.</p>", unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_register, tab_reset = st.tabs(["🔒 Login", "📝 Register", "🔑 Reset Password"])

        # LOGIN TAB
        with tab_login:
            st.subheader("Welcome Back")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("Log In", use_container_width=True, type="primary"):
                    success, msg, user_data = auth_mgr.login_user(username, password)
                    if success:
                        u_obj = user_data or {"id": 1, "username": username}
                        st.session_state.user = u_obj
                        st.query_params["user_id"] = str(u_obj["id"])
                        st.query_params["username"] = str(u_obj["username"])
                        st.query_params["currency"] = st.session_state.currency
                        st.success(f"Welcome, {username}!")
                        st.rerun()
                    else:
                        st.error(msg)
            
            with col_btn2:
                if st.button("🚀 Demo Login", use_container_width=True):
                    demo_user = {"id": 1, "username": "DemoUser"}
                    st.session_state.user = demo_user
                    st.query_params["user_id"] = "1"
                    st.query_params["username"] = "DemoUser"
                    st.query_params["currency"] = st.session_state.currency
                    st.success("Logged in as Demo User!")
                    st.rerun()

        # REGISTER TAB
        with tab_register:
            st.subheader("Create New Account")
            new_user = st.text_input("Choose Username", key="reg_user")
            new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", key="reg_confirm")

            if st.button("Sign Up", use_container_width=True, type="primary"):
                if new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                else:
                    success, msg = auth_mgr.register_user(new_user, new_pass)
                    if success:
                        st.success("Account created successfully! Please head to the Login tab.")
                    else:
                        st.error(msg)

        # RESET PASSWORD TAB
        with tab_reset:
            st.subheader("Reset Password")
            reset_user = st.text_input("Account Username", key="reset_user")
            reset_pass = st.text_input("New Password", type="password", key="reset_pass")
            reset_confirm = st.text_input("Confirm New Password", type="password", key="reset_confirm")

            if st.button("Reset Password", use_container_width=True, type="primary"):
                if reset_pass != reset_confirm:
                    st.error("New passwords do not match.")
                else:
                    success, msg = auth_mgr.reset_password(reset_user, reset_pass)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)


# ==========================================
# MAIN APPLICATION INTERFACE
# ==========================================
def render_main_app():
    user = st.session_state.user
    user_id = user.get("id", 1)
    curr = st.session_state.get("currency", "$")

    # Sidebar Navigation
    with st.sidebar:
        st.title("💰 FinanceTracker")
        st.caption(f"👤 Logged in as: **{user.get('username', 'User')}**")
        st.caption(f"💱 Active Currency: **{curr}**")
        st.divider()

        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "💳 Transactions", "📈 Analytics & Reports", "⚙️ Settings"],
            index=0
        )
        
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.query_params.clear()
            st.rerun()

    # Load Transactions for user
    transactions = trans_mgr.get_user_transactions(user_id)
    metrics = trans_mgr.calculate_summary_metrics(transactions)

    # ------------------------------------------
    # PAGE 1: DASHBOARD OVERVIEW
    # ------------------------------------------
    if page == "📊 Dashboard":
        st.header("📊 Financial Dashboard")
        st.caption("Real-time summary of your financial health")

        # Summary Metric Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="color: #94a3b8;">Total Income</div>
                <div class="metric-value income-val">{curr}{metrics['total_income']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="color: #94a3b8;">Total Expenses</div>
                <div class="metric-value expense-val">{curr}{metrics['total_expense']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div style="color: #94a3b8;">Net Balance</div>
                <div class="metric-value balance-val">{curr}{metrics['net_balance']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            savings_rate = metrics.get('savings_rate', 0.0)
            st.markdown(f"""
            <div class="metric-card">
                <div style="color: #94a3b8;">Savings Rate</div>
                <div class="metric-value" style="color: #f59e0b;">{savings_rate:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts Section
        c_left, c_right = st.columns(2)
        with c_left:
            st.subheader("Expenses by Category")
            if transactions:
                df = pd.DataFrame(transactions)
                exp_df = df[df["type"] == "Expense"]
                if not exp_df.empty:
                    fig_pie = px.pie(
                        exp_df,
                        names="category",
                        values="amount",
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("No expense data logged yet.")
            else:
                st.info("No transaction data available.")

        with c_right:
            st.subheader("Income vs Expenses Overview")
            bar_data = pd.DataFrame({
                "Type": ["Income", "Expense"],
                "Amount": [metrics['total_income'], metrics['total_expense']]
            })
            fig_bar = px.bar(
                bar_data,
                x="Type",
                y="Amount",
                color="Type",
                color_discrete_map={"Income": "#10b981", "Expense": "#f43f5e"}
            )
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
            st.plotly_chart(fig_bar, use_container_width=True)

        # Recent Activity Table
        st.subheader("🕒 Recent Activity")
        if transactions:
            df_recent = pd.DataFrame(transactions)[["date", "type", "category", "description", "amount"]]
            df_recent["amount"] = df_recent["amount"].apply(lambda x: f"{curr}{float(x):,.2f}")
            st.dataframe(df_recent.head(5), use_container_width=True, hide_index=True)
        else:
            st.info("No recent transactions.")

    # ------------------------------------------
    # PAGE 2: TRANSACTIONS MANAGEMENT
    # ------------------------------------------
    elif page == "💳 Transactions":
        st.header("💳 Transaction Management")

        # Add New Transaction Expander
        with st.expander("➕ Add New Transaction", expanded=True):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                t_type = st.selectbox("Type", ["Expense", "Income"])
                t_amount = st.number_input(f"Amount ({curr})", min_value=0.01, step=10.00, value=50.00)

            with col_b:
                categories = (
                    ["Food & Dining", "Rent & Housing", "Shopping", "Entertainment", "Transportation", "Utilities", "Healthcare", "Other"]
                    if t_type == "Expense" else
                    ["Salary", "Freelance", "Investment", "Bonus", "Gift", "Other"]
                )
                t_cat = st.selectbox("Category", categories)
                t_date = st.date_input("Date", value=datetime.date.today())

            with col_c:
                t_desc = st.text_area("Description", value="Transaction note")

            if st.button("Add Transaction", type="primary"):
                is_valid, msg, parsed = trans_mgr.validate_transaction_data(
                    t_amount, t_type, t_cat, t_date.strftime("%Y-%m-%d")
                )
                if is_valid:
                    success, res_msg, _ = trans_mgr.add_transaction(
                        user_id=user_id,
                        username=user.get("username", "User"),
                        amount=parsed["amount"],
                        trans_type=parsed["type"],
                        category=parsed["category"],
                        description=t_desc,
                        date_str=parsed["date"]
                    )
                    if success:
                        st.success("Transaction recorded successfully!")
                        st.rerun()
                    else:
                        st.error(res_msg)
                else:
                    st.error(msg)

        st.divider()

        # Transactions History & Table
        st.subheader("History & Logs")
        if transactions:
            df = pd.DataFrame(transactions)
            
            # Filters
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filter_type = st.multiselect("Filter by Type", ["Income", "Expense"], default=["Income", "Expense"])
            with col_f2:
                search_query = st.text_input("Search Description / Category", "")

            filtered_df = df[df["type"].isin(filter_type)].copy()
            if search_query:
                filtered_df = filtered_df[
                    filtered_df["category"].str.contains(search_query, case=False, na=False) |
                    filtered_df["description"].str.contains(search_query, case=False, na=False)
                ]

            filtered_display = filtered_df[["id", "date", "type", "category", "description", "amount"]].copy()
            filtered_display["amount"] = filtered_display["amount"].apply(lambda x: f"{curr}{float(x):,.2f}")
            st.dataframe(filtered_display, use_container_width=True, hide_index=True)

            # Delete Option
            st.caption("Delete a transaction")
            del_id = st.number_input("Enter Transaction ID to delete", min_value=1, step=1, value=1)
            if st.button("Delete Transaction", type="secondary"):
                success, msg = trans_mgr.delete_transaction(del_id, user_id)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # ------------------------------------------
    # PAGE 3: ANALYTICS & REPORTS
    # ------------------------------------------
    elif page == "📈 Analytics & Reports":
        st.header("📈 Analytics & Reports")
        st.caption("Export data and inspect detailed financial breakdowns")

        if transactions:
            df = pd.DataFrame(transactions)

            # Category Summary Table
            st.subheader("Category Wise Breakdown")
            cat_df = df.groupby(["type", "category"])["amount"].sum().reset_index()
            cat_df["total_amount"] = cat_df["amount"].apply(lambda x: f"{curr}{float(x):,.2f}")
            st.dataframe(cat_df[["type", "category", "total_amount"]], use_container_width=True, hide_index=True)

            st.divider()

            # CSV Export
            st.subheader("📥 Export Data")
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Financial Report (CSV)",
                data=csv_data,
                file_name=f"finance_report_{datetime.date.today()}.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.info("No transaction data available for reports.")

    # ------------------------------------------
    # PAGE 4: SETTINGS
    # ------------------------------------------
    elif page == "⚙️ Settings":
        st.header("⚙️ Application Settings")
        
        # Section 1: User Account Profile
        st.subheader("👤 User Profile")
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            st.write(f"**Username**: `{user.get('username')}`")
        with col_u2:
            st.write(f"**User ID**: `#{user.get('id')}`")

        st.divider()

        # Section 2: Currency Preferences
        st.subheader("💱 Currency Preferences")
        currency_options = {
            "USD ($) - US Dollar": "$",
            "EUR (€) - Euro": "€",
            "GBP (£) - British Pound": "£",
            "INR (₹) - Indian Rupee": "₹",
            "JPY (¥) - Japanese Yen": "¥",
            "CAD (CA$) - Canadian Dollar": "CA$",
            "AUD (A$) - Australian Dollar": "A$"
        }

        current_curr_sym = st.session_state.get("currency", "$")
        default_index = 0
        for idx, (label_text, sym_char) in enumerate(currency_options.items()):
            if sym_char == current_curr_sym:
                default_index = idx
                break

        selected_curr_label = st.selectbox(
            "Select Preferred Currency Symbol",
            list(currency_options.keys()),
            index=default_index
        )
        new_symbol = currency_options[selected_curr_label]

        if new_symbol != current_curr_sym:
            st.session_state.currency = new_symbol
            st.query_params["currency"] = new_symbol
            save_settings({
                "theme": "dark",
                "currency_symbol": new_symbol,
                "currency_name": selected_curr_label
            })
            st.success(f"Currency updated to {new_symbol} ({selected_curr_label})!")
            st.rerun()

        st.divider()

        # Section 3: Password & Security
        st.subheader("🔒 Security & Change Password")
        with st.expander("🔑 Change Account Password", expanded=False):
            curr_pass = st.text_input("Current Password", type="password", key="chg_curr_pass")
            new_pass_val = st.text_input("New Password", type="password", key="chg_new_pass")
            conf_pass_val = st.text_input("Confirm New Password", type="password", key="chg_conf_pass")

            if st.button("Update Password", type="primary"):
                if new_pass_val != conf_pass_val:
                    st.error("New passwords do not match.")
                else:
                    success, msg = auth_mgr.change_password(user_id, curr_pass, new_pass_val)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

        st.divider()

        # Section 4: System Status
        st.subheader("🖥️ System Status")
        st.success("🟢 Active Session: Running Streamlit Web Frontend")
        st.info("💡 Storage Mode: Dual-Engine (Auto MySQL Connection with Session Fallback)")


# Main Entry Control Flow
if st.session_state.user is None:
    render_auth_screen()
else:
    render_main_app()

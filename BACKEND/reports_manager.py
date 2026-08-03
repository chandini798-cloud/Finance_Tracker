"""
reports_manager.py
------------------
Reports, Analytics, and Data Export Subsystem for FinanceTracker.
Handles search queries, multi-criteria filtering, Monthly Summary generation,
Category Breakdown calculations, and CSV export using pandas (or fallback csv engine).
"""

import csv
from datetime import datetime
from db_manager import DatabaseManager

# Try importing pandas for DataFrame operations & CSV Export
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class ReportsManager:
    """
    Manages Report Generation, Searching, Multi-Criteria Filtering, Summaries, and CSV Exports.
    """

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_mgr = db_manager or DatabaseManager()

    def filter_transactions(self, transactions: list[dict], search_query: str = "", month: str = "All Months", year: str = "All Years", category: str = "All Categories", trans_type: str = "All Types") -> list[dict]:
        """
        Applies multi-criteria search and filter conditions to transaction dataset.
        
        :param transactions: Raw list of transaction dicts.
        :param search_query: Free text query matching category or description.
        :param month: Month name (e.g. "August" or "All Months").
        :param year: Year string (e.g. "2026" or "All Years").
        :param category: Category string (e.g. "Salary" or "All Categories").
        :param trans_type: Type string ("Income", "Expense", or "All Types").
        :return: Filtered list of transaction dictionaries.
        """
        search_q = str(search_query).strip().lower()
        filtered = []

        for item in transactions:
            date_str = str(item.get("date", ""))
            try:
                d_obj = datetime.strptime(date_str, "%Y-%m-%d")
                month_name = d_obj.strftime("%B")
                year_str = str(d_obj.year)
            except ValueError:
                month_name = ""
                year_str = ""

            # Search Query filter
            if search_q:
                desc = str(item.get("description", "")).lower()
                cat = str(item.get("category", "")).lower()
                ttype = str(item.get("type", "")).lower()
                if search_q not in desc and search_q not in cat and search_q not in ttype:
                    continue

            # Month filter
            if month != "All Months" and month_name != month:
                continue

            # Year filter
            if year != "All Years" and year_str != year:
                continue

            # Category filter
            if category != "All Categories" and item.get("category") != category:
                continue

            # Type filter
            if trans_type != "All Types" and str(item.get("type")).strip().capitalize() != trans_type:
                continue

            filtered.append(item)

        return filtered

    def generate_monthly_summary(self, transactions: list[dict]) -> dict:
        """
        Generates Monthly Income vs Expense Breakdown.
        
        :return: Dict mapping (Year, Month) -> {"income": float, "expense": float, "savings": float}
        """
        monthly_summary = {}

        for t in transactions:
            date_str = str(t.get("date", ""))
            try:
                d_obj = datetime.strptime(date_str, "%Y-%m-%d")
                period_key = d_obj.strftime("%Y-%m (%B)")
            except ValueError:
                period_key = "Unknown Period"

            if period_key not in monthly_summary:
                monthly_summary[period_key] = {"income": 0.0, "expense": 0.0, "savings": 0.0}

            amt = float(t.get("amount", 0.0))
            ttype = str(t.get("type", "")).strip().lower()

            if ttype == "income":
                monthly_summary[period_key]["income"] += amt
            elif ttype == "expense":
                monthly_summary[period_key]["expense"] += amt

        for period, data in monthly_summary.items():
            data["savings"] = data["income"] - data["expense"]

        return monthly_summary

    def generate_category_summary(self, transactions: list[dict]) -> dict:
        """
        Generates Category Breakdown with percentage calculations.
        
        :return: Dict mapping category -> {"amount": float, "percentage": float, "type": str}
        """
        category_summary = {}
        total_spending = sum(float(t.get("amount", 0)) for t in transactions if str(t.get("type", "")).strip().lower() == "expense")

        for t in transactions:
            cat = str(t.get("category", "Other")).strip()
            amt = float(t.get("amount", 0.0))
            ttype = str(t.get("type", "")).strip().capitalize()

            if cat not in category_summary:
                category_summary[cat] = {"amount": 0.0, "type": ttype, "percentage": 0.0}

            category_summary[cat]["amount"] += amt

        if total_spending > 0:
            for cat, data in category_summary.items():
                if data["type"] == "Expense":
                    data["percentage"] = round((data["amount"] / total_spending) * 100, 2)

        return category_summary

    def export_to_csv_pandas(self, transactions: list[dict], output_filepath: str) -> tuple[bool, str]:
        """
        Exports transaction dataset to CSV using pandas DataFrame (with standard CSV fallback).
        
        :param transactions: List of transaction dicts.
        :param output_filepath: File path string where CSV will be saved.
        :return: Tuple (success: bool, message: str)
        """
        if not transactions:
            return False, "No transaction records found to export."

        try:
            if HAS_PANDAS:
                # pandas DataFrame Export Engine
                df = pd.DataFrame(transactions)
                columns_order = ["id", "date", "type", "category", "amount", "description"]
                existing_cols = [col for col in columns_order if col in df.columns]
                df = df[existing_cols]
                df.to_csv(output_filepath, index=False, encoding="utf-8")
                return True, f"Report exported successfully using pandas to:\n{output_filepath}"
            else:
                # Standard Python CSV Exporter Fallback
                with open(output_filepath, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Date", "Type", "Category", "Amount ($)", "Description"])

                    for t in transactions:
                        writer.writerow([
                            t.get("id", ""),
                            t.get("date", ""),
                            t.get("type", ""),
                            t.get("category", ""),
                            f"{float(t.get('amount', 0)):.2f}",
                            t.get("description", "")
                        ])

                return True, f"Report exported successfully using standard CSV engine to:\n{output_filepath}"

        except Exception as e:
            return False, f"Failed to export CSV report: {e}"

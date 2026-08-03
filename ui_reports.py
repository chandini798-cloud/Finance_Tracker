"""
ui_reports.py
------------
Professional Tkinter Reports & Analytics View for Personal Finance Tracker.
Includes Multi-Criteria Filtering (Month, Year, Category, Type), Monthly Summary Cards,
Category Breakdown Summary, Report Data Table, and Export to CSV functionality.
"""

import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from theme import (
    COLOR_BG_DARK, COLOR_CARD_BG, COLOR_INPUT_BG, COLOR_INPUT_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_INCOME_GREEN,
    COLOR_EXPENSE_RED, COLOR_BALANCE_BLUE, COLOR_PRIMARY_EMERALD,
    COLOR_PRIMARY_HOVER, COLOR_ACCENT_INDIGO, COLOR_ACCENT_HOVER,
    COLOR_NEUTRAL_SLATE, COLOR_NEUTRAL_HOVER, FONT_TITLE, FONT_HEADER,
    FONT_LABEL, FONT_ENTRY, FONT_BUTTON, FONT_CARD_TITLE, FONT_CARD_VALUE,
    format_currency
)


class ReportsView(tk.Frame):
    """
    Reports and Financial Analytics View component.
    """

    MONTH_NAMES = [
        "All Months", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    YEAR_OPTIONS = ["All Years", "2026", "2025", "2024", "2023"]

    CATEGORY_OPTIONS = [
        "All Categories", "Salary", "Freelance", "Investments", "Food & Dining",
        "Rent & Housing", "Utilities", "Entertainment", "Shopping",
        "Transportation", "Healthcare", "Education", "Other"
    ]

    TYPE_OPTIONS = ["All Types", "Income", "Expense"]

    def __init__(self, parent, get_transactions_func):
        """
        Initializes Reports View.
        
        :param parent: Parent frame container.
        :param get_transactions_func: Function returning list of all transactions dicts.
        """
        super().__init__(parent, bg=COLOR_BG_DARK)
        self.get_transactions_func = get_transactions_func
        self.filtered_transactions = []

        # Filter state variables
        self.search_var = tk.StringVar()
        self.month_var = tk.StringVar(value=self.MONTH_NAMES[0])
        self.year_var = tk.StringVar(value=self.YEAR_OPTIONS[0])
        self.category_var = tk.StringVar(value=self.CATEGORY_OPTIONS[0])
        self.type_var = tk.StringVar(value=self.TYPE_OPTIONS[0])

        # Bind filter updates
        self.search_var.trace_add("write", lambda *args: self._apply_filters())

        self._create_widgets()
        self.refresh_report()

    def _create_widgets(self):
        """Builds all UI sub-panels for Reports Page."""

        # ----------------------------------------------------
        # 1. Header Toolbar (Title + Export CSV Button)
        # ----------------------------------------------------
        header_frame = tk.Frame(self, bg=COLOR_BG_DARK)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        title_lbl = tk.Label(
            header_frame,
            text="Financial Reports & Analytics",
            font=FONT_TITLE,
            bg=COLOR_BG_DARK,
            fg=COLOR_TEXT_PRIMARY
        )
        title_lbl.pack(side=tk.LEFT)

        export_btn = tk.Button(
            header_frame,
            text="📥 Export CSV Report",
            font=FONT_BUTTON,
            bg=COLOR_PRIMARY_EMERALD,
            fg="#FFFFFF",
            activebackground=COLOR_PRIMARY_HOVER,
            activeforeground="#FFFFFF",
            bd=0,
            cursor="hand2",
            padx=12,
            command=self._export_to_csv
        )
        export_btn.pack(side=tk.RIGHT, ipady=6)

        # ----------------------------------------------------
        # 2. Multi-Criteria Filter Bar Container
        # ----------------------------------------------------
        filter_card = tk.Frame(self, bg=COLOR_CARD_BG, padx=15, pady=12)
        filter_card.pack(fill=tk.X, pady=(0, 15))

        filter_grid = tk.Frame(filter_card, bg=COLOR_CARD_BG)
        filter_grid.pack(fill=tk.X)

        # Search Field
        search_lbl = tk.Label(filter_grid, text="Search Keywords", font=FONT_LABEL, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY)
        search_lbl.grid(row=0, column=0, sticky="w", padx=5, pady=(0, 2))

        search_entry = tk.Entry(
            filter_grid,
            textvariable=self.search_var,
            font=FONT_ENTRY,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT_PRIMARY,
            insertbackground="white",
            bd=1,
            relief=tk.SOLID,
            width=18
        )
        search_entry.grid(row=1, column=0, padx=5, ipady=3)

        # Month Filter
        month_lbl = tk.Label(filter_grid, text="Month", font=FONT_LABEL, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY)
        month_lbl.grid(row=0, column=1, sticky="w", padx=5, pady=(0, 2))

        month_cb = ttk.Combobox(
            filter_grid, textvariable=self.month_var, values=self.MONTH_NAMES, state="readonly", width=14
        )
        month_cb.grid(row=1, column=1, padx=5, ipady=2)
        month_cb.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())

        # Year Filter
        year_lbl = tk.Label(filter_grid, text="Year", font=FONT_LABEL, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY)
        year_lbl.grid(row=0, column=2, sticky="w", padx=5, pady=(0, 2))

        year_cb = ttk.Combobox(
            filter_grid, textvariable=self.year_var, values=self.YEAR_OPTIONS, state="readonly", width=12
        )
        year_cb.grid(row=1, column=2, padx=5, ipady=2)
        year_cb.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())

        # Category Filter
        cat_lbl = tk.Label(filter_grid, text="Category", font=FONT_LABEL, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY)
        cat_lbl.grid(row=0, column=3, sticky="w", padx=5, pady=(0, 2))

        cat_cb = ttk.Combobox(
            filter_grid, textvariable=self.category_var, values=self.CATEGORY_OPTIONS, state="readonly", width=16
        )
        cat_cb.grid(row=1, column=3, padx=5, ipady=2)
        cat_cb.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())

        # Type Filter
        type_lbl = tk.Label(filter_grid, text="Type", font=FONT_LABEL, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY)
        type_lbl.grid(row=0, column=4, sticky="w", padx=5, pady=(0, 2))

        type_cb = ttk.Combobox(
            filter_grid, textvariable=self.type_var, values=self.TYPE_OPTIONS, state="readonly", width=12
        )
        type_cb.grid(row=1, column=4, padx=5, ipady=2)
        type_cb.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())

        # Reset Button
        reset_btn = tk.Button(
            filter_grid,
            text="🧹 Reset",
            font=FONT_BUTTON,
            bg=COLOR_NEUTRAL_SLATE,
            fg="#FFFFFF",
            activebackground=COLOR_NEUTRAL_HOVER,
            activeforeground="#FFFFFF",
            bd=0,
            cursor="hand2",
            padx=10,
            command=self._reset_filters
        )
        reset_btn.grid(row=1, column=5, padx=(10, 0), ipady=3)

        # ----------------------------------------------------
        # 3. Monthly & Category Summaries Section (Split Frame)
        # ----------------------------------------------------
        summary_section = tk.Frame(self, bg=COLOR_BG_DARK)
        summary_section.pack(fill=tk.X, pady=(0, 15))

        # 3A. Monthly Summary Card (Left)
        monthly_card = tk.Frame(summary_section, bg=COLOR_CARD_BG, padx=15, pady=12)
        monthly_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        tk.Label(
            monthly_card, text="📊 Period Summary", font=FONT_HEADER, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY
        ).pack(anchor=tk.W, pady=(0, 10))

        m_metrics_frame = tk.Frame(monthly_card, bg=COLOR_CARD_BG)
        m_metrics_frame.pack(fill=tk.X)

        self.m_income_val = self._create_sub_metric(m_metrics_frame, "Period Income", "$0.00", COLOR_INCOME_GREEN, 0)
        self.m_expense_val = self._create_sub_metric(m_metrics_frame, "Period Expense", "$0.00", COLOR_EXPENSE_RED, 1)
        self.m_net_val = self._create_sub_metric(m_metrics_frame, "Net Savings", "$0.00", COLOR_BALANCE_BLUE, 2)

        # 3B. Category Summary Breakdown (Right)
        cat_card = tk.Frame(summary_section, bg=COLOR_CARD_BG, padx=15, pady=12)
        cat_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        tk.Label(
            cat_card, text="🏷️ Top Category Breakdown", font=FONT_HEADER, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY
        ).pack(anchor=tk.W, pady=(0, 6))

        self.cat_breakdown_frame = tk.Frame(cat_card, bg=COLOR_CARD_BG)
        self.cat_breakdown_frame.pack(fill=tk.BOTH, expand=True)

        # ----------------------------------------------------
        # 4. Report Data Table (ttk.Treeview)
        # ----------------------------------------------------
        table_frame = tk.Frame(self, bg=COLOR_CARD_BG)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "date", "type", "category", "amount", "description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("type", text="Type")
        self.tree.heading("category", text="Category")
        self.tree.heading("amount", text="Amount ($)")
        self.tree.heading("description", text="Description")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("date", width=110, anchor="center")
        self.tree.column("type", width=100, anchor="center")
        self.tree.column("category", width=140, anchor="w")
        self.tree.column("amount", width=120, anchor="e")
        self.tree.column("description", width=280, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Zebra striping
        self.tree.tag_configure("even", background="#1E1F2E")
        self.tree.tag_configure("odd", background="#232538")
        self.tree.tag_configure("income", foreground=COLOR_INCOME_GREEN)
        self.tree.tag_configure("expense", foreground=COLOR_EXPENSE_RED)

        # Footer Status Bar
        self.status_lbl = tk.Label(
            self, text="Total Records: 0", font=FONT_LABEL, bg=COLOR_BG_DARK, fg=COLOR_TEXT_SECONDARY
        )
        self.status_lbl.pack(anchor=tk.W, pady=(8, 0))

    def _create_sub_metric(self, parent, title, initial_val, color, col):
        """Creates a metric display inside Period Summary card."""
        sub_frame = tk.Frame(parent, bg=COLOR_CARD_BG)
        sub_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)

        tk.Label(sub_frame, text=title, font=FONT_CARD_TITLE, bg=COLOR_CARD_BG, fg=COLOR_TEXT_SECONDARY).pack(anchor=tk.W)
        val_lbl = tk.Label(sub_frame, text=initial_val, font=("Segoe UI", 14, "bold"), bg=COLOR_CARD_BG, fg=color)
        val_lbl.pack(anchor=tk.W, pady=(2, 0))

        return val_lbl

    def refresh_report(self):
        """Fetches latest dataset and updates view."""
        self._apply_filters()

    def _apply_filters(self):
        """Filters transaction list based on search, month, year, category, and type."""
        all_trans = self.get_transactions_func()

        search_q = self.search_var.get().strip().lower()
        sel_month = self.month_var.get()
        sel_year = self.year_var.get()
        sel_cat = self.category_var.get()
        sel_type = self.type_var.get()

        filtered = []

        for item in all_trans:
            date_str = str(item.get("date", ""))
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                month_name = date_obj.strftime("%B")
                year_str = str(date_obj.year)
            except ValueError:
                month_name = ""
                year_str = ""

            # Check 1: Search Query
            if search_q:
                desc = str(item.get("description", "")).lower()
                cat = str(item.get("category", "")).lower()
                if search_q not in desc and search_q not in cat and search_q not in str(item.get("type", "")).lower():
                    continue

            # Check 2: Month Filter
            if sel_month != "All Months" and month_name != sel_month:
                continue

            # Check 3: Year Filter
            if sel_year != "All Years" and year_str != sel_year:
                continue

            # Check 4: Category Filter
            if sel_cat != "All Categories" and item.get("category") != sel_cat:
                continue

            # Check 5: Type Filter
            if sel_type != "All Types" and item.get("type") != sel_type:
                continue

            filtered.append(item)

        self.filtered_transactions = filtered
        self._render_table_rows(filtered)
        self._update_summaries(filtered)

    def _render_table_rows(self, data_list):
        """Populates report Treeview table."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        for idx, item in enumerate(data_list):
            row_tag = "even" if idx % 2 == 0 else "odd"
            type_tag = "income" if item.get("type") == "Income" else "expense"
            formatted_amt = format_currency(item['amount'])

            self.tree.insert(
                "",
                tk.END,
                values=(
                    item.get("id", ""),
                    item.get("date", ""),
                    item.get("type", ""),
                    item.get("category", ""),
                    formatted_amt,
                    item.get("description", "")
                ),
                tags=(row_tag, type_tag)
            )

        self.status_lbl.config(
            text=f"Showing {len(data_list)} matching record(s) in report."
        )

    def _update_summaries(self, data_list):
        """Recalculates Period Summary & Category Breakdown."""
        period_income = sum(float(t["amount"]) for t in data_list if t.get("type") == "Income")
        period_expense = sum(float(t["amount"]) for t in data_list if t.get("type") == "Expense")
        net_cash = period_income - period_expense

        self.m_income_val.config(text=format_currency(period_income))
        self.m_expense_val.config(text=format_currency(period_expense))
        self.m_net_val.config(
            text=format_currency(net_cash),
            fg=COLOR_INCOME_GREEN if net_cash >= 0 else COLOR_EXPENSE_RED
        )

        # Clear existing category breakdown widgets
        for widget in self.cat_breakdown_frame.winfo_children():
            widget.destroy()

        # Compute Category Breakdown Totals
        cat_totals = {}
        for t in data_list:
            cat = t.get("category", "Other")
            amt = float(t.get("amount", 0))
            cat_totals[cat] = cat_totals.get(cat, 0.0) + amt

        sorted_cats = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)[:3]

        if not sorted_cats:
            tk.Label(
                self.cat_breakdown_frame,
                text="No data for selected filters.",
                font=FONT_LABEL,
                bg=COLOR_CARD_BG,
                fg=COLOR_TEXT_SECONDARY
            ).pack(anchor=tk.W, pady=5)
        else:
            cat_row = tk.Frame(self.cat_breakdown_frame, bg=COLOR_CARD_BG)
            cat_row.pack(fill=tk.X, pady=2)

            for cat_name, total_amt in sorted_cats:
                pill = tk.Frame(cat_row, bg=COLOR_INPUT_BG, padx=8, pady=4)
                pill.pack(side=tk.LEFT, padx=(0, 8))

                tk.Label(
                    pill, text=f"{cat_name}: ", font=FONT_SMALL, bg=COLOR_INPUT_BG, fg=COLOR_TEXT_SECONDARY
                ).pack(side=tk.LEFT)
                tk.Label(
                    pill, text=format_currency(total_amt), font=("Segoe UI", 9, "bold"), bg=COLOR_INPUT_BG, fg=COLOR_TEXT_PRIMARY
                ).pack(side=tk.LEFT)

    def _reset_filters(self):
        """Resets all filter variables to default."""
        self.search_var.set("")
        self.month_var.set(self.MONTH_NAMES[0])
        self.year_var.set(self.YEAR_OPTIONS[0])
        self.category_var.set(self.CATEGORY_OPTIONS[0])
        self.type_var.set(self.TYPE_OPTIONS[0])
        self._apply_filters()

    def _export_to_csv(self):
        """Exports currently filtered transaction dataset to CSV file."""
        if not self.filtered_transactions:
            messagebox.showwarning("Export Warning", "No transaction records found to export.", parent=self)
            return

        filename = filedialog.asksaveasfilename(
            parent=self,
            title="Save Financial Report CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialfile=f"finance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        if not filename:
            return

        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Write CSV Header
                writer.writerow(["ID", "Date", "Type", "Category", "Amount ($)", "Description"])

                # Write Transaction Rows
                for t in self.filtered_transactions:
                    writer.writerow([
                        t.get("id", ""),
                        t.get("date", ""),
                        t.get("type", ""),
                        t.get("category", ""),
                        f"{float(t.get('amount', 0)):.2f}",
                        t.get("description", "")
                    ])

            messagebox.showinfo("Export Success", f"Report exported successfully to:\n{filename}", parent=self)
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred while exporting: {e}", parent=self)

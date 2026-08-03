"""
ui_transaction_dialog.py
------------------------
Modal Dialog for Adding and Editing Income / Expense Transactions.
"""

from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from theme import (
    COLOR_BG_DARK, COLOR_CARD_BG, COLOR_INPUT_BG, COLOR_INPUT_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_PRIMARY_EMERALD,
    COLOR_PRIMARY_HOVER, COLOR_ACCENT_INDIGO, COLOR_ACCENT_HOVER,
    COLOR_DANGER_RED, COLOR_DANGER_HOVER, FONT_TITLE, FONT_LABEL, FONT_ENTRY,
    FONT_BUTTON, FONT_HEADER
)


class TransactionDialog:
    """
    Modal Dialog component for Add / Edit Transaction.
    """

    CATEGORIES = [
        "Salary", "Freelance", "Investments", "Food & Dining",
        "Rent & Housing", "Utilities", "Entertainment", "Shopping",
        "Transportation", "Healthcare", "Education", "Other"
    ]

    def __init__(self, parent, title="Add Transaction", initial_data=None, on_save_callback=None):
        """
        Initializes the transaction modal dialog.
        
        :param parent: Parent Tkinter root or window.
        :param title: Dialog title string.
        :param initial_data: Dict with transaction fields for edit mode, or None for new.
        :param on_save_callback: Function called with saved transaction dict.
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("440x550")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=COLOR_BG_DARK)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.initial_data = initial_data or {}
        self.on_save_callback = on_save_callback

        # Form variables
        self.type_var = tk.StringVar(value=self.initial_data.get("type", "Income"))
        self.amount_var = tk.StringVar(value=str(self.initial_data.get("amount", "")))
        self.category_var = tk.StringVar(
            value=self.initial_data.get("category", self.CATEGORIES[0])
        )
        default_date = datetime.now().strftime("%Y-%m-%d")
        self.date_var = tk.StringVar(value=self.initial_data.get("date", default_date))
        self.description_var = tk.StringVar(value=self.initial_data.get("description", ""))

        self._create_widgets(title)

    def _create_widgets(self, title_text):
        """Builds dialog form fields and controls."""
        card_frame = tk.Frame(self.dialog, bg=COLOR_CARD_BG, bd=0)
        card_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=390, height=500)

        # Header Title
        title_label = tk.Label(
            card_frame,
            text=title_text,
            font=FONT_HEADER,
            bg=COLOR_CARD_BG,
            fg=COLOR_TEXT_PRIMARY
        )
        title_label.pack(pady=(20, 15))

        form_frame = tk.Frame(card_frame, bg=COLOR_CARD_BG)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=25)

        # 1. Transaction Type (Income vs Expense)
        type_label = tk.Label(
            form_frame, text="Transaction Type", font=FONT_LABEL, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY
        )
        type_label.pack(anchor=tk.W, pady=(0, 4))

        type_btn_frame = tk.Frame(form_frame, bg=COLOR_CARD_BG)
        type_btn_frame.pack(fill=tk.X, pady=(0, 12))

        inc_rb = tk.Radiobutton(
            type_btn_frame,
            text="🟢 Income",
            variable=self.type_var,
            value="Income",
            bg=COLOR_CARD_BG,
            fg=COLOR_TEXT_PRIMARY,
            selectcolor=COLOR_INPUT_BG,
            activebackground=COLOR_CARD_BG,
            activeforeground=COLOR_TEXT_PRIMARY,
            font=FONT_LABEL
        )
        inc_rb.pack(side=tk.LEFT, padx=(0, 20))

        exp_rb = tk.Radiobutton(
            type_btn_frame,
            text="🔴 Expense",
            variable=self.type_var,
            value="Expense",
            bg=COLOR_CARD_BG,
            fg=COLOR_TEXT_PRIMARY,
            selectcolor=COLOR_INPUT_BG,
            activebackground=COLOR_CARD_BG,
            activeforeground=COLOR_TEXT_PRIMARY,
            font=FONT_LABEL
        )
        exp_rb.pack(side=tk.LEFT)

        # 2. Amount Field
        amount_label = tk.Label(
            form_frame, text="Amount ($)", font=FONT_LABEL, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY
        )
        amount_label.pack(anchor=tk.W, pady=(0, 2))

        self.amount_entry = tk.Entry(
            form_frame,
            textvariable=self.amount_var,
            font=FONT_ENTRY,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT_PRIMARY,
            insertbackground="white",
            bd=1,
            relief=tk.SOLID,
            highlightbackground=COLOR_INPUT_BORDER,
            highlightcolor=COLOR_ACCENT_INDIGO,
            highlightthickness=1
        )
        self.amount_entry.pack(fill=tk.X, ipady=5, pady=(0, 10))
        self.amount_entry.focus_set()

        # 3. Category Field
        category_label = tk.Label(
            form_frame, text="Category", font=FONT_LABEL, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY
        )
        category_label.pack(anchor=tk.W, pady=(0, 2))

        category_combo = ttk.Combobox(
            form_frame,
            textvariable=self.category_var,
            values=self.CATEGORIES,
            state="readonly",
            font=FONT_ENTRY
        )
        category_combo.pack(fill=tk.X, ipady=4, pady=(0, 10))

        # 4. Date Field
        date_label = tk.Label(
            form_frame, text="Date (YYYY-MM-DD)", font=FONT_LABEL, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY
        )
        date_label.pack(anchor=tk.W, pady=(0, 2))

        self.date_entry = tk.Entry(
            form_frame,
            textvariable=self.date_var,
            font=FONT_ENTRY,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT_PRIMARY,
            insertbackground="white",
            bd=1,
            relief=tk.SOLID,
            highlightbackground=COLOR_INPUT_BORDER,
            highlightcolor=COLOR_ACCENT_INDIGO,
            highlightthickness=1
        )
        self.date_entry.pack(fill=tk.X, ipady=5, pady=(0, 10))

        # 5. Description Field
        desc_label = tk.Label(
            form_frame, text="Description (Optional)", font=FONT_LABEL, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY
        )
        desc_label.pack(anchor=tk.W, pady=(0, 2))

        self.desc_entry = tk.Entry(
            form_frame,
            textvariable=self.description_var,
            font=FONT_ENTRY,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT_PRIMARY,
            insertbackground="white",
            bd=1,
            relief=tk.SOLID,
            highlightbackground=COLOR_INPUT_BORDER,
            highlightcolor=COLOR_ACCENT_INDIGO,
            highlightthickness=1
        )
        self.desc_entry.pack(fill=tk.X, ipady=5, pady=(0, 15))

        # Buttons Bar
        btn_bar = tk.Frame(form_frame, bg=COLOR_CARD_BG)
        btn_bar.pack(fill=tk.X, pady=(5, 0))

        save_btn = tk.Button(
            btn_bar,
            text="Save",
            font=FONT_BUTTON,
            bg=COLOR_PRIMARY_EMERALD,
            fg="#FFFFFF",
            activebackground=COLOR_PRIMARY_HOVER,
            activeforeground="#FFFFFF",
            bd=0,
            cursor="hand2",
            command=self._handle_save
        )
        save_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=6, padx=(0, 5))

        cancel_btn = tk.Button(
            btn_bar,
            text="Cancel",
            font=FONT_BUTTON,
            bg=COLOR_DANGER_RED,
            fg="#FFFFFF",
            activebackground=COLOR_DANGER_HOVER,
            activeforeground="#FFFFFF",
            bd=0,
            cursor="hand2",
            command=self.dialog.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, ipady=6, padx=(5, 0))

    def _handle_save(self):
        """Validates form data and passes back result."""
        amount_str = self.amount_var.get().strip()
        date_str = self.date_var.get().strip()
        category = self.category_var.get().strip()
        description = self.description_var.get().strip()
        trans_type = self.type_var.get()

        # Validate Amount
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Validation Error",
                "Please enter a valid positive numerical amount (e.g. 150.00).",
                parent=self.dialog
            )
            return

        # Validate Date format YYYY-MM-DD
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning(
                "Validation Error",
                "Please enter a valid date in YYYY-MM-DD format (e.g. 2026-08-02).",
                parent=self.dialog
            )
            return

        data = {
            "id": self.initial_data.get("id"),
            "type": trans_type,
            "amount": amount,
            "category": category,
            "date": date_str,
            "description": description
        }

        if self.on_save_callback:
            self.on_save_callback(data)

        self.dialog.destroy()

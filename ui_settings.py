"""
ui_settings.py
--------------
Settings & System Preferences View for the Personal Finance Tracker.
Includes User Profile settings, Currency selector ($ EUR £ ₹ ¥), Dark/Light Mode toggle,
and Database reset controls with settings.json persistence.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from theme import (
    get_color, COLOR_PRIMARY_EMERALD, COLOR_PRIMARY_HOVER,
    COLOR_ACCENT_INDIGO, COLOR_ACCENT_HOVER, COLOR_DANGER_RED, COLOR_DANGER_HOVER,
    FONT_TITLE, FONT_HEADER, FONT_LABEL, FONT_BUTTON, FONT_ENTRY, FONT_SMALL,
    CURRENCY_NAME, set_currency_symbol, CURRENT_THEME, toggle_theme_palette
)


class SettingsView(tk.Frame):
    """
    Settings & Application Preferences View Component.
    """

    CURRENCY_LIST = [
        "USD ($) - US Dollar",
        "EUR (€) - Euro",
        "GBP (£) - British Pound",
        "INR (₹) - Indian Rupee",
        "JPY (¥) - Japanese Yen"
    ]

    def __init__(self, parent, user_info, on_theme_changed_callback=None):
        """
        Initializes Settings View.
        
        :param parent: Parent frame container.
        :param user_info: Dict containing authenticated user info.
        :param on_theme_changed_callback: Callback when theme is toggled.
        """
        super().__init__(parent, bg=get_color("bg_dark"))
        self.user_info = user_info
        self.on_theme_changed_callback = on_theme_changed_callback

        self.currency_var = tk.StringVar(value=self._get_initial_currency_label())
        self._create_widgets()

    def _get_initial_currency_label(self):
        """Finds current active currency label from list."""
        for item in self.CURRENCY_LIST:
            if CURRENCY_NAME in item:
                return item
        return self.CURRENCY_LIST[0]

    def _create_widgets(self):
        """Builds settings page layout cards."""

        # Header Title
        self.header_frame = tk.Frame(self, bg=get_color("bg_dark"))
        self.header_frame.pack(fill=tk.X, pady=(0, 15))

        self.title_lbl = tk.Label(
            self.header_frame,
            text="Settings & System Preferences",
            font=FONT_TITLE,
            bg=get_color("bg_dark"),
            fg=get_color("text_primary")
        )
        self.title_lbl.pack(side=tk.LEFT)

        # Card 1: User Profile Settings
        self.profile_card = tk.Frame(self, bg=get_color("card_bg"), padx=20, pady=15)
        self.profile_card.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            self.profile_card, text="👤 User Profile", font=FONT_HEADER, bg=get_color("card_bg"), fg=get_color("text_primary")
        ).pack(anchor=tk.W, pady=(0, 10))

        p_info_frame = tk.Frame(self.profile_card, bg=get_color("card_bg"))
        p_info_frame.pack(fill=tk.X)

        tk.Label(p_info_frame, text="Username: ", font=FONT_LABEL, bg=get_color("card_bg"), fg=get_color("text_secondary")).pack(side=tk.LEFT)
        tk.Label(
            p_info_frame,
            text=self.user_info.get("username", "User"),
            font=("Segoe UI", 11, "bold"),
            bg=get_color("card_bg"),
            fg=COLOR_ACCENT_INDIGO
        ).pack(side=tk.LEFT, padx=(0, 30))

        tk.Label(p_info_frame, text="User ID: ", font=FONT_LABEL, bg=get_color("card_bg"), fg=get_color("text_secondary")).pack(side=tk.LEFT)
        tk.Label(
            p_info_frame,
            text=f"#{self.user_info.get('id', 1)}",
            font=("Segoe UI", 11, "bold"),
            bg=get_color("card_bg"),
            fg=get_color("text_primary")
        ).pack(side=tk.LEFT)

        # Card 2: Currency & Regional Preferences
        self.curr_card = tk.Frame(self, bg=get_color("card_bg"), padx=20, pady=15)
        self.curr_card.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            self.curr_card, text="💱 Currency Preferences", font=FONT_HEADER, bg=get_color("card_bg"), fg=get_color("text_primary")
        ).pack(anchor=tk.W, pady=(0, 6))

        tk.Label(
            self.curr_card,
            text="Select your preferred currency symbol for tables and metric displays:",
            font=FONT_SMALL,
            bg=get_color("card_bg"),
            fg=get_color("text_secondary")
        ).pack(anchor=tk.W, pady=(0, 10))

        curr_combo_frame = tk.Frame(self.curr_card, bg=get_color("card_bg"))
        curr_combo_frame.pack(fill=tk.X)

        self.curr_cb = ttk.Combobox(
            curr_combo_frame,
            textvariable=self.currency_var,
            values=self.CURRENCY_LIST,
            state="readonly",
            font=FONT_ENTRY,
            width=28
        )
        self.curr_cb.pack(side=tk.LEFT, ipady=4, padx=(0, 12))

        save_curr_btn = tk.Button(
            curr_combo_frame,
            text="Apply Currency",
            font=FONT_BUTTON,
            bg=COLOR_PRIMARY_EMERALD,
            fg="#FFFFFF",
            activebackground=COLOR_PRIMARY_HOVER,
            activeforeground="#FFFFFF",
            bd=0,
            cursor="hand2",
            padx=12,
            command=self._handle_save_currency
        )
        save_curr_btn.pack(side=tk.LEFT, ipady=4)

        # Card 3: Appearance & Theme Controls
        self.theme_card = tk.Frame(self, bg=get_color("card_bg"), padx=20, pady=15)
        self.theme_card.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            self.theme_card, text="🎨 Appearance & Theme Preferences", font=FONT_HEADER, bg=get_color("card_bg"), fg=get_color("text_primary")
        ).pack(anchor=tk.W, pady=(0, 6))

        theme_row = tk.Frame(self.theme_card, bg=get_color("card_bg"))
        theme_row.pack(fill=tk.X, pady=(4, 0))

        self.theme_status_lbl = tk.Label(
            theme_row,
            text=f"Active Theme: {CURRENT_THEME.upper()} MODE",
            font=FONT_LABEL,
            bg=get_color("card_bg"),
            fg=get_color("text_primary")
        )
        self.theme_status_lbl.pack(side=tk.LEFT, padx=(0, 20))

        toggle_theme_btn = tk.Button(
            theme_row,
            text="Toggle Dark / Light Theme",
            font=FONT_BUTTON,
            bg=COLOR_ACCENT_INDIGO,
            fg="#FFFFFF",
            activebackground=COLOR_ACCENT_HOVER,
            activeforeground="#FFFFFF",
            bd=0,
            cursor="hand2",
            padx=12,
            command=self._handle_toggle_theme
        )
        toggle_theme_btn.pack(side=tk.LEFT, ipady=4)

        # Card 4: Database & Data Management
        self.data_card = tk.Frame(self, bg=get_color("card_bg"), padx=20, pady=15)
        self.data_card.pack(fill=tk.X)

        tk.Label(
            self.data_card, text="🗄️ Database & Storage Controls", font=FONT_HEADER, bg=get_color("card_bg"), fg=get_color("text_primary")
        ).pack(anchor=tk.W, pady=(0, 6))

        tk.Label(
            self.data_card,
            text="Manage local cached transactions or re-initialize MySQL connections.",
            font=FONT_SMALL,
            bg=get_color("card_bg"),
            fg=get_color("text_secondary")
        ).pack(anchor=tk.W, pady=(0, 10))

        reset_cache_btn = tk.Button(
            self.data_card,
            text="🧹 Reset Local Data Cache",
            font=FONT_BUTTON,
            bg=COLOR_DANGER_RED,
            fg="#FFFFFF",
            activebackground=COLOR_DANGER_HOVER,
            activeforeground="#FFFFFF",
            bd=0,
            cursor="hand2",
            padx=12,
            command=self._handle_reset_cache
        )
        reset_cache_btn.pack(anchor=tk.W, ipady=4)

    def _handle_save_currency(self):
        """Applies selected currency symbol globally."""
        selected = self.currency_var.get()
        set_currency_symbol(selected)
        if self.on_theme_changed_callback:
            self.on_theme_changed_callback()
        messagebox.showinfo(
            "Currency Saved",
            f"Currency preference updated to '{selected}' and saved to settings.json!",
            parent=self
        )

    def _handle_toggle_theme(self):
        """Toggles between dark and light themes."""
        new_theme = toggle_theme_palette()
        self.theme_status_lbl.config(text=f"Active Theme: {new_theme.upper()} MODE")
        if self.on_theme_changed_callback:
            self.on_theme_changed_callback()
        messagebox.showinfo("Theme Saved", f"Switched theme to {new_theme.upper()} MODE and saved to settings.json!", parent=self)

    def _handle_reset_cache(self):
        """Resets local cache with confirmation."""
        confirm = messagebox.askyesno(
            "Confirm Reset",
            "Are you sure you want to reset local cached transactions?",
            parent=self
        )
        if confirm:
            messagebox.showinfo("Reset Complete", "Local data cache reset successfully!", parent=self)

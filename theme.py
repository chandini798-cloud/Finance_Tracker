"""
theme.py
--------
Centralized design system for the Personal Finance Tracker Tkinter frontend.
Defines color palettes for Dark & Light Mode themes, persistent settings manager (settings.json),
currency formatting, typography standards, and TTK theme configurations.
"""

import json
import os
import tkinter as tk
from tkinter import ttk

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

# Default Preferences
DEFAULT_SETTINGS = {
    "theme": "dark",
    "currency_symbol": "$",
    "currency_name": "USD ($)"
}


def load_settings():
    """Loads settings from settings.json or creates default if missing."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """Saves settings to settings.json."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"[WARN] Failed to save settings.json: {e}")


# Load initial saved preferences
saved_config = load_settings()
CURRENT_THEME = saved_config.get("theme", "dark")
CURRENCY_SYMBOL = saved_config.get("currency_symbol", "$")
CURRENCY_NAME = saved_config.get("currency_name", "USD ($)")

# ==========================================
# Dark Theme Color Palette
# ==========================================
DARK_PALETTE = {
    "bg_dark": "#12131C",
    "sidebar_bg": "#181926",
    "card_bg": "#1E1F2E",
    "card_hover": "#27293D",
    "input_bg": "#27293D",
    "input_border": "#3A3D5A",
    "text_primary": "#FFFFFF",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B"
}

# ==========================================
# Light Theme Color Palette
# ==========================================
LIGHT_PALETTE = {
    "bg_dark": "#F1F5F9",
    "sidebar_bg": "#FFFFFF",
    "card_bg": "#FFFFFF",
    "card_hover": "#F8FAFC",
    "input_bg": "#F8FAFC",
    "input_border": "#CBD5E1",
    "text_primary": "#0F172A",
    "text_secondary": "#475569",
    "text_muted": "#94A3B8"
}


def get_current_palette():
    """Returns active palette dictionary based on CURRENT_THEME."""
    return LIGHT_PALETTE if CURRENT_THEME == "light" else DARK_PALETTE


# Active Color Aliases (functions for dynamic lookups)
def get_color(key):
    return get_current_palette().get(key, "#12131C")


COLOR_BG_DARK = get_color("bg_dark")
COLOR_SIDEBAR_BG = get_color("sidebar_bg")
COLOR_CARD_BG = get_color("card_bg")
COLOR_CARD_HOVER = get_color("card_hover")
COLOR_INPUT_BG = get_color("input_bg")
COLOR_INPUT_BORDER = get_color("input_border")
COLOR_INPUT_FOCUS = "#6366F1"

COLOR_TEXT_PRIMARY = get_color("text_primary")
COLOR_TEXT_SECONDARY = get_color("text_secondary")
COLOR_TEXT_MUTED = get_color("text_muted")

# Metric & Accent Colors
COLOR_INCOME_GREEN = "#10B981"  # Emerald Green for Total Income
COLOR_EXPENSE_RED = "#EF4444"   # Rose Red for Total Expense
COLOR_BALANCE_BLUE = "#3B82F6"  # Blue for Current Balance
COLOR_SAVINGS_PURPLE = "#8B5CF6"# Purple for Monthly Savings

# Button & Interactive State Colors
COLOR_PRIMARY_EMERALD = "#10B981"
COLOR_PRIMARY_HOVER = "#059669"
COLOR_ACCENT_INDIGO = "#6366F1"
COLOR_ACCENT_HOVER = "#4F46E5"
COLOR_DANGER_RED = "#EF4444"
COLOR_DANGER_HOVER = "#DC2626"
COLOR_NEUTRAL_SLATE = "#334155"
COLOR_NEUTRAL_HOVER = "#475569"

# ==========================================
# Typography Standards
# ==========================================
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_HEADER = ("Segoe UI", 14, "bold")
FONT_SUBTITLE = ("Segoe UI", 10)
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_ENTRY = ("Segoe UI", 11)
FONT_BUTTON = ("Segoe UI", 10, "bold")
FONT_LINK = ("Segoe UI", 9, "underline")
FONT_SMALL = ("Segoe UI", 9)
FONT_CARD_TITLE = ("Segoe UI", 9, "bold")
FONT_CARD_VALUE = ("Segoe UI", 18, "bold")


def set_currency_symbol(currency_str):
    """Sets active currency symbol and saves preference."""
    global CURRENCY_SYMBOL, CURRENCY_NAME
    CURRENCY_NAME = currency_str
    if "EUR" in currency_str or "€" in currency_str:
        CURRENCY_SYMBOL = "€"
    elif "GBP" in currency_str or "£" in currency_str:
        CURRENCY_SYMBOL = "£"
    elif "INR" in currency_str or "₹" in currency_str:
        CURRENCY_SYMBOL = "₹"
    elif "JPY" in currency_str or "¥" in currency_str:
        CURRENCY_SYMBOL = "¥"
    else:
        CURRENCY_SYMBOL = "$"

    conf = load_settings()
    conf["currency_symbol"] = CURRENCY_SYMBOL
    conf["currency_name"] = CURRENCY_NAME
    save_settings(conf)


def format_currency(amount):
    """Formats numeric amount with active currency symbol."""
    try:
        val = float(amount)
        return f"{CURRENCY_SYMBOL}{val:,.2f}"
    except (ValueError, TypeError):
        return f"{CURRENCY_SYMBOL}0.00"


def toggle_theme_palette():
    """Toggles global theme state between dark and light mode and saves preference."""
    global CURRENT_THEME, COLOR_BG_DARK, COLOR_SIDEBAR_BG, COLOR_CARD_BG, COLOR_CARD_HOVER, COLOR_INPUT_BG, COLOR_INPUT_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED

    if CURRENT_THEME == "dark":
        CURRENT_THEME = "light"
    else:
        CURRENT_THEME = "dark"

    palette = get_current_palette()
    COLOR_BG_DARK = palette["bg_dark"]
    COLOR_SIDEBAR_BG = palette["sidebar_bg"]
    COLOR_CARD_BG = palette["card_bg"]
    COLOR_CARD_HOVER = palette["card_hover"]
    COLOR_INPUT_BG = palette["input_bg"]
    COLOR_INPUT_BORDER = palette["input_border"]
    COLOR_TEXT_PRIMARY = palette["text_primary"]
    COLOR_TEXT_SECONDARY = palette["text_secondary"]
    COLOR_TEXT_MUTED = palette["text_muted"]

    # Save to settings.json
    conf = load_settings()
    conf["theme"] = CURRENT_THEME
    save_settings(conf)

    return CURRENT_THEME


def configure_ttk_dark_theme(root):
    """Configures theme styles for TTK widgets based on active theme."""
    style = ttk.Style(root)
    style.theme_use("clam")

    palette = get_current_palette()
    bg = palette["card_bg"]
    fg = palette["text_primary"]
    side_bg = palette["sidebar_bg"]
    input_bg = palette["input_bg"]
    border_col = palette["input_border"]

    style.configure(
        "Treeview",
        background=bg,
        foreground=fg,
        fieldbackground=bg,
        rowheight=32,
        font=("Segoe UI", 10),
        borderwidth=0
    )
    style.configure(
        "Treeview.Heading",
        background=side_bg,
        foreground=fg,
        font=("Segoe UI", 10, "bold"),
        borderwidth=1,
        relief="flat"
    )
    style.map(
        "Treeview",
        background=[("selected", "#3730A3")],
        foreground=[("selected", "#FFFFFF")]
    )
    style.configure(
        "TCombobox",
        fieldbackground=input_bg,
        background=input_bg,
        foreground=fg,
        arrowcolor=fg,
        bordercolor=border_col,
        padding=5
    )


def draw_app_logo(canvas, width=60, height=60):
    """Draws a modern vector finance icon badge on a Canvas."""
    canvas.delete("all")
    cx, cy = width / 2, height / 2

    canvas.create_oval(
        4, 4, width - 4, height - 4,
        fill="#2A2C44", outline="#3F4267", width=2
    )
    canvas.create_rectangle(
        cx - 15, cy - 10, cx + 15, cy + 12,
        fill="#6366F1", outline="", width=0
    )
    canvas.create_rectangle(
        cx + 5, cy - 3, cx + 15, cy + 5,
        fill="#10B981", outline=""
    )
    canvas.create_oval(
        cx + 8, cy - 1, cx + 12, cy + 3,
        fill="#FFFFFF", outline=""
    )

"""
ui_about.py
-----------
About & Application Details View for the Personal Finance Tracker.
Displays application architecture, feature list, version info, and credits.
"""

import tkinter as tk
from theme import (
    get_color, COLOR_ACCENT_INDIGO, FONT_TITLE, FONT_HEADER,
    FONT_LABEL, FONT_SUBTITLE, FONT_SMALL, draw_app_logo
)


class AboutView(tk.Frame):
    """
    About Page View Component.
    """

    def __init__(self, parent):
        """
        Initializes About View.
        
        :param parent: Parent frame container.
        """
        super().__init__(parent, bg=get_color("bg_dark"))
        self._create_widgets()

    def _create_widgets(self):
        """Builds about page layout."""

        # Centered Container Card
        self.card = tk.Frame(self, bg=get_color("card_bg"), padx=30, pady=25)
        self.card.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # Header Badge & Logo
        logo_canvas = tk.Canvas(self.card, width=60, height=60, bg=get_color("card_bg"), highlightthickness=0)
        logo_canvas.pack(pady=(0, 10))
        draw_app_logo(logo_canvas, width=60, height=60)

        tk.Label(
            self.card, text="Personal Finance Tracker", font=FONT_TITLE, bg=get_color("card_bg"), fg=get_color("text_primary")
        ).pack(pady=(0, 2))

        tk.Label(
            self.card, text="Version 1.0.0 (Release Edition)", font=FONT_SUBTITLE, bg=get_color("card_bg"), fg=COLOR_ACCENT_INDIGO
        ).pack(pady=(0, 20))

        # Technical Architecture Card
        tech_frame = tk.Frame(self.card, bg=get_color("card_hover"), padx=20, pady=15)
        tech_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            tech_frame, text="💻 Technical Architecture & Stack", font=FONT_HEADER, bg=get_color("card_hover"), fg=get_color("text_primary")
        ).pack(anchor=tk.W, pady=(0, 8))

        tech_specs = [
            ("Core Programming Language:", "Python 3.10+ (Standard Library)"),
            ("GUI Framework:", "Tkinter & TTK Vector Rendering Engine"),
            ("Database Management:", "MySQL (via mysql-connector-python)"),
            ("Security & Hashing:", "PBKDF2-HMAC-SHA256 with Per-User Salt (100,000 Iterations)"),
            ("Theme Persistence Engine:", "JSON Settings Manager (settings.json)")
        ]

        for label, val in tech_specs:
            row = tk.Frame(tech_frame, bg=get_color("card_hover"))
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"• {label} ", font=FONT_LABEL, bg=get_color("card_hover"), fg=get_color("text_secondary")).pack(side=tk.LEFT)
            tk.Label(row, text=val, font=("Segoe UI", 10, "bold"), bg=get_color("card_hover"), fg=get_color("text_primary")).pack(side=tk.LEFT)

        # Feature Highlights List
        features_frame = tk.Frame(self.card, bg=get_color("card_bg"))
        features_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            features_frame, text="✨ Key Features & Capabilities", font=FONT_HEADER, bg=get_color("card_bg"), fg=get_color("text_primary")
        ).pack(anchor=tk.W, pady=(0, 8))

        feature_items = [
            "🔐 Secure Authentication: Hashed passwords with unique salts & duplicate username prevention.",
            "📊 Dashboard Central Hub: Real-time Income, Expenses, Balance, Savings & Multi-Criteria Filters.",
            "📈 Interactive Analytics: Native Vector Canvas charts (Pie, Income vs Expense Bar, Line graph).",
            "📥 Data Exporter: One-click CSV export directly from filtered Dashboard rows.",
            "🎨 Persistent Light & Dark Theme System: Instant theme switching saved to settings.json."
        ]

        for item in feature_items:
            tk.Label(
                features_frame, text=f"  {item}", font=FONT_SUBTITLE, bg=get_color("card_bg"), fg=get_color("text_secondary"), anchor="w"
            ).pack(fill=tk.X, pady=2)

        # Footer Credits
        footer_lbl = tk.Label(
            self.card,
            text="Developed by Google DeepMind Agentic Systems • MIT License",
            font=FONT_SMALL,
            bg=get_color("card_bg"),
            fg=get_color("text_secondary")
        )
        footer_lbl.pack(side=tk.BOTTOM, pady=(15, 0))

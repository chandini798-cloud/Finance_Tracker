"""
ui_analytics.py
---------------
Professional Native Tkinter Analytics View for Personal Finance Tracker.
Renders Vector Canvas Visualizations (Expense Pie Chart, Income vs Expense Bar Chart,
Monthly Spending Line Chart) with 100% Dark/Light Mode compatibility and instant redraws.
"""

import math
from datetime import datetime
import tkinter as tk

from theme import (
    get_color, COLOR_INCOME_GREEN, COLOR_EXPENSE_RED,
    COLOR_BALANCE_BLUE, COLOR_PRIMARY_EMERALD, COLOR_PRIMARY_HOVER,
    COLOR_ACCENT_INDIGO, COLOR_ACCENT_HOVER, COLOR_NEUTRAL_SLATE,
    COLOR_NEUTRAL_HOVER, FONT_TITLE, FONT_HEADER, FONT_LABEL, FONT_BUTTON,
    CURRENT_THEME, toggle_theme_palette
)


class AnalyticsView(tk.Frame):
    """
    Analytics View Component rendering high-performance native Canvas charts.
    """

    SLICE_COLORS = [
        "#EF4444",  # Primary Expense Red
        "#6366F1",  # Indigo
        "#F97316",  # Bright Orange
        "#F59E0B",  # Amber / Gold
        "#8B5CF6",  # Purple
        "#EC4899",  # Pink / Rose
        "#3B82F6",  # Royal Blue
        "#14B8A6"   # Teal
    ]

    def __init__(self, parent, get_transactions_func, on_back_callback=None):
        """
        Initializes Analytics View.
        
        :param parent: Parent frame container.
        :param get_transactions_func: Function returning transaction dicts.
        :param on_back_callback: Function to navigate back to dashboard.
        """
        super().__init__(parent, bg=get_color("bg_dark"))
        self.get_transactions_func = get_transactions_func
        self.on_back_callback = on_back_callback

        # Active chart state ("pie", "bar", "line")
        self.active_chart = "pie"

        self._create_widgets()
        self.bind("<Configure>", lambda e: self.refresh_analytics())
        self.refresh_analytics()

    def _create_widgets(self):
        """Builds analytics screen layout."""

        # ----------------------------------------------------
        # 1. Top Header Toolbar (Title + Back Button + Dark Mode Toggle)
        # ----------------------------------------------------
        self.header_frame = tk.Frame(self, bg=get_color("bg_dark"))
        self.header_frame.pack(fill=tk.X, pady=(0, 12))

        title_group = tk.Frame(self.header_frame, bg=get_color("bg_dark"))
        title_group.pack(side=tk.LEFT)

        if self.on_back_callback:
            back_btn = tk.Button(
                title_group,
                text="⬅️ Back to Dashboard",
                font=FONT_BUTTON,
                bg=COLOR_NEUTRAL_SLATE,
                fg="#FFFFFF",
                activebackground=COLOR_NEUTRAL_HOVER,
                activeforeground="#FFFFFF",
                bd=0,
                cursor="hand2",
                padx=10,
                command=self.on_back_callback
            )
            back_btn.pack(side=tk.LEFT, padx=(0, 15), ipady=5)

        self.title_lbl = tk.Label(
            title_group,
            text="Financial Analytics & Visual Trends",
            font=FONT_TITLE,
            bg=get_color("bg_dark"),
            fg=get_color("text_primary")
        )
        self.title_lbl.pack(side=tk.LEFT)

        self.theme_btn = tk.Button(
            self.header_frame,
            text="🌙 Dark Mode" if CURRENT_THEME == "dark" else "☀️ Light Mode",
            font=FONT_BUTTON,
            bg=COLOR_ACCENT_INDIGO,
            fg="#FFFFFF",
            activebackground=COLOR_ACCENT_HOVER,
            activeforeground="#FFFFFF",
            bd=0,
            cursor="hand2",
            padx=12,
            command=self._handle_theme_toggle
        )
        self.theme_btn.pack(side=tk.RIGHT, ipady=6)

        # ----------------------------------------------------
        # 2. Interactive Chart Selector Buttons Bar
        # ----------------------------------------------------
        self.chart_selector_card = tk.Frame(self, bg=get_color("card_bg"), padx=15, pady=10)
        self.chart_selector_card.pack(fill=tk.X, pady=(0, 12))

        self.sel_lbl = tk.Label(
            self.chart_selector_card,
            text="Select Visualization:",
            font=FONT_LABEL,
            bg=get_color("card_bg"),
            fg=get_color("text_primary")
        )
        self.sel_lbl.pack(side=tk.LEFT, padx=(0, 15))

        self.btn_pie = tk.Button(
            self.chart_selector_card,
            text="🥧 Expense Pie Chart",
            font=FONT_BUTTON,
            bg=COLOR_ACCENT_INDIGO,
            fg="#FFFFFF",
            activebackground=COLOR_ACCENT_HOVER,
            activeforeground="#FFFFFF",
            bd=0,
            cursor="hand2",
            padx=12,
            command=lambda: self._select_chart("pie")
        )
        self.btn_pie.pack(side=tk.LEFT, padx=(0, 8), ipady=5)

        self.btn_bar = tk.Button(
            self.chart_selector_card,
            text="📊 Income vs Expense Bar",
            font=FONT_BUTTON,
            bg=COLOR_NEUTRAL_SLATE,
            fg="#FFFFFF",
            activebackground=COLOR_NEUTRAL_HOVER,
            activeforeground="#FFFFFF",
            bd=0,
            cursor="hand2",
            padx=12,
            command=lambda: self._select_chart("bar")
        )
        self.btn_bar.pack(side=tk.LEFT, padx=(0, 8), ipady=5)

        self.btn_line = tk.Button(
            self.chart_selector_card,
            text="📈 Monthly Spending Line",
            font=FONT_BUTTON,
            bg=COLOR_NEUTRAL_SLATE,
            fg="#FFFFFF",
            activebackground=COLOR_NEUTRAL_HOVER,
            activeforeground="#FFFFFF",
            bd=0,
            cursor="hand2",
            padx=12,
            command=lambda: self._select_chart("line")
        )
        self.btn_line.pack(side=tk.LEFT, ipady=5)

        # ----------------------------------------------------
        # 3. Canvas Viewport Container
        # ----------------------------------------------------
        self.chart_card = tk.Frame(self, bg=get_color("card_bg"), padx=20, pady=15)
        self.chart_card.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        self.chart_title_lbl = tk.Label(
            self.chart_card,
            text="Expense Category Breakdown (Pie Chart)",
            font=FONT_HEADER,
            bg=get_color("card_bg"),
            fg=get_color("text_primary")
        )
        self.chart_title_lbl.pack(anchor=tk.W, pady=(0, 8))

        # Native Vector Canvas Engine
        self.canvas = tk.Canvas(
            self.chart_card,
            bg=get_color("card_bg"),
            bd=0,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # ----------------------------------------------------
        # 4. Insights Footer Bar
        # ----------------------------------------------------
        self.insights_card = tk.Frame(self, bg=get_color("card_bg"), padx=15, pady=10)
        self.insights_card.pack(fill=tk.X)

        self.insight_lbl = tk.Label(
            self.insights_card,
            text="💡 Insights: Loading financial trends...",
            font=FONT_LABEL,
            bg=get_color("card_bg"),
            fg=get_color("text_secondary")
        )
        self.insight_lbl.pack(anchor=tk.W)

    def refresh_analytics(self):
        """Redraws active chart with latest transactions and palette colors."""
        card_bg = get_color("card_bg")
        bg_dark = get_color("bg_dark")
        text_primary = get_color("text_primary")
        text_secondary = get_color("text_secondary")

        self.configure(bg=bg_dark)
        self.header_frame.configure(bg=bg_dark)
        self.title_lbl.configure(bg=bg_dark, fg=text_primary)
        self.chart_selector_card.configure(bg=card_bg)
        self.sel_lbl.configure(bg=card_bg, fg=text_primary)
        self.chart_card.configure(bg=card_bg)
        self.chart_title_lbl.configure(bg=card_bg, fg=text_primary)
        self.canvas.configure(bg=card_bg)
        self.insights_card.configure(bg=card_bg)
        self.insight_lbl.configure(bg=card_bg, fg=text_secondary)

        transactions = self.get_transactions_func()
        self.canvas.delete("all")

        if self.active_chart == "pie":
            self._render_pie_chart(transactions)
        elif self.active_chart == "bar":
            self._render_bar_chart(transactions)
        elif self.active_chart == "line":
            self._render_line_chart(transactions)

    def _select_chart(self, chart_type):
        """Switches active visualization chart."""
        self.active_chart = chart_type

        self.btn_pie.config(bg=COLOR_ACCENT_INDIGO if chart_type == "pie" else COLOR_NEUTRAL_SLATE)
        self.btn_bar.config(bg=COLOR_ACCENT_INDIGO if chart_type == "bar" else COLOR_NEUTRAL_SLATE)
        self.btn_line.config(bg=COLOR_ACCENT_INDIGO if chart_type == "line" else COLOR_NEUTRAL_SLATE)

        titles = {
            "pie": "Expense Category Breakdown (Pie Chart)",
            "bar": "Income vs Expense Comparison (Bar Chart)",
            "line": "Monthly Expense Trend (Line Graph)"
        }
        self.chart_title_lbl.config(text=titles.get(chart_type, ""))
        self.refresh_analytics()

    # ----------------------------------------------------
    # 🎨 High-Performance Native Canvas Visualizers
    # ----------------------------------------------------
    def _render_pie_chart(self, transactions):
        """Renders Income (Green) vs Expense (Red) Pie Chart."""
        self.canvas.update_idletasks()
        w = max(self.canvas.winfo_width(), 650)
        h = max(self.canvas.winfo_height(), 320)

        if not transactions:
            self.canvas.create_text(
                w / 2, h / 2,
                text="No transaction data available.",
                font=("Segoe UI", 13, "bold"),
                fill=get_color("text_secondary")
            )
            self.insight_lbl.config(text="💡 Insights: Add income or expense records to generate pie chart analytics.")
            return

        total_income = sum(float(t.get("amount", 0)) for t in transactions if str(t.get("type", "")).strip().lower() == "income")
        total_expense = sum(float(t.get("amount", 0)) for t in transactions if str(t.get("type", "")).strip().lower() == "expense")

        total_sum = total_income + total_expense

        if total_sum <= 0:
            self.canvas.create_text(
                w / 2, h / 2,
                text="No transaction data available.",
                font=("Segoe UI", 13, "bold"),
                fill=get_color("text_secondary")
            )
            return

        # Prepare slices: Income (Green) and Expense (Red)
        slices = []
        if total_income > 0:
            slices.append(("Total Income", total_income, COLOR_INCOME_GREEN))  # #10B981 Emerald Green
        if total_expense > 0:
            slices.append(("Total Expense", total_expense, COLOR_EXPENSE_RED))  # #EF4444 Rose Red

        cx = w * 0.35
        cy = h * 0.48
        radius = min(w * 0.25, h * 0.35)
        bbox = (cx - radius, cy - radius, cx + radius, cy + radius)

        legend_x = w * 0.62
        legend_y = max(25, h * 0.25)

        start_angle = 0
        for idx, (label, amount, color) in enumerate(slices):
            pct = (amount / total_sum) * 100
            extent = (amount / total_sum) * 360

            if len(slices) == 1:
                self.canvas.create_oval(
                    bbox, fill=color, outline=get_color("card_bg"), width=2
                )
            else:
                self.canvas.create_arc(
                    bbox, start=start_angle, extent=min(extent, 359.9),
                    fill=color, outline=get_color("card_bg"), width=2
                )

            # Draw On-Slice Percentage Tag
            if pct > 4:
                mid_rad = math.radians(start_angle + extent / 2)
                lbl_dist = radius * 0.62
                lx = cx + lbl_dist * math.cos(mid_rad)
                ly = cy - lbl_dist * math.sin(mid_rad)
                self.canvas.create_text(
                    lx, ly,
                    text=f"{pct:.1f}%",
                    font=("Segoe UI", 10, "bold"),
                    fill="#FFFFFF"
                )

            # Draw Legend Entry
            ly_pos = legend_y + (idx * 32)
            self.canvas.create_rectangle(
                legend_x, ly_pos, legend_x + 16, ly_pos + 16,
                fill=color, outline=""
            )
            self.canvas.create_text(
                legend_x + 24, ly_pos + 8,
                text=f"{label}: ${amount:,.2f} ({pct:.1f}%)",
                font=("Segoe UI", 11, "bold"),
                fill=get_color("text_primary"),
                anchor="w"
            )

            start_angle += extent

        inc_pct = (total_income / total_sum * 100) if total_sum > 0 else 0
        exp_pct = (total_expense / total_sum * 100) if total_sum > 0 else 0

        self.insight_lbl.config(
            text=f"💡 Insights: Financial Breakdown — Income: ${total_income:,.2f} ({inc_pct:.1f}%) in Green vs Expense: ${total_expense:,.2f} ({exp_pct:.1f}%) in Red."
        )

    def _render_bar_chart(self, transactions):
        """Renders an Income vs Expense Comparative Bar Chart."""
        self.canvas.update_idletasks()
        w = max(self.canvas.winfo_width(), 650)
        h = max(self.canvas.winfo_height(), 320)

        total_income = 0.0
        total_expense = 0.0

        for t in transactions:
            try:
                amt = float(t.get("amount", 0.0))
                ttype = str(t.get("type", "")).strip().lower()
                if ttype == "income":
                    total_income += amt
                elif ttype == "expense":
                    total_expense += amt
            except (ValueError, TypeError):
                continue

        max_val = max(total_income, total_expense, 1.0)
        chart_top = 40
        chart_bottom = h - 60

        bar_width = 110
        gap = 80
        start_x = (w - (bar_width * 2 + gap)) / 2

        # 1. Income Bar (Green)
        inc_x0 = start_x
        inc_h = (total_income / max_val) * (chart_bottom - chart_top)
        inc_y0 = chart_bottom - inc_h

        self.canvas.create_rectangle(
            inc_x0, inc_y0, inc_x0 + bar_width, chart_bottom,
            fill=COLOR_INCOME_GREEN, outline=""
        )
        self.canvas.create_text(
            inc_x0 + (bar_width / 2), inc_y0 - 15,
            text=f"${total_income:,.2f}",
            font=("Segoe UI", 11, "bold"),
            fill=COLOR_INCOME_GREEN
        )
        self.canvas.create_text(
            inc_x0 + (bar_width / 2), chart_bottom + 22,
            text="Total Income",
            font=("Segoe UI", 11, "bold"),
            fill=get_color("text_primary")
        )

        # 2. Expense Bar (Red)
        exp_x0 = start_x + bar_width + gap
        exp_h = (total_expense / max_val) * (chart_bottom - chart_top)
        exp_y0 = chart_bottom - exp_h

        self.canvas.create_rectangle(
            exp_x0, exp_y0, exp_x0 + bar_width, chart_bottom,
            fill=COLOR_EXPENSE_RED, outline=""
        )
        self.canvas.create_text(
            exp_x0 + (bar_width / 2), exp_y0 - 15,
            text=f"${total_expense:,.2f}",
            font=("Segoe UI", 11, "bold"),
            fill=COLOR_EXPENSE_RED
        )
        self.canvas.create_text(
            exp_x0 + (bar_width / 2), chart_bottom + 22,
            text="Total Expense",
            font=("Segoe UI", 11, "bold"),
            fill=get_color("text_primary")
        )

        # Baseline axis line
        self.canvas.create_line(
            start_x - 30, chart_bottom, exp_x0 + bar_width + 30, chart_bottom,
            fill=get_color("input_border"), width=2
        )

        net_val = total_income - total_expense
        status_text = "Net Savings" if net_val >= 0 else "Net Deficit"
        self.insight_lbl.config(
            text=f"💡 Insights: {status_text} is ${net_val:,.2f}. Total Income is ${total_income:,.2f} vs Expense ${total_expense:,.2f}."
        )

    def _render_line_chart(self, transactions):
        """Renders a Monthly Expense Spending Trend Line Chart."""
        self.canvas.update_idletasks()
        w = max(self.canvas.winfo_width(), 650)
        h = max(self.canvas.winfo_height(), 320)

        expenses = [t for t in transactions if str(t.get("type", "")).strip().lower() == "expense"]
        if not expenses:
            self.canvas.create_text(
                w / 2, h / 2,
                text="No Expense Data Available to Plot Trend Line",
                font=("Segoe UI", 13, "bold"),
                fill=get_color("text_secondary")
            )
            return

        date_totals = {}
        for t in expenses:
            d = str(t.get("date", "2026-08-01"))
            date_totals[d] = date_totals.get(d, 0.0) + float(t.get("amount", 0))

        sorted_dates = sorted(date_totals.keys())
        if len(sorted_dates) == 1:
            sorted_dates.insert(0, "2026-07-31")
            date_totals["2026-07-31"] = 0.0

        max_val = max(date_totals.values()) or 1.0
        padding_x = 70
        padding_y = 50

        chart_w = w - (padding_x * 2)
        chart_h = h - (padding_y * 2)

        # Background grid lines
        for i in range(4):
            gy = padding_y + (i * (chart_h / 3))
            self.canvas.create_line(
                padding_x, gy, w - padding_x, gy,
                fill=get_color("input_bg"), width=1
            )

        points = []
        step_x = chart_w / (len(sorted_dates) - 1)

        for idx, date_key in enumerate(sorted_dates):
            amt = date_totals[date_key]
            x = padding_x + (idx * step_x)
            y = (h - padding_y) - ((amt / max_val) * chart_h)
            points.append((x, y, date_key, amt))

        # Connecting line
        for i in range(len(points) - 1):
            x1, y1, _, _ = points[i]
            x2, y2, _, _ = points[i + 1]
            self.canvas.create_line(x1, y1, x2, y2, fill=COLOR_ACCENT_INDIGO, width=3)

        # Plot nodes
        for x, y, date_key, amt in points:
            self.canvas.create_oval(
                x - 5, y - 5, x + 5, y + 5,
                fill=COLOR_INCOME_GREEN, outline="#FFFFFF", width=2
            )
            self.canvas.create_text(
                x, y - 14,
                text=f"${amt:,.0f}",
                font=("Segoe UI", 9, "bold"),
                fill=get_color("text_primary")
            )
            self.canvas.create_text(
                x, h - padding_y + 18,
                text=date_key[-5:],
                font=("Segoe UI", 9),
                fill=get_color("text_secondary")
            )

        self.insight_lbl.config(
            text=f"💡 Insights: Tracked {len(sorted_dates)} spending data points. Peak expense day recorded at ${max_val:,.2f}."
        )

    def _handle_theme_toggle(self):
        """Toggles theme state globally."""
        new_theme = toggle_theme_palette()
        self.theme_btn.config(
            text="🌙 Dark Mode" if new_theme == "dark" else "☀️ Light Mode"
        )
        self.refresh_analytics()

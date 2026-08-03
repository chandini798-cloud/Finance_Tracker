"""
ui_splash.py
------------
Animated Splash / Loading Screen for the Personal Finance Tracker application.
Displays animated boot progress bar while checking system initializations.
"""

import time
import tkinter as tk
from tkinter import ttk
from theme import (
    COLOR_BG_DARK, COLOR_CARD_BG, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_ACCENT_INDIGO, FONT_TITLE, FONT_SUBTITLE, FONT_SMALL, draw_app_logo
)


class SplashScreen:
    """
    Animated Loading Splash Window.
    """

    def __init__(self, root, on_complete_callback):
        """
        Initializes Splash Screen.
        
        :param root: Tkinter root instance.
        :param on_complete_callback: Function called when loading completes.
        """
        self.root = root
        self.on_complete_callback = on_complete_callback

        self.root.title("Personal Finance Tracker - Initializing")
        self.root.geometry("460x300")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOR_BG_DARK)

        # Center window on screen
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - 460) // 2
        y = (sh - 300) // 2
        self.root.geometry(f"460x300+{x}+{y}")

        self._create_widgets()
        self._start_boot_animation()

    def _create_widgets(self):
        """Builds splash screen UI widgets."""
        card = tk.Frame(self.root, bg=COLOR_CARD_BG, bd=0)
        card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=420, height=260)

        # App Logo Badge
        logo_canvas = tk.Canvas(card, width=50, height=50, bg=COLOR_CARD_BG, highlightthickness=0)
        logo_canvas.pack(pady=(20, 5))
        draw_app_logo(logo_canvas, width=50, height=50)

        # Title & Subtitle
        title_label = tk.Label(
            card, text="Personal Finance Tracker", font=("Segoe UI", 16, "bold"), bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY
        )
        title_label.pack(pady=(2, 2))

        version_label = tk.Label(
            card, text="Version 1.0.0 • Desktop Edition", font=FONT_SMALL, bg=COLOR_CARD_BG, fg=COLOR_TEXT_SECONDARY
        )
        version_label.pack(pady=(0, 20))

        # Status Label
        self.status_lbl = tk.Label(
            card, text="Initializing database & security components...", font=FONT_SMALL, bg=COLOR_CARD_BG, fg=COLOR_TEXT_SECONDARY
        )
        self.status_lbl.pack(pady=(0, 6))

        # Progress Bar
        style = ttk.Style(self.root)
        style.configure("Splash.Horizontal.TProgressbar", thickness=8, troughcolor=COLOR_BG_DARK, background=COLOR_ACCENT_INDIGO)

        self.progress = ttk.Progressbar(
            card, style="Splash.Horizontal.TProgressbar", orient="horizontal", length=340, mode="determinate"
        )
        self.progress.pack(pady=(0, 15))

    def _start_boot_animation(self):
        """Simulates smooth loading animation step by step."""
        steps = [
            (20, "Loading system configuration tokens..."),
            (45, "Verifying database connection status..."),
            (70, "Initializing PBKDF2 password hashing engine..."),
            (90, "Preparing Tkinter Graphical User Interface..."),
            (100, "Boot Complete! Launching Application...")
        ]

        def step_sequence(idx=0):
            if idx < len(steps):
                pct, msg = steps[idx]
                self.progress["value"] = pct
                self.status_lbl.config(text=msg)
                self.root.after(280, lambda: step_sequence(idx + 1))
            else:
                self.root.after(200, self.on_complete_callback)

        step_sequence()

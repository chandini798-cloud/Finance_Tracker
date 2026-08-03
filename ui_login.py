"""
ui_login.py
-----------
Professional Tkinter Login GUI window for the Personal Finance Tracker.
Includes modern dark aesthetic, app logo, validation handlers, and exit controls.
"""

import sys
import tkinter as tk
from tkinter import messagebox
from auth import validate_login_input, login_user
from theme import (
    COLOR_BG_DARK, COLOR_CARD_BG, COLOR_INPUT_BG, COLOR_INPUT_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_PRIMARY_EMERALD,
    COLOR_PRIMARY_HOVER, COLOR_ACCENT_INDIGO, COLOR_ACCENT_HOVER,
    COLOR_DANGER_RED, COLOR_DANGER_HOVER, FONT_TITLE, FONT_SUBTITLE,
    FONT_LABEL, FONT_ENTRY, FONT_BUTTON, FONT_LINK, FONT_SMALL,
    draw_app_logo
)


class LoginWindow:
    """
    Professional Tkinter Login View Component.
    """

    def __init__(self, root, switch_to_register_callback, on_login_success_callback=None):
        """
        Initializes the Login Window.
        
        :param root: Tkinter root instance.
        :param switch_to_register_callback: Callback to navigate to Register screen.
        :param on_login_success_callback: Callback upon successful user authentication.
        """
        self.root = root
        self.switch_to_register_callback = switch_to_register_callback
        self.on_login_success_callback = on_login_success_callback

        self.root.title("Personal Finance Tracker - Login")
        self.root.geometry("480x620")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOR_BG_DARK)

        self.show_password_var = tk.BooleanVar(value=False)
        self._create_widgets()
        self._bind_events()

    def _create_widgets(self):
        """Builds all UI components inside a centered card container."""

        # Floating Card Container
        card_frame = tk.Frame(self.root, bg=COLOR_CARD_BG, bd=0, relief=tk.FLAT)
        card_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=410, height=550)

        # Header Section with App Logo & Title
        header_frame = tk.Frame(card_frame, bg=COLOR_CARD_BG)
        header_frame.pack(pady=(20, 10))

        logo_canvas = tk.Canvas(
            header_frame, width=60, height=60, bg=COLOR_CARD_BG, highlightthickness=0
        )
        logo_canvas.pack()
        draw_app_logo(logo_canvas, width=60, height=60)

        title_label = tk.Label(
            header_frame,
            text="Finance Tracker",
            font=FONT_TITLE,
            bg=COLOR_CARD_BG,
            fg=COLOR_TEXT_PRIMARY
        )
        title_label.pack(pady=(8, 2))

        subtitle_label = tk.Label(
            header_frame,
            text="Welcome back! Log in to manage your budget.",
            font=FONT_SUBTITLE,
            bg=COLOR_CARD_BG,
            fg=COLOR_TEXT_SECONDARY
        )
        subtitle_label.pack()

        # Form Fields Container
        form_frame = tk.Frame(card_frame, bg=COLOR_CARD_BG)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=35, pady=(15, 10))

        # Username Input
        username_label = tk.Label(
            form_frame, text="Username", font=FONT_LABEL, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY
        )
        username_label.pack(anchor=tk.W, pady=(0, 3))

        self.username_entry = tk.Entry(
            form_frame,
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
        self.username_entry.pack(fill=tk.X, ipady=7, pady=(0, 12))
        self.username_entry.focus_set()

        # Password Input
        password_label = tk.Label(
            form_frame, text="Password", font=FONT_LABEL, bg=COLOR_CARD_BG, fg=COLOR_TEXT_PRIMARY
        )
        password_label.pack(anchor=tk.W, pady=(0, 3))

        self.password_entry = tk.Entry(
            form_frame,
            font=FONT_ENTRY,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT_PRIMARY,
            insertbackground="white",
            bd=1,
            relief=tk.SOLID,
            highlightbackground=COLOR_INPUT_BORDER,
            highlightcolor=COLOR_ACCENT_INDIGO,
            highlightthickness=1,
            show="*"
        )
        self.password_entry.pack(fill=tk.X, ipady=7, pady=(0, 6))

        # Show Password Checkbox
        show_cb = tk.Checkbutton(
            form_frame,
            text="Show Password",
            variable=self.show_password_var,
            command=self._toggle_password_visibility,
            bg=COLOR_CARD_BG,
            fg=COLOR_TEXT_SECONDARY,
            selectcolor=COLOR_INPUT_BG,
            activebackground=COLOR_CARD_BG,
            activeforeground=COLOR_TEXT_PRIMARY,
            font=FONT_SMALL
        )
        show_cb.pack(anchor=tk.W, pady=(0, 15))

        # Button Group Container
        btn_frame = tk.Frame(form_frame, bg=COLOR_CARD_BG)
        btn_frame.pack(fill=tk.X, pady=(0, 15))

        # 1. Login Button
        self.login_btn = tk.Button(
            btn_frame,
            text="LOG IN",
            font=FONT_BUTTON,
            bg=COLOR_PRIMARY_EMERALD,
            fg="#FFFFFF",
            activebackground=COLOR_PRIMARY_HOVER,
            activeforeground="#FFFFFF",
            bd=0,
            cursor="hand2",
            command=self._handle_login
        )
        self.login_btn.pack(fill=tk.X, ipady=7, pady=(0, 8))
        self._add_button_hover(self.login_btn, COLOR_PRIMARY_EMERALD, COLOR_PRIMARY_HOVER)

        # Action Links Grid: Register Button + Exit Button
        action_bar = tk.Frame(btn_frame, bg=COLOR_CARD_BG)
        action_bar.pack(fill=tk.X)

        # 2. Register Navigation Button
        self.register_btn = tk.Button(
            action_bar,
            text="Create Account",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_ACCENT_INDIGO,
            fg="#FFFFFF",
            activebackground=COLOR_ACCENT_HOVER,
            activeforeground="#FFFFFF",
            bd=0,
            cursor="hand2",
            command=self.switch_to_register_callback
        )
        self.register_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=5, padx=(0, 4))
        self._add_button_hover(self.register_btn, COLOR_ACCENT_INDIGO, COLOR_ACCENT_HOVER)

        # 3. Exit Application Button
        self.exit_btn = tk.Button(
            action_bar,
            text="Exit App",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_DANGER_RED,
            fg="#FFFFFF",
            activebackground=COLOR_DANGER_HOVER,
            activeforeground="#FFFFFF",
            bd=0,
            cursor="hand2",
            command=self._handle_exit
        )
        self.exit_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, ipady=5, padx=(4, 0))
        self._add_button_hover(self.exit_btn, COLOR_DANGER_RED, COLOR_DANGER_HOVER)

    def _bind_events(self):
        """Binds keyboard shortcuts for user convenience."""
        self.root.bind("<Return>", lambda event: self._handle_login())

    def _add_button_hover(self, button, normal_color, hover_color):
        """Adds smooth background hover effect to Tkinter buttons."""
        button.bind("<Enter>", lambda e: button.config(bg=hover_color))
        button.bind("<Leave>", lambda e: button.config(bg=normal_color))

    def _toggle_password_visibility(self):
        """Toggles password entry mask."""
        char = "" if self.show_password_var.get() else "*"
        self.password_entry.config(show=char)

    def _handle_login(self):
        """Validates credentials and attempts login."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        is_valid, error_msg = validate_login_input(username, password)
        if not is_valid:
            messagebox.showwarning("Validation Error", error_msg, parent=self.root)
            return

        success, response_msg, user_info = login_user(username, password)
        if success:
            messagebox.showinfo("Login Success", f"Welcome back, {user_info['username']}!", parent=self.root)
            if self.on_login_success_callback:
                self.on_login_success_callback(user_info)
        else:
            messagebox.showerror("Login Failed", response_msg, parent=self.root)

    def _handle_exit(self):
        """Confirms and exits the application."""
        if messagebox.askokcancel("Exit Application", "Are you sure you want to quit?", parent=self.root):
            self.root.destroy()
            sys.exit(0)

"""Tkinter widget catalog for learning (Python 3.9).

Run: python tkinter_widget_catalog.py
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class WidgetCatalog(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Tkinter Widget Catalog (Python 3.9)")
        self.geometry("1100x720")

        self._build_menu()
        self._build_layout()

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="New", command=lambda: self._set_status("New clicked"))
        file_menu.add_command(label="Open", command=lambda: self._set_status("Open clicked"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)

        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About", command=self._open_toplevel)

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        self.status_var = tk.StringVar(value="Ready")

        paned = ttk.Panedwindow(root, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left = ttk.Frame(paned, padding=8)
        right = ttk.Frame(paned, padding=8)
        paned.add(left, weight=1)
        paned.add(right, weight=2)

        self._build_left_panel(left)
        self._build_right_panel(right)

        status = ttk.Label(root, textvariable=self.status_var, anchor="w")
        status.pack(fill="x", pady=(8, 0))

    def _build_left_panel(self, parent: ttk.Frame) -> None:
        # LabelFrame
        lf = ttk.LabelFrame(parent, text="Inputs")
        lf.pack(fill="x", pady=(0, 10))

        ttk.Label(lf, text="Label: Name").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.name_var = tk.StringVar(value="Alice")
        entry = ttk.Entry(lf, textvariable=self.name_var, width=22)  # Entry
        entry.grid(row=0, column=1, sticky="ew", padx=6, pady=4)

        ttk.Label(lf, text="OptionMenu:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.option_var = tk.StringVar(value="Option A")
        option_menu = ttk.OptionMenu(lf, self.option_var, "Option A", "Option A", "Option B", "Option C")
        option_menu.grid(row=1, column=1, sticky="ew", padx=6, pady=4)

        ttk.Label(lf, text="Combobox:").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.combo_var = tk.StringVar(value="Alpha")
        combo = ttk.Combobox(
            lf,
            textvariable=self.combo_var,
            values=("Alpha", "Beta", "Gamma"),
            state="normal",
        )
        combo.grid(row=2, column=1, sticky="ew", padx=6, pady=4)

        ttk.Label(lf, text="Spinbox:").grid(row=3, column=0, sticky="w", padx=6, pady=4)
        self.spin_var = tk.StringVar(value="5")
        spin = tk.Spinbox(lf, from_=0, to=20, textvariable=self.spin_var, width=8)  # Spinbox
        spin.grid(row=3, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(lf, text="Scale:").grid(row=4, column=0, sticky="w", padx=6, pady=4)
        self.scale_var = tk.IntVar(value=50)
        scale = ttk.Scale(lf, from_=0, to=100, variable=self.scale_var, orient="horizontal")  # Scale
        scale.grid(row=4, column=1, sticky="ew", padx=6, pady=4)

        lf.columnconfigure(1, weight=1)

        # Frame and Checkbutton / Radiobutton
        group = ttk.Frame(parent)  # Frame
        group.pack(fill="x", pady=(0, 10))

        self.check_a = tk.BooleanVar(value=True)
        self.check_b = tk.BooleanVar(value=False)
        ttk.Checkbutton(group, text="Check A", variable=self.check_a).grid(row=0, column=0, sticky="w", padx=6)
        ttk.Checkbutton(group, text="Check B", variable=self.check_b).grid(row=0, column=1, sticky="w", padx=6)

        self.radio_var = tk.StringVar(value="R1")
        ttk.Radiobutton(group, text="Radio 1", variable=self.radio_var, value="R1").grid(
            row=1, column=0, sticky="w", padx=6
        )
        ttk.Radiobutton(group, text="Radio 2", variable=self.radio_var, value="R2").grid(
            row=1, column=1, sticky="w", padx=6
        )

        # Button
        button = ttk.Button(parent, text="Button: Show Values", command=self._show_values)
        button.pack(fill="x", pady=(0, 10))

        # Menubutton
        menu_btn = tk.Menubutton(parent, text="Menubutton")
        menu = tk.Menu(menu_btn, tearoff=False)
        menu.add_command(label="Action 1", command=lambda: self._set_status("Action 1"))
        menu.add_command(label="Action 2", command=lambda: self._set_status("Action 2"))
        menu_btn.config(menu=menu)
        menu_btn.pack(fill="x", pady=(0, 10))

        # Listbox + Scrollbar
        list_frame = ttk.LabelFrame(parent, text="Listbox")
        list_frame.pack(fill="both", expand=False)
        listbox = tk.Listbox(list_frame, height=6, exportselection=False)  # Listbox
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)  # Scrollbar
        listbox.configure(yscrollcommand=scrollbar.set)
        for i in range(1, 21):
            listbox.insert("end", f"Item {i}")
        listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        list_frame.columnconfigure(0, weight=1)

    def _build_right_panel(self, parent: ttk.Frame) -> None:
        # Message
        msg = tk.Message(
            parent,
            text="Message: This text wraps automatically to fit the width of the widget.",
            width=420,
        )
        msg.pack(fill="x", pady=(0, 10))

        # Canvas with shapes and PhotoImage
        canvas_frame = ttk.LabelFrame(parent, text="Canvas + PhotoImage")
        canvas_frame.pack(fill="both", expand=False, pady=(0, 10))
        canvas = tk.Canvas(canvas_frame, width=420, height=200, bg="white")  # Canvas
        canvas.pack(fill="x", padx=6, pady=6)
        canvas.create_rectangle(20, 20, 140, 90, fill="#4ea8de", outline="")
        canvas.create_oval(170, 20, 290, 90, fill="#9bde7e", outline="")
        canvas.create_text(220, 150, text="Canvas Text", fill="#333")

        # PhotoImage (simple generated image)
        self.photo = tk.PhotoImage(width=60, height=60)  # PhotoImage
        self.photo.put("#ffcc00", to=(0, 0, 59, 59))
        self.photo.put("#333333", to=(10, 10, 49, 49))
        canvas.create_image(340, 60, image=self.photo)

        # Text + Scrollbar
        text_frame = ttk.LabelFrame(parent, text="Text")
        text_frame.pack(fill="both", expand=True)
        text = tk.Text(text_frame, wrap="word", height=8)  # Text
        text_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=text.yview)  # Scrollbar
        text.configure(yscrollcommand=text_scroll.set)
        text.insert("end", "Text widget supports multi-line editing.\nAdd more lines here.")
        text.grid(row=0, column=0, sticky="nsew")
        text_scroll.grid(row=0, column=1, sticky="ns")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

    def _show_values(self) -> None:
        summary = (
            f"Name={self.name_var.get()} | "
            f"Option={self.option_var.get()} | "
            f"Combo={self.combo_var.get()} | "
            f"Spin={self.spin_var.get()} | "
            f"Scale={self.scale_var.get()} | "
            f"CheckA={self.check_a.get()} | "
            f"CheckB={self.check_b.get()} | "
            f"Radio={self.radio_var.get()}"
        )
        self._set_status(summary)

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _open_toplevel(self) -> None:
        win = tk.Toplevel(self)  # Toplevel
        win.title("About")
        win.geometry("360x180")
        ttk.Label(win, text="Tkinter Widget Catalog", font=("Segoe UI", 12, "bold")).pack(
            pady=(20, 6)
        )
        ttk.Label(win, text="This window is a Toplevel example.").pack(pady=4)
        ttk.Button(win, text="Close", command=win.destroy).pack(pady=10)


if __name__ == "__main__":
    app = WidgetCatalog()
    app.mainloop()

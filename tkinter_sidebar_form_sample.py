import tkinter as tk
from tkinter import ttk, messagebox


class SidebarFormApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Tkinter Sidebar Form Sample")
        self.root.geometry("900x560")
        self.root.minsize(760, 480)

        self._build_layout()

    def _build_layout(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(self.root, padding=12)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.columnconfigure(0, weight=1)

        ttk.Label(sidebar, text="Menu", font=("Yu Gothic UI", 12, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )
        ttk.Button(sidebar, text="Dashboard", command=lambda: self._show_view("dashboard")).grid(
            row=1, column=0, sticky="ew", pady=4
        )
        ttk.Button(sidebar, text="Users", command=lambda: self._show_view("users")).grid(
            row=2, column=0, sticky="ew", pady=4
        )
        ttk.Button(sidebar, text="Settings", command=lambda: self._show_view("settings")).grid(
            row=3, column=0, sticky="ew", pady=4
        )
        ttk.Separator(sidebar, orient="horizontal").grid(row=4, column=0, sticky="ew", pady=12)
        ttk.Button(sidebar, text="Clear Form", command=self._clear_form).grid(
            row=5, column=0, sticky="ew", pady=4
        )

        self.status_var = tk.StringVar(value="Ready")
        self.content_area = ttk.Frame(self.root, padding=16)
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.columnconfigure(0, weight=1)
        self.content_area.rowconfigure(0, weight=1)
        self.views = {}

        self._build_dashboard_view()
        self._build_users_view()
        self._build_settings_view()
        self._show_view("dashboard")

        status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor="w", padding=(10, 6))
        status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

    def _build_dashboard_view(self) -> None:
        frame = ttk.Frame(self.content_area)
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text="Dashboard", font=("Yu Gothic UI", 14, "bold")).pack(anchor="w", pady=(0, 8))
        ttk.Label(frame, text="左側メニューのボタンで表示を切り替えられます。").pack(anchor="w")
        self.views["dashboard"] = frame

    def _build_users_view(self) -> None:
        frame = ttk.Frame(self.content_area)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(5, weight=1)

        ttk.Label(frame, text="Profile Form", font=("Yu Gothic UI", 14, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )

        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.role_var = tk.StringVar(value="Viewer")
        self.active_var = tk.BooleanVar(value=True)

        ttk.Label(frame, text="Name").grid(row=1, column=0, sticky="w", pady=6, padx=(0, 12))
        ttk.Entry(frame, textvariable=self.name_var).grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Email").grid(row=2, column=0, sticky="w", pady=6, padx=(0, 12))
        ttk.Entry(frame, textvariable=self.email_var).grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Role").grid(row=3, column=0, sticky="w", pady=6, padx=(0, 12))
        ttk.Combobox(
            frame,
            textvariable=self.role_var,
            values=("Admin", "Editor", "Viewer"),
            state="readonly",
        ).grid(row=3, column=1, sticky="ew", pady=6)

        ttk.Checkbutton(frame, text="Active user", variable=self.active_var).grid(
            row=4, column=1, sticky="w", pady=6
        )

        ttk.Label(frame, text="Notes").grid(row=5, column=0, sticky="nw", pady=6, padx=(0, 12))
        self.notes_text = tk.Text(frame, height=8, wrap="word")
        self.notes_text.grid(row=5, column=1, sticky="nsew", pady=6)

        button_row = ttk.Frame(frame)
        button_row.grid(row=6, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(button_row, text="Save", command=self._save).grid(row=0, column=0, padx=4)
        ttk.Button(button_row, text="Cancel", command=self._clear_form).grid(row=0, column=1, padx=4)
        self.views["users"] = frame

    def _build_settings_view(self) -> None:
        frame = ttk.Frame(self.content_area)
        frame.grid(row=0, column=0, sticky="nsew")
        ttk.Label(frame, text="Settings", font=("Yu Gothic UI", 14, "bold")).pack(anchor="w", pady=(0, 8))
        ttk.Label(frame, text="設定画面のサンプル領域です。").pack(anchor="w")
        self.dark_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Enable dark mode (sample)", variable=self.dark_mode_var).pack(
            anchor="w", pady=8
        )
        self.views["settings"] = frame

    def _show_view(self, name: str) -> None:
        for view_name, frame in self.views.items():
            if view_name == name:
                frame.tkraise()
        self._set_status(f"{name.capitalize()} selected")

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _clear_form(self) -> None:
        self.name_var.set("")
        self.email_var.set("")
        self.role_var.set("Viewer")
        self.active_var.set(True)
        self.notes_text.delete("1.0", "end")
        self._set_status("Form cleared")

    def _save(self) -> None:
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        if not name or not email:
            messagebox.showwarning("Validation", "Name and Email are required.")
            self._set_status("Validation error")
            return

        self._set_status("Saved successfully")
        messagebox.showinfo("Saved", "Form data has been saved.")


def main() -> None:
    root = tk.Tk()
    SidebarFormApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

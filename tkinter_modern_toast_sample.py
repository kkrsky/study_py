import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import Callable, List, Optional


@dataclass
class ToastStyle:
    bg: str
    fg: str
    accent: str


class ToastManager:
    """Show modern toast notifications with stack, fade and optional actions."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.toasts: List[tk.Toplevel] = []
        self.styles = {
            "info": ToastStyle(bg="#1F2937", fg="#F9FAFB", accent="#60A5FA"),
            "success": ToastStyle(bg="#064E3B", fg="#ECFDF5", accent="#34D399"),
            "warning": ToastStyle(bg="#78350F", fg="#FFFBEB", accent="#FBBF24"),
            "error": ToastStyle(bg="#7F1D1D", fg="#FEF2F2", accent="#F87171"),
        }

    def show(self, message: str, kind: str = "info", duration_ms: int = 2600) -> None:
        title_map = {
            "info": "Info",
            "success": "Success",
            "warning": "Warning",
            "error": "Error",
        }
        toast, _frame, _body, _style = self._create_toast_base(
            kind,
            title_map.get(kind, "Info"),
            message,
        )
        toast.after(duration_ms, lambda: self._fade_out_and_destroy(toast))

    def show_input_toast(
        self,
        title: str,
        message: str,
        on_submit: Callable[[str], None],
        on_cancel: Optional[Callable[[], None]] = None,
        kind: str = "info",
    ) -> None:
        """Show text-input toast that stays until Submit/Cancel is pressed."""
        toast, _frame, body, style = self._create_toast_base(kind, title, message)

        entry_var = tk.StringVar()
        entry = tk.Entry(
            body,
            textvariable=entry_var,
            bg="#111827",
            fg="#F9FAFB",
            insertbackground="#F9FAFB",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#374151",
            highlightcolor=style.accent,
        )
        entry.pack(fill="x", pady=(8, 6))
        entry.focus_set()

        btn_row = tk.Frame(body, bg=style.bg)
        btn_row.pack(fill="x")

        def submit() -> None:
            on_submit(entry_var.get())
            self._fade_out_and_destroy(toast)

        def cancel() -> None:
            if on_cancel:
                on_cancel()
            self._fade_out_and_destroy(toast)

        tk.Button(
            btn_row,
            text="Submit",
            command=submit,
            bg=style.accent,
            fg="#111827",
            activebackground=style.accent,
            activeforeground="#111827",
            relief="flat",
            padx=10,
        ).pack(side="right", padx=(6, 0))

        tk.Button(
            btn_row,
            text="Cancel",
            command=cancel,
            bg="#374151",
            fg=style.fg,
            activebackground="#4B5563",
            activeforeground=style.fg,
            relief="flat",
            padx=10,
        ).pack(side="right")

        entry.bind("<Return>", lambda _e: submit())
        entry.bind("<Escape>", lambda _e: cancel())
        self._reposition()

    def show_yes_no_toast(
        self,
        title: str,
        message: str,
        on_yes: Callable[[], None],
        on_no: Callable[[], None],
        kind: str = "warning",
    ) -> None:
        """Show Yes/No toast that stays until user chooses one action."""
        toast, _frame, body, style = self._create_toast_base(kind, title, message)

        btn_row = tk.Frame(body, bg=style.bg)
        btn_row.pack(fill="x", pady=(10, 0))

        def choose_yes() -> None:
            on_yes()
            self._fade_out_and_destroy(toast)

        def choose_no() -> None:
            on_no()
            self._fade_out_and_destroy(toast)

        tk.Button(
            btn_row,
            text="Yes",
            command=choose_yes,
            bg=style.accent,
            fg="#111827",
            activebackground=style.accent,
            activeforeground="#111827",
            relief="flat",
            padx=12,
        ).pack(side="right", padx=(6, 0))

        tk.Button(
            btn_row,
            text="No",
            command=choose_no,
            bg="#374151",
            fg=style.fg,
            activebackground="#4B5563",
            activeforeground=style.fg,
            relief="flat",
            padx=12,
        ).pack(side="right")
        self._reposition()

    def _create_toast_base(self, kind: str, title: str, message: str):
        style = self.styles.get(kind, self.styles["info"])
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.attributes("-alpha", 0.0)
        toast.configure(bg=style.bg)

        frame = tk.Frame(toast, bg=style.bg, bd=0, highlightthickness=1, highlightbackground="#111827")
        frame.pack(fill="both", expand=True)

        accent = tk.Frame(frame, bg=style.accent, width=5)
        accent.pack(side="left", fill="y")

        body = tk.Frame(frame, bg=style.bg, padx=12, pady=10)
        body.pack(side="left", fill="both", expand=True)

        tk.Label(
            body,
            text=title,
            bg=style.bg,
            fg=style.fg,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            body,
            text=message,
            bg=style.bg,
            fg=style.fg,
            font=("Segoe UI", 10),
            anchor="w",
            justify="left",
            wraplength=280,
        ).pack(fill="x", pady=(4, 0))

        close_btn = tk.Label(
            frame,
            text="x",
            bg=style.bg,
            fg="#D1D5DB",
            font=("Segoe UI", 10, "bold"),
            padx=8,
            pady=6,
            cursor="hand2",
        )
        close_btn.pack(side="right", anchor="n")
        close_btn.bind("<Button-1>", lambda _e: self._fade_out_and_destroy(toast))

        self.toasts.append(toast)
        self._reposition()
        self._fade_in(toast)
        return toast, frame, body, style

    def _reposition(self) -> None:
        self.root.update_idletasks()
        self.toasts = [t for t in self.toasts if t.winfo_exists()]

        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_w = self.root.winfo_width()

        margin = 16
        top = root_y + 16
        for toast in self.toasts:
            toast.update_idletasks()
            w = max(340, toast.winfo_reqwidth())
            h = max(78, toast.winfo_reqheight())
            x = root_x + root_w - w - margin
            y = top
            toast.geometry(f"{w}x{h}+{x}+{y}")
            top += h + 10

    def _fade_in(self, toast: tk.Toplevel, alpha: float = 0.0) -> None:
        if not toast.winfo_exists():
            return
        alpha = min(alpha + 0.12, 1.0)
        toast.attributes("-alpha", alpha)
        if alpha < 1.0:
            toast.after(20, lambda: self._fade_in(toast, alpha))

    def _fade_out_and_destroy(self, toast: tk.Toplevel, alpha: float = 1.0) -> None:
        if not toast.winfo_exists():
            return
        alpha = max(alpha - 0.14, 0.0)
        toast.attributes("-alpha", alpha)
        if alpha > 0.0:
            toast.after(20, lambda: self._fade_out_and_destroy(toast, alpha))
            return

        try:
            toast.destroy()
        finally:
            self.toasts = [t for t in self.toasts if t.winfo_exists()]
            self._reposition()


def main() -> None:
    root = tk.Tk()
    root.title("Tkinter Modern Toast Sample")
    root.geometry("860x520")
    root.configure(bg="#F3F4F6")

    manager = ToastManager(root)
    result_var = tk.StringVar(value="Action result: (none)")

    container = ttk.Frame(root, padding=20)
    container.pack(fill="both", expand=True)

    ttk.Label(container, text="Toast Demo", font=("Segoe UI", 18, "bold")).pack(anchor="w")
    ttk.Label(
        container,
        text="Click buttons to show modern toast notifications.",
        font=("Segoe UI", 10),
    ).pack(anchor="w", pady=(4, 14))

    buttons = ttk.Frame(container)
    buttons.pack(anchor="w")

    ttk.Button(
        buttons,
        text="Info Toast",
        command=lambda: manager.show("New updates are available.", "info"),
    ).grid(row=0, column=0, padx=(0, 8), pady=4)

    ttk.Button(
        buttons,
        text="Warning Toast",
        command=lambda: manager.show("Session will expire in 2 minutes.", "warning"),
    ).grid(row=0, column=1, padx=(0, 8), pady=4)

    ttk.Button(
        buttons,
        text="Success Toast",
        command=lambda: manager.show("Your profile has been saved successfully.", "success"),
    ).grid(row=0, column=2, padx=(0, 8), pady=4)

    ttk.Button(
        buttons,
        text="Error Toast",
        command=lambda: manager.show("Failed to connect to the server.", "error"),
    ).grid(row=0, column=3, padx=(0, 8), pady=4)

    ttk.Button(
        buttons,
        text="Input Toast",
        command=lambda: manager.show_input_toast(
            title="Input Required",
            message="Please enter your display name.",
            on_submit=lambda text: result_var.set(f"Action result: input='{text}'"),
            on_cancel=lambda: result_var.set("Action result: input canceled"),
            kind="info",
        ),
    ).grid(row=1, column=0, padx=(0, 8), pady=4, sticky="w")

    ttk.Button(
        buttons,
        text="Yes/No Toast",
        command=lambda: manager.show_yes_no_toast(
            title="Confirm",
            message="Do you want to apply the latest settings?",
            on_yes=lambda: result_var.set("Action result: YES selected"),
            on_no=lambda: result_var.set("Action result: NO selected"),
            kind="warning",
        ),
    ).grid(row=1, column=1, padx=(0, 8), pady=4, sticky="w")

    ttk.Separator(container).pack(fill="x", pady=16)
    ttk.Label(
        container,
        text="Tips: Input/YesNo toasts stay until an action is taken.",
        font=("Segoe UI", 10),
    ).pack(anchor="w")
    ttk.Label(container, textvariable=result_var, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 0))

    root.bind("<Configure>", lambda _e: manager._reposition())
    root.mainloop()


if __name__ == "__main__":
    main()

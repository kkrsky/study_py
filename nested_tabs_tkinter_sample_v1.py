import tkinter as tk
from tkinter import ttk


def build_nested_notebook(parent: ttk.Frame, title_prefix: str) -> ttk.Notebook:
    nested = ttk.Notebook(parent)

    for i in range(1, 4):
        child_tab = ttk.Frame(nested, padding=12)
        nested.add(child_tab, text=f"{title_prefix} - 内側タブ{i}")

        label = ttk.Label(
            child_tab,
            text=f"{title_prefix} の内側タブ{i}です。",
            anchor="center",
        )
        label.pack(fill="both", expand=True)

    return nested


def main() -> None:
    root = tk.Tk()
    root.title("tkinter ネストタブ サンプル")
    root.geometry("720x420")

    outer = ttk.Notebook(root)
    outer.pack(fill="both", expand=True, padx=10, pady=10)

    for section in ("セクションA", "セクションB"):
        outer_tab = ttk.Frame(outer, padding=8)
        outer.add(outer_tab, text=section)

        title = ttk.Label(
            outer_tab,
            text=f"{section} (外側タブ) の中に内側タブがあります",
        )
        title.pack(anchor="w", pady=(0, 8))

        inner = build_nested_notebook(outer_tab, section)
        inner.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()

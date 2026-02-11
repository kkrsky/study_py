import tkinter as tk
from tkinter import ttk


def setup_styles(root: tk.Tk) -> None:
    style = ttk.Style(root)
    style.configure("Outer.TNotebook.Tab", padding=(12, 6), font=("Yu Gothic UI", 10))
    style.configure("Inner.TNotebook.Tab", padding=(10, 5), font=("Yu Gothic UI", 9))
    style.configure("Content.TLabel", font=("Yu Gothic UI", 10))

    # Remove focus element to hide dotted focus rectangle on tabs.
    simple_tab_layout = [
        (
            "Notebook.tab",
            {
                "sticky": "nswe",
                "children": [
                    (
                        "Notebook.padding",
                        {
                            "side": "top",
                            "sticky": "nswe",
                            "children": [("Notebook.label", {"side": "top", "sticky": ""})],
                        },
                    )
                ],
            },
        )
    ]
    style.layout("Outer.TNotebook.Tab", simple_tab_layout)
    style.layout("Inner.TNotebook.Tab", simple_tab_layout)


def build_nested_notebook(parent: ttk.Frame, title_prefix: str) -> ttk.Notebook:
    nested = ttk.Notebook(parent, style="Inner.TNotebook")
    nested.configure(takefocus=False)

    for i in range(1, 4):
        child_tab = ttk.Frame(nested, padding=12)
        nested.add(child_tab, text=f"Inner Tab {i}")

        label = ttk.Label(
            child_tab,
            text=f"{title_prefix}: inner tab {i}",
            anchor="center",
            style="Content.TLabel",
        )
        label.pack(fill="both", expand=True)

    return nested


def main() -> None:
    root = tk.Tk()
    root.title("Tkinter Nested Tabs")
    root.geometry("720x420")
    setup_styles(root)

    app = ttk.Frame(root, padding=10)
    app.pack(fill="both", expand=True)

    outer = ttk.Notebook(app, style="Outer.TNotebook")
    outer.configure(takefocus=False)
    outer.pack(fill="both", expand=True)

    for section in ("Section A", "Section B"):
        outer_tab = ttk.Frame(outer, padding=(6, 2, 6, 6))
        outer.add(outer_tab, text=section)

        inner = build_nested_notebook(outer_tab, section)
        inner.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import ttk


def setup_styles(root: tk.Tk) -> None:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("App.TFrame", background="#E7ECF3")
    style.configure("OuterContent.TFrame", background="#F4F7FB")
    style.configure("InnerContent.TFrame", background="#FFFFFF", borderwidth=1, relief="solid")
    style.configure("Content.TLabel", background="#FFFFFF", foreground="#1A1A1A", font=("Yu Gothic UI", 10))

    # Outer notebook style: strong border and clear selected tab.
    style.configure(
        "Outer.TNotebook",
        background="#C7D4E5",
        bordercolor="#7A90B2",
        borderwidth=2,
        tabmargins=(6, 6, 6, 0),
    )
    style.configure(
        "Outer.TNotebook.Tab",
        padding=(14, 8),
        font=("Yu Gothic UI", 10, "bold"),
        background="#D5DFEC",
        foreground="#23324D",
        relief="flat",
    )
    style.map(
        "Outer.TNotebook.Tab",
        background=[("active", "#E8EEF7"), ("selected", "#FFFFFF")],
        foreground=[("selected", "#0F1D36")],
        relief=[("selected", "flat"), ("active", "flat")],
        padding=[("selected", (14, 8)), ("active", (14, 8))],
    )
    # Remove focus element from outer tabs to hide dotted focus rectangle.
    style.layout(
        "Outer.TNotebook.Tab",
        [
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
        ],
    )

    # Inner notebook style: separate tone from outer notebook.
    style.configure(
        "Inner.TNotebook",
        background="#BFCFDE",
        bordercolor="#6987A6",
        borderwidth=2,
        tabmargins=(0, 0, 0, 0),
    )
    style.configure(
        "Inner.TNotebook.Tab",
        padding=(10, 6),
        font=("Yu Gothic UI", 9),
        background="#CAD8E6",
        foreground="#25334A",
        relief="flat",
    )
    style.map(
        "Inner.TNotebook.Tab",
        background=[("active", "#DEE7F2"), ("selected", "#FFFFFF")],
        foreground=[("selected", "#0F1D36")],
        relief=[("selected", "flat"), ("active", "flat")],
        padding=[("selected", (10, 6)), ("active", (10, 6))],
    )
    # Remove focus element from inner tabs to hide dotted focus rectangle.
    style.layout(
        "Inner.TNotebook.Tab",
        [
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
        ],
    )


def build_nested_notebook(parent: ttk.Frame, title_prefix: str) -> ttk.Notebook:
    nested = ttk.Notebook(parent, style="Inner.TNotebook")
    nested.configure(takefocus=False)

    for i in range(1, 4):
        child_tab = ttk.Frame(nested, style="InnerContent.TFrame", padding=14)
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
    root.configure(background="#E7ECF3")
    setup_styles(root)

    app = ttk.Frame(root, style="App.TFrame", padding=12)
    app.pack(fill="both", expand=True)

    outer = ttk.Notebook(app, style="Outer.TNotebook")
    outer.configure(takefocus=False)
    outer.pack(fill="both", expand=True)

    for section in ("Section A", "Section B"):
        # Keep top padding small so the nested tab buttons sit just below the outer tabs.
        outer_tab = ttk.Frame(outer, style="OuterContent.TFrame", padding=(8, 2, 8, 8))
        outer.add(outer_tab, text=section)

        inner = build_nested_notebook(outer_tab, section)
        inner.pack(fill="both", expand=True, padx=0, pady=0)

    root.mainloop()


if __name__ == "__main__":
    main()

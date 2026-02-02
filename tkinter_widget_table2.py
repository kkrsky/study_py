"""Generic, configurable table using Tkinter widgets (Python 3.9).

Run: python tkinter_widget_table.py
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Iterable, List, Optional


ColumnSpec = Dict[str, Any]
RowSpec = Dict[str, Any]


class WidgetTable(ttk.Frame):
    """A widget-based table built from column specs and row data."""

    def __init__(
        self,
        master: tk.Widget,
        columns: Iterable[ColumnSpec],
        rows: Iterable[RowSpec],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, *args, **kwargs)
        self._columns = list(columns)
        self._rows = list(rows)
        self._cell_vars: Dict[str, tk.Variable] = {}
        self._row_widgets: Dict[str, List[tk.Widget]] = {}
        self._selected_row_id: Optional[str] = None
        self._sort_state: Dict[str, bool] = {}

        self._style = ttk.Style(self)
        self._style.configure("Selected.TLabel", background="#dbeafe")
        self._style.configure("Selected.TEntry", fieldbackground="#dbeafe")
        self._style.configure("Selected.TCombobox", fieldbackground="#dbeafe")
        self._style.configure("Selected.TCheckbutton", background="#dbeafe")
        self._style.configure("Selected.TButton", background="#dbeafe")
        self._style.configure("Selected.TProgressbar", background="#93c5fd")

        self._canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self._container = ttk.Frame(self._canvas)
        self._vsb = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._hsb = ttk.Scrollbar(self, orient="horizontal", command=self._canvas.xview)
        self._canvas.configure(yscrollcommand=self._vsb.set, xscrollcommand=self._hsb.set)

        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._vsb.grid(row=0, column=1, sticky="ns")
        self._hsb.grid(row=1, column=0, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._canvas.create_window((0, 0), window=self._container, anchor="nw")
        self._container.bind("<Configure>", self._on_container_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        self._build_header()
        self._build_rows()

    def _on_container_configure(self, _event: tk.Event) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self._canvas.itemconfig("all", width=event.width)

    def _build_header(self) -> None:
        for col_index, col in enumerate(self._columns):
            header = ttk.Button(
                self._container,
                text=col.get("label", col["key"]),
                command=lambda k=col["key"]: self._toggle_sort(k),
            )
            header.grid(row=0, column=col_index, sticky="nsew", padx=4, pady=4)
            self._container.grid_columnconfigure(col_index, weight=col.get("weight", 1))

    def _build_rows(self) -> None:
        for row_index, row in enumerate(self._rows, start=1):
            row_id = row.get("id", str(row_index))
            self._row_widgets[row_id] = []
            for col_index, col in enumerate(self._columns):
                cell_key = f"{row_id}::{col['key']}"
                widget = self._make_cell_widget(self._container, row, col, cell_key)
                widget.grid(row=row_index, column=col_index, sticky="nsew", padx=4, pady=3)
                self._bind_row_select(widget, row_id)
                self._row_widgets[row_id].append(widget)

    def _make_cell_widget(
        self, parent: ttk.Frame, row: RowSpec, col: ColumnSpec, cell_key: str
    ) -> tk.Widget:
        col_type = col.get("type", "label")
        value = row.get("values", {}).get(col["key"], "")

        if col_type == "button":
            text = str(value) if value else col.get("label", "Action")
            return ttk.Button(parent, text=text, command=lambda r=row: self._on_action(r))

        if col_type == "checkbutton":
            var = tk.BooleanVar(value=bool(value))
            self._cell_vars[cell_key] = var
            return ttk.Checkbutton(parent, variable=var)

        if col_type == "entry":
            var = tk.StringVar(value=str(value))
            self._cell_vars[cell_key] = var
            return ttk.Entry(parent, textvariable=var)

        if col_type == "entry_ro":
            var = tk.StringVar(value=str(value))
            self._cell_vars[cell_key] = var
            entry = ttk.Entry(parent, textvariable=var, state="readonly")
            return entry

        if col_type == "optionmenu":
            options = col.get("options", [])
            initial = value if value in options else (options[0] if options else "")
            var = tk.StringVar(value=str(initial))
            self._cell_vars[cell_key] = var
            return ttk.OptionMenu(parent, var, var.get(), *options)

        if col_type == "combobox":
            options = col.get("options", [])
            var = tk.StringVar(value=str(value))
            self._cell_vars[cell_key] = var
            return ttk.Combobox(parent, textvariable=var, values=options, state="normal")

        if col_type == "spinbox":
            var = tk.StringVar(value=str(value))
            self._cell_vars[cell_key] = var
            return tk.Spinbox(
                parent,
                from_=col.get("from_", 0),
                to=col.get("to", 100),
                increment=col.get("step", 1),
                textvariable=var,
                width=6,
            )

        if col_type == "label":
            return ttk.Label(parent, text=str(value), anchor="w")

        if col_type == "progress":
            var = tk.IntVar(value=int(value) if str(value).isdigit() else 0)
            self._cell_vars[cell_key] = var
            return ttk.Progressbar(parent, value=var.get(), maximum=100)

        return ttk.Label(parent, text=str(value), anchor="w")

    def _on_action(self, row: RowSpec) -> None:
        row_id = row.get("id", "")
        print(f"Action clicked: {row_id}")

    def _bind_row_select(self, widget: tk.Widget, row_id: str) -> None:
        widget.bind("<Button-1>", lambda _e, r=row_id: self.select_row(r), add="+")

    def select_row(self, row_id: str) -> None:
        if self._selected_row_id == row_id:
            return
        if self._selected_row_id:
            self._apply_row_style(self._selected_row_id, selected=False)
        self._selected_row_id = row_id
        self._apply_row_style(row_id, selected=True)

    def _apply_row_style(self, row_id: str, selected: bool) -> None:
        widgets = self._row_widgets.get(row_id, [])
        for widget in widgets:
            if isinstance(widget, ttk.Entry):
                widget.configure(style="Selected.TEntry" if selected else "TEntry")
            elif isinstance(widget, ttk.Combobox):
                widget.configure(style="Selected.TCombobox" if selected else "TCombobox")
            elif isinstance(widget, ttk.Checkbutton):
                widget.configure(style="Selected.TCheckbutton" if selected else "TCheckbutton")
            elif isinstance(widget, ttk.Button):
                widget.configure(style="Selected.TButton" if selected else "TButton")
            elif isinstance(widget, ttk.Label):
                widget.configure(style="Selected.TLabel" if selected else "TLabel")
            elif isinstance(widget, ttk.Progressbar):
                widget.configure(style="Selected.TProgressbar" if selected else "TProgressbar")
            elif isinstance(widget, tk.Spinbox):
                widget.configure(background="#dbeafe" if selected else "white")

    def _toggle_sort(self, key: str) -> None:
        ascending = not self._sort_state.get(key, True)
        self._sort_state[key] = ascending
        self._sort_rows(key, ascending)

    def _sort_rows(self, key: str, ascending: bool) -> None:
        rows = list(self._rows)

        def get_value(row: RowSpec) -> Any:
            row_id = row.get("id", "")
            cell_key = f"{row_id}::{key}"
            var = self._cell_vars.get(cell_key)
            if var is not None:
                return var.get()
            return row.get("values", {}).get(key, "")

        rows.sort(key=get_value, reverse=not ascending)
        self._rows = rows
        for child in self._container.winfo_children():
            child.destroy()
        self._row_widgets.clear()
        self._build_header()
        self._build_rows()

    def add_row(self, values: Optional[Dict[str, Any]] = None) -> None:
        values = values or {}
        new_id = f"row-{len(self._rows) + 1}"
        row: RowSpec = {"id": new_id, "values": values}
        self._rows.append(row)
        for child in self._container.winfo_children():
            child.destroy()
        self._row_widgets.clear()
        self._build_header()
        self._build_rows()

    def remove_selected(self) -> None:
        if not self._selected_row_id:
            return
        self._rows = [r for r in self._rows if r.get("id") != self._selected_row_id]
        self._selected_row_id = None
        for child in self._container.winfo_children():
            child.destroy()
        self._row_widgets.clear()
        self._build_header()
        self._build_rows()


def build_columns() -> List[ColumnSpec]:
    return [
        {"key": "action", "label": "Button", "type": "button", "weight": 1},
        {"key": "flag", "label": "Checkbutton", "type": "checkbutton", "weight": 1},
        {"key": "name", "label": "Entry", "type": "entry", "weight": 2},
        {"key": "code", "label": "Entry (Read Only)", "type": "entry_ro", "weight": 2},
        {"key": "status", "label": "Label", "type": "label", "weight": 2},
        {
            "key": "choice",
            "label": "OptionMenu",
            "type": "optionmenu",
            "options": ["A", "B", "C"],
            "weight": 1,
        },
        {
            "key": "combo",
            "label": "Combobox",
            "type": "combobox",
            "options": ["Alpha", "Beta", "Gamma"],
            "weight": 2,
        },
        {"key": "count", "label": "Spinbox", "type": "spinbox", "from_": 0, "to": 20, "weight": 1},
        {"key": "progress", "label": "Progress", "type": "progress", "weight": 2},
    ]


def build_rows() -> List[RowSpec]:
    return [
        {
            "id": "row-1",
            "values": {
                "action": "Open",
                "flag": True,
                "name": "Alice",
                "code": "A-001",
                "status": "Active",
                "choice": "A",
                "combo": "Alpha",
                "count": 3,
                "progress": 70,
            },
        },
        {
            "id": "row-2",
            "values": {
                "action": "Edit",
                "flag": False,
                "name": "Bob",
                "code": "B-015",
                "status": "Pending",
                "choice": "B",
                "combo": "Beta",
                "count": 8,
                "progress": 40,
            },
        },
        {
            "id": "row-3",
            "values": {
                "action": "View",
                "flag": True,
                "name": "Cara",
                "code": "C-023",
                "status": "Inactive",
                "choice": "C",
                "combo": "Gamma",
                "count": 1,
                "progress": 90,
            },
        },
    ]


def main() -> None:
    root = tk.Tk()
    root.title("Widget Table (Generic)")
    root.geometry("1100x460")

    toolbar = ttk.Frame(root, padding=(10, 10, 10, 0))
    toolbar.pack(fill="x")

    table = WidgetTable(root, build_columns(), build_rows(), padding=10)
    table.pack(fill="both", expand=True)

    def on_add() -> None:
        table.add_row(
            {
                "action": "New",
                "flag": False,
                "name": "",
                "code": "NEW",
                "status": "Draft",
                "choice": "A",
                "combo": "",
                "count": 0,
                "progress": 0,
            }
        )

    def on_remove() -> None:
        table.remove_selected()

    ttk.Button(toolbar, text="Add Row", command=on_add).pack(side="left")
    ttk.Button(toolbar, text="Remove Row", command=on_remove).pack(side="left", padx=(8, 0))

    root.mainloop()


if __name__ == "__main__":
    main()

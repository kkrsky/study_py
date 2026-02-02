"""Generic table + form editor (Tkinter, Python 3.9).

Run: python table_form_editor.py
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Iterable, List, Optional


ColumnSpec = Dict[str, Any]
RowSpec = Dict[str, Any]
FieldSpec = Dict[str, Any]


class TableFormEditor(ttk.Frame):
    def __init__(
        self,
        master: tk.Widget,
        columns: Iterable[ColumnSpec],
        rows: Iterable[RowSpec],
        form_fields: Iterable[FieldSpec],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, *args, **kwargs)
        self._columns = list(columns)
        self._rows = list(rows)
        self._form_fields = list(form_fields)
        self._tree = ttk.Treeview(
            self,
            columns=[c["key"] for c in self._columns],
            show="headings",
            selectmode="browse",
        )
        self._vsb = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._hsb = ttk.Scrollbar(self, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=self._vsb.set, xscrollcommand=self._hsb.set)

        self._build_columns()
        self._layout()
        self.set_data(self._rows)

        self._tree.bind("<Button-1>", self._on_click)

    def _layout(self) -> None:
        self._tree.grid(row=0, column=0, sticky="nsew")
        self._vsb.grid(row=0, column=1, sticky="ns")
        self._hsb.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _build_columns(self) -> None:
        for col in self._columns:
            key = col["key"]
            self._tree.heading(key, text=col.get("label", key), anchor=col.get("anchor", "w"))
            self._tree.column(
                key,
                width=col.get("width", 120),
                minwidth=col.get("minwidth", 60),
                anchor=col.get("anchor", "w"),
                stretch=col.get("stretch", True),
            )

    def set_data(self, rows: Iterable[RowSpec]) -> None:
        for item in self._tree.get_children(""):
            self._tree.delete(item)
        for row in rows:
            values = [row.get("values", {}).get(c["key"], "") for c in self._columns]
            self._tree.insert("", "end", iid=row.get("id"), values=values)

    def _on_click(self, event: tk.Event) -> None:
        region = self._tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        row_id = self._tree.identify_row(event.y)
        col_id = self._tree.identify_column(event.x)
        if not row_id or not col_id:
            return
        col_index = int(col_id[1:]) - 1
        col_key = self._columns[col_index]["key"]
        if col_key == "action":
            self._open_form(row_id)

    def _open_form(self, row_id: str) -> None:
        row_values = self._get_row_values(row_id)
        FormDialog(self, "Edit Row", self._form_fields, row_values, lambda v: self._apply_form(row_id, v))

    def _apply_form(self, row_id: str, values: Dict[str, Any]) -> None:
        row = self._find_row(row_id)
        if row is None:
            return
        row["values"].update(values)
        self.set_data(self._rows)

    def _find_row(self, row_id: str) -> Optional[RowSpec]:
        for row in self._rows:
            if row.get("id") == row_id:
                return row
        return None

    def _get_row_values(self, row_id: str) -> Dict[str, Any]:
        row = self._find_row(row_id)
        if row is None:
            return {}
        return dict(row.get("values", {}))


class FormDialog(tk.Toplevel):
    def __init__(
        self,
        master: tk.Widget,
        title: str,
        fields: Iterable[FieldSpec],
        initial: Dict[str, Any],
        on_submit,
    ) -> None:
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self._fields = list(fields)
        self._vars: Dict[str, tk.Variable] = {}
        self._on_submit = on_submit

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        for i, field in enumerate(self._fields):
            key = field["key"]
            label = field.get("label", key)
            ftype = field.get("type", "string")
            ttk.Label(body, text=label).grid(row=i, column=0, sticky="w", padx=4, pady=4)
            widget = self._build_input(body, field, initial.get(key, ""))
            widget.grid(row=i, column=1, sticky="ew", padx=4, pady=4)

        body.columnconfigure(1, weight=1)

        actions = ttk.Frame(self, padding=(12, 0, 12, 12))
        actions.pack(fill="x")
        ttk.Button(actions, text="Cancel", command=self.destroy).pack(side="right")
        ttk.Button(actions, text="Apply", command=self._apply).pack(side="right", padx=(0, 8))

        self.grab_set()
        self.transient(master)

    def _build_input(self, parent: ttk.Frame, field: FieldSpec, value: Any) -> tk.Widget:
        key = field["key"]
        ftype = field.get("type", "string")

        if ftype == "bool":
            var = tk.BooleanVar(value=bool(value))
            self._vars[key] = var
            return ttk.Checkbutton(parent, variable=var)

        if ftype in ("option", "combo"):
            options = field.get("options", [])
            var = tk.StringVar(value=str(value))
            self._vars[key] = var
            state = "readonly" if ftype == "option" else "normal"
            return ttk.Combobox(parent, textvariable=var, values=options, state=state)

        if ftype == "int":
            var = tk.StringVar(value=str(value))
            self._vars[key] = var
            return ttk.Entry(parent, textvariable=var)

        var = tk.StringVar(value=str(value))
        self._vars[key] = var
        return ttk.Entry(parent, textvariable=var)

    def _apply(self) -> None:
        values: Dict[str, Any] = {}
        for field in self._fields:
            key = field["key"]
            ftype = field.get("type", "string")
            raw = self._vars[key].get()
            if ftype == "bool":
                values[key] = bool(raw)
            elif ftype == "int":
                try:
                    values[key] = int(raw)
                except ValueError:
                    values[key] = raw
            else:
                values[key] = raw
        self._on_submit(values)
        self.destroy()


def build_columns() -> List[ColumnSpec]:
    return [
        {"key": "id", "label": "ID", "width": 60, "anchor": "e"},
        {"key": "title", "label": "Title", "width": 200},
        {"key": "category", "label": "Category", "width": 120},
        {"key": "status", "label": "Status", "width": 120},
        {"key": "active", "label": "Active", "width": 80, "anchor": "center"},
        {"key": "qty", "label": "Qty", "width": 80, "anchor": "e"},
        {"key": "action", "label": "Action", "width": 90, "anchor": "center"},
    ]


def build_rows() -> List[RowSpec]:
    return [
        {
            "id": "row-1",
            "values": {
                "id": 1,
                "title": "Buy apples",
                "category": "Food",
                "status": "New",
                "active": True,
                "qty": 10,
                "action": "Edit",
            },
        },
        {
            "id": "row-2",
            "values": {
                "id": 2,
                "title": "Make coffee",
                "category": "Drink",
                "status": "Hold",
                "active": True,
                "qty": 1,
                "action": "Edit",
            },
        },
    ]


def build_form_fields() -> List[FieldSpec]:
    return [
        {"key": "title", "label": "Title", "type": "string"},
        {
            "key": "category",
            "label": "Category",
            "type": "combo",
            "options": ["Food", "Drink", "Daily", "Work", "Hobby"],
        },
        {
            "key": "status",
            "label": "Status",
            "type": "option",
            "options": ["New", "Hold", "Done", "Canceled"],
        },
        {"key": "active", "label": "Active", "type": "bool"},
        {"key": "qty", "label": "Qty", "type": "int"},
    ]


def main() -> None:
    root = tk.Tk()
    root.title("Table + Form Editor (Generic)")
    root.geometry("900x460")

    app = TableFormEditor(root, build_columns(), build_rows(), build_form_fields(), padding=10)
    app.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()

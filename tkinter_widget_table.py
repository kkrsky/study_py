"""Treeview-based, sortable, editable widget table (Python 3.9).

Run: python tkinter_widget_table.py
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Iterable, List, Optional, Tuple


ColumnSpec = Dict[str, Any]
RowSpec = Dict[str, Any]


class EditableSortableTable(ttk.Frame):
    """Treeview table with sortable headers and type-aware editors."""

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
        self._sort_state: Dict[str, bool] = {}

        self._tree = ttk.Treeview(
            self,
            columns=[c["key"] for c in self._columns],
            show="headings",
            selectmode="browse",
        )
        self._vsb = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._hsb = ttk.Scrollbar(self, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=self._vsb.set, xscrollcommand=self._hsb.set)

        self._editor: Optional[tk.Widget] = None
        self._editing: Optional[Tuple[str, str]] = None

        self._build_columns()
        self._layout()
        self._apply_tags()
        self.set_data(self._rows)

        self._tree.bind("<Double-1>", self._on_double_click)
        self._tree.bind("<Button-1>", self._on_single_click)

    def _layout(self) -> None:
        self._tree.grid(row=0, column=0, sticky="nsew")
        self._vsb.grid(row=0, column=1, sticky="ns")
        self._hsb.grid(row=1, column=0, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _build_columns(self) -> None:
        for col in self._columns:
            key = col["key"]
            self._tree.heading(
                key,
                text=col.get("label", key),
                anchor=col.get("anchor", "w"),
                command=lambda k=key: self._toggle_sort(k),
            )
            self._tree.column(
                key,
                width=col.get("width", 140),
                minwidth=col.get("minwidth", 60),
                anchor=col.get("anchor", "w"),
                stretch=col.get("stretch", True),
            )

    def _apply_tags(self) -> None:
        self._tree.tag_configure("odd", background="#f7f7f7")
        self._tree.tag_configure("even", background="#ffffff")

    def set_data(self, rows: Iterable[RowSpec]) -> None:
        for item in self._tree.get_children(""):
            self._tree.delete(item)
        for idx, row in enumerate(rows):
            values = [row.get("values", {}).get(c["key"], "") for c in self._columns]
            tag = "even" if idx % 2 == 0 else "odd"
            self._tree.insert("", "end", iid=row.get("id"), values=values, tags=(tag,))

    def add_row(self, values: Optional[Dict[str, Any]] = None) -> None:
        values = values or {}
        new_id = f"row-{len(self._rows) + 1}"
        row: RowSpec = {"id": new_id, "values": values}
        self._rows.append(row)
        self.set_data(self._rows)

    def remove_selected(self) -> None:
        selection = self._tree.selection()
        if not selection:
            return
        row_id = selection[0]
        self._rows = [r for r in self._rows if r.get("id") != row_id]
        self.set_data(self._rows)

    def _toggle_sort(self, key: str) -> None:
        ascending = not self._sort_state.get(key, True)
        self._sort_state[key] = ascending
        col = self._get_column(key)
        if not col:
            return
        col_type = col.get("type", "string")

        def sort_key(item_id: str) -> Any:
            value = self._tree.set(item_id, key)
            return self._cast_value(value, col_type)

        items = list(self._tree.get_children(""))
        items.sort(key=sort_key, reverse=not ascending)
        for idx, item_id in enumerate(items):
            self._tree.move(item_id, "", idx)
            self._tree.item(item_id, tags=("even" if idx % 2 == 0 else "odd",))

    def _get_column(self, key: str) -> Optional[ColumnSpec]:
        for col in self._columns:
            if col["key"] == key:
                return col
        return None

    def _cast_value(self, value: str, col_type: str) -> Any:
        if col_type == "int":
            try:
                return int(value)
            except ValueError:
                return 0
        if col_type == "float":
            try:
                return float(value)
            except ValueError:
                return 0.0
        if col_type == "bool":
            return value.lower() in ("1", "true", "yes", "y", "on")
        return value.lower()

    def _on_single_click(self, event: tk.Event) -> None:
        if self._editor and self._is_click_inside_editor(event):
            return
        self._cancel_editor()

    def _on_double_click(self, event: tk.Event) -> None:
        region = self._tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        row_id = self._tree.identify_row(event.y)
        col_id = self._tree.identify_column(event.x)
        if not row_id or not col_id:
            return
        col_index = int(col_id[1:]) - 1
        if col_index < 0:
            return
        col = self._columns[col_index]
        self._edit_cell(row_id, col, col_index)

    def _edit_cell(self, row_id: str, col: ColumnSpec, col_index: int) -> None:
        self._cancel_editor()
        x, y, width, height = self._tree.bbox(row_id, f"#{col_index + 1}")
        value = self._tree.set(row_id, col["key"])
        editor = self._create_editor(col, value)
        if editor is None:
            return
        editor.place(in_=self._tree, x=x, y=y, width=width, height=height)
        editor.focus_set()
        if isinstance(editor, ttk.Entry):
            editor.selection_range(0, "end")
        self._editor = editor
        self._editing = (row_id, col["key"])

    def _create_editor(self, col: ColumnSpec, value: str) -> Optional[tk.Widget]:
        col_type = col.get("type", "string")
        if col_type in ("string", "int", "float", "label"):
            var = tk.StringVar(value=str(value))
            entry = ttk.Entry(self._tree, textvariable=var)
            entry.bind("<Return>", self._commit_editor)
            entry.bind("<Escape>", lambda _e: self._cancel_editor())
            entry.bind("<FocusOut>", self._commit_editor)
            return entry
        if col_type == "readonly":
            var = tk.StringVar(value=str(value))
            entry = ttk.Entry(self._tree, textvariable=var, state="readonly")
            entry.bind("<Escape>", lambda _e: self._cancel_editor())
            entry.bind("<FocusOut>", self._commit_editor)
            return entry
        if col_type == "bool":
            value_str = str(value).lower()
            options = ("true", "false")
            if value_str not in options:
                value_str = "false"
            var = tk.StringVar(value=value_str)
            combo = ttk.Combobox(
                self._tree, textvariable=var, values=options, state="readonly"
            )
            combo.bind("<<ComboboxSelected>>", self._commit_editor)
            combo.bind("<FocusOut>", self._commit_editor)
            return combo
        if col_type in ("option", "combo"):
            values = [str(v) for v in col.get("options", [])]
            value_str = str(value)
            if value_str and value_str not in values:
                values = [value_str] + values
            var = tk.StringVar(value=value_str)
            combo = ttk.Combobox(self._tree, textvariable=var, values=values, state="normal")
            combo.bind("<Return>", self._commit_editor)
            combo.bind("<<ComboboxSelected>>", self._commit_editor)
            combo.bind("<FocusOut>", self._commit_editor)
            return combo
        if col_type == "spin":
            var = tk.StringVar(value=str(value))
            spin = tk.Spinbox(
                self._tree,
                from_=col.get("from_", 0),
                to=col.get("to", 100),
                increment=col.get("step", 1),
                textvariable=var,
            )
            spin.bind("<Return>", self._commit_editor)
            spin.bind("<Escape>", lambda _e: self._cancel_editor())
            spin.bind("<FocusOut>", self._commit_editor)
            return spin
        if col_type == "button":
            btn = ttk.Button(self._tree, text=str(value), command=lambda: self._on_action())
            return btn
        return None

    def _commit_editor(self, _event: Optional[tk.Event] = None) -> None:
        if not self._editor or not self._editing:
            return
        row_id, key = self._editing
        value = ""
        if isinstance(self._editor, ttk.Entry):
            value = self._editor.get()
        elif isinstance(self._editor, ttk.Combobox):
            value = self._editor.get()
        elif isinstance(self._editor, tk.Spinbox):
            value = self._editor.get()
        self._tree.set(row_id, key, value)
        self._cancel_editor()

    def _cancel_editor(self) -> None:
        if self._editor:
            self._editor.destroy()
        self._editor = None
        self._editing = None

    def _is_click_inside_editor(self, event: tk.Event) -> bool:
        if not self._editor:
            return False
        widget = self._editor.winfo_containing(event.x_root, event.y_root)
        return widget is self._editor

    def _on_action(self) -> None:
        selection = self._tree.selection()
        if not selection:
            return
        row_id = selection[0]
        print(f"Action clicked: {row_id}")


def build_columns() -> List[ColumnSpec]:
    return [
        {"key": "action", "label": "Button", "type": "button", "width": 100},
        {"key": "flag", "label": "Checkbutton", "type": "bool", "width": 120},
        {"key": "name", "label": "Entry", "type": "string", "width": 150},
        {"key": "code", "label": "Entry (Read Only)", "type": "readonly", "width": 150},
        {"key": "status", "label": "Label", "type": "label", "width": 120},
        {
            "key": "choice",
            "label": "OptionMenu",
            "type": "option",
            "options": ["A", "B", "C"],
            "width": 120,
        },
        {
            "key": "combo",
            "label": "Combobox",
            "type": "combo",
            "options": ["Alpha", "Beta", "Gamma"],
            "width": 140,
        },
        {"key": "count", "label": "Spinbox", "type": "spin", "from_": 0, "to": 20, "width": 110},
    ]


def build_rows() -> List[RowSpec]:
    return [
        {
            "id": "row-1",
            "values": {
                "action": "Open",
                "flag": "true",
                "name": "Alice",
                "code": "A-001",
                "status": "Active",
                "choice": "A",
                "combo": "Alpha",
                "count": 3,
            },
        },
        {
            "id": "row-2",
            "values": {
                "action": "Edit",
                "flag": "false",
                "name": "Bob",
                "code": "B-015",
                "status": "Pending",
                "choice": "B",
                "combo": "Beta",
                "count": 8,
            },
        },
        {
            "id": "row-3",
            "values": {
                "action": "View",
                "flag": "true",
                "name": "Cara",
                "code": "C-023",
                "status": "Inactive",
                "choice": "C",
                "combo": "Gamma",
                "count": 1,
            },
        },
    ]


def main() -> None:
    root = tk.Tk()
    root.title("Widget Table (Treeview)")
    root.geometry("1100x460")

    toolbar = ttk.Frame(root, padding=(10, 10, 10, 0))
    toolbar.pack(fill="x")

    table = EditableSortableTable(root, build_columns(), build_rows(), padding=10)
    table.pack(fill="both", expand=True)

    def on_add() -> None:
        table.add_row(
            {
                "action": "New",
                "flag": "false",
                "name": "",
                "code": "NEW",
                "status": "Draft",
                "choice": "A",
                "combo": "",
                "count": 0,
            }
        )

    def on_remove() -> None:
        table.remove_selected()

    ttk.Button(toolbar, text="Add Row", command=on_add).pack(side="left")
    ttk.Button(toolbar, text="Remove Row", command=on_remove).pack(side="left", padx=(8, 0))

    root.mainloop()


if __name__ == "__main__":
    main()

"""Tabbed Tkinter demo with a tree table and a sortable, editable table.

Run: python tabbed_tree_and_table.py
Python: 3.9
"""

from __future__ import annotations

import datetime as dt
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Iterable, List, Optional, Tuple


ColumnSpec = Dict[str, Any]
RowSpec = Dict[str, Any]


class TreeTable(ttk.Frame):
    """Reusable tree table widget."""

    def __init__(
        self,
        master: tk.Widget,
        columns: Iterable[ColumnSpec],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, *args, **kwargs)
        self._columns = list(columns)

        self._tree = ttk.Treeview(
            self,
            columns=[c["key"] for c in self._columns],
            show="tree headings",
            selectmode="browse",
        )
        self._vsb = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._hsb = ttk.Scrollbar(self, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=self._vsb.set, xscrollcommand=self._hsb.set)

        self._build_columns()
        self._layout()
        self._apply_tags()

    def _layout(self) -> None:
        self._tree.grid(row=0, column=0, sticky="nsew")
        self._vsb.grid(row=0, column=1, sticky="ns")
        self._hsb.grid(row=1, column=0, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _build_columns(self) -> None:
        self._tree.heading("#0", text="Item", anchor="w")
        self._tree.column("#0", width=220, anchor="w", stretch=True)

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

    def _apply_tags(self) -> None:
        self._tree.tag_configure("odd", background="#f7f7f7")
        self._tree.tag_configure("even", background="#ffffff")

    def clear(self) -> None:
        for item in self._tree.get_children(""):
            self._tree.delete(item)

    def set_data(self, rows: Iterable[RowSpec]) -> None:
        self.clear()
        self._insert_rows("", rows, start_index=0)

    def _insert_rows(self, parent: str, rows: Iterable[RowSpec], start_index: int) -> int:
        index = start_index
        for row in rows:
            row_id = row.get("id")
            text = row.get("text", "")
            values = [row.get("values", {}).get(c["key"], "") for c in self._columns]
            tag = "even" if index % 2 == 0 else "odd"

            item_id = self._tree.insert(
                parent,
                "end",
                iid=row_id if row_id else None,
                text=text,
                values=values,
                tags=(tag,),
                open=row.get("open", False),
            )

            children = row.get("children") or []
            if children:
                index = self._insert_rows(item_id, children, index + 1)
            else:
                index += 1
        return index

    def expand_all(self) -> None:
        for item in self._tree.get_children(""):
            self._set_open_recursive(item, True)

    def collapse_all(self) -> None:
        for item in self._tree.get_children(""):
            self._set_open_recursive(item, False)

    def _set_open_recursive(self, item: str, is_open: bool) -> None:
        self._tree.item(item, open=is_open)
        for child in self._tree.get_children(item):
            self._set_open_recursive(child, is_open)


class EditableSortableTable(ttk.Frame):
    """Sortable, editable table with type-aware editors."""

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
                width=col.get("width", 120),
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
        if col_type == "date":
            try:
                return dt.datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                return dt.date.min
        if col_type == "datetime":
            try:
                return dt.datetime.strptime(value, "%Y-%m-%d %H:%M")
            except ValueError:
                return dt.datetime.min
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
        if col_type in ("string", "int", "float", "date", "datetime"):
            var = tk.StringVar(value=str(value))
            entry = ttk.Entry(self._tree, textvariable=var)
            entry.bind("<Return>", self._commit_editor)
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
        if col_type in ("combo", "dropdown"):
            values = [str(v) for v in col.get("options", [])]
            value_str = str(value)
            if value_str and value_str not in values:
                values = [value_str] + values
            var = tk.StringVar(value=value_str)
            combo = ttk.Combobox(self._tree, textvariable=var, values=values, state="readonly")
            combo.bind("<<ComboboxSelected>>", self._commit_editor)
            combo.bind("<FocusOut>", self._commit_editor)
            return combo
        return None

    def _is_click_inside_editor(self, event: tk.Event) -> bool:
        if not self._editor:
            return False
        widget = self._editor.winfo_containing(event.x_root, event.y_root)
        return widget is self._editor

    def _commit_editor(self, _event: Optional[tk.Event] = None) -> None:
        if not self._editor or not self._editing:
            return
        row_id, key = self._editing
        value = ""
        if isinstance(self._editor, ttk.Entry):
            value = self._editor.get()
        elif isinstance(self._editor, ttk.Combobox):
            value = self._editor.get()
        self._tree.set(row_id, key, value)
        self._cancel_editor()

    def _cancel_editor(self) -> None:
        if self._editor:
            self._editor.destroy()
        self._editor = None
        self._editing = None


def build_tree_sample_data() -> List[RowSpec]:
    return [
        {
            "id": "dept-1",
            "text": "Engineering",
            "values": {"head": "Aki", "budget": 3200000, "status": "Active"},
            "open": True,
            "children": [
                {
                    "id": "team-1",
                    "text": "Platform",
                    "values": {"head": "Ken", "budget": 1400000, "status": "Active"},
                    "children": [
                        {
                            "id": "proj-1",
                            "text": "Auth Revamp",
                            "values": {"head": "Mina", "budget": 350000, "status": "On Track"},
                        },
                        {
                            "id": "proj-2",
                            "text": "Data Lake",
                            "values": {"head": "Sora", "budget": 500000, "status": "At Risk"},
                        },
                    ],
                },
                {
                    "id": "team-2",
                    "text": "Product",
                    "values": {"head": "Hana", "budget": 1100000, "status": "Active"},
                    "children": [
                        {
                            "id": "proj-3",
                            "text": "Mobile Refresh",
                            "values": {"head": "Rui", "budget": 400000, "status": "On Hold"},
                        },
                    ],
                },
            ],
        },
        {
            "id": "dept-2",
            "text": "Sales",
            "values": {"head": "Tomo", "budget": 2100000, "status": "Active"},
            "children": [
                {
                    "id": "team-3",
                    "text": "Domestic",
                    "values": {"head": "Nori", "budget": 900000, "status": "Active"},
                    "children": [
                        {
                            "id": "proj-4",
                            "text": "Retail Expansion",
                            "values": {"head": "Aya", "budget": 250000, "status": "On Track"},
                        }
                    ],
                },
                {
                    "id": "team-4",
                    "text": "International",
                    "values": {"head": "Leo", "budget": 1200000, "status": "Active"},
                },
            ],
        },
    ]


def build_table_columns() -> List[ColumnSpec]:
    return [
        {"key": "name", "label": "Name", "type": "string", "width": 160},
        {"key": "age", "label": "Age", "type": "int", "anchor": "e", "width": 80},
        {"key": "score", "label": "Score", "type": "float", "anchor": "e", "width": 90},
        {"key": "active", "label": "Active", "type": "bool", "width": 90},
        {"key": "date", "label": "Date", "type": "date", "width": 110},
        {"key": "timestamp", "label": "DateTime", "type": "datetime", "width": 140},
        {
            "key": "role",
            "label": "Role (Combo)",
            "type": "combo",
            "options": ["Engineer", "Designer", "PM", "Sales"],
            "width": 140,
        },
        {
            "key": "region",
            "label": "Region (Dropdown)",
            "type": "dropdown",
            "options": ["APAC", "EMEA", "AMER"],
            "width": 140,
        },
    ]


def build_table_rows() -> List[RowSpec]:
    return [
        {
            "id": "row-1",
            "values": {
                "name": "Aki",
                "age": "29",
                "score": "88.5",
                "active": "true",
                "date": "2026-02-01",
                "timestamp": "2026-02-01 09:30",
                "role": "Engineer",
                "region": "APAC",
            },
        },
        {
            "id": "row-2",
            "values": {
                "name": "Hana",
                "age": "35",
                "score": "92.0",
                "active": "false",
                "date": "2026-01-28",
                "timestamp": "2026-01-28 15:45",
                "role": "Designer",
                "region": "EMEA",
            },
        },
        {
            "id": "row-3",
            "values": {
                "name": "Leo",
                "age": "41",
                "score": "76.2",
                "active": "true",
                "date": "2026-02-02",
                "timestamp": "2026-02-02 11:10",
                "role": "Sales",
                "region": "AMER",
            },
        },
        {
            "id": "row-4",
            "values": {
                "name": "Mina",
                "age": "27",
                "score": "84.8",
                "active": "true",
                "date": "2026-01-22",
                "timestamp": "2026-01-22 08:05",
                "role": "PM",
                "region": "APAC",
            },
        },
    ]


def main() -> None:
    root = tk.Tk()
    root.title("Tabbed Tree + Sortable Table")
    root.geometry("1000x620")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    tree_tab = ttk.Frame(notebook)
    table_tab = ttk.Frame(notebook)

    notebook.add(tree_tab, text="Tree Table")
    notebook.add(table_tab, text="Editable Table")

    tree_columns = [
        {"key": "head", "label": "Lead", "width": 140},
        {"key": "budget", "label": "Budget", "width": 120, "anchor": "e"},
        {"key": "status", "label": "Status", "width": 140},
    ]

    tree_table = TreeTable(tree_tab, tree_columns)
    tree_table.pack(fill="both", expand=True, padx=12, pady=12)
    tree_table.set_data(build_tree_sample_data())

    header = ttk.Label(
        table_tab, text="Sortable & Editable Table (MECE Types)", font=("Segoe UI", 12, "bold")
    )
    header.pack(side="top", anchor="w", padx=12, pady=(12, 6))

    table = EditableSortableTable(table_tab, build_table_columns(), build_table_rows())
    table.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    root.mainloop()


if __name__ == "__main__":
    main()

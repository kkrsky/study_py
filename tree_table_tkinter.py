"""Tree-structure, collapsible table using Tkinter (Python 3.9).

Run: python tree_table_tkinter.py
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Iterable, List, Optional


ColumnSpec = Dict[str, Any]
RowSpec = Dict[str, Any]


class TreeTable(ttk.Frame):
    """Reusable tree table widget.

    RowSpec format:
      {
        "id": "unique_id",
        "text": "Tree label",
        "values": {"col_key": value, ...},
        "children": [RowSpec, ...]
      }
    """

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
        # Tree column (#0)
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

    def search(self, keyword: str) -> Optional[str]:
        if not keyword:
            return None
        needle = keyword.lower()
        for item in self._tree.get_children(""):
            found = self._search_recursive(item, needle)
            if found:
                self._tree.selection_set(found)
                self._tree.see(found)
                return found
        return None

    def _search_recursive(self, item: str, needle: str) -> Optional[str]:
        text = str(self._tree.item(item, "text")).lower()
        values = " ".join(str(v) for v in self._tree.item(item, "values")).lower()
        if needle in text or needle in values:
            return item
        for child in self._tree.get_children(item):
            found = self._search_recursive(child, needle)
            if found:
                return found
        return None


def build_sample_data() -> List[RowSpec]:
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


def main() -> None:
    root = tk.Tk()
    root.title("Tree Table Sample")
    root.geometry("900x520")

    columns = [
        {"key": "head", "label": "Lead", "width": 140},
        {"key": "budget", "label": "Budget", "width": 120, "anchor": "e"},
        {"key": "status", "label": "Status", "width": 140},
    ]

    header = ttk.Frame(root)
    header.pack(side="top", fill="x", padx=12, pady=8)

    ttk.Label(header, text="Organization Overview", font=("Segoe UI", 14, "bold")).pack(
        side="left"
    )

    controls = ttk.Frame(root)
    controls.pack(side="top", fill="x", padx=12, pady=(0, 8))

    ttk.Label(controls, text="Search:").pack(side="left")
    search_var = tk.StringVar()
    search_entry = ttk.Entry(controls, textvariable=search_var, width=28)
    search_entry.pack(side="left", padx=(6, 12))

    table = TreeTable(root, columns)
    table.pack(side="top", fill="both", expand=True, padx=12, pady=8)

    table.set_data(build_sample_data())

    def on_search() -> None:
        table.search(search_var.get().strip())

    def on_expand() -> None:
        table.expand_all()

    def on_collapse() -> None:
        table.collapse_all()

    ttk.Button(controls, text="Search", command=on_search).pack(side="left")
    ttk.Button(controls, text="Expand All", command=on_expand).pack(side="left", padx=(12, 0))
    ttk.Button(controls, text="Collapse All", command=on_collapse).pack(
        side="left", padx=(6, 0)
    )

    search_entry.bind("<Return>", lambda _event: on_search())

    root.mainloop()


if __name__ == "__main__":
    main()

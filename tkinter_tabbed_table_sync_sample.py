import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from typing import Dict, List, Optional


TAB_COLUMNS = ("id", "item", "qty", "price")
MAIN_COLUMNS = ("tab", "id", "item", "qty", "price")


class EditableTree(ttk.Treeview):
    """Treeview with basic double-click inline editing."""

    def __init__(self, parent: tk.Widget, columns: List[str], on_changed):
        super().__init__(parent, columns=columns, show="headings", selectmode="extended")
        self._on_changed = on_changed
        self._editor: Optional[tk.Entry] = None
        self._editing_target: Optional[tuple] = None
        self.bind("<Double-1>", self._begin_edit)
        self.bind("<Escape>", lambda _e: self._cancel_edit())

    def _begin_edit(self, event) -> None:
        region = self.identify("region", event.x, event.y)
        if region != "cell":
            return
        item_id = self.identify_row(event.y)
        col_id = self.identify_column(event.x)
        if not item_id or not col_id:
            return
        col_index = int(col_id.replace("#", "")) - 1
        bbox = self.bbox(item_id, column=col_id)
        if not bbox:
            return

        x, y, w, h = bbox
        values = list(self.item(item_id, "values"))
        current = str(values[col_index])

        self._cancel_edit()
        entry = tk.Entry(self)
        entry.insert(0, current)
        entry.place(x=x, y=y, width=w, height=h)
        entry.focus_set()
        entry.selection_range(0, tk.END)
        entry.bind("<Return>", lambda _e: self._commit_edit())
        entry.bind("<Escape>", lambda _e: self._cancel_edit())
        entry.bind("<FocusOut>", lambda _e: self._commit_edit())

        self._editor = entry
        self._editing_target = (item_id, col_index)

    def _commit_edit(self) -> None:
        if not self._editor or not self._editing_target:
            return
        item_id, col_index = self._editing_target
        new_value = self._editor.get()
        values = list(self.item(item_id, "values"))
        values[col_index] = new_value
        self.item(item_id, values=values)
        self._cancel_edit()
        self._on_changed()

    def _cancel_edit(self) -> None:
        if self._editor is not None:
            self._editor.destroy()
        self._editor = None
        self._editing_target = None


class TabTableFrame(ttk.Frame):
    """One tab with its own table and row operations."""

    def __init__(self, parent: tk.Widget, on_changed):
        super().__init__(parent, padding=8)
        self._on_changed = on_changed
        self._next_id = 1

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 6))
        ttk.Button(toolbar, text="行追加", command=self.add_row).pack(side="left")
        ttk.Button(toolbar, text="選択行削除", command=self.delete_selected).pack(side="left", padx=(6, 0))

        table_wrap = ttk.Frame(self)
        table_wrap.pack(fill="both", expand=True)
        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)

        self.table = EditableTree(table_wrap, list(TAB_COLUMNS), self._on_changed)
        self.table.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.table.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.table.configure(yscrollcommand=yscroll.set)

        self.table.heading("id", text="ID")
        self.table.heading("item", text="Item")
        self.table.heading("qty", text="Qty")
        self.table.heading("price", text="Price")

        self.table.column("id", width=60, anchor="e")
        self.table.column("item", width=180, anchor="w")
        self.table.column("qty", width=80, anchor="e")
        self.table.column("price", width=100, anchor="e")

    def add_row(self) -> None:
        row = (self._next_id, f"Item-{self._next_id}", 0, 0.0)
        self._next_id += 1
        self.table.insert("", "end", values=row)
        self._on_changed()

    def delete_selected(self) -> None:
        for item_id in self.table.selection():
            self.table.delete(item_id)
        self._on_changed()

    def get_rows(self) -> List[Dict[str, str]]:
        rows = []
        for item_id in self.table.get_children(""):
            values = list(self.table.item(item_id, "values"))
            rows.append(
                {
                    "id": str(values[0]) if len(values) > 0 else "",
                    "item": str(values[1]) if len(values) > 1 else "",
                    "qty": str(values[2]) if len(values) > 2 else "",
                    "price": str(values[3]) if len(values) > 3 else "",
                }
            )
        return rows


class TabbedTableSyncApp(ttk.Frame):
    """Generic sample app: dynamic tabs + per-tab table + main synchronized table."""

    def __init__(self, parent: tk.Tk):
        super().__init__(parent, padding=10)
        self.pack(fill="both", expand=True)

        self.tabs_by_id: Dict[str, TabTableFrame] = {}
        self._tab_seq = 1

        self._build_ui()
        self.add_tab("Default")

    def _build_ui(self) -> None:
        top = ttk.Frame(self)
        top.pack(fill="x", pady=(0, 8))

        ttk.Button(top, text="タブ追加", command=self._add_tab_dialog).pack(side="left")
        ttk.Button(top, text="タブ名編集", command=self._rename_current_tab).pack(side="left", padx=(6, 0))
        ttk.Button(top, text="タブ削除", command=self._delete_current_tab).pack(side="left", padx=(6, 0))

        body = ttk.Panedwindow(self, orient="vertical")
        body.pack(fill="both", expand=True)

        tab_area = ttk.Frame(body)
        main_area = ttk.Frame(body, padding=(0, 8, 0, 0))
        body.add(tab_area, weight=3)
        body.add(main_area, weight=2)

        self.notebook = ttk.Notebook(tab_area)
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", lambda _e: self.refresh_main_table())

        ttk.Label(main_area, text="メイン表（全タブのデータ同期表示）").pack(anchor="w")
        main_wrap = ttk.Frame(main_area)
        main_wrap.pack(fill="both", expand=True, pady=(4, 0))
        main_wrap.columnconfigure(0, weight=1)
        main_wrap.rowconfigure(0, weight=1)

        self.main_table = ttk.Treeview(main_wrap, columns=MAIN_COLUMNS, show="headings", selectmode="browse")
        self.main_table.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(main_wrap, orient="vertical", command=self.main_table.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.main_table.configure(yscrollcommand=yscroll.set)

        self.main_table.heading("tab", text="Tab")
        self.main_table.heading("id", text="ID")
        self.main_table.heading("item", text="Item")
        self.main_table.heading("qty", text="Qty")
        self.main_table.heading("price", text="Price")

        self.main_table.column("tab", width=140, anchor="w")
        self.main_table.column("id", width=60, anchor="e")
        self.main_table.column("item", width=220, anchor="w")
        self.main_table.column("qty", width=90, anchor="e")
        self.main_table.column("price", width=110, anchor="e")

    def _next_tab_id(self) -> str:
        tab_id = f"tab-{self._tab_seq}"
        self._tab_seq += 1
        return tab_id

    def _add_tab_dialog(self) -> None:
        name = simpledialog.askstring("タブ追加", "新しいタブ名を入力してください:", parent=self)
        if name is None:
            return
        name = name.strip()
        if not name:
            messagebox.showwarning("入力エラー", "タブ名を入力してください。", parent=self)
            return
        self.add_tab(name)

    def add_tab(self, tab_name: str) -> None:
        tab_id = self._next_tab_id()
        frame = TabTableFrame(self.notebook, self.refresh_main_table)
        self.tabs_by_id[tab_id] = frame
        self.notebook.add(frame, text=tab_name)
        self.notebook.select(frame)
        self.refresh_main_table()

    def _current_tab_widget(self) -> Optional[tk.Widget]:
        current = self.notebook.select()
        if not current:
            return None
        return self.nametowidget(current)

    def _rename_current_tab(self) -> None:
        current = self.notebook.select()
        if not current:
            return
        old_name = self.notebook.tab(current, "text")
        new_name = simpledialog.askstring("タブ名編集", "新しいタブ名:", initialvalue=old_name, parent=self)
        if new_name is None:
            return
        new_name = new_name.strip()
        if not new_name:
            messagebox.showwarning("入力エラー", "タブ名を入力してください。", parent=self)
            return
        self.notebook.tab(current, text=new_name)
        self.refresh_main_table()

    def _delete_current_tab(self) -> None:
        current_widget = self._current_tab_widget()
        if current_widget is None:
            return
        tab_name = self.notebook.tab(self.notebook.select(), "text")
        if not messagebox.askyesno("タブ削除", f"タブ '{tab_name}' を削除しますか？", parent=self):
            return

        # Remove from dict by object identity.
        remove_key = None
        for key, frame in self.tabs_by_id.items():
            if frame is current_widget:
                remove_key = key
                break
        if remove_key is not None:
            del self.tabs_by_id[remove_key]

        self.notebook.forget(current_widget)
        current_widget.destroy()
        self.refresh_main_table()

    def refresh_main_table(self) -> None:
        self.main_table.delete(*self.main_table.get_children(""))
        for tab_id, frame in self.tabs_by_id.items():
            tab_name = self._tab_name_from_frame(frame)
            for row in frame.get_rows():
                self.main_table.insert(
                    "",
                    "end",
                    values=(tab_name, row["id"], row["item"], row["qty"], row["price"]),
                )

    def _tab_name_from_frame(self, frame: TabTableFrame) -> str:
        for tab_id in self.notebook.tabs():
            if self.nametowidget(tab_id) is frame:
                return self.notebook.tab(tab_id, "text")
        return "(unknown)"


def main() -> None:
    root = tk.Tk()
    root.title("Tkinter Dynamic Tabs + Table Sync Sample")
    root.geometry("980x620")
    TabbedTableSyncApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

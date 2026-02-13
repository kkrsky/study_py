import tkinter as tk
from dataclasses import dataclass, field
from tkinter import ttk
from typing import Dict, List, Optional, Tuple

CHECK_ON = "[x]"
CHECK_OFF = "[ ]"


@dataclass(frozen=True)
class TagDefinition:
    """Category-aware tag definition."""

    key: str
    category: str
    name: str
    description: str


@dataclass
class RowData:
    """One table row."""

    id: int
    title: str
    category: str
    status: str
    tag_keys: List[str] = field(default_factory=list)
    notes: str = ""


class CategoryAwareTagTableDemo(ttk.Frame):
    """Demo table with category-aware duplicate tag names."""

    columns: Tuple[str, ...] = ("id", "title", "category", "status", "tags", "notes")

    def __init__(self, parent: tk.Misc):
        super().__init__(parent, padding=10)
        self.categories = ["Food", "Drink", "Daily", "Work", "Hobby"]
        self.statuses = ["New", "Hold", "Done", "Canceled"]
        self.done_required_tags = ("Food::Learning", "Drink::Learning")

        self.tag_definitions = [
            TagDefinition("Food::Learning", "Food", "Learning", "食材や料理に関する学習"),
            TagDefinition("Drink::Learning", "Drink", "Learning", "飲み物や抽出に関する学習"),
            TagDefinition("Food::Urgent", "Food", "Urgent", "優先度が高い食関連タスク"),
            TagDefinition("Drink::Home", "Drink", "Home", "自宅での飲料タスク"),
            TagDefinition("Work::FollowUp", "Work", "FollowUp", "後で確認が必要な業務タスク"),
        ]
        self.tag_by_key: Dict[str, TagDefinition] = {tag.key: tag for tag in self.tag_definitions}

        self.rows_by_iid: Dict[str, RowData] = {}
        self._editor: Optional[tk.Widget] = None
        self._editing_target: Optional[Tuple[str, str]] = None

        self._build_ui()
        self._insert_demo_rows()

    def _build_ui(self) -> None:
        top = ttk.Frame(self)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(
            top,
            text="Tags列は名前のみ表示。フォームではCategory付きで同名タグを識別できます。",
        ).pack(anchor="w")

        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True)
        wrap.columnconfigure(0, weight=1)
        wrap.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(wrap, columns=self.columns, show="headings", selectmode="browse", height=14)
        self.tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=yscroll.set)

        headings = {
            "id": "ID",
            "title": "Title",
            "category": "Category",
            "status": "Status",
            "tags": "Tags",
            "notes": "Notes",
        }
        widths = {"id": 60, "title": 180, "category": 120, "status": 120, "tags": 220, "notes": 260}
        anchors = {"id": "e", "title": "w", "category": "w", "status": "w", "tags": "w", "notes": "w"}
        for col in self.columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor=anchors[col], minwidth=60, stretch=(col in ("title", "tags", "notes")))

        self.message = ttk.Label(self, text="", anchor="w")
        self.message.pack(fill="x", pady=(6, 0))

        self.tree.bind("<Button-1>", self._on_click, add=True)
        self.tree.bind("<Double-1>", self._on_double_click, add=True)
        self.tree.bind("<Escape>", lambda _e: self._cancel_inline_edit(), add=True)

    def _insert_demo_rows(self) -> None:
        demo_rows = [
            RowData(1, "Buy apples", "Food", "New", ["Food::Urgent"], "From supermarket"),
            RowData(2, "Make coffee", "Drink", "Hold", ["Drink::Home"], "Try new beans"),
            RowData(3, "Done sample row", "Daily", "Done", [], "Done row forces two Learning tags"),
        ]
        for row in demo_rows:
            self._upsert_row(row)

    def _upsert_row(self, row: RowData) -> None:
        if row.status == "Done":
            self._ensure_done_required_tags(row)
        values = (
            row.id,
            row.title,
            row.category,
            row.status,
            self._format_tags_for_cell(row.tag_keys),
            row.notes,
        )
        iid = self.tree.insert("", "end", values=values)
        self.rows_by_iid[iid] = row

    def _format_tags_for_cell(self, tag_keys: List[str]) -> str:
        names = [self.tag_by_key[key].name for key in tag_keys if key in self.tag_by_key]
        if not names:
            return ""
        return f"{', '.join(names)}"

    def _ensure_done_required_tags(self, row: RowData) -> None:
        """Done row must always include Food::Learning and Drink::Learning."""
        for required_key in self.done_required_tags:
            if required_key not in row.tag_keys:
                row.tag_keys.append(required_key)

    def _refresh_row(self, item_id: str) -> None:
        row = self.rows_by_iid.get(item_id)
        if row is None:
            return
        if row.status == "Done":
            self._ensure_done_required_tags(row)
        self.tree.item(
            item_id,
            values=(
                row.id,
                row.title,
                row.category,
                row.status,
                self._format_tags_for_cell(row.tag_keys),
                row.notes,
            ),
        )

    def _on_click(self, event) -> Optional[str]:
        self._cancel_inline_edit()

        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return None
        item_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if not item_id or not col_id:
            return None

        col_name = self.columns[int(col_id.replace("#", "")) - 1]
        if col_name == "tags":
            self._open_tag_selector_dialog(item_id)
            return "break"
        return None

    def _on_double_click(self, event) -> Optional[str]:
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return None

        item_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if not item_id or not col_id:
            return None

        col_name = self.columns[int(col_id.replace("#", "")) - 1]
        if col_name in ("id", "tags"):
            return None
        self._begin_inline_edit(item_id, col_name)
        return "break"

    def _begin_inline_edit(self, item_id: str, col_name: str) -> None:
        self._cancel_inline_edit()

        col_index = self.columns.index(col_name)
        bbox = self.tree.bbox(item_id, column=f"#{col_index + 1}")
        if not bbox:
            return
        x, y, w, h = bbox

        current = str(self.tree.item(item_id, "values")[col_index])
        editor: tk.Widget
        if col_name == "status":
            editor = ttk.Combobox(self.tree, values=self.statuses, state="readonly")
            editor.set(current)
        elif col_name == "category":
            editor = ttk.Combobox(self.tree, values=self.categories, state="readonly")
            editor.set(current)
        else:
            entry = tk.Entry(self.tree)
            entry.insert(0, current)
            editor = entry

        editor.place(x=x, y=y, width=w, height=h)
        editor.focus_set()

        self._editor = editor
        self._editing_target = (item_id, col_name)

        editor.bind("<Return>", lambda _e: self._commit_inline_edit())
        editor.bind("<Escape>", lambda _e: self._cancel_inline_edit())
        editor.bind("<FocusOut>", lambda _e: self._commit_inline_edit())

    def _commit_inline_edit(self) -> None:
        if self._editor is None or self._editing_target is None:
            return
        item_id, col_name = self._editing_target
        row = self.rows_by_iid.get(item_id)
        if row is None:
            self._cancel_inline_edit()
            return

        if isinstance(self._editor, ttk.Combobox):
            new_value = self._editor.get().strip()
        else:
            new_value = self._editor.get().strip()

        if col_name == "title":
            row.title = new_value
        elif col_name == "category":
            row.category = new_value if new_value in self.categories else row.category
        elif col_name == "status":
            row.status = new_value if new_value in self.statuses else row.status
            if row.status == "Done":
                self._ensure_done_required_tags(row)
        elif col_name == "notes":
            row.notes = new_value

        self._destroy_editor()
        self._refresh_row(item_id)

    def _cancel_inline_edit(self) -> None:
        self._destroy_editor()

    def _destroy_editor(self) -> None:
        if self._editor is not None:
            try:
                self._editor.destroy()
            except tk.TclError:
                pass
        self._editor = None
        self._editing_target = None

    def _update_tag_definition(self, key: str, category: str, name: str, description: str) -> None:
        """Update one tag definition while keeping its stable key."""
        updated = TagDefinition(key=key, category=category, name=name, description=description)
        self.tag_by_key[key] = updated
        for index, tag in enumerate(self.tag_definitions):
            if tag.key == key:
                self.tag_definitions[index] = updated
                break

    def _refresh_all_rows(self) -> None:
        """Redraw all rows (used after tag metadata updates)."""
        for item_id in list(self.rows_by_iid.keys()):
            self._refresh_row(item_id)

    def _open_tag_selector_dialog(self, item_id: str) -> None:
        row = self.rows_by_iid.get(item_id)
        if row is None:
            return

        dialog = tk.Toplevel(self)
        dialog.title("Select Tags")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.geometry("900x460")

        body = ttk.Frame(dialog, padding=10)
        body.pack(fill="both", expand=True)

        ttk.Label(
            body,
            text="同名タグはCategoryで区別されます。Doneの場合はFood/DrinkのLearningが必須です。",
        ).pack(anchor="w", pady=(0, 6))

        table_wrap = ttk.Frame(body)
        table_wrap.pack(fill="both", expand=True)
        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)

        tag_tree = ttk.Treeview(
            table_wrap,
            columns=("use", "category", "tag_name", "description"),
            show="headings",
            selectmode="browse",
            height=min(max(len(self.tag_definitions), 6), 12),
        )
        tag_tree.grid(row=0, column=0, sticky="nsew")
        yscroll = ttk.Scrollbar(table_wrap, orient="vertical", command=tag_tree.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        tag_tree.configure(yscrollcommand=yscroll.set)

        tag_tree.heading("use", text="Use")
        tag_tree.heading("category", text="Category")
        tag_tree.heading("tag_name", text="Tag Name")
        tag_tree.heading("description", text="Description")
        tag_tree.column("use", width=72, anchor="center", stretch=False)
        tag_tree.column("category", width=130, anchor="w", stretch=False)
        tag_tree.column("tag_name", width=150, anchor="w", stretch=False)
        tag_tree.column("description", width=430, anchor="w", stretch=True)

        selected = set(row.tag_keys)
        state_by_key: Dict[str, bool] = {}
        key_by_row_iid: Dict[str, str] = {}
        editable_by_key: Dict[str, Dict[str, str]] = {}

        for tag in self.tag_definitions:
            checked = tag.key in selected
            state_by_key[tag.key] = checked
            editable_by_key[tag.key] = {
                "category": tag.category,
                "name": tag.name,
                "description": tag.description,
            }
            row_iid = tag_tree.insert(
                "",
                "end",
                values=(CHECK_ON if checked else CHECK_OFF, tag.category, tag.name, tag.description),
            )
            key_by_row_iid[row_iid] = tag.key

        dialog_editor: Optional[tk.Widget] = None
        dialog_editing_target: Optional[Tuple[str, str]] = None

        def refresh_use(row_iid: str) -> None:
            key = key_by_row_iid.get(row_iid)
            if not key:
                return
            current_values = list(tag_tree.item(row_iid, "values"))
            current_values[0] = CHECK_ON if state_by_key.get(key, False) else CHECK_OFF
            tag_tree.item(row_iid, values=current_values)

        def refresh_row_values(row_iid: str) -> None:
            key = key_by_row_iid.get(row_iid)
            if not key:
                return
            editable = editable_by_key.get(key)
            if not editable:
                return
            tag_tree.item(
                row_iid,
                values=(
                    CHECK_ON if state_by_key.get(key, False) else CHECK_OFF,
                    editable["category"],
                    editable["name"],
                    editable["description"],
                ),
            )

        def toggle(row_iid: str) -> None:
            key = key_by_row_iid.get(row_iid)
            if not key:
                return
            state_by_key[key] = not state_by_key.get(key, False)
            refresh_use(row_iid)

        def destroy_dialog_editor() -> None:
            nonlocal dialog_editor, dialog_editing_target
            if dialog_editor is not None:
                try:
                    dialog_editor.destroy()
                except tk.TclError:
                    pass
            dialog_editor = None
            dialog_editing_target = None

        def commit_dialog_editor() -> None:
            nonlocal dialog_editor, dialog_editing_target
            if dialog_editor is None or dialog_editing_target is None:
                return
            target_row_iid, target_col_name = dialog_editing_target
            key = key_by_row_iid.get(target_row_iid)
            if not key:
                destroy_dialog_editor()
                return

            new_value = dialog_editor.get().strip()
            editable = editable_by_key.get(key, {})
            if target_col_name == "category":
                if new_value in self.categories:
                    editable["category"] = new_value
            elif target_col_name == "tag_name":
                if new_value:
                    editable["name"] = new_value
            elif target_col_name == "description":
                editable["description"] = new_value
            editable_by_key[key] = editable
            destroy_dialog_editor()
            refresh_row_values(target_row_iid)

        def begin_dialog_edit(row_iid: str, col_name: str) -> None:
            nonlocal dialog_editor, dialog_editing_target
            if col_name not in ("category", "tag_name", "description"):
                return

            commit_dialog_editor()
            col_index = ("use", "category", "tag_name", "description").index(col_name)
            bbox = tag_tree.bbox(row_iid, column=f"#{col_index + 1}")
            if not bbox:
                return
            x, y, w, h = bbox

            key = key_by_row_iid.get(row_iid)
            if not key:
                return
            editable = editable_by_key.get(key, {})
            current = ""
            if col_name == "category":
                current = editable.get("category", "")
                editor: tk.Widget = ttk.Combobox(tag_tree, values=self.categories, state="readonly")
                editor.set(current)
            elif col_name == "tag_name":
                current = editable.get("name", "")
                entry = tk.Entry(tag_tree)
                entry.insert(0, current)
                editor = entry
            else:
                current = editable.get("description", "")
                entry = tk.Entry(tag_tree)
                entry.insert(0, current)
                editor = entry

            editor.place(x=x, y=y, width=w, height=h)
            editor.focus_set()
            if isinstance(editor, tk.Entry):
                editor.selection_range(0, tk.END)
            dialog_editor = editor
            dialog_editing_target = (row_iid, col_name)
            editor.bind("<Return>", lambda _e: commit_dialog_editor())
            editor.bind("<Escape>", lambda _e: destroy_dialog_editor())
            editor.bind("<FocusOut>", lambda _e: commit_dialog_editor())

        def on_click(event) -> Optional[str]:
            commit_dialog_editor()
            if tag_tree.identify("region", event.x, event.y) != "cell":
                return None
            row_iid = tag_tree.identify_row(event.y)
            col_id = tag_tree.identify_column(event.x)
            if row_iid and col_id == "#1":
                toggle(row_iid)
                return "break"
            return None

        def on_double_click(event) -> Optional[str]:
            row_iid = tag_tree.identify_row(event.y)
            col_id = tag_tree.identify_column(event.x)
            if row_iid and col_id == "#1":
                toggle(row_iid)
                return "break"
            if row_iid and col_id in ("#2", "#3", "#4"):
                col_name = {"#2": "category", "#3": "tag_name", "#4": "description"}[col_id]
                begin_dialog_edit(row_iid, col_name)
                return "break"
            return None

        def on_space(_event) -> str:
            current = tag_tree.selection()
            if current:
                toggle(current[0])
            return "break"

        def on_escape(_event) -> str:
            destroy_dialog_editor()
            return "break"

        tag_tree.bind("<Button-1>", on_click, add=True)
        tag_tree.bind("<Double-1>", on_double_click, add=True)
        tag_tree.bind("<space>", on_space, add=True)
        tag_tree.bind("<Escape>", on_escape, add=True)

        button_row = ttk.Frame(body)
        button_row.pack(fill="x", pady=(10, 0))

        def on_ok() -> None:
            commit_dialog_editor()
            for key, editable in editable_by_key.items():
                self._update_tag_definition(
                    key=key,
                    category=editable.get("category", ""),
                    name=editable.get("name", ""),
                    description=editable.get("description", ""),
                )
            selected_keys = [tag.key for tag in self.tag_definitions if state_by_key.get(tag.key, False)]
            row.tag_keys = selected_keys
            if row.status == "Done":
                self._ensure_done_required_tags(row)
            self._refresh_all_rows()
            dialog.destroy()

        def on_cancel() -> None:
            destroy_dialog_editor()
            dialog.destroy()

        ttk.Button(button_row, text="OK", command=on_ok).pack(side="right")
        ttk.Button(button_row, text="Cancel", command=on_cancel).pack(side="right", padx=(0, 6))

        dialog.bind("<Return>", lambda _e: on_ok())
        dialog.bind("<Escape>", lambda _e: on_cancel())
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)
        dialog.focus_set()


def main() -> None:
    root = tk.Tk()
    root.title("SortableTableDemo - Category Aware Duplicate Tag Names")
    root.geometry("1040x560")
    app = CategoryAwareTagTableDemo(root)
    app.pack(fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    main()

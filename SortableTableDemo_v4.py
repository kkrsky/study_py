import tkinter as tk
from tkinter import ttk
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

CHECK_ON = "[x]"
CHECK_OFF = "[ ]"


@dataclass
class ColumnConfig:
    key: str
    heading: str
    sort_type: str = "text"
    width: int = 120
    anchor: str = "w"
    editor: str = "entry"  # entry | combobox | checkbox | action


@dataclass
class TableDemoConfig:
    title_text: str
    button_labels: Dict[str, str]
    columns: List[ColumnConfig]
    dropdown_values: Dict[str, List[str]]
    demo_rows: List[Dict[str, object]]
    new_row_defaults: Dict[str, object]
    custom_dropdown_columns: List[str] = field(default_factory=list)
    date_format: str = "%Y-%m-%d"
    tree_style_name: str = "Table.Treeview"
    action_button_style_name: str = "ActionOverlay.TButton"
    row_height: int = 28
    tree_font: Tuple[str, int] = ("Segoe UI", 10)
    heading_font: Tuple[str, int, str] = ("Segoe UI", 10, "bold")
    action_button_padding: Tuple[int, int] = (4, 1)
    action_button_inset: int = 2
    action_button_min_width: int = 24
    action_button_min_height: int = 22
    toolbar_padx: int = 10
    toolbar_pady_top: int = 10
    toolbar_pady_bottom: int = 6
    toolbar_button_padx: int = 6
    content_padx: int = 10
    content_pady_bottom: int = 6
    error_bar_padx: int = 10
    error_bar_pady_bottom: int = 10
    action_button_text: str = "Run"


DEFAULT_CONFIG = TableDemoConfig(
    title_text=(
        "Header sortable / Active toggle on click / Action button shown in cell / "
        "Dropdown and text inline edit"
    ),
    button_labels={
        "add": "Add Row",
        "delete": "Delete Selected",
        "validate": "Validate All",
        "all_ok": "All rows are valid.",
        "validation_block": "Fix invalid cell before sorting.",
        "action_done": "Action executed",
    },
    columns=[
        ColumnConfig("id", "ID", sort_type="int", width=60, anchor="e"),
        ColumnConfig("title", "Title"),
        ColumnConfig("category", "Category", editor="combobox"),
        ColumnConfig("status", "Status", editor="combobox"),
        ColumnConfig("active", "Active", sort_type="bool", width=70, anchor="center", editor="checkbox"),
        ColumnConfig("qty", "Qty", sort_type="int", width=70, anchor="e"),
        ColumnConfig("price", "Price", sort_type="float", width=90, anchor="e"),
        ColumnConfig("progress", "Progress(%)", sort_type="int", width=110, anchor="e"),
        ColumnConfig("due", "Due(YYYY-MM-DD)", sort_type="date", width=130),
        ColumnConfig("action", "Action(Button)", width=130, anchor="center", editor="action"),
        ColumnConfig("notes", "Notes", width=220),
    ],
    dropdown_values={
        "category": ["Food", "Drink", "Daily", "Work", "Hobby"],
        "status": ["New", "Hold", "Done", "Canceled"],
    },
    custom_dropdown_columns=["category"],
    demo_rows=[
        {
            "id": 1,
            "title": "Buy apples",
            "category": "Food",
            "status": "New",
            "active": True,
            "qty": 10,
            "price": 120.5,
            "progress": 0,
            "due": "2026-02-05",
            "action": "Run",
            "notes": "From supermarket",
        },
        {
            "id": 2,
            "title": "Make coffee",
            "category": "Drink",
            "status": "Hold",
            "active": True,
            "qty": 1,
            "price": 980.0,
            "progress": 20,
            "due": "2026-02-01",
            "action": "Run",
            "notes": "Try new beans",
        },
        {
            "id": 3,
            "title": "Daily jog",
            "category": "Daily",
            "status": "Done",
            "active": False,
            "qty": 1,
            "price": 0.0,
            "progress": 100,
            "due": "2026-01-25",
            "action": "Run",
            "notes": "5km",
        },
        {
            "id": 4,
            "title": "Write report",
            "category": "Work",
            "status": "New",
            "active": True,
            "qty": 1,
            "price": 0.0,
            "progress": 10,
            "due": "2026-02-10",
            "action": "Run",
            "notes": "Draft first",
        },
        {
            "id": 5,
            "title": "Blender practice",
            "category": "Hobby",
            "status": "Hold",
            "active": True,
            "qty": 1,
            "price": 0.0,
            "progress": 35,
            "due": "2026-02-12",
            "action": "Run",
            "notes": "Modeling",
        },
    ],
    new_row_defaults={
        "title": "Task {id}",
        "category": "Food",
        "status": "New",
        "active": True,
        "qty": 0,
        "price": 0.0,
        "progress": 0,
        "due": "{today}",
        "action": "Run",
        "notes": "",
    },
)


class SortableTableDemo(ttk.Frame):
    """ソート・インライン編集・バリデーション対応の再利用可能なTreeviewテーブル。"""

    def __init__(self, parent: tk.Misc, config: Optional[TableDemoConfig] = None):
        """設定を読み込み、状態初期化とUI構築を行う。"""
        super().__init__(parent)
        self.table_config = config or DEFAULT_CONFIG
        self.columns = tuple(col.key for col in self.table_config.columns)
        self.column_map = {col.key: col for col in self.table_config.columns}
        self.headings = {col.key: col.heading for col in self.table_config.columns}
        self.sort_types = {col.key: col.sort_type for col in self.table_config.columns}
        self.sort_ascending = {c: True for c in self.columns}

        self.dropdown_values = {
            key: list(values) for key, values in self.table_config.dropdown_values.items()
        }
        self.dropdown_cols = set(self.dropdown_values.keys())
        self.custom_dropdown_cols = set(self.table_config.custom_dropdown_columns)
        self.checkbox_cols = {c.key for c in self.table_config.columns if c.editor == "checkbox"}
        action_cols = [c.key for c in self.table_config.columns if c.editor == "action"]
        self.action_col = action_cols[0] if action_cols else ""

        self._editor = None
        self._editing = None
        self._editing_original = None
        self._editing_bbox = None
        self._editor_var = None
        self._invalid = False
        self._last_error = ""

        self._action_button = None
        self._action_target = None
        self._next_row_id = 1

        self._build_ui()
        self._insert_demo_rows()
        self._bind_events()

    def _bind_events(self) -> None:
        """テーブル操作に必要なマウス/キーボードイベントを関連付ける。"""
        self.tree.bind("<Button-1>", self._on_click, add=True)
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Escape>", lambda e: self._cancel_edit())
        self.tree.bind("<Configure>", lambda e: self._hide_overlays())
        self.tree.bind("<MouseWheel>", lambda e: self._hide_overlays(), add=True)

    def _build_ui(self) -> None:
        """ツールバー、Treeview、本体スクロールバーを作成する。"""
        top = ttk.Frame(self)
        top.pack(
            fill="x",
            padx=self.table_config.toolbar_padx,
            pady=(self.table_config.toolbar_pady_top, self.table_config.toolbar_pady_bottom),
        )

        ttk.Label(top, text=self.table_config.title_text).pack(side="left")
        ttk.Button(top, text=self.table_config.button_labels["add"], command=self.add_row).pack(side="right")
        ttk.Button(
            top,
            text=self.table_config.button_labels["delete"],
            command=self.delete_selected,
        ).pack(side="right", padx=self.table_config.toolbar_button_padx)
        ttk.Button(
            top,
            text=self.table_config.button_labels["validate"],
            command=self.validate_all_rows,
        ).pack(side="right", padx=self.table_config.toolbar_button_padx)

        mid = ttk.Frame(self)
        mid.pack(fill="both", expand=True, padx=self.table_config.content_padx, pady=(0, self.table_config.content_pady_bottom))

        # Styles are configurable via TableDemoConfig for reuse across forms.
        style = ttk.Style(self)
        style.configure(
            self.table_config.tree_style_name,
            rowheight=self.table_config.row_height,
            font=self.table_config.tree_font,
        )
        style.configure(
            f"{self.table_config.tree_style_name}.Heading",
            font=self.table_config.heading_font,
        )
        style.configure(
            self.table_config.action_button_style_name,
            padding=self.table_config.action_button_padding,
        )

        self.tree = ttk.Treeview(mid, columns=self.columns, show="headings", selectmode="extended")
        self.tree.configure(style=self.table_config.tree_style_name)

        for col in self.table_config.columns:
            self.tree.heading(col.key, text=col.heading, command=lambda c=col.key: self.sort_by_column(c))
            self.tree.column(col.key, width=col.width, anchor=col.anchor)

        xscroll = ttk.Scrollbar(mid, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=xscroll.set)

        yscroll = ttk.Scrollbar(mid, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        mid.grid_rowconfigure(0, weight=1)
        mid.grid_columnconfigure(0, weight=1)

        self.error_bar = ttk.Label(self, text="", anchor="w")
        self.error_bar.pack(fill="x", padx=self.table_config.error_bar_padx, pady=(0, self.table_config.error_bar_pady_bottom))

    def _insert_demo_rows(self) -> None:
        """設定の初期データ行をテーブルへ挿入する。"""
        for row in self.table_config.demo_rows:
            self.tree.insert("", "end", values=self._normalize_row_dict(row))
        self._next_row_id = max((int(r.get("id", 0)) for r in self.table_config.demo_rows), default=0) + 1

    def _normalize_row_dict(self, row: Dict[str, object]) -> Tuple[object, ...]:
        """行dictをTreeview用tupleへ変換し、boolをチェック表示に変換する。"""
        values = []
        for key in self.columns:
            v = row.get(key, "")
            if key in self.checkbox_cols:
                v = CHECK_ON if bool(v) else CHECK_OFF
            values.append(v)
        return tuple(values)

    def _set_error(self, message: str) -> None:
        """フッターのエラーバーにメッセージを表示する。"""
        self._last_error = message
        self.error_bar.config(text=message)

    def _clear_error(self) -> None:
        """フッターのメッセージ表示をクリアする。"""
        self._last_error = ""
        self.error_bar.config(text="")

    def add_row(self) -> None:
        """単調増加IDと既定テンプレート値を使って新規行を追加する。"""
        next_id = max(self._next_row_id, self._max_existing_id() + 1)
        self._next_row_id = next_id + 1

        today = datetime.now().strftime(self.table_config.date_format)
        row = {"id": next_id}
        for key, value in self.table_config.new_row_defaults.items():
            if isinstance(value, str):
                row[key] = value.format(id=next_id, today=today)
            else:
                row[key] = value

        self.tree.insert("", "end", values=self._normalize_row_dict(row))

    def _max_existing_id(self) -> int:
        """現在の行データから最大IDを取得する。"""
        idx = self.columns.index("id") if "id" in self.columns else -1
        if idx < 0:
            return 0

        max_id = 0
        for item_id in self.tree.get_children(""):
            vals = self.tree.item(item_id, "values")
            try:
                max_id = max(max_id, int(vals[idx]))
            except Exception:
                continue
        return max_id

    def delete_selected(self) -> None:
        """選択中の行を削除する。"""
        self._commit_edit(force=True)
        for item_id in self.tree.selection():
            self.tree.delete(item_id)

    def get_data(self) -> List[Dict[str, object]]:
        """テーブル値を list[dict] で返す（数値/真偽値は可能な範囲で変換）。"""
        out = []
        for item_id in self.tree.get_children(""):
            vals = list(self.tree.item(item_id, "values"))
            row = {col: vals[i] for i, col in enumerate(self.columns)}
            if "active" in row:
                row["active"] = row["active"] == CHECK_ON

            for col, sort_type in self.sort_types.items():
                if col not in row:
                    continue
                if sort_type == "int":
                    row[col] = self._try_int(row[col])
                elif sort_type == "float":
                    row[col] = self._try_float(row[col])
            out.append(row)
        return out

    @staticmethod
    def _try_int(x: object) -> object:
        """可能な場合のみ int に変換する。"""
        try:
            return int(x)
        except Exception:
            return x

    @staticmethod
    def _try_float(x: object) -> object:
        """可能な場合のみ float に変換する。"""
        try:
            return float(x)
        except Exception:
            return x

    def validate_cell(self, col_name: str, value: str) -> Tuple[bool, str]:
        """列ルールに基づいて1セル分の値を検証する。"""
        v = value.strip()

        if col_name in self.dropdown_cols:
            if col_name in self.custom_dropdown_cols:
                return True, ""
            if v not in self.dropdown_values[col_name]:
                return False, f"{col_name} must be one of {self.dropdown_values[col_name]}"
            return True, ""

        if col_name in self.checkbox_cols:
            return (v in (CHECK_ON, CHECK_OFF), f"{col_name} must be {CHECK_ON}/{CHECK_OFF}")

        if col_name == "id":
            try:
                if int(v) < 0:
                    return False, "ID must be >= 0"
            except Exception:
                return False, "ID must be integer"
            return True, ""

        if col_name == "qty":
            try:
                if int(v) < 0:
                    return False, "Qty must be >= 0"
            except Exception:
                return False, "Qty must be integer"
            return True, ""

        if col_name == "progress":
            try:
                p = int(v)
                if not (0 <= p <= 100):
                    return False, "Progress must be 0-100"
            except Exception:
                return False, "Progress must be integer (0-100)"
            return True, ""

        if col_name == "price":
            try:
                if float(v) < 0:
                    return False, "Price must be >= 0"
            except Exception:
                return False, "Price must be numeric"
            return True, ""

        if col_name == "due":
            try:
                datetime.strptime(v, self.table_config.date_format)
            except Exception:
                return False, f"Due must match {self.table_config.date_format}"
            return True, ""

        return True, ""

    def validate_all_rows(self) -> bool:
        """全行を検証し、最初のエラーを表示して結果を返す。"""
        self._commit_edit(force=True)
        for item_id in self.tree.get_children(""):
            vals = list(self.tree.item(item_id, "values"))
            for i, col in enumerate(self.columns):
                ok, msg = self.validate_cell(col, str(vals[i]))
                if not ok:
                    row_id = vals[self.columns.index("id")] if "id" in self.columns else "?"
                    self._set_error(f"RowID={row_id} / {col}: {msg}")
                    return False
        self._set_error(self.table_config.button_labels["all_ok"])
        return True

    def sort_by_column(self, col: str) -> None:
        """指定列で行をソートし、昇順/降順をトグルする。"""
        if self._editor is not None and self._invalid:
            self._set_error(self.table_config.button_labels["validation_block"])
            return

        self._commit_edit(force=True)
        self._hide_overlays()

        asc = self.sort_ascending[col]
        sort_type = self.sort_types.get(col, "text")
        col_index = self.columns.index(col)

        items = list(self.tree.get_children(""))

        def key_func(item_id: str):
            vals = self.tree.item(item_id, "values")
            v = vals[col_index]
            try:
                if sort_type == "int":
                    return (0, int(v))
                if sort_type == "float":
                    return (0, float(v))
                if sort_type == "date":
                    return (0, datetime.strptime(v, self.table_config.date_format))
                if sort_type == "bool":
                    return (0, 1 if v == CHECK_ON else 0)
                return (0, str(v).lower())
            except Exception:
                return (1, str(v))

        items.sort(key=key_func, reverse=not asc)
        for i, item_id in enumerate(items):
            self.tree.move(item_id, "", i)

        for c in self.columns:
            self.tree.heading(c, text=self.headings[c], command=lambda cc=c: self.sort_by_column(cc))
        arrow = " ▲" if asc else " ▼"
        self.tree.heading(col, text=self.headings[col] + arrow, command=lambda cc=col: self.sort_by_column(cc))
        self.sort_ascending[col] = not asc

    def _on_click(self, event) -> None:
        """シングルクリック操作（チェック切替・Action表示など）を処理する。"""
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            self._handle_editor_transition_on_cell_change(None, None)
            self._hide_overlays()
            return

        item_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if not item_id or not col_id:
            self._handle_editor_transition_on_cell_change(None, None)
            self._hide_overlays()
            return

        col_index = int(col_id.replace("#", "")) - 1
        col_name = self.columns[col_index]

        if not self._handle_editor_transition_on_cell_change(item_id, col_name):
            return

        if col_name == self.action_col:
            self._show_action_button(item_id)
            return

        if col_name in self.checkbox_cols:
            self._hide_overlays()
            self._toggle_checkbox(item_id, col_name)
            return

        self._hide_overlays()

    def _on_double_click(self, event) -> None:
        """編集可能セルでインラインエディタを開始する。"""
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        item_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if not item_id or not col_id:
            return

        col_index = int(col_id.replace("#", "")) - 1
        col_name = self.columns[col_index]

        if col_name == self.action_col or col_name in self.checkbox_cols:
            return

        if not self._handle_editor_transition_on_cell_change(item_id, col_name):
            return

        self._hide_overlays()
        if col_name in self.dropdown_cols:
            self._begin_combobox_edit(item_id, col_name)
        else:
            self._begin_entry_edit(item_id, col_name)

    def _handle_editor_transition_on_cell_change(
        self, target_item_id: Optional[str], target_col_name: Optional[str]
    ) -> bool:
        """セル移動時に編集中値を確定または元に戻し、遷移可否を返す。"""
        if self._editor is None or self._editing is None:
            return True

        editing_item_id, editing_col_name = self._editing
        if editing_item_id == target_item_id and editing_col_name == target_col_name:
            return True

        try:
            current_value = self._editor.get()
        except tk.TclError:
            # Stale editor reference must never block future edits.
            self._destroy_editor()
            return True
        ok, _ = self.validate_cell(editing_col_name, current_value)
        if ok:
            self._commit_edit(force=False)
            return self._editor is None

        self._revert_current_edit()
        return True

    def _toggle_checkbox(self, item_id: str, col_name: str) -> None:
        """チェックボックス列の表示値をトグルする。"""
        idx = self.columns.index(col_name)
        vals = list(self.tree.item(item_id, "values"))
        vals[idx] = CHECK_OFF if vals[idx] == CHECK_ON else CHECK_ON
        self.tree.item(item_id, values=vals)

    def _show_action_button(self, item_id: str) -> None:
        """Actionセル上に実ボタンを重ねて表示する。"""
        self._hide_overlays()

        col_index = self.columns.index(self.action_col)
        bbox = self.tree.bbox(item_id, column=f"#{col_index + 1}")
        if not bbox:
            return
        x, y, w, h = bbox

        self._action_target = item_id
        inset = self.table_config.action_button_inset
        btn_x = x + inset
        btn_y = y + inset
        btn_w = max(self.table_config.action_button_min_width, w - (inset * 2))
        btn_h = max(self.table_config.action_button_min_height, h - (inset * 2))

        self._action_button = ttk.Button(
            self.tree,
            text=self.table_config.action_button_text,
            style=self.table_config.action_button_style_name,
            command=self._run_action_for_row,
        )
        self._action_button.place(x=btn_x, y=btn_y, width=btn_w, height=btn_h)

    def _run_action_for_row(self) -> None:
        """Actionボタン押下時のサンプル処理を実行する。"""
        if not self._action_target:
            return
        item_id = self._action_target
        vals = list(self.tree.item(item_id, "values"))
        row_id = vals[self.columns.index("id")]
        title = vals[self.columns.index("title")]
        status = vals[self.columns.index("status")]
        self._set_error(f"{self.table_config.button_labels['action_done']}: RowID={row_id}, Title='{title}', Status='{status}'")
        self._hide_overlays()

    def _hide_overlays(self) -> None:
        """一時的に重ねたウィジェット（ボタン等）を削除する。"""
        if self._action_button is not None:
            self._action_button.destroy()
            self._action_button = None
            self._action_target = None

    def _begin_combobox_edit(self, item_id: str, col_name: str) -> None:
        """列挙値列に対するCombobox編集を開始する。"""
        self._commit_edit(force=True)

        col_index = self.columns.index(col_name)
        bbox = self.tree.bbox(item_id, column=f"#{col_index + 1}")
        if not bbox:
            return
        x, y, w, h = bbox

        vals = list(self.tree.item(item_id, "values"))
        current = str(vals[col_index])

        values = list(self.dropdown_values[col_name])
        if current and current not in values:
            values.insert(0, current)

        state = "normal" if col_name in self.custom_dropdown_cols else "readonly"
        cb = ttk.Combobox(self.tree, values=values, state=state)
        cb.set(current if current else values[0])
        cb.place(x=x, y=y, width=w, height=h)

        self._editor = cb
        self._editing = (item_id, col_name)
        self._editing_original = current
        self._editing_bbox = bbox
        self._invalid = False
        self._clear_error()

        def on_change(_e=None):
            ok, msg = self.validate_cell(col_name, cb.get())
            self._apply_validation_ui(ok, msg)

        cb.bind("<<ComboboxSelected>>", on_change)
        cb.bind("<Return>", lambda e: self._commit_edit(force=False))
        cb.bind("<Escape>", lambda e: self._cancel_edit())
        cb.bind("<FocusOut>", lambda e: self._on_combobox_focus_out(cb))

        cb.focus_set()
        on_change()

    def _on_combobox_focus_out(self, cb: ttk.Combobox) -> None:
        """
        Comboboxのフォーカスアウト時処理。
        ドロップダウン表示中は確定しないことで、矢印クリック時に
        エディタが先に閉じてしまう問題を防ぐ。
        """
        def commit_if_safe() -> None:
            if self._editor is not cb:
                return
            try:
                popdown = cb.tk.call("ttk::combobox::PopdownWindow", str(cb))
                is_mapped = cb.tk.call("winfo", "ismapped", popdown)
            except tk.TclError:
                is_mapped = "0"
            if str(is_mapped) == "1":
                return
            self._commit_edit(force=False)

        cb.after_idle(commit_if_safe)

    def _begin_entry_edit(self, item_id: str, col_name: str) -> None:
        """通常編集セルに対するテキスト入力編集を開始する。"""
        self._commit_edit(force=True)

        col_index = self.columns.index(col_name)
        bbox = self.tree.bbox(item_id, column=f"#{col_index + 1}")
        if not bbox:
            return
        x, y, w, h = bbox

        vals = list(self.tree.item(item_id, "values"))
        current = str(vals[col_index])

        var = tk.StringVar(value=current)
        ent = tk.Entry(self.tree, textvariable=var, relief="solid", bd=1)
        ent.place(x=x, y=y, width=w, height=h)

        self._editor = ent
        self._editor_var = var
        self._editing = (item_id, col_name)
        self._editing_original = current
        self._editing_bbox = bbox
        self._invalid = False
        self._clear_error()

        def live_validate(*_):
            ok, msg = self.validate_cell(col_name, var.get())
            self._apply_validation_ui(ok, msg)

        var.trace_add("write", live_validate)

        ent.bind("<Return>", lambda e: self._commit_edit(force=False))
        ent.bind("<Escape>", lambda e: self._cancel_edit())
        ent.bind("<FocusOut>", lambda e: self._commit_edit(force=False))

        ent.focus_set()
        ent.selection_range(0, tk.END)
        live_validate()

    def _apply_validation_ui(self, ok: bool, msg: str) -> None:
        """検証結果に応じた見た目とメッセージ表示を反映する。"""
        self._invalid = not ok
        if ok:
            self._clear_error()
        else:
            self._set_error(msg)

        if isinstance(self._editor, tk.Entry) and not isinstance(self._editor, ttk.Combobox):
            self._editor.configure(bg=("white" if ok else "#ffcccc"))
        elif isinstance(self._editor, ttk.Combobox):
            style = ttk.Style(self)
            if ok:
                self._editor.configure(style="TCombobox")
            else:
                style.configure("Invalid.TCombobox", fieldbackground="#ffcccc")
                self._editor.configure(style="Invalid.TCombobox")

    def _commit_edit(self, force: bool) -> None:
        """編集中の値をセルへ反映する。未強制かつ不正値なら編集を継続する。"""
        if self._editor is None or self._editing is None:
            return

        item_id, col_name = self._editing
        col_index = self.columns.index(col_name)

        try:
            new_value = self._editor.get()
        except tk.TclError:
            # Editor widget was already destroyed by focus/event race.
            self._destroy_editor()
            return
        if col_name in self.custom_dropdown_cols and new_value and new_value not in self.dropdown_values[col_name]:
            self.dropdown_values[col_name].append(new_value)

        ok, msg = self.validate_cell(col_name, new_value)
        if not ok and not force:
            self._apply_validation_ui(False, msg)
            return

        vals = list(self.tree.item(item_id, "values"))
        vals[col_index] = new_value
        self.tree.item(item_id, values=vals)

        self._destroy_editor()

        if ok:
            self._clear_error()
        else:
            self._set_error(msg)

    def _cancel_edit(self) -> None:
        """現在の編集をキャンセルし、元の値へ戻す。"""
        if self._editor is None:
            return
        self._revert_current_edit()
        self._clear_error()

    def _revert_current_edit(self) -> None:
        """編集開始時に保持した元の値をセルへ復元する。"""
        if self._editing is not None and self._editing_original is not None:
            item_id, col_name = self._editing
            col_index = self.columns.index(col_name)
            vals = list(self.tree.item(item_id, "values"))
            vals[col_index] = self._editing_original
            self.tree.item(item_id, values=vals)
        self._destroy_editor()

    def _destroy_editor(self) -> None:
        """インラインエディタを安全に破棄し、関連状態を初期化する。"""
        if self._editor is not None:
            try:
                self._editor.destroy()
            except tk.TclError:
                pass
        self._editor = None
        self._editor_var = None
        self._editing = None
        self._editing_original = None
        self._editing_bbox = None
        self._invalid = False


def create_sortable_table(parent: tk.Misc, config: Optional[TableDemoConfig] = None) -> SortableTableDemo:
    """他フォームへ埋め込むためのテーブル生成ヘルパー。"""
    return SortableTableDemo(parent, config=config)


def main() -> None:
    """単体デモ起動用エントリポイント。"""
    root = tk.Tk()
    root.title("tkinter Treeview: reusable sortable table demo")
    root.geometry("1250x520")
    ui = SortableTableDemo(root)
    ui.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()

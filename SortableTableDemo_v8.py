import tkinter as tk
from tkinter import ttk
import re
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

CHECK_ON = "[x]"
CHECK_OFF = "[ ]"
FILTER_ALL = ""
FILTER_SPACER_IID = "__filter_spacer__"


@dataclass
class ColumnConfig:
    key: str
    heading: str
    sort_type: str = "text"
    width: int = 120
    anchor: str = "w"
    editor: str = "entry"  # entry | combobox | checkbox | action | tags


@dataclass(frozen=True)
class TagItem:
    """Tag metadata managed by stable ID."""

    tag_id: str
    name: str
    category: str = ""
    description: str = ""


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
    heading_background: str = "#d3d3d3"
    heading_foreground: str = "#1f2937"
    filter_row_background: str = "#fff9cc"
    filter_row_foreground: str = "#111827"
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
    tag_items: List[TagItem] = field(default_factory=list)
    available_tags: List[str] = field(default_factory=list)
    tag_descriptions: Dict[str, str] = field(default_factory=dict)
    tag_separator: str = ", "


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
        ColumnConfig("tags", "Tags", width=180, editor="tags"),
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
            "tags": ["food::urgent", "food::home"],
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
            "tags": ["drink::home"],
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
            "tags": ["daily::health"],
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
            "tags": ["work::urgent", "work::office"],
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
            "tags": ["food::learning", "drink::learning"],
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
        "tags": "",
        "active": True,
        "qty": 0,
        "price": 0.0,
        "progress": 0,
        "due": "{today}",
        "action": "Run",
        "notes": "",
    },
    tag_items=[
        TagItem("food::urgent", "Urgent", category="Food", description="優先的に対応が必要な食関連タスク"),
        TagItem("work::urgent", "Urgent", category="Work", description="優先的に対応が必要な業務タスク"),
        TagItem("food::home", "Home", category="Food", description="自宅の食関連タスク"),
        TagItem("drink::home", "Home", category="Drink", description="自宅の飲み物関連タスク"),
        TagItem("work::office", "Office", category="Work", description="職場関連のタスク"),
        TagItem("daily::health", "Health", category="Daily", description="健康管理に関するタスク"),
        TagItem("food::learning", "Learning", category="Food", description="食材・料理の学習タスク"),
        TagItem("drink::learning", "Learning", category="Drink", description="飲料・抽出の学習タスク"),
        TagItem("work::follow_up", "FollowUp", category="Work", description="後で確認・追跡が必要なタスク"),
    ],
    available_tags=["Urgent", "Home", "Office", "Health", "Learning", "FollowUp"],
    tag_descriptions={
        "Urgent": "優先的に対応が必要なタスク",
        "Home": "自宅関連のタスク",
        "Office": "職場関連のタスク",
        "Health": "健康管理に関するタスク",
        "Learning": "学習・トレーニング目的のタスク",
        "FollowUp": "後で確認・追跡が必要なタスク",
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
        self.tag_selector_cols = {c.key for c in self.table_config.columns if c.editor == "tags"}
        action_cols = [c.key for c in self.table_config.columns if c.editor == "action"]
        self.action_col = action_cols[0] if action_cols else ""
        self.tag_items = self._build_tag_items()
        self.tag_item_by_id: Dict[str, TagItem] = {item.tag_id: item for item in self.tag_items}
        self._tag_ids_by_name: Dict[str, List[str]] = {}
        for item in self.tag_items:
            self._tag_ids_by_name.setdefault(item.name, []).append(item.tag_id)
        self._row_tag_ids: Dict[str, Dict[str, List[str]]] = {}
        self._copy_target_cols = [c for c in self.columns if c != self.action_col]
        self._copy_col_vars: Dict[str, tk.BooleanVar] = {}

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
        self._filter_values: Dict[str, str] = {}
        self._filter_candidates: Dict[str, List[str]] = {}
        self._data_item_ids: List[str] = []
        self._copied_columns: Tuple[str, ...] = tuple()
        self._copied_rows: List[Tuple[str, ...]] = []
        self._copied_tag_ids: List[Dict[str, List[str]]] = []
        self._undo_stack: List[Dict[str, object]] = []
        self._redo_stack: List[Dict[str, object]] = []
        self._history_restoring = False
        for col in self.columns:
            if col != self.action_col:
                self._filter_values[col] = FILTER_ALL

        self._build_ui()
        self._insert_demo_rows()
        self._rebuild_filter_values()
        self._apply_filters()
        self._bind_events()

    def _bind_events(self) -> None:
        """テーブル操作に必要なマウス/キーボードイベントを関連付ける。"""
        self.tree.bind("<Button-1>", self._on_click, add=True)
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Control-c>", self._on_copy_rows, add=True)
        self.tree.bind("<Control-C>", self._on_copy_rows, add=True)
        self.tree.bind("<Control-v>", self._on_paste_rows, add=True)
        self.tree.bind("<Control-V>", self._on_paste_rows, add=True)
        self.tree.bind("<Control-z>", self._on_undo, add=True)
        self.tree.bind("<Control-Z>", self._on_undo, add=True)
        self.tree.bind("<Control-y>", self._on_redo, add=True)
        self.tree.bind("<Control-Y>", self._on_redo, add=True)
        self.tree.bind("<Escape>", lambda e: self._cancel_edit())
        self.tree.bind("<Configure>", lambda e: self._hide_overlays())
        self.tree.bind("<MouseWheel>", lambda e: self._hide_overlays(), add=True)

    def _build_ui(self) -> None:
        """ツールバー、Treeview、本体スクロールバーを作成する。"""
        info = ttk.Frame(self)
        info.pack(
            fill="x",
            padx=self.table_config.toolbar_padx,
            pady=(self.table_config.toolbar_pady_top, 4),
        )
        info_text = (
            "このフォームでできること: 行追加/削除、ソート、フィルター、インライン編集、タグ選択、選択行コピー&ペースト\n"
            "ショートカット: Ctrl+C=選択行コピー, Ctrl+V=選択行へ貼り付け, "
            "Ctrl+Z=Undo, Ctrl+Y=Redo, Esc=編集中セルのキャンセル"
        )
        ttk.Label(info, text=info_text, justify="left", anchor="w").pack(fill="x")

        copy_opts = ttk.LabelFrame(self, text="Copy Columns")
        copy_opts.pack(fill="x", padx=self.table_config.toolbar_padx, pady=(0, self.table_config.toolbar_pady_bottom))

        columns_per_row = 6
        for index, col_name in enumerate(self._copy_target_cols):
            var = tk.BooleanVar(value=True)
            self._copy_col_vars[col_name] = var
            label = self.headings.get(col_name, col_name)
            chk = ttk.Checkbutton(copy_opts, text=label, variable=var)
            chk.grid(row=index // columns_per_row, column=index % columns_per_row, sticky="w", padx=(6, 8), pady=2)

        top = ttk.Frame(self)
        top.pack(
            fill="x",
            padx=self.table_config.toolbar_padx,
            pady=(0, self.table_config.toolbar_pady_bottom),
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
            background=self.table_config.heading_background,
            foreground=self.table_config.heading_foreground,
        )
        style.map(
            f"{self.table_config.tree_style_name}.Heading",
            background=[("active", self.table_config.heading_background)],
            foreground=[("active", self.table_config.heading_foreground)],
        )
        style.configure(
            self.table_config.action_button_style_name,
            padding=self.table_config.action_button_padding,
        )

        self.tree = ttk.Treeview(mid, columns=self.columns, show="headings", selectmode="extended")
        self.tree.configure(style=self.table_config.tree_style_name)
        self.tree.tag_configure(
            "filter_row",
            background=self.table_config.filter_row_background,
            foreground=self.table_config.filter_row_foreground,
        )

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
        self._insert_filter_spacer_row()

        self.error_bar = ttk.Label(self, text="", anchor="w")
        self.error_bar.pack(fill="x", padx=self.table_config.error_bar_padx, pady=(0, self.table_config.error_bar_pady_bottom))

    def _build_tag_items(self) -> List[TagItem]:
        """Build tag metadata list with backward-compatible fallback."""
        if self.table_config.tag_items:
            uniq: Dict[str, TagItem] = {}
            for item in self.table_config.tag_items:
                if item.tag_id not in uniq:
                    uniq[item.tag_id] = item
            return list(uniq.values())

        built: List[TagItem] = []
        for index, name in enumerate(self.table_config.available_tags):
            description = self.table_config.tag_descriptions.get(name, "")
            built.append(TagItem(tag_id=f"tag::{index}", name=name, description=description))
        return built

    def _display_name_for_tag_id(self, tag_id: str) -> str:
        """Resolve one tag ID to display name."""
        item = self.tag_item_by_id.get(tag_id)
        return item.name if item is not None else tag_id

    def _category_for_tag_id(self, tag_id: str) -> str:
        """Resolve one tag ID to category text."""
        item = self.tag_item_by_id.get(tag_id)
        return item.category if item is not None else ""

    def _description_for_tag_id(self, tag_id: str) -> str:
        """Resolve one tag ID to description text."""
        item = self.tag_item_by_id.get(tag_id)
        return item.description if item is not None else ""

    def _format_tag_display_text(self, tag_ids: List[str]) -> str:
        """Format ID list into visible tag names."""
        names = [self._display_name_for_tag_id(tag_id) for tag_id in tag_ids]
        return self.table_config.tag_separator.join([name for name in names if name])

    def _normalize_tag_ids(self, raw_value: object) -> List[str]:
        """Convert mixed tag input (IDs/names/text) into tag ID list."""
        if raw_value is None:
            return []

        tokens: List[str] = []
        if isinstance(raw_value, (list, tuple, set)):
            tokens = [str(value).strip() for value in raw_value]
        else:
            tokens = self._parse_tag_text(str(raw_value))

        resolved: List[str] = []
        seen = set()
        for token in tokens:
            if not token:
                continue
            if token in self.tag_item_by_id:
                tag_id = token
            else:
                candidate_ids = self._tag_ids_by_name.get(token, [])
                if not candidate_ids:
                    continue
                tag_id = candidate_ids[0]
            if tag_id in seen:
                continue
            seen.add(tag_id)
            resolved.append(tag_id)
        return resolved

    def _extract_tag_id_map_from_row(self, row: Dict[str, object]) -> Dict[str, List[str]]:
        """Extract tag ID lists for each tag-selector column from row dict."""
        tag_map: Dict[str, List[str]] = {}
        for col_name in self.tag_selector_cols:
            tag_map[col_name] = self._normalize_tag_ids(row.get(col_name, ""))
        return tag_map

    def _set_item_tag_ids(self, item_id: str, col_name: str, tag_ids: List[str]) -> None:
        """Persist tag ID list for one item/column."""
        self._row_tag_ids.setdefault(item_id, {})[col_name] = list(tag_ids)

    def _get_item_tag_ids(self, item_id: str, col_name: str, fallback_text: str = "") -> List[str]:
        """Read stored tag IDs for one item/column, with text fallback for legacy rows."""
        if item_id == FILTER_SPACER_IID:
            return []
        tag_map = self._row_tag_ids.setdefault(item_id, {})
        if col_name not in tag_map:
            tag_map[col_name] = self._normalize_tag_ids(fallback_text)
        return list(tag_map.get(col_name, []))

    def _all_tag_display_names(self) -> List[str]:
        """Get all known visible tag names."""
        if self.tag_items:
            return [item.name for item in self.tag_items]
        return list(self.table_config.available_tags)

    def _insert_demo_rows(self) -> None:
        """設定の初期データ行をテーブルへ挿入する。"""
        for row in self.table_config.demo_rows:
            item_id = self.tree.insert("", "end", values=self._normalize_row_dict(row))
            tag_id_map = self._extract_tag_id_map_from_row(row)
            for col_name, tag_ids in tag_id_map.items():
                self._set_item_tag_ids(item_id, col_name, tag_ids)
            self._data_item_ids.append(item_id)
        self._next_row_id = max((int(r.get("id", 0)) for r in self.table_config.demo_rows), default=0) + 1

    def _normalize_row_dict(self, row: Dict[str, object]) -> Tuple[object, ...]:
        """行dictをTreeview用tupleへ変換し、タグはIDから表示名へ整形する。"""
        values = []
        for key in self.columns:
            v = row.get(key, "")
            if key in self.checkbox_cols:
                v = CHECK_ON if bool(v) else CHECK_OFF
            elif key in self.tag_selector_cols:
                tag_ids = self._normalize_tag_ids(v)
                v = self._format_tag_display_text(tag_ids)
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
        self._record_undo_snapshot()
        next_id = max(self._next_row_id, self._max_existing_id() + 1)
        self._next_row_id = next_id + 1

        today = datetime.now().strftime(self.table_config.date_format)
        row = {"id": next_id}
        for key, value in self.table_config.new_row_defaults.items():
            if isinstance(value, str):
                row[key] = value.format(id=next_id, today=today)
            else:
                row[key] = value

        item_id = self.tree.insert("", "end", values=self._normalize_row_dict(row))
        tag_id_map = self._extract_tag_id_map_from_row(row)
        for col_name, tag_ids in tag_id_map.items():
            self._set_item_tag_ids(item_id, col_name, tag_ids)
        self._data_item_ids.append(item_id)
        self._rebuild_filter_values()
        self._apply_filters()

    def _max_existing_id(self) -> int:
        """現在の行データから最大IDを取得する。"""
        idx = self.columns.index("id") if "id" in self.columns else -1
        if idx < 0:
            return 0

        max_id = 0
        for item_id in self._iter_data_item_ids():
            vals = self.tree.item(item_id, "values")
            try:
                max_id = max(max_id, int(vals[idx]))
            except Exception:
                continue
        return max_id

    def delete_selected(self) -> None:
        """選択中の行を削除する。"""
        self._commit_edit(force=True)
        selected_rows = [iid for iid in self.tree.selection() if iid != FILTER_SPACER_IID and self.tree.exists(iid)]
        if not selected_rows:
            return
        self._record_undo_snapshot()
        for item_id in self.tree.selection():
            if item_id == FILTER_SPACER_IID:
                continue
            self.tree.delete(item_id)
            if item_id in self._data_item_ids:
                self._data_item_ids.remove(item_id)
            self._row_tag_ids.pop(item_id, None)
        self._rebuild_filter_values()
        self._apply_filters()

    def get_data(self) -> List[Dict[str, object]]:
        """テーブル値を list[dict] で返す（数値/真偽値は可能な範囲で変換）。"""
        out = []
        for item_id in self._iter_data_item_ids():
            vals = list(self.tree.item(item_id, "values"))
            row = {col: vals[i] for i, col in enumerate(self.columns)}
            for col_name in self.tag_selector_cols:
                if col_name not in row:
                    continue
                row[f"{col_name}_ids"] = self._get_item_tag_ids(item_id, col_name, str(row[col_name]))
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

    def _selected_data_item_ids_sorted(self) -> List[str]:
        """Return selected data rows sorted by current display order."""
        selected = [iid for iid in self.tree.selection() if iid != FILTER_SPACER_IID and self.tree.exists(iid)]
        selected.sort(key=self.tree.index)
        return selected

    def _active_copy_columns(self) -> Tuple[str, ...]:
        """Return currently enabled copy columns."""
        selected_cols = []
        for col_name in self._copy_target_cols:
            var = self._copy_col_vars.get(col_name)
            if var is None:
                selected_cols.append(col_name)
            elif bool(var.get()):
                selected_cols.append(col_name)
        return tuple(selected_cols)

    def _current_selected_data_indices(self) -> List[int]:
        """Return currently selected data-row indices based on _data_item_ids order."""
        selected_set = set(self.tree.selection())
        item_ids = self._iter_data_item_ids()
        return [idx for idx, item_id in enumerate(item_ids) if item_id in selected_set]

    def _capture_history_snapshot(self) -> Dict[str, object]:
        """Capture current table data/selection state for undo-redo."""
        rows: List[Tuple[str, ...]] = []
        row_tag_ids: List[Dict[str, List[str]]] = []

        item_ids = self._iter_data_item_ids()
        for idx, item_id in enumerate(item_ids):
            row_values = tuple(str(v) for v in self.tree.item(item_id, "values"))
            rows.append(row_values)

            tag_map: Dict[str, List[str]] = {}
            for col_name in self.tag_selector_cols:
                col_index = self.columns.index(col_name)
                fallback = row_values[col_index] if col_index < len(row_values) else ""
                tag_map[col_name] = self._get_item_tag_ids(item_id, col_name, str(fallback))
            row_tag_ids.append(tag_map)

        return {
            "rows": rows,
            "row_tag_ids": row_tag_ids,
            "next_row_id": self._next_row_id,
            "filter_values": dict(self._filter_values),
            "data_count": len(item_ids),
        }

    def _restore_history_snapshot(
        self, snapshot: Dict[str, object], preserve_selected_indices: Optional[List[int]] = None
    ) -> None:
        """Restore table data/selection state from one snapshot."""
        rows = snapshot.get("rows", [])
        row_tag_ids = snapshot.get("row_tag_ids", [])

        for item_id in self._iter_data_item_ids():
            self.tree.delete(item_id)
        self._data_item_ids = []
        self._row_tag_ids = {}

        for index, row_values in enumerate(rows):
            item_id = self.tree.insert("", "end", values=tuple(row_values))
            self._data_item_ids.append(item_id)

            if index < len(row_tag_ids):
                tag_map = row_tag_ids[index]
                if isinstance(tag_map, dict):
                    for col_name, tag_ids in tag_map.items():
                        self._set_item_tag_ids(item_id, col_name, list(tag_ids))

        next_row_id = snapshot.get("next_row_id", self._next_row_id)
        if isinstance(next_row_id, int):
            self._next_row_id = next_row_id

        filter_values = snapshot.get("filter_values", {})
        if isinstance(filter_values, dict):
            for col_name in self._filter_values.keys():
                if col_name in filter_values:
                    self._filter_values[col_name] = str(filter_values[col_name])

        self._rebuild_filter_values()
        self._apply_filters()

        if preserve_selected_indices is not None:
            selected_iids: List[str] = []
            for index in preserve_selected_indices:
                if isinstance(index, int) and 0 <= index < len(self._data_item_ids):
                    iid = self._data_item_ids[index]
                    if self.tree.exists(iid) and self.tree.parent(iid) == "":
                        selected_iids.append(iid)
            if selected_iids:
                self.tree.selection_set(selected_iids)
                self.tree.see(selected_iids[-1])
            else:
                self.tree.selection_remove(self.tree.selection())

    def _record_undo_snapshot(self) -> None:
        """Push current state to undo stack and clear redo stack."""
        if self._history_restoring:
            return
        self._undo_stack.append(self._capture_history_snapshot())
        if len(self._undo_stack) > 100:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def _on_undo(self, _event=None) -> str:
        """Undo one state-changing operation."""
        self._commit_edit(force=True)
        if not self._undo_stack:
            self._set_error("Undo skipped: no history.")
            self.bell()
            return "break"

        current = self._capture_history_snapshot()
        snapshot = self._undo_stack.pop()
        self._redo_stack.append(current)
        preserve_selected_indices = self._current_selected_data_indices()

        self._history_restoring = True
        try:
            self._restore_history_snapshot(snapshot, preserve_selected_indices=preserve_selected_indices)
        finally:
            self._history_restoring = False
        self._set_error("Undo applied.")
        return "break"

    def _on_redo(self, _event=None) -> str:
        """Redo one previously undone operation."""
        self._commit_edit(force=True)
        if not self._redo_stack:
            self._set_error("Redo skipped: no history.")
            self.bell()
            return "break"

        current = self._capture_history_snapshot()
        snapshot = self._redo_stack.pop()
        self._undo_stack.append(current)
        preserve_selected_indices = self._current_selected_data_indices()

        self._history_restoring = True
        try:
            self._restore_history_snapshot(snapshot, preserve_selected_indices=preserve_selected_indices)
        finally:
            self._history_restoring = False
        self._set_error("Redo applied.")
        return "break"

    def _on_copy_rows(self, _event=None) -> str:
        """Copy selected data rows for table-level paste operation."""
        self._commit_edit(force=True)
        selected = self._selected_data_item_ids_sorted()
        if not selected:
            self._set_error("Copy skipped: select at least one data row.")
            self.bell()
            return "break"

        copy_columns = self._active_copy_columns()
        if not copy_columns:
            self._set_error("Copy skipped: select at least one copy column.")
            self.bell()
            return "break"

        copied_rows: List[Tuple[str, ...]] = []
        copied_tag_ids: List[Dict[str, List[str]]] = []
        for item_id in selected:
            full_row_values = tuple(str(v) for v in self.tree.item(item_id, "values"))
            partial_values: List[str] = []
            for col_name in copy_columns:
                col_index = self.columns.index(col_name)
                partial_values.append(full_row_values[col_index] if col_index < len(full_row_values) else "")
            copied_rows.append(tuple(partial_values))

            tag_map: Dict[str, List[str]] = {}
            for col_name in self.tag_selector_cols:
                if col_name not in copy_columns:
                    continue
                col_index = self.columns.index(col_name)
                fallback = full_row_values[col_index] if col_index < len(full_row_values) else ""
                tag_map[col_name] = self._get_item_tag_ids(item_id, col_name, str(fallback))
            copied_tag_ids.append(tag_map)

        self._copied_columns = copy_columns
        self._copied_rows = copied_rows
        self._copied_tag_ids = copied_tag_ids
        copied_labels = [self.headings.get(col_name, col_name) for col_name in copy_columns]
        self._set_error(f"Copied {len(copied_rows)} row(s): {', '.join(copied_labels)}")
        return "break"

    def _on_paste_rows(self, _event=None) -> str:
        """
        Paste copied rows onto currently selected rows.

        Behavior:
        - Overwrite selected rows only (no insertion).
        - If copied row count differs, source rows are reused cyclically.
        """
        self._commit_edit(force=True)
        if not self._copied_rows:
            self._set_error("Paste skipped: copy rows first with Ctrl+C.")
            self.bell()
            return "break"
        if not self._copied_columns:
            self._set_error("Paste skipped: copy columns are not available.")
            self.bell()
            return "break"

        targets = self._selected_data_item_ids_sorted()
        if not targets:
            self._set_error("Paste skipped: select target row(s).")
            self.bell()
            return "break"

        self._record_undo_snapshot()
        source_len = len(self._copied_rows)
        for index, target_item_id in enumerate(targets):
            source_index = index % source_len
            partial_values = list(self._copied_rows[source_index])
            target_values = list(self.tree.item(target_item_id, "values"))
            if len(target_values) < len(self.columns):
                target_values.extend([""] * (len(self.columns) - len(target_values)))
            for partial_idx, col_name in enumerate(self._copied_columns):
                if col_name not in self.columns:
                    continue
                col_index = self.columns.index(col_name)
                value = partial_values[partial_idx] if partial_idx < len(partial_values) else ""
                target_values[col_index] = value

            self.tree.item(target_item_id, values=target_values)

            source_tag_map = self._copied_tag_ids[source_index] if source_index < len(self._copied_tag_ids) else {}
            for col_name in self.tag_selector_cols:
                if col_name not in self._copied_columns:
                    continue
                col_index = self.columns.index(col_name)
                fallback = target_values[col_index] if col_index < len(target_values) else ""
                copied_ids = list(source_tag_map.get(col_name, self._normalize_tag_ids(str(fallback))))
                self._set_item_tag_ids(target_item_id, col_name, copied_ids)

        self._hide_overlays()
        self._rebuild_filter_values()
        self._apply_filters()

        visible_targets = [iid for iid in targets if self.tree.exists(iid) and self.tree.parent(iid) == ""]
        if visible_targets:
            self.tree.selection_set(visible_targets)
            self.tree.see(visible_targets[-1])
        else:
            self.tree.selection_remove(self.tree.selection())

        self._set_error(
            f"Pasted {len(self._copied_rows)} copied row(s) to {len(targets)} selected row(s)."
        )
        return "break"

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
        for item_id in self._iter_data_item_ids():
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

        items = self._iter_data_item_ids()

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
        self._data_item_ids = items
        self._apply_filters()

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
        if item_id == FILTER_SPACER_IID:
            self._hide_overlays()
            col_index = int(col_id.replace("#", "")) - 1
            col_name = self.columns[col_index]
            if col_name != self.action_col:
                self._begin_filter_combobox_edit(col_name)
            return "break"

        col_index = int(col_id.replace("#", "")) - 1
        col_name = self.columns[col_index]

        if not self._handle_editor_transition_on_cell_change(item_id, col_name):
            return

        if col_name == self.action_col:
            self._show_action_button(item_id)
            return

        if col_name in self.tag_selector_cols:
            self._hide_overlays()
            self._open_tag_selector_dialog(item_id, col_name)
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
        if item_id == FILTER_SPACER_IID:
            col_index = int(col_id.replace("#", "")) - 1
            col_name = self.columns[col_index]
            if col_name != self.action_col:
                self._begin_filter_combobox_edit(col_name)
            return "break"

        col_index = int(col_id.replace("#", "")) - 1
        col_name = self.columns[col_index]

        if col_name == self.action_col or col_name in self.checkbox_cols or col_name in self.tag_selector_cols:
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
        if editing_item_id == FILTER_SPACER_IID:
            self._commit_edit(force=True)
            return self._editor is None
        ok, _ = self.validate_cell(editing_col_name, current_value)
        if ok:
            self._commit_edit(force=False)
            return self._editor is None

        self._revert_current_edit()
        return True

    def _toggle_checkbox(self, item_id: str, col_name: str) -> None:
        """チェックボックス列の表示値をトグルする。"""
        self._record_undo_snapshot()
        idx = self.columns.index(col_name)
        vals = list(self.tree.item(item_id, "values"))
        vals[idx] = CHECK_OFF if vals[idx] == CHECK_ON else CHECK_ON
        self.tree.item(item_id, values=vals)
        self._rebuild_filter_values()
        self._apply_filters()

    def _open_tag_selector_dialog(self, item_id: str, col_name: str) -> None:
        """タグ列セルをクリックした際にタグ選択フォームを表示する。"""
        available_tag_items = list(self.tag_items)
        if not available_tag_items:
            self._set_error("No tags are configured.")
            return

        col_index = self.columns.index(col_name)
        vals = list(self.tree.item(item_id, "values"))
        current_value = str(vals[col_index]) if col_index < len(vals) else ""
        selected_tag_ids = set(self._get_item_tag_ids(item_id, col_name, current_value))

        dialog = tk.Toplevel(self)
        dialog.title(f"Select {self.headings.get(col_name, col_name)}")
        dialog.transient(self.winfo_toplevel())
        dialog.resizable(True, True)
        dialog.grab_set()

        body = ttk.Frame(dialog, padding=10)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text="UseをONにしてOKを押すと、選択したタグIDに対応する表示名をセルへ反映します。").pack(
            anchor="w", pady=(0, 6)
        )

        table_wrap = ttk.Frame(body)
        table_wrap.pack(fill="both", expand=True)

        visible_rows = min(max(len(available_tag_items), 6), 12)
        tag_tree = ttk.Treeview(
            table_wrap,
            columns=("use", "tag_id", "tag_name", "category", "description"),
            show="headings",
            selectmode="browse",
            height=visible_rows,
            style=self.table_config.tree_style_name,
        )
        tag_tree.heading("use", text="Use")
        tag_tree.heading("tag_id", text="Tag ID")
        tag_tree.heading("tag_name", text="タグ名")
        tag_tree.heading("category", text="Category")
        tag_tree.heading("description", text="説明")
        tag_tree.column("use", width=72, minwidth=72, anchor="center", stretch=False)
        tag_tree.column("tag_id", width=180, minwidth=140, anchor="w", stretch=False)
        tag_tree.column("tag_name", width=140, minwidth=120, anchor="w", stretch=False)
        tag_tree.column("category", width=120, minwidth=90, anchor="w", stretch=False)
        tag_tree.column("description", width=300, minwidth=220, anchor="w", stretch=True)

        yscroll = ttk.Scrollbar(table_wrap, orient="vertical", command=tag_tree.yview)
        tag_tree.configure(yscrollcommand=yscroll.set)
        tag_tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        table_wrap.grid_rowconfigure(0, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)

        row_iid_by_tag_id: Dict[str, str] = {}
        tag_use_state: Dict[str, bool] = {
            item.tag_id: (item.tag_id in selected_tag_ids) for item in available_tag_items
        }
        for item in available_tag_items:
            use_text = CHECK_ON if tag_use_state[item.tag_id] else CHECK_OFF
            description = item.description or self.table_config.tag_descriptions.get(item.name, "")
            row_iid = tag_tree.insert(
                "",
                "end",
                values=(use_text, item.tag_id, item.name, item.category, description),
            )
            row_iid_by_tag_id[item.tag_id] = row_iid

        def refresh_row_use(tag_id: str) -> None:
            row_iid = row_iid_by_tag_id.get(tag_id, "")
            if not row_iid:
                return
            row_values = list(tag_tree.item(row_iid, "values"))
            if len(row_values) < 5:
                return
            row_values[0] = CHECK_ON if tag_use_state.get(tag_id, False) else CHECK_OFF
            tag_tree.item(row_iid, values=row_values)

        def toggle_use_for_row(row_iid: str) -> None:
            if not row_iid:
                return
            row_values = list(tag_tree.item(row_iid, "values"))
            if len(row_values) < 2:
                return
            tag_id = str(row_values[1]).strip()
            if not tag_id:
                return
            tag_use_state[tag_id] = not tag_use_state.get(tag_id, False)
            refresh_row_use(tag_id)

        def on_tree_click(event) -> Optional[str]:
            region = tag_tree.identify("region", event.x, event.y)
            if region != "cell":
                return None
            row_iid = tag_tree.identify_row(event.y)
            col_id = tag_tree.identify_column(event.x)
            if row_iid and col_id == "#1":
                toggle_use_for_row(row_iid)
                return "break"
            return None

        def on_tree_double_click(event) -> Optional[str]:
            row_iid = tag_tree.identify_row(event.y)
            if row_iid:
                toggle_use_for_row(row_iid)
                return "break"
            return None

        def on_tree_space(_event) -> str:
            selected_iids = tag_tree.selection()
            if selected_iids:
                toggle_use_for_row(selected_iids[0])
            return "break"

        tag_tree.bind("<Button-1>", on_tree_click, add=True)
        tag_tree.bind("<Double-1>", on_tree_double_click, add=True)
        tag_tree.bind("<space>", on_tree_space, add=True)

        buttons = ttk.Frame(body)
        buttons.pack(fill="x", pady=(10, 0))

        def on_ok() -> None:
            selected_ids = [item.tag_id for item in available_tag_items if tag_use_state.get(item.tag_id, False)]
            current_ids = self._get_item_tag_ids(item_id, col_name, current_value)
            if selected_ids != current_ids:
                self._record_undo_snapshot()
            self._set_item_tag_ids(item_id, col_name, selected_ids)
            vals[col_index] = self._format_tag_display_text(selected_ids)
            self.tree.item(item_id, values=vals)
            self._rebuild_filter_values()
            self._apply_filters()
            dialog.destroy()

        def on_cancel() -> None:
            dialog.destroy()

        ttk.Button(buttons, text="OK", command=on_ok).pack(side="right")
        ttk.Button(buttons, text="Cancel", command=on_cancel).pack(side="right", padx=(0, 6))

        dialog.bind("<Return>", lambda _e: on_ok())
        dialog.bind("<Escape>", lambda _e: on_cancel())
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)
        dialog_width = 860
        dialog_height = min(700, max(460, 180 + (visible_rows * self.table_config.row_height)))
        dialog.minsize(760, 420)
        dialog.geometry(f"{dialog_width}x{dialog_height}")
        dialog.focus_set()

    def _parse_tag_text(self, text: str) -> List[str]:
        """セル文字列からタグ名リストへ変換する。"""
        if not text:
            return []
        return [part.strip() for part in re.split(r"\s*,\s*", text.strip()) if part.strip()]

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

    def _begin_filter_combobox_edit(self, col_name: str) -> None:
        """フィルター行セルに対するCombobox編集を開始する。"""
        self._commit_edit(force=True)

        item_id = FILTER_SPACER_IID
        col_index = self.columns.index(col_name)
        bbox = self.tree.bbox(item_id, column=f"#{col_index + 1}")
        if not bbox:
            return
        x, y, w, h = bbox

        current = self._filter_values.get(col_name, FILTER_ALL)
        values = list(self._filter_candidates.get(col_name, [FILTER_ALL]))
        if not values:
            values = [FILTER_ALL]
        if current not in values:
            values.insert(0, current)

        cb = ttk.Combobox(self.tree, values=values, state="normal")
        cb.set(current)
        cb.place(x=x, y=y, width=w, height=h)

        self._editor = cb
        self._editing = (item_id, col_name)
        self._editing_original = current
        self._editing_bbox = bbox
        self._invalid = False
        self._clear_error()

        cb.bind("<<ComboboxSelected>>", lambda e: self._on_filter_input_change(col_name, cb))
        cb.bind("<KeyRelease>", lambda e: self._on_filter_input_change(col_name, cb))
        cb.bind("<Return>", lambda e: self._commit_edit(force=False))
        cb.bind("<Escape>", lambda e: self._cancel_edit())
        cb.bind("<FocusOut>", lambda e: self._on_combobox_focus_out(cb))

        cb.focus_set()

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

        if item_id == FILTER_SPACER_IID:
            ok, msg = self._commit_filter_edit(col_name, new_value)
            if not ok and not force:
                self._apply_validation_ui(False, msg)
                return
            self._destroy_editor()
            if ok:
                self._clear_error()
            else:
                self._set_error(msg)
            return

        if col_name in self.custom_dropdown_cols and new_value and new_value not in self.dropdown_values[col_name]:
            self.dropdown_values[col_name].append(new_value)

        ok, msg = self.validate_cell(col_name, new_value)
        if not ok and not force:
            self._apply_validation_ui(False, msg)
            return

        vals = list(self.tree.item(item_id, "values"))
        old_value = str(vals[col_index]) if col_index < len(vals) else ""
        if new_value != old_value:
            self._record_undo_snapshot()
        vals[col_index] = new_value
        self.tree.item(item_id, values=vals)
        self._rebuild_filter_values()
        self._apply_filters()

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
            if item_id == FILTER_SPACER_IID:
                self._filter_values[col_name] = self._editing_original
                self._refresh_filter_row_values()
                self._destroy_editor()
                return
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

    def _iter_data_item_ids(self) -> List[str]:
        """Return existing data row IDs excluding the filter spacer row."""
        return [
            item_id
            for item_id in self._data_item_ids
            if item_id != FILTER_SPACER_IID and self.tree.exists(item_id)
        ]

    def _insert_filter_spacer_row(self) -> None:
        """Insert a first-row filter row."""
        if self.tree.exists(FILTER_SPACER_IID):
            return
        self.tree.insert(
            "",
            0,
            iid=FILTER_SPACER_IID,
            values=self._build_filter_row_values(),
            tags=("filter_row",),
        )

    def _move_filter_spacer_to_top(self) -> None:
        """Keep the filter row pinned to the top."""
        if self.tree.exists(FILTER_SPACER_IID):
            self.tree.move(FILTER_SPACER_IID, "", 0)

    def _build_filter_row_values(self) -> Tuple[object, ...]:
        """Build the visible values for the filter row."""
        values = []
        for col in self.columns:
            if col == self.action_col:
                values.append("")
            else:
                values.append(self._filter_values.get(col, FILTER_ALL))
        return tuple(values)

    def _refresh_filter_row_values(self) -> None:
        """Redraw current filter values on the filter row."""
        if not self.tree.exists(FILTER_SPACER_IID):
            return
        self.tree.item(FILTER_SPACER_IID, values=self._build_filter_row_values())

    def _rebuild_filter_values(self) -> None:
        """Refresh filter candidates from current data rows."""
        for col in self.columns:
            if col == self.action_col:
                continue
            col_index = self.columns.index(col)
            values = []
            for item_id in self._iter_data_item_ids():
                row_values = self.tree.item(item_id, "values")
                if col_index < len(row_values):
                    cell_text = str(row_values[col_index])
                    if col in self.tag_selector_cols:
                        values.extend(self._parse_tag_text(cell_text))
                    else:
                        values.append(cell_text)
            if col in self.tag_selector_cols:
                values.extend(self._all_tag_display_names())
            uniq = sorted(set(values))
            candidates = [FILTER_ALL] + uniq
            self._filter_candidates[col] = candidates
            current = self._filter_values.get(col, FILTER_ALL)
            if current != FILTER_ALL:
                if self._is_numeric_filter_column(col):
                    if not self._is_valid_numeric_filter(col, current):
                        self._filter_values[col] = FILTER_ALL
                elif not self._is_valid_regex(self._to_effective_regex(current)):
                    self._filter_values[col] = FILTER_ALL
        self._refresh_filter_row_values()

    def _row_matches_filters(self, item_id: str) -> bool:
        """Check whether a row satisfies all active filter selections."""
        row_values = self.tree.item(item_id, "values")
        for col, selected in self._filter_values.items():
            if col == self.action_col:
                continue
            col_index = self.columns.index(col)
            value = str(row_values[col_index]) if col_index < len(row_values) else ""
            if not self._match_filter_value(col, value, selected):
                return False
        return True

    def _apply_filters(self) -> None:
        """Apply filter row selections by detaching non-matching rows."""
        data_item_ids = self._iter_data_item_ids()
        for item_id in data_item_ids:
            self.tree.detach(item_id)
        for item_id in data_item_ids:
            if self._row_matches_filters(item_id):
                self.tree.reattach(item_id, "", "end")
        self._refresh_filter_row_values()
        self._move_filter_spacer_to_top()

    def _on_filter_input_change(self, col_name: str, cb: ttk.Combobox) -> None:
        """Apply filter immediately while typing in filter combobox."""
        if self._editor is not cb or self._editing != (FILTER_SPACER_IID, col_name):
            return
        ok, msg = self._commit_filter_edit(col_name, cb.get())
        if ok:
            self._invalid = False
            self._clear_error()
        else:
            self._invalid = True
            self._set_error(msg)

    def _commit_filter_edit(self, col_name: str, new_value: str) -> Tuple[bool, str]:
        """Commit one filter cell change and re-apply row filtering."""
        if col_name == self.action_col:
            return True, ""

        normalized = new_value.strip()
        if not normalized:
            normalized = FILTER_ALL
        if normalized != FILTER_ALL:
            if self._is_numeric_filter_column(col_name):
                if not self._is_valid_numeric_filter(col_name, normalized):
                    return False, f"Invalid numeric filter for {col_name}"
            else:
                effective_pattern = self._to_effective_regex(normalized)
                if not self._is_valid_regex(effective_pattern):
                    return False, f"Invalid regex for {col_name}"

        self._filter_values[col_name] = normalized

        self._apply_filters()
        return True, ""

    def _is_valid_regex(self, pattern: str) -> bool:
        """Return True if the pattern can be compiled as regex."""
        try:
            re.compile(pattern)
            return True
        except re.error:
            return False

    def _to_effective_regex(self, selected: str) -> str:
        """
        Convert wildcard shorthand to effective regex.

        Special cases:
        - "text*" -> "^text.*"
        - "*text" -> "text$"
        - "*text*" -> "text" (contains)
        - "a*b" -> "a.*b" (order match)
        """
        s = selected.strip()
        if s == FILTER_ALL:
            return s

        if not self._contains_regex_meta_except_star(s):
            # Keep explicit edge wildcard semantics.
            if s.startswith("*") and s.endswith("*") and len(s) >= 2:
                inner = s[1:-1].strip()
                return re.escape(inner) if inner else ".*"
            if s.endswith("*") and not s.startswith("*"):
                prefix = s[:-1].strip()
                return f"^{re.escape(prefix)}.*"
            if s.startswith("*") and not s.endswith("*"):
                suffix = s[1:].strip()
                return f"{re.escape(suffix)}$"
            # Internal wildcard(s): match tokens in order.
            if "*" in s:
                parts = [re.escape(part.strip()) for part in s.split("*") if part.strip()]
                if not parts:
                    return ".*"
                return ".*".join(parts)
        return s

    @staticmethod
    def _contains_regex_meta_except_star(text: str) -> bool:
        """Return True if text includes regex metacharacters except '*'."""
        return any(ch in ".^$+?{}[]|()\\" for ch in text)

    def _is_numeric_filter_column(self, col_name: str) -> bool:
        """Return True for numeric filter columns."""
        return self.sort_types.get(col_name) in ("int", "float")

    def _is_valid_numeric_filter(self, col_name: str, selected: str) -> bool:
        """Return True if selected text can be parsed for the numeric column type."""
        try:
            if self.sort_types.get(col_name) == "int":
                int(selected)
            elif self.sort_types.get(col_name) == "float":
                float(selected)
            else:
                return False
            return True
        except Exception:
            return False

    def _match_filter_value(self, col_name: str, value: str, selected: str) -> bool:
        """Match one cell value against filter text."""
        if selected == FILTER_ALL:
            return True
        if self._is_numeric_filter_column(col_name):
            try:
                if self.sort_types.get(col_name) == "int":
                    return int(value) == int(selected)
                return float(value) == float(selected)
            except Exception:
                return False

        if col_name in self.tag_selector_cols:
            try:
                pattern = self._to_effective_regex(selected)
                return any(re.search(pattern, tag) is not None for tag in self._parse_tag_text(value))
            except re.error:
                return False

        try:
            return re.search(self._to_effective_regex(selected), value) is not None
        except re.error:
            return False


# ============================================================
# Test Section (future split target)
# File name (future): test_sortable_table_regex_filter.py
# ============================================================
def test_regex_filter_mece() -> bool:
    """
    MECE coverage for regex filter behavior.

    Scope:
    - Valid regex: all rows match
    - Valid regex: subset rows match
    - Valid regex: no rows match
    - Invalid regex: rejected

    Returns:
    - True: all tests passed
    - False: any test failed
    """
    root = tk.Tk()
    root.withdraw()
    table = SortableTableDemo(root)

    category_col = "category"
    category_index = table.columns.index(category_col)
    id_col = "id"
    id_index = table.columns.index(id_col)

    def visible_categories() -> List[str]:
        visible_item_ids = [iid for iid in table.tree.get_children("") if iid != FILTER_SPACER_IID]
        return [str(table.tree.item(iid, "values")[category_index]) for iid in visible_item_ids]

    def visible_ids() -> List[int]:
        visible_item_ids = [iid for iid in table.tree.get_children("") if iid != FILTER_SPACER_IID]
        return [int(table.tree.item(iid, "values")[id_index]) for iid in visible_item_ids]

    all_categories = sorted({str(row[category_col]) for row in table.table_config.demo_rows})
    cases = [
        {
            "name": "all_rows_empty_pattern",
            "pattern": "",
            "expect_ok": True,
            "expected": all_categories,
        },
        {
            "name": "subset_prefix_anchor",
            "pattern": "^D.*",
            "expect_ok": True,
            "expected": sorted(["Daily", "Drink"]),
        },
        {
            "name": "subset_wildcard_prefix",
            "pattern": "D*",
            "expect_ok": True,
            "expected": sorted(["Daily", "Drink"]),
        },
        {
            "name": "subset_wildcard_suffix",
            "pattern": "*nk",
            "expect_ok": True,
            "expected": sorted(["Drink"]),
        },
        {
            "name": "subset_wildcard_suffix_with_space",
            "pattern": "* nk",
            "expect_ok": True,
            "expected": sorted(["Drink"]),
        },
        {
            "name": "subset_wildcard_contains",
            "pattern": "*nk*",
            "expect_ok": True,
            "expected": sorted(["Drink"]),
        },
        {
            "name": "subset_wildcard_contains_with_space",
            "pattern": "* nk *",
            "expect_ok": True,
            "expected": sorted(["Drink"]),
        },
        {
            "name": "subset_wildcard_order_internal",
            "pattern": "D*nk",
            "expect_ok": True,
            "expected": sorted(["Drink"]),
        },
        {
            "name": "subset_alternation",
            "pattern": "^(Food|Work)$",
            "expect_ok": True,
            "expected": sorted(["Food", "Work"]),
        },
        {
            "name": "no_rows_pattern",
            "pattern": "^Z",
            "expect_ok": True,
            "expected": [],
        },
        {
            "name": "invalid_regex",
            "pattern": "[",
            "expect_ok": False,
            "expected": None,
        },
    ]

    failures: List[str] = []
    try:
        for case in cases:
            ok, msg = table._commit_filter_edit(category_col, case["pattern"])
            if ok != case["expect_ok"]:
                failures.append(
                    f"{case['name']}: ok={ok}, expected_ok={case['expect_ok']}, msg={msg}"
                )
                continue

            if case["expect_ok"]:
                got = sorted(set(visible_categories()))
                expected = case["expected"]
                if got != expected:
                    failures.append(f"{case['name']}: got={got}, expected={expected}")

        numeric_cases = [
            {
                "name": "numeric_exact_id",
                "pattern": "2",
                "expect_ok": True,
                "expected_ids": [2],
            },
            {
                "name": "numeric_invalid_regex_like",
                "pattern": "^2$",
                "expect_ok": False,
                "expected_ids": None,
            },
        ]

        table._commit_filter_edit(category_col, FILTER_ALL)
        for case in numeric_cases:
            ok, msg = table._commit_filter_edit(id_col, case["pattern"])
            if ok != case["expect_ok"]:
                failures.append(
                    f"{case['name']}: ok={ok}, expected_ok={case['expect_ok']}, msg={msg}"
                )
                continue

            if case["expect_ok"]:
                got_ids = sorted(set(visible_ids()))
                expected_ids = case["expected_ids"]
                if got_ids != expected_ids:
                    failures.append(f"{case['name']}: got={got_ids}, expected={expected_ids}")

        if failures:
            print("[test_regex_filter_mece] FAILED")
            for failure in failures:
                print(f" - {failure}")
            return False

        print("[test_regex_filter_mece] PASSED")
        return True
    finally:
        table.destroy()
        root.destroy()


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

    # test
    test_regex_filter_mece()

    root.mainloop()


if __name__ == "__main__":
    main()

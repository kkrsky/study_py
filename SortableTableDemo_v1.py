import tkinter as tk
from tkinter import ttk
from datetime import datetime

CHECK_ON = "☑"
CHECK_OFF = "☐"


class SortableTableDemo(ttk.Frame):
    """
    - ヘッダクリックでソート
    - Active列クリックで ☑/☐ トグル
    - Dropdown列: ダブルクリックでCombobox編集
    - その他列: ダブルクリックでEntry編集
    - Action列: セル上に“本物のボタン”をオーバーレイ表示して押せる
    - バリデーション: 入力中にセルを赤く、フォーム下部にエラーメッセージ表示（ポップアップなし）
    """

    def __init__(self, parent):
        super().__init__(parent)

        # ---- 列（MECE: ID/text/numeric/date/enum/bool/action）----
        self.columns = (
            "id", "title", "category", "status",
            "active", "qty", "price", "progress", "due", "action", "notes"
        )
        self.headings = {
            "id": "ID",
            "title": "Title",
            "category": "Category",
            "status": "Status",
            "active": "Active",
            "qty": "Qty",
            "price": "Price",
            "progress": "Progress(%)",
            "due": "Due(YYYY-MM-DD)",
            "action": "Action(Button)",
            "notes": "Notes",
        }

        self.sort_types = {
            "id": "int",
            "title": "text",
            "category": "text",
            "status": "text",
            "active": "bool",
            "qty": "int",
            "price": "float",
            "progress": "int",
            "due": "date",
            "action": "text",
            "notes": "text",
        }
        self.sort_ascending = {c: True for c in self.columns}

        # enum候補
        self.dropdown_values = {
            "category": ["Food", "Drink", "Daily", "Work", "Hobby"],
            "status": ["New", "Hold", "Done", "Canceled"],
        }
        self.dropdown_cols = set(self.dropdown_values.keys())
        self.checkbox_cols = {"active"}
        self.action_col = "action"

        # インライン編集（Entry/Combobox）
        self._editor = None              # tk.Entry or ttk.Combobox
        self._editing = None             # (item_id, col_name)
        self._editing_bbox = None        # (x,y,w,h) - 色反映のため
        self._editor_var = None          # tk.StringVar
        self._invalid = False            # 現在編集セルが不正か
        self._last_error = ""            # エラー文
        self._editing_original = None    # 元の値（変更有無判定）

        # ボタンオーバーレイ
        self._action_button = None
        self._action_target = None       # item_id

        self._build_ui()
        self._insert_demo_rows()

        # イベント
        self.tree.bind("<Button-1>", self._on_click, add=True)
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Escape>", lambda e: self._cancel_edit())

        # スクロールやサイズ変更時にオーバーレイを隠す（ズレ防止）
        self.tree.bind("<Configure>", lambda e: self._hide_overlays())
        self.tree.bind("<MouseWheel>", lambda e: self._hide_overlays(), add=True)

    # ---------------- UI ----------------
    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=(10, 6))

        ttk.Label(
            top,
            text="ヘッダ:ソート / Active:クリックで☑ / Actionセル:ボタン表示→押下 / ダブルクリック:編集（赤＝不正）"
        ).pack(side="left")

        ttk.Button(top, text="行追加", command=self.add_row).pack(side="right")
        ttk.Button(top, text="選択行削除", command=self.delete_selected).pack(side="right", padx=6)
        ttk.Button(top, text="全件バリデーション", command=self.validate_all_rows).pack(side="right", padx=6)

        mid = ttk.Frame(self)
        mid.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        self.tree = ttk.Treeview(mid, columns=self.columns, show="headings", selectmode="extended")

        for col in self.columns:
            self.tree.heading(col, text=self.headings[col], command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=120, anchor="w")

        self.tree.column("id", width=60, anchor="e")
        self.tree.column("active", width=70, anchor="center")
        self.tree.column("qty", width=70, anchor="e")
        self.tree.column("price", width=90, anchor="e")
        self.tree.column("progress", width=110, anchor="e")
        self.tree.column("due", width=130, anchor="w")
        self.tree.column("action", width=130, anchor="center")
        self.tree.column("notes", width=220, anchor="w")

        xscroll = ttk.Scrollbar(mid, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=xscroll.set)

        yscroll = ttk.Scrollbar(mid, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        mid.grid_rowconfigure(0, weight=1)
        mid.grid_columnconfigure(0, weight=1)

        # エラーバー（ポップアップの代わり）
        self.error_bar = ttk.Label(self, text="", anchor="w")
        self.error_bar.pack(fill="x", padx=10, pady=(0, 10))

        # ttk側の“赤背景”はOSテーマで効きにくいので、
        # Entry編集は tk.Entry を使い bg変更を確実にする（下で実装）。

    def _insert_demo_rows(self):
        rows = [
            (1, "Buy apples", "Food", "New", True, 10, 120.5, 0, "2026-02-05", "Run", "From supermarket"),
            (2, "Make coffee", "Drink", "Hold", True, 1, 980.0, 20, "2026-02-01", "Run", "Try new beans"),
            (3, "Daily jog", "Daily", "Done", False, 1, 0.0, 100, "2026-01-25", "Run", "5km"),
            (4, "Write report", "Work", "New", True, 1, 0.0, 10, "2026-02-10", "Run", "Draft first"),
            (5, "Blender practice", "Hobby", "Hold", True, 1, 0.0, 35, "2026-02-12", "Run", "Modeling"),
        ]
        for r in rows:
            self.tree.insert("", "end", values=self._normalize_row(r))

    def _normalize_row(self, row_tuple):
        row = list(row_tuple)
        active_idx = self.columns.index("active")
        row[active_idx] = CHECK_ON if row[active_idx] else CHECK_OFF
        return tuple(row)

    # ---------------- Error UI ----------------
    def _set_error(self, message: str):
        self._last_error = message
        self.error_bar.config(text=message)

    def _clear_error(self):
        self._last_error = ""
        self.error_bar.config(text="")

    # ---------------- Data ops ----------------
    def add_row(self):
        next_id = len(self.tree.get_children()) + 1
        today = datetime.now().strftime("%Y-%m-%d")
        row = (
            next_id, f"Task {next_id}",
            self.dropdown_values["category"][0],
            self.dropdown_values["status"][0],
            True,
            0, 0.0, 0, today, "Run", ""
        )
        self.tree.insert("", "end", values=self._normalize_row(row))

    def delete_selected(self):
        self._commit_edit(force=True)
        for item_id in self.tree.selection():
            self.tree.delete(item_id)

    def get_data(self):
        out = []
        for item_id in self.tree.get_children(""):
            vals = list(self.tree.item(item_id, "values"))
            d = {col: vals[i] for i, col in enumerate(self.columns)}
            d["active"] = (d["active"] == CHECK_ON)
            # 変換できる範囲で変換
            d["id"] = self._try_int(d["id"])
            d["qty"] = self._try_int(d["qty"])
            d["progress"] = self._try_int(d["progress"])
            d["price"] = self._try_float(d["price"])
            out.append(d)
        return out

    @staticmethod
    def _try_int(x):
        try:
            return int(x)
        except Exception:
            return x

    @staticmethod
    def _try_float(x):
        try:
            return float(x)
        except Exception:
            return x

    # ---------------- Validation ----------------
    def validate_cell(self, col_name: str, value: str) -> tuple[bool, str]:
        v = value.strip()

        # enum
        if col_name in self.dropdown_cols:
            if col_name == "category":
                return True, ""
            if v not in self.dropdown_values[col_name]:
                return False, f"{col_name} は候補から選択してください: {self.dropdown_values[col_name]}"
            return True, ""

        # bool
        if col_name in self.checkbox_cols:
            if v not in (CHECK_ON, CHECK_OFF):
                return False, f"{col_name} は {CHECK_ON}/{CHECK_OFF} のみ"
            return True, ""

        # numeric
        if col_name == "id":
            try:
                if int(v) < 0:
                    return False, "ID は 0以上の整数"
            except Exception:
                return False, "ID は整数"
            return True, ""

        if col_name == "qty":
            try:
                if int(v) < 0:
                    return False, "Qty は 0以上の整数"
            except Exception:
                return False, "Qty は整数"
            return True, ""

        if col_name == "progress":
            try:
                p = int(v)
                if not (0 <= p <= 100):
                    return False, "Progress は 0〜100 の整数"
            except Exception:
                return False, "Progress は整数(0〜100)"
            return True, ""

        if col_name == "price":
            try:
                if float(v) < 0:
                    return False, "Price は 0以上の数値"
            except Exception:
                return False, "Price は数値"
            return True, ""

        # date
        if col_name == "due":
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except Exception:
                return False, "Due は YYYY-MM-DD 形式の正しい日付"
            return True, ""

        # action列は固定文言でも自由でもOK（ここでは常にOK）
        return True, ""

    def validate_all_rows(self):
        self._commit_edit(force=True)
        for item_id in self.tree.get_children(""):
            vals = list(self.tree.item(item_id, "values"))
            for i, col in enumerate(self.columns):
                ok, msg = self.validate_cell(col, str(vals[i]))
                if not ok:
                    self._set_error(f"RowID={vals[self.columns.index('id')]} / {col}: {msg}")
                    return False
        self._set_error("全てOKです。")
        return True

    # ---------------- Sorting ----------------
    def sort_by_column(self, col: str):
        # 不正入力中はソートしない（行が動いて編集位置が壊れるため）
        if self._editor is not None and self._invalid:
            self._set_error("修正が必要です（赤いセル）。ソート前に入力を正しくしてください。")
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
                    return (0, datetime.strptime(v, "%Y-%m-%d"))
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

    # ---------------- Click / double click ----------------
    def _on_click(self, event):
        region = self.tree.identify("region", event.x, event.y)

        # 表外クリック：編集を確定（ただし不正なら確定させない）
        if region != "cell":
            self._commit_edit(force=False)
            self._hide_overlays()
            return

        item_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if not item_id or not col_id:
            self._commit_edit(force=False)
            self._hide_overlays()
            return

        col_index = int(col_id.replace("#", "")) - 1
        col_name = self.columns[col_index]

        # Action列：セル上に“本物のボタン”を出す
        if col_name == self.action_col:
            # 不正入力中ならボタン操作より修正優先
            if self._editor is not None and self._invalid:
                self._set_error("修正が必要です（赤いセル）。ボタン実行前に入力を正しくしてください。")
                return
            self._commit_edit(force=True)
            self._show_action_button(item_id)
            return

        # checkbox列：クリックでトグル
        if col_name in self.checkbox_cols:
            if self._editor is not None and self._invalid:
                self._set_error("修正が必要です（赤いセル）。チェック変更前に入力を正しくしてください。")
                return
            self._commit_edit(force=True)
            self._hide_overlays()
            self._toggle_checkbox(item_id, col_name)
            return

        # dropdown列はシングルクリックで編集開始
        if col_name in self.dropdown_cols:
            if self._editor is not None and self._invalid:
                self._set_error("修正が必要です（赤いセル）。先に入力を正しくしてください。")
                return
            self._hide_overlays()
            self._begin_combobox_edit(item_id, col_name)
            return

        # 他セルクリック：編集確定（不正なら確定しない＝編集を継続）
        self._hide_overlays()
        self._commit_edit(force=False)

    def _on_double_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        item_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if not item_id or not col_id:
            return

        col_index = int(col_id.replace("#", "")) - 1
        col_name = self.columns[col_index]

        # action/checkboxは編集しない
        if col_name == self.action_col or col_name in self.checkbox_cols:
            return

        # 不正入力中は他セル編集に移れない
        if self._editor is not None and self._invalid:
            self._set_error("修正が必要です（赤いセル）。先に入力を正しくしてください。")
            self._cancel_edit()

        self._hide_overlays()
        if col_name in self.dropdown_cols:
            return
        self._begin_entry_edit(item_id, col_name)

    def _toggle_checkbox(self, item_id: str, col_name: str):
        idx = self.columns.index(col_name)
        vals = list(self.tree.item(item_id, "values"))
        vals[idx] = CHECK_OFF if vals[idx] == CHECK_ON else CHECK_ON
        self.tree.item(item_id, values=vals)

    # ---------------- Action button overlay ----------------
    def _show_action_button(self, item_id: str):
        self._hide_overlays()

        col_index = self.columns.index(self.action_col)
        bbox = self.tree.bbox(item_id, column=f"#{col_index + 1}")
        if not bbox:
            return
        x, y, w, h = bbox

        # “本物のボタン”をセル上に重ねる
        self._action_target = item_id
        self._action_button = ttk.Button(self.tree, text="Run", command=self._run_action_for_row)
        self._action_button.place(x=x, y=y, width=w, height=h)

    def _run_action_for_row(self):
        if not self._action_target:
            return
        item_id = self._action_target
        vals = list(self.tree.item(item_id, "values"))
        row_id = vals[self.columns.index("id")]
        title = vals[self.columns.index("title")]
        status = vals[self.columns.index("status")]
        self._set_error(f"Action実行: RowID={row_id} / Title='{title}' / Status='{status}'（ここで任意関数を呼べます）")
        # 任意の処理をここに書く（例：詳細画面を開く / API呼ぶ / ファイル出力 etc）

        self._hide_overlays()

    def _hide_overlays(self):
        if self._action_button is not None:
            self._action_button.destroy()
            self._action_button = None
            self._action_target = None

    # ---------------- Inline editors (with live validation) ----------------
    def _begin_combobox_edit(self, item_id: str, col_name: str):
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
        state = "normal" if col_name == "category" else "readonly"
        cb = ttk.Combobox(self.tree, values=values, state=state)
        cb.set(current if current else values[0])
        cb.place(x=x, y=y, width=w, height=h)

        self._editor = cb
        self._editing = (item_id, col_name)
        self._editing_bbox = bbox
        self._invalid = False
        self._clear_error()
        self._editing_original = current

        # Comboboxは入力中というより選択時に検証
        def on_change(_e=None):
            self._commit_edit(force=False)

        cb.bind("<<ComboboxSelected>>", on_change)
        cb.bind("<Return>", lambda e: self._commit_edit(force=False))
        cb.bind("<Escape>", lambda e: self._cancel_edit())
        cb.bind("<FocusOut>", lambda e: self._commit_edit(force=False))

        cb.focus_set()

    def _begin_entry_edit(self, item_id: str, col_name: str):
        self._commit_edit(force=True)

        col_index = self.columns.index(col_name)
        bbox = self.tree.bbox(item_id, column=f"#{col_index + 1}")
        if not bbox:
            return
        x, y, w, h = bbox

        vals = list(self.tree.item(item_id, "values"))
        current = str(vals[col_index])

        # ttk.Entryは背景色変更が効かない環境があるので、tk.Entryで確実に赤にする
        var = tk.StringVar(value=current)
        ent = tk.Entry(self.tree, textvariable=var, relief="solid", bd=1)
        ent.place(x=x, y=y, width=w, height=h)

        self._editor = ent
        self._editor_var = var
        self._editing = (item_id, col_name)
        self._editing_bbox = bbox
        self._invalid = False
        self._clear_error()
        self._editing_original = current

        def live_validate(*_):
            ok, msg = self.validate_cell(col_name, var.get())
            self._apply_validation_ui(ok, msg)

        # 入力中に随時検証
        var.trace_add("write", live_validate)

        ent.bind("<Return>", lambda e: self._commit_edit(force=False))
        ent.bind("<Escape>", lambda e: self._cancel_edit())
        ent.bind("<FocusOut>", lambda e: self._commit_edit(force=False))

        ent.focus_set()
        ent.selection_range(0, tk.END)
        live_validate()

    def _apply_validation_ui(self, ok: bool, msg: str):
        self._invalid = not ok
        if ok:
            self._clear_error()
        else:
            self._set_error(msg)

        # 背景色を変える（Entryのみ確実に反映）
        if isinstance(self._editor, tk.Entry) and not isinstance(self._editor, ttk.Combobox):
            self._editor.configure(bg=("white" if ok else "#ffcccc"))
        elif isinstance(self._editor, ttk.Combobox):
            style = ttk.Style(self)
            if ok:
                self._editor.configure(style="TCombobox")
            else:
                style.configure("Invalid.TCombobox", fieldbackground="#ffcccc")
                self._editor.configure(style="Invalid.TCombobox")

        # Comboboxはテーマ依存で色変更が難しいので、エラーバー表示で補助（必要ならStyleで拡張可能）
        # ※ “必ず赤くしたい”なら ComboboxをEntry風にして手入力＋候補リスト実装が必要になります。

    def _commit_edit(self, force: bool):
        """
        force=True: 強制確定（外部操作のために閉じる）
        force=False: 不正なら閉じずに編集継続（ここが“ポップアップ無しで赤にする”の肝）
        """
        if self._editor is None or self._editing is None:
            return

        item_id, col_name = self._editing
        col_index = self.columns.index(col_name)

        new_value = self._editor.get()
        selection = set(self.tree.selection())
        if col_name == "category" and new_value:
            if new_value not in self.dropdown_values["category"]:
                self.dropdown_values["category"].append(new_value)
        ok, msg = self.validate_cell(col_name, new_value)

        if not ok and not force:
            # 不正なら確定しない＝編集を続ける（赤セル＋エラーバー）
            self._apply_validation_ui(False, msg)
            return

        # ??????????????????????
        if col_name in self.dropdown_cols and new_value == self._editing_original:
            self._editor.destroy()
            self._editor = None
            self._editor_var = None
            self._editing = None
            self._editing_bbox = None
            self._editing_original = None
            self._invalid = False
            if ok:
                self._clear_error()
            else:
                self._set_error(msg)
            return

        # 強制確定時は「値を反映しない」ほうが安全な場合があるが、
        # ここでは force=True でも反映する（必要ならここを“元に戻す”に変更可）
        if col_name in self.dropdown_cols and len(selection) > 1:
            for sel_id in selection:
                vals = list(self.tree.item(sel_id, "values"))
                vals[col_index] = new_value
                self.tree.item(sel_id, values=vals)
        else:
            vals = list(self.tree.item(item_id, "values"))
            vals[col_index] = new_value
            self.tree.item(item_id, values=vals)

        self._editor.destroy()
        self._editor = None
        self._editor_var = None
        self._editing = None
        self._editing_bbox = None
        self._editing_original = None
        self._invalid = False

        if ok:
            self._clear_error()
        else:
            self._set_error(msg)

    def _cancel_edit(self):
        if self._editor is None:
            return
        self._editor.destroy()
        self._editor = None
        self._editor_var = None
        self._editing = None
        self._editing_bbox = None
        self._editing_original = None
        self._invalid = False
        self._clear_error()


def main():
    root = tk.Tk()
    root.title("tkinter Treeview: button column + live validation (no popup)")
    root.geometry("1250x520")

    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True)

    tab = ttk.Frame(nb)
    nb.add(tab, text="Table Demo")

    ui = SortableTableDemo(tab)
    ui.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()

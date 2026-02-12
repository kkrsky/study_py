import tkinter as tk
from tkinter import ttk, messagebox


class TagAndHeaderFilterDemo(ttk.Frame):
    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent, padding=12)
        self.pack(fill="both", expand=True)

        self.all_headers = ["ID", "Title", "Tags", "Status", "Owner", "Priority"]
        self.source_rows = [
            {"ID": "T001", "Title": "Login page", "Tags": "ui,auth", "Status": "Open", "Owner": "Alice", "Priority": "High"},
            {"ID": "T002", "Title": "Token refresh", "Tags": "backend,auth", "Status": "In Progress", "Owner": "Bob", "Priority": "Medium"},
            {"ID": "T003", "Title": "Export CSV", "Tags": "backend,report", "Status": "Done", "Owner": "Carol", "Priority": "Low"},
            {"ID": "T004", "Title": "Table style", "Tags": "ui,table", "Status": "Open", "Owner": "Dave", "Priority": "Low"},
            {"ID": "T005", "Title": "Filter logic", "Tags": "table,search", "Status": "In Progress", "Owner": "Erin", "Priority": "High"},
            {"ID": "T006", "Title": "Usage guide", "Tags": "doc,report", "Status": "Open", "Owner": "Frank", "Priority": "Medium"},
        ]

        self.all_tags = self._collect_all_tags()
        self.selected_tags = set(self.all_tags)
        self.selected_headers = list(self.all_headers)

        self.info_var = tk.StringVar(value="フィルターオプションで条件を変更できます")

        self._build_ui()
        self.apply_filters()

    def _collect_all_tags(self) -> list[str]:
        tag_set = set()
        for row in self.source_rows:
            for tag in row["Tags"].split(","):
                tag_set.add(tag.strip())
        return sorted(tag_set)

    def _build_ui(self) -> None:
        ttk.Label(self, text="タグ行フィルタ + ヘッダー列表示 サンプル", font=("Segoe UI", 14, "bold")).pack(anchor="w")

        action = ttk.Frame(self)
        action.pack(fill="x", pady=(8, 8))
        ttk.Button(action, text="フィルターオプション", command=self.open_filter_dialog).pack(side="left")
        ttk.Button(action, text="全解除(初期化)", command=self.reset_filters).pack(side="left", padx=(8, 0))

        ttk.Label(self, textvariable=self.info_var).pack(anchor="w", pady=(0, 6))

        self.table = ttk.Treeview(self, show="headings")
        self.table.pack(fill="both", expand=True)

    def _render_table(self, headers: list[str], rows: list[dict[str, str]]) -> None:
        self.table.delete(*self.table.get_children())
        self.table["columns"] = headers

        for header in headers:
            self.table.heading(header, text=header)
            self.table.column(header, width=130, anchor="w")

        for row in rows:
            self.table.insert("", "end", values=[row[h] for h in headers])

    def apply_filters(self) -> None:
        if not self.selected_headers:
            return

        filtered_rows = []
        for row in self.source_rows:
            row_tags = {tag.strip() for tag in row["Tags"].split(",")}
            if row_tags & self.selected_tags:
                filtered_rows.append(row)

        self._render_table(self.selected_headers, filtered_rows)
        self.info_var.set(
            f"表示中: 行 {len(filtered_rows)} 件 / 列 {len(self.selected_headers)} 件 "
            f"(ONタグ: {len(self.selected_tags)} 件)"
        )

    def reset_filters(self) -> None:
        self.selected_tags = set(self.all_tags)
        self.selected_headers = list(self.all_headers)
        self.apply_filters()

    def open_filter_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("フィルターオプション")
        dialog.geometry("760x360")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        body = ttk.Frame(dialog, padding=12)
        body.pack(fill="both", expand=True)

        tag_vars: dict[str, tk.BooleanVar] = {}
        header_vars: dict[str, tk.BooleanVar] = {}

        tag_frame = ttk.LabelFrame(body, text="タグ一覧 ON/OFF (行フィルタ)", padding=8)
        tag_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))

        for i, tag in enumerate(self.all_tags):
            var = tk.BooleanVar(value=(tag in self.selected_tags))
            tag_vars[tag] = var
            ttk.Checkbutton(tag_frame, text=tag, variable=var).grid(row=i // 3, column=i % 3, sticky="w", padx=6, pady=2)

        tag_ctrl = ttk.Frame(tag_frame)
        tag_ctrl.grid(row=(len(self.all_tags) // 3) + 1, column=0, columnspan=3, sticky="w", pady=(8, 0))
        ttk.Button(tag_ctrl, text="タグ全ON", command=lambda: self._set_all(tag_vars, True)).pack(side="left")
        ttk.Button(tag_ctrl, text="タグ全OFF", command=lambda: self._set_all(tag_vars, False)).pack(side="left", padx=(6, 0))

        header_frame = ttk.LabelFrame(body, text="ヘッダー一覧 ON/OFF (列表示)", padding=8)
        header_frame.pack(side="left", fill="both", expand=True, padx=(6, 0))

        for i, header in enumerate(self.all_headers):
            var = tk.BooleanVar(value=(header in self.selected_headers))
            header_vars[header] = var
            ttk.Checkbutton(header_frame, text=header, variable=var).grid(row=i // 2, column=i % 2, sticky="w", padx=6, pady=2)

        header_ctrl = ttk.Frame(header_frame)
        header_ctrl.grid(row=(len(self.all_headers) // 2) + 1, column=0, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Button(header_ctrl, text="ヘッダー全ON", command=lambda: self._set_all(header_vars, True)).pack(side="left")
        ttk.Button(header_ctrl, text="ヘッダー全OFF", command=lambda: self._set_all(header_vars, False)).pack(side="left", padx=(6, 0))

        footer = ttk.Frame(dialog, padding=(12, 0, 12, 12))
        footer.pack(fill="x")

        def on_ok() -> None:
            new_headers = [h for h, var in header_vars.items() if var.get()]
            if not new_headers:
                messagebox.showwarning("入力エラー", "表示するヘッダーを1つ以上ONにしてください。", parent=dialog)
                return

            self.selected_tags = {tag for tag, var in tag_vars.items() if var.get()}
            self.selected_headers = new_headers
            self.apply_filters()
            dialog.destroy()

        ttk.Button(footer, text="Cancel", command=dialog.destroy).pack(side="right", padx=(0, 0))
        ttk.Button(footer, text="OK", command=on_ok).pack(side="right", padx=(0, 8))

        dialog.wait_window()

    def _set_all(self, vars_map: dict[str, tk.BooleanVar], state: bool) -> None:
        for var in vars_map.values():
            var.set(state)


def main() -> None:
    root = tk.Tk()
    root.title("Tkinter タグ/ヘッダー ON/OFF サンプル")
    root.geometry("980x520")
    TagAndHeaderFilterDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()

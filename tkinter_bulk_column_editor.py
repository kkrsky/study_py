import tkinter as tk
from tkinter import messagebox, ttk


class BulkColumnEditorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("tkinter column bulk editor (Python 3.9)")
        self.geometry("860x480")

        self.columns = ("ID", "Name", "Department", "Status", "Note")
        self._editor = None
        self._editor_item = None
        self._editor_col_index = None

        self._build_widgets()
        self._load_sample_data()

    def _build_widgets(self):
        frame_top = ttk.Frame(self, padding=10)
        frame_top.pack(fill=tk.X)

        ttk.Label(frame_top, text="Target column").grid(row=0, column=0, padx=(0, 8), pady=4)
        self.target_col = tk.StringVar(value=self.columns[1])
        self.col_combo = ttk.Combobox(
            frame_top,
            textvariable=self.target_col,
            values=self.columns,
            width=14,
            state="readonly",
        )
        self.col_combo.grid(row=0, column=1, padx=(0, 16), pady=4)

        ttk.Label(frame_top, text="Mode").grid(row=0, column=2, padx=(0, 8), pady=4)
        self.mode = tk.StringVar(value="set")
        self.mode_combo = ttk.Combobox(
            frame_top,
            textvariable=self.mode,
            values=("set", "replace", "prefix", "suffix"),
            width=12,
            state="readonly",
        )
        self.mode_combo.grid(row=0, column=3, padx=(0, 16), pady=4)
        self.mode_combo.bind("<<ComboboxSelected>>", self._on_mode_changed)

        ttk.Label(frame_top, text="Value").grid(row=0, column=4, padx=(0, 8), pady=4)
        self.value_entry = ttk.Entry(frame_top, width=20)
        self.value_entry.grid(row=0, column=5, padx=(0, 16), pady=4)

        ttk.Label(frame_top, text="Replace from").grid(row=1, column=4, padx=(0, 8), pady=4)
        self.before_entry = ttk.Entry(frame_top, width=20)
        self.before_entry.grid(row=1, column=5, padx=(0, 16), pady=4)

        self.apply_btn = ttk.Button(frame_top, text="Apply bulk edit", command=self.apply_bulk_edit)
        self.apply_btn.grid(row=0, column=6, rowspan=2, sticky="ns", padx=(0, 8))

        ttk.Label(
            frame_top,
            text="Rows selected: apply to selected rows. No selection: apply to all rows.",
            foreground="#555",
        ).grid(row=2, column=0, columnspan=7, sticky="w", pady=(6, 0))

        frame_table = ttk.Frame(self, padding=(10, 0, 10, 10))
        frame_table.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            frame_table,
            columns=self.columns,
            show="headings",
            selectmode="extended",
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=tk.W)

        self.tree.column("ID", width=70, anchor=tk.CENTER)
        self.tree.bind("<Button-1>", self._on_tree_click, add=True)
        self.tree.bind("<Double-1>", self._on_cell_double_click, add=True)

        scrollbar = ttk.Scrollbar(frame_table, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self._on_mode_changed()

    def _load_sample_data(self):
        sample_rows = [
            ("1001", "Tanaka", "Sales", "Active", "Tokyo"),
            ("1002", "Sato", "IT", "Active", "Remote"),
            ("1003", "Suzuki", "HR", "Inactive", ""),
            ("1004", "Kobayashi", "Sales", "Active", "Part-time"),
            ("1005", "Yamada", "IT", "Active", ""),
        ]
        for row in sample_rows:
            self.tree.insert("", tk.END, values=row)

    def _on_mode_changed(self, _event=None):
        mode = self.mode.get()
        if mode == "replace":
            self.before_entry.state(["!disabled"])
        else:
            self.before_entry.delete(0, tk.END)
            self.before_entry.state(["disabled"])

    def _on_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "heading":
            self._commit_editor()
            return
        self._commit_editor()
        col_id = self.tree.identify_column(event.x)
        index = int(col_id.replace("#", "")) - 1
        if 0 <= index < len(self.columns):
            self.target_col.set(self.columns[index])

    def _on_cell_double_click(self, event):
        self._commit_editor()

        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if not row_id or not col_id:
            return

        col_index = int(col_id.replace("#", "")) - 1
        if col_index <= 0:
            return

        bbox = self.tree.bbox(row_id, col_id)
        if not bbox:
            return

        x, y, width, height = bbox
        current_values = list(self.tree.item(row_id, "values"))
        current_value = current_values[col_index]

        editor = ttk.Entry(self.tree)
        editor.insert(0, current_value)
        editor.select_range(0, tk.END)
        editor.focus_set()
        editor.place(x=x, y=y, width=width, height=height)

        self._editor = editor
        self._editor_item = row_id
        self._editor_col_index = col_index

        editor.bind("<Return>", self._commit_editor)
        editor.bind("<Escape>", lambda _e: self._destroy_editor())
        editor.bind("<FocusOut>", self._commit_editor)

    def _commit_editor(self, _event=None):
        if not self._editor:
            return
        row_id = self._editor_item
        col_index = self._editor_col_index
        new_value = self._editor.get()

        values = list(self.tree.item(row_id, "values"))
        values[col_index] = new_value
        self.tree.item(row_id, values=values)

        self._destroy_editor()

    def _destroy_editor(self):
        if self._editor is not None:
            self._editor.destroy()
        self._editor = None
        self._editor_item = None
        self._editor_col_index = None

    def apply_bulk_edit(self):
        self._commit_editor()

        col = self.target_col.get()
        mode = self.mode.get()
        value = self.value_entry.get()
        before = self.before_entry.get()
        col_index = self.columns.index(col)

        if mode == "replace" and before == "":
            messagebox.showwarning("Missing value", "Please input 'Replace from' value.")
            return

        target_items = self.tree.selection()
        if not target_items:
            target_items = self.tree.get_children("")

        updated_count = 0
        for item in target_items:
            current_values = list(self.tree.item(item, "values"))
            old = current_values[col_index]
            current_values[col_index] = self._edit_value(mode, old, value, before)
            if current_values[col_index] != old:
                self.tree.item(item, values=current_values)
                updated_count += 1

        messagebox.showinfo("Done", f"Updated: {updated_count} row(s)")

    @staticmethod
    def _edit_value(mode, old, value, before):
        if mode == "set":
            return value
        if mode == "replace":
            return old.replace(before, value)
        if mode == "prefix":
            return value + old
        if mode == "suffix":
            return old + value
        return old


if __name__ == "__main__":
    app = BulkColumnEditorApp()
    app.mainloop()

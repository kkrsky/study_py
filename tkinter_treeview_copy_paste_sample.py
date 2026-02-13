import csv
import io
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Sequence, Tuple

CLIPBOARD_HEADER = "__TREEVIEW_COPY_COLUMNS__"


class CopyPasteTableDemo(ttk.Frame):
    """Treeview sample for multi-row copy and paste with Ctrl+C / Ctrl+V."""

    columns: Tuple[str, ...] = ("id", "title", "category", "status", "qty")

    def __init__(self, parent: tk.Misc):
        super().__init__(parent, padding=10)
        self._copied_columns: Tuple[str, ...] = self.columns
        self._copied_rows: List[Tuple[str, ...]] = []
        self._column_index_by_name: Dict[str, int] = {name: i for i, name in enumerate(self.columns)}
        self._copy_enabled: Dict[str, bool] = {name: True for name in self.columns}
        self._copy_toggle_buttons: Dict[str, ttk.Button] = {}
        self._undo_stack: List[Dict[str, object]] = []
        self._redo_stack: List[Dict[str, object]] = []
        self._build_ui()
        self._insert_demo_rows()
        self._bind_shortcuts()

    def _build_ui(self) -> None:
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 8))

        ttk.Label(
            toolbar,
            text="Ctrl+C: copy selected rows (ON columns only) / Ctrl+V: paste / Ctrl+Z: undo / Ctrl+Y: redo",
        ).pack(side="left")

        copy_opt = ttk.LabelFrame(self, text="Copy Columns (ON/OFF)")
        copy_opt.pack(fill="x", pady=(0, 8))
        for col in self.columns:
            item = ttk.Frame(copy_opt)
            item.pack(side="left", padx=(0, 8), pady=6)
            ttk.Label(item, text=col.upper()).pack(side="left")
            btn = ttk.Button(item, width=4, command=lambda c=col: self._toggle_copy_column(c))
            btn.pack(side="left", padx=(4, 0))
            self._copy_toggle_buttons[col] = btn
            self._refresh_copy_toggle_button(col)

        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True)
        wrap.columnconfigure(0, weight=1)
        wrap.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(wrap, columns=self.columns, show="headings", selectmode="extended", height=14)
        self.tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=yscroll.set)

        headings = {
            "id": "ID",
            "title": "Title",
            "category": "Category",
            "status": "Status",
            "qty": "Qty",
        }
        widths = {"id": 70, "title": 240, "category": 140, "status": 120, "qty": 80}
        anchors = {"id": "e", "title": "w", "category": "w", "status": "w", "qty": "e"}

        for col in self.columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor=anchors[col], stretch=(col == "title"))

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status_var, anchor="w").pack(fill="x", pady=(8, 0))

    def _insert_demo_rows(self) -> None:
        demo_rows = [
            ("1", "Buy apples", "Food", "New", "10"),
            ("2", "Make coffee", "Drink", "Hold", "1"),
            ("3", "Daily jog", "Daily", "Done", "1"),
            ("4", "Write report", "Work", "New", "1"),
            ("5", "Blender practice", "Hobby", "Hold", "1"),
            ("6", "Read article", "Daily", "New", "2"),
        ]
        for row in demo_rows:
            self.tree.insert("", "end", values=row)

    def _bind_shortcuts(self) -> None:
        self.tree.bind("<Control-c>", self._on_copy, add=True)
        self.tree.bind("<Control-C>", self._on_copy, add=True)
        self.tree.bind("<Control-v>", self._on_paste, add=True)
        self.tree.bind("<Control-V>", self._on_paste, add=True)
        self.bind_all("<Control-z>", self._on_undo, add=True)
        self.bind_all("<Control-Z>", self._on_undo, add=True)
        self.bind_all("<Control-y>", self._on_redo, add=True)
        self.bind_all("<Control-Y>", self._on_redo, add=True)
        self.tree.bind("<Button-1>", lambda _e: self.tree.focus_set(), add=True)
        self.tree.focus_set()

    def _toggle_copy_column(self, col_name: str) -> None:
        self._copy_enabled[col_name] = not self._copy_enabled.get(col_name, True)
        self._refresh_copy_toggle_button(col_name)

    def _refresh_copy_toggle_button(self, col_name: str) -> None:
        btn = self._copy_toggle_buttons.get(col_name)
        if btn is None:
            return
        is_on = self._copy_enabled.get(col_name, True)
        btn.configure(text=("ON" if is_on else "OFF"))

    def _active_copy_columns(self) -> Tuple[str, ...]:
        return tuple(col for col in self.columns if self._copy_enabled.get(col, False))

    def _on_copy(self, _event=None) -> str:
        selected = self._get_selected_items_sorted()
        if not selected:
            self.status_var.set("Copy skipped: no selected rows.")
            self.bell()
            return "break"

        active_cols = self._active_copy_columns()
        if not active_cols:
            self.status_var.set("Copy skipped: turn ON at least one column.")
            self.bell()
            return "break"

        copied_rows = [
            self._extract_partial_row(tuple(str(v) for v in self.tree.item(iid, "values")), active_cols)
            for iid in selected
        ]
        self._copied_columns = active_cols
        self._copied_rows = copied_rows
        self._set_clipboard_rows(active_cols, copied_rows)
        self.status_var.set(
            f"Copied {len(copied_rows)} row(s), columns: {', '.join(active_cols)}."
        )
        return "break"

    def _on_paste(self, _event=None) -> str:
        source_columns, source_rows = self._resolve_paste_source()
        if not source_rows:
            self.status_var.set("Paste skipped: clipboard has no table rows.")
            self.bell()
            return "break"
        if not source_columns:
            self.status_var.set("Paste skipped: no valid columns in clipboard payload.")
            self.bell()
            return "break"

        self._push_undo_state()
        targets = self._get_selected_items_sorted()
        if not targets:
            for partial in source_rows:
                self.tree.insert("", "end", values=self._build_full_row_from_partial(partial, source_columns))
            self.status_var.set(
                f"Pasted {len(source_rows)} row(s) at end (columns: {', '.join(source_columns)})."
            )
            return "break"

        if len(targets) == 1:
            self._paste_to_single_target(targets[0], source_columns, source_rows)
            self.status_var.set(
                f"Pasted {len(source_rows)} row(s) from selected row (columns: {', '.join(source_columns)})."
            )
            return "break"

        self._paste_to_multiple_targets(targets, source_columns, source_rows)
        self.status_var.set(
            f"Pasted {len(source_rows)} row(s) to {len(targets)} selected row(s) (columns: {', '.join(source_columns)})."
        )
        return "break"

    def _paste_to_single_target(
        self,
        target_iid: str,
        source_columns: Sequence[str],
        source_rows: Sequence[Tuple[str, ...]],
    ) -> None:
        target_values = tuple(str(v) for v in self.tree.item(target_iid, "values"))
        self.tree.item(
            target_iid,
            values=self._build_full_row_from_partial(source_rows[0], source_columns, base_row=target_values),
        )
        self.tree.selection_set(target_iid)
        self.tree.see(target_iid)

    def _paste_to_multiple_targets(
        self,
        target_iids: Sequence[str],
        source_columns: Sequence[str],
        source_rows: Sequence[Tuple[str, ...]],
    ) -> None:
        source_len = len(source_rows)
        for i, target_iid in enumerate(target_iids):
            target_values = tuple(str(v) for v in self.tree.item(target_iid, "values"))
            partial = source_rows[i % source_len]
            self.tree.item(
                target_iid,
                values=self._build_full_row_from_partial(partial, source_columns, base_row=target_values),
            )

        self.tree.selection_set(target_iids)
        self.tree.see(target_iids[-1])

    def _get_selected_items_sorted(self) -> List[str]:
        selected = list(self.tree.selection())
        selected.sort(key=self.tree.index)
        return selected

    def _extract_partial_row(self, full_row: Sequence[str], columns: Sequence[str]) -> Tuple[str, ...]:
        return tuple(full_row[self._column_index_by_name[col]] for col in columns)

    def _build_full_row_from_partial(
        self,
        partial_row: Sequence[str],
        partial_columns: Sequence[str],
        base_row: Sequence[str] = (),
    ) -> Tuple[str, ...]:
        if base_row:
            full = [str(v) for v in base_row]
            if len(full) < len(self.columns):
                full.extend([""] * (len(self.columns) - len(full)))
            elif len(full) > len(self.columns):
                full = full[: len(self.columns)]
        else:
            full = [""] * len(self.columns)

        for i, col in enumerate(partial_columns):
            if col not in self._column_index_by_name:
                continue
            value = str(partial_row[i]) if i < len(partial_row) else ""
            full[self._column_index_by_name[col]] = value
        return tuple(full)

    def _set_clipboard_rows(self, columns: Sequence[str], rows: Sequence[Tuple[str, ...]]) -> None:
        data = self._serialize_rows(columns, rows)
        root = self.winfo_toplevel()
        root.clipboard_clear()
        root.clipboard_append(data)
        root.update_idletasks()

    def _get_clipboard_rows(self) -> Tuple[Tuple[str, ...], List[Tuple[str, ...]]]:
        root = self.winfo_toplevel()
        try:
            text = root.clipboard_get()
        except tk.TclError:
            return (), []
        columns, rows = self._deserialize_rows(text)
        if not columns or not rows:
            return (), []

        width = len(columns)
        normalized: List[Tuple[str, ...]] = []
        for row in rows:
            if len(row) < width:
                row = tuple(list(row) + [""] * (width - len(row)))
            elif len(row) > width:
                row = row[:width]
            normalized.append(tuple(row))
        return tuple(columns), normalized

    def _resolve_paste_source(self) -> Tuple[Tuple[str, ...], List[Tuple[str, ...]]]:
        if self._copied_rows and self._copied_columns:
            return self._copied_columns, list(self._copied_rows)
        return self._get_clipboard_rows()

    def _capture_table_state(self) -> Dict[str, object]:
        item_ids = list(self.tree.get_children(""))
        rows = [tuple(str(v) for v in self.tree.item(iid, "values")) for iid in item_ids]
        selected = set(self.tree.selection())
        selected_indices = [i for i, iid in enumerate(item_ids) if iid in selected]
        return {"rows": rows, "selected_indices": selected_indices}

    def _restore_table_state(self, state: Dict[str, object]) -> None:
        rows = state.get("rows", [])
        selected_indices = state.get("selected_indices", [])
        self.tree.delete(*self.tree.get_children(""))
        new_ids: List[str] = []
        for row in rows:
            new_ids.append(self.tree.insert("", "end", values=row))

        selection: List[str] = []
        for index in selected_indices:
            if isinstance(index, int) and 0 <= index < len(new_ids):
                selection.append(new_ids[index])
        if selection:
            self.tree.selection_set(selection)
            self.tree.see(selection[-1])
        else:
            self.tree.selection_remove(self.tree.selection())

    def _push_undo_state(self) -> None:
        self._undo_stack.append(self._capture_table_state())
        if len(self._undo_stack) > 100:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def _on_undo(self, _event=None) -> str:
        if not self._undo_stack:
            self.status_var.set("Undo skipped: no history.")
            self.bell()
            return "break"
        current = self._capture_table_state()
        prev = self._undo_stack.pop()
        self._redo_stack.append(current)
        self._restore_table_state(prev)
        self.status_var.set("Undo applied.")
        return "break"

    def _on_redo(self, _event=None) -> str:
        if not self._redo_stack:
            self.status_var.set("Redo skipped: no history.")
            self.bell()
            return "break"
        current = self._capture_table_state()
        nxt = self._redo_stack.pop()
        self._undo_stack.append(current)
        self._restore_table_state(nxt)
        self.status_var.set("Redo applied.")
        return "break"

    @staticmethod
    def _serialize_rows(columns: Sequence[str], rows: Sequence[Tuple[str, ...]]) -> str:
        out = io.StringIO()
        writer = csv.writer(out, delimiter="\t", lineterminator="\n")
        writer.writerow([CLIPBOARD_HEADER, *columns])
        writer.writerows(rows)
        return out.getvalue()

    def _deserialize_rows(self, text: str) -> Tuple[Tuple[str, ...], List[Tuple[str, ...]]]:
        if not text.strip():
            return (), []
        src = io.StringIO(text)
        reader = csv.reader(src, delimiter="\t")
        all_rows = [tuple(row) for row in reader if row]
        if not all_rows:
            return (), []

        if all_rows[0] and all_rows[0][0] == CLIPBOARD_HEADER:
            raw_columns = all_rows[0][1:]
            columns = tuple(col for col in raw_columns if col in self._column_index_by_name)
            return columns, all_rows[1:]

        return self.columns, all_rows


def main() -> None:
    root = tk.Tk()
    root.title("Tkinter Treeview Copy/Paste Sample (Ctrl+C / Ctrl+V)")
    root.geometry("900x500")

    app = CopyPasteTableDemo(root)
    app.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()

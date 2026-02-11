import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class PopupMessagesDemo(ttk.Frame):
    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent, padding=20)
        self.pack(fill="both", expand=True)

        self.result_var = tk.StringVar(value="結果: まだ操作していません")
        self._build_ui()

    def _build_ui(self) -> None:
        ttk.Label(self, text="Tkinter Popup Messages Demo", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(
            self,
            text="Info / Warning / Error / Input / YesNo のポップアップを確認できます。",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 14))

        buttons = ttk.Frame(self)
        buttons.pack(anchor="w")

        ttk.Button(buttons, text="Info", command=self.show_info).grid(row=0, column=0, padx=(0, 8), pady=4)
        ttk.Button(buttons, text="Warning", command=self.show_warning).grid(row=0, column=1, padx=(0, 8), pady=4)
        ttk.Button(buttons, text="Error", command=self.show_error).grid(row=0, column=2, padx=(0, 8), pady=4)
        ttk.Button(buttons, text="Input", command=self.show_input).grid(row=0, column=3, padx=(0, 8), pady=4)
        ttk.Button(buttons, text="Yes/No", command=self.show_yes_no).grid(row=0, column=4, pady=4)

        ttk.Separator(self).pack(fill="x", pady=16)
        ttk.Label(self, textvariable=self.result_var, font=("Segoe UI", 10, "bold")).pack(anchor="w")

    def show_info(self) -> None:
        messagebox.showinfo("Info", "これは情報メッセージです。")
        self.result_var.set("結果: Info を表示しました")

    def show_warning(self) -> None:
        messagebox.showwarning("Warning", "これは警告メッセージです。")
        self.result_var.set("結果: Warning を表示しました")

    def show_error(self) -> None:
        messagebox.showerror("Error", "これはエラーメッセージです。")
        self.result_var.set("結果: Error を表示しました")

    def show_input(self) -> None:
        text = simpledialog.askstring("Input", "名前を入力してください:")
        if text is None:
            self.result_var.set("結果: Input はキャンセルされました")
        else:
            self.result_var.set(f"結果: Input = '{text}'")

    def show_yes_no(self) -> None:
        ok = messagebox.askyesno("Yes / No", "この処理を実行しますか？")
        self.result_var.set("結果: Yes を選択しました" if ok else "結果: No を選択しました")


def main() -> None:
    root = tk.Tk()
    root.title("Tkinter Popup Messages Sample")
    root.geometry("760x280")
    PopupMessagesDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()

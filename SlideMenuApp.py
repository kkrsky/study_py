import tkinter as tk


class SlideMenuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter Slide Hamburger Menu - Pages")
        self.geometry("900x520")
        self.minsize(640, 360)

        # ===== 設定 =====
        self.menu_width = 260
        self.anim_step = 20
        self.anim_delay = 10
        self.menu_open = False
        self.animating = False

        # ===== レイアウト =====
        self._build_topbar()
        self._build_menu()
        self._build_main_with_pages()

        # 初期位置：メニューを隠す
        self.menu_x = -self.menu_width
        self.menu_frame.place(x=self.menu_x, y=0, relheight=1)

        # 初期ページ
        self.show_page("Home")

    # ----------------------------
    # UI構築
    # ----------------------------
    def _build_topbar(self):
        self.topbar = tk.Frame(self, height=48, bg="#2c3e50")
        self.topbar.pack(side="top", fill="x")

        self.hamburger_btn = tk.Button(
            self.topbar,
            text="☰",
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#2c3e50",
            activebackground="#34495e",
            activeforeground="white",
            bd=0,
            command=self.toggle_menu,
        )
        self.hamburger_btn.pack(side="left", padx=12)

        self.page_title = tk.StringVar(value="Home")
        self.title_label = tk.Label(
            self.topbar,
            textvariable=self.page_title,
            fg="white",
            bg="#2c3e50",
            font=("Segoe UI", 14),
        )
        self.title_label.pack(side="left", padx=8)

    def _build_menu(self):
        self.menu_frame = tk.Frame(self, bg="#34495e", width=self.menu_width)

        header = tk.Label(
            self.menu_frame,
            text="MENU",
            fg="white",
            bg="#34495e",
            font=("Segoe UI", 14, "bold"),
        )
        header.pack(anchor="w", padx=16, pady=(16, 10))

        # 各メニュー → 対応ページへ
        items = [
            ("Home", lambda: self.show_page("Home")),
            ("Profile", lambda: self.show_page("Profile")),
            ("Settings", lambda: self.show_page("Settings")),
            ("Help", lambda: self.show_page("Help")),
        ]

        for text, cmd in items:
            b = tk.Button(
                self.menu_frame,
                text=text,
                command=lambda c=cmd: self._on_menu_click(c),
                anchor="w",
                padx=16,
                font=("Segoe UI", 12),
                fg="white",
                bg="#34495e",
                activebackground="#3d566e",
                activeforeground="white",
                bd=0,
                relief="flat",
                height=2,
            )
            b.pack(fill="x")

        tk.Frame(self.menu_frame, height=1, bg="#2c3e50").pack(fill="x", pady=8)

        close_btn = tk.Button(
            self.menu_frame,
            text="Close",
            command=self.toggle_menu,
            anchor="w",
            padx=16,
            font=("Segoe UI", 12),
            fg="white",
            bg="#34495e",
            activebackground="#3d566e",
            activeforeground="white",
            bd=0,
            relief="flat",
            height=2,
        )
        close_btn.pack(fill="x", pady=(0, 8))

    def _build_main_with_pages(self):
        # メイン領域
        self.main = tk.Frame(self, bg="#ecf0f1")
        self.main.pack(side="top", fill="both", expand=True)

        # オーバーレイ（メニューが開いている時のクリック領域）
        self.overlay = tk.Frame(self.main, bg="#000000")
        self.overlay.bind("<Button-1>", lambda e: self.toggle_menu())

        # ページを載せるコンテナ
        self.page_container = tk.Frame(self.main, bg="#ecf0f1")
        self.page_container.pack(fill="both", expand=True)

        # ページ群
        self.pages = {}
        self.pages["Home"] = HomePage(self.page_container)
        self.pages["Profile"] = ProfilePage(self.page_container)
        self.pages["Settings"] = SettingsPage(self.page_container)
        self.pages["Help"] = HelpPage(self.page_container)

        for p in self.pages.values():
            p.place(x=0, y=0, relwidth=1, relheight=1)

        # 下部ステータス
        self.status = tk.StringVar(value="Ready")
        status_bar = tk.Frame(self.main, bg="#dfe6e9", height=28)
        status_bar.pack(side="bottom", fill="x")
        tk.Label(status_bar, textvariable=self.status, bg="#dfe6e9", fg="#2c3e50").pack(
            side="left", padx=10
        )

    # ----------------------------
    # ページ切り替え
    # ----------------------------
    def show_page(self, name: str):
        if name not in self.pages:
            self.status.set(f"Unknown page: {name}")
            return

        self.pages[name].tkraise()
        self.page_title.set(name)
        self.status.set(f"Switched to: {name}")

    def _on_menu_click(self, cmd):
        cmd()
        # ページ切り替え後にメニューを閉じる
        if self.menu_open:
            self.toggle_menu()

    # ----------------------------
    # メニュー開閉（スライド）
    # ----------------------------
    def toggle_menu(self):
        if self.animating:
            return

        self.menu_open = not self.menu_open
        self.animating = True

        if self.menu_open:
            # オーバーレイを置いてメインをクリックしたら閉じる
            self.overlay.place(x=0, y=0, relwidth=1, relheight=1)
            self.menu_frame.lift()
            self.topbar.lift()

        self._animate_menu()

    def _animate_menu(self):
        target_x = 0 if self.menu_open else -self.menu_width

        if self.menu_x < target_x:
            self.menu_x = min(self.menu_x + self.anim_step, target_x)
        elif self.menu_x > target_x:
            self.menu_x = max(self.menu_x - self.anim_step, target_x)

        self.menu_frame.place(x=self.menu_x, y=0, relheight=1)

        if self.menu_x != target_x:
            self.after(self.anim_delay, self._animate_menu)
        else:
            self.animating = False
            if not self.menu_open:
                self.overlay.place_forget()


# =========================================================
# Pages（簡単なページ）
# =========================================================
class BasePage(tk.Frame):
    def __init__(self, parent, title: str):
        super().__init__(parent, bg="#ecf0f1")
        tk.Label(
            self,
            text=title,
            bg="#ecf0f1",
            fg="#2c3e50",
            font=("Segoe UI", 22, "bold"),
        ).pack(pady=(30, 10))


class HomePage(BasePage):
    def __init__(self, parent):
        super().__init__(parent, "Home")
        tk.Label(
            self,
            text="Welcome! ここはホーム画面です。",
            bg="#ecf0f1",
            fg="#2c3e50",
            font=("Segoe UI", 12),
        ).pack(pady=6)

        # ダミーのカード風エリア
        card = tk.Frame(self, bg="white", bd=0, highlightthickness=1, highlightbackground="#d0d0d0")
        card.pack(pady=18, padx=24, fill="x")
        tk.Label(card, text="News", bg="white", fg="#2c3e50", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=12, pady=(10, 4)
        )
        tk.Label(card, text="・メニューからページを切り替えできます。", bg="white", fg="#2c3e50").pack(
            anchor="w", padx=12, pady=2
        )
        tk.Label(card, text="・オーバーレイ（黒い領域）クリックでメニューを閉じます。", bg="white", fg="#2c3e50").pack(
            anchor="w", padx=12, pady=(2, 10)
        )


class ProfilePage(BasePage):
    def __init__(self, parent):
        super().__init__(parent, "Profile")

        form = tk.Frame(self, bg="#ecf0f1")
        form.pack(pady=10)

        def row(label, widget):
            r = tk.Frame(form, bg="#ecf0f1")
            r.pack(fill="x", pady=6)
            tk.Label(r, text=label, width=10, anchor="e", bg="#ecf0f1", fg="#2c3e50").pack(side="left")
            widget.pack(side="left", padx=10)

        self.name_var = tk.StringVar(value="Taro")
        self.email_var = tk.StringVar(value="taro@example.com")

        row("Name", tk.Entry(form, textvariable=self.name_var, width=30))
        row("Email", tk.Entry(form, textvariable=self.email_var, width=30))

        btns = tk.Frame(self, bg="#ecf0f1")
        btns.pack(pady=14)

        tk.Button(btns, text="Save (dummy)", command=lambda: None).pack(side="left", padx=6)
        tk.Button(btns, text="Reset", command=self._reset).pack(side="left", padx=6)

    def _reset(self):
        self.name_var.set("Taro")
        self.email_var.set("taro@example.com")


class SettingsPage(BasePage):
    def __init__(self, parent):
        super().__init__(parent, "Settings")

        box = tk.Frame(self, bg="white", highlightthickness=1, highlightbackground="#d0d0d0")
        box.pack(padx=24, pady=12, fill="x")

        tk.Label(box, text="Preferences", bg="white", fg="#2c3e50", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=12, pady=(10, 6)
        )

        self.dark_var = tk.BooleanVar(value=False)
        self.notify_var = tk.BooleanVar(value=True)

        tk.Checkbutton(
            box, text="Enable dark mode (dummy)", variable=self.dark_var, bg="white"
        ).pack(anchor="w", padx=12, pady=4)
        tk.Checkbutton(
            box, text="Enable notifications (dummy)", variable=self.notify_var, bg="white"
        ).pack(anchor="w", padx=12, pady=(0, 10))

        tk.Button(self, text="Apply (dummy)", command=lambda: None).pack(pady=10)


class HelpPage(BasePage):
    def __init__(self, parent):
        super().__init__(parent, "Help")
        msg = (
            "操作:\n"
            "1) 左上の ☰ を押すとメニューが左から出ます\n"
            "2) メニュー項目を押すとページが切り替わります\n"
            "3) 黒い領域クリック or Close でメニューが閉じます\n"
        )
        tk.Label(self, text=msg, justify="left", bg="#ecf0f1", fg="#2c3e50", font=("Segoe UI", 12)).pack(
            padx=24, pady=12, anchor="w"
        )


if __name__ == "__main__":
    SlideMenuApp().mainloop()

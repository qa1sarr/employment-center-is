import tkinter as tk
from tkinter import ttk

from lab11.db_setup import create_demo_db
from lab11.auth import login_vulnerable, login_secure
from lab11.vulnerable_search import search_vulnerable
from lab11.secure_search import search_secure

MODES = {
    "vulnerable": ("ОСАЛ режим", login_vulnerable, search_vulnerable),
    "secure": ("ҚАУІПСІЗ режим", login_secure, search_secure),
}


class App:
    def __init__(self, root):
        self.root = root
        self.conn = create_demo_db()
        self.mode = tk.StringVar(value="vulnerable")
        self.user = None
        root.geometry("760x520")
        self.show_login()

    # ---------- жалпы ----------
    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    # ---------- 1-терезе: кіру ----------
    def show_login(self):
        self.clear()
        self.user = None
        self.root.title("Жұмыспен қамту орталығы — жүйеге кіру")
        f = ttk.Frame(self.root, padding=20)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text="Жүйеге кіру", font=("Arial", 16, "bold")).pack(anchor="w")
        ttk.Label(f, text="Демо: aigerim@mail.kz / 123456", foreground="gray").pack(anchor="w", pady=(0, 10))

        ttk.Label(f, text="Логин (email):").pack(anchor="w")
        self.login_entry = ttk.Entry(f, width=60)
        self.login_entry.pack(anchor="w", pady=(0, 8))

        ttk.Label(f, text="Пароль:").pack(anchor="w")
        self.password_entry = ttk.Entry(f, width=60, show="*")
        self.password_entry.pack(anchor="w", pady=(0, 8))

        box = ttk.LabelFrame(f, text="Режим", padding=8)
        box.pack(anchor="w", fill="x", pady=(0, 8))
        ttk.Radiobutton(box, text="ОСАЛ (мәтінді біріктіру)", variable=self.mode, value="vulnerable").pack(side="left", padx=8)
        ttk.Radiobutton(box, text="ҚАУІПСІЗ (параметрленген сұраныс)", variable=self.mode, value="secure").pack(side="left", padx=8)

        ttk.Button(f, text="Кіру", command=self.do_login).pack(anchor="w", pady=(0, 8))
        self.login_status = ttk.Label(f, text="", font=("Arial", 11, "bold"))
        self.login_status.pack(anchor="w")

        ttk.Label(f, text="Орындалған SQL сұранысы:").pack(anchor="w", pady=(10, 0))
        self.login_sql = tk.Text(f, height=5, wrap="word", state="disabled")
        self.login_sql.pack(fill="x")

        self.password_entry.bind("<Return>", lambda e: self.do_login())
        self.login_entry.focus_set()

    def set_text(self, widget, text):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.config(state="disabled")

    def do_login(self):
        email = self.login_entry.get()
        password = self.password_entry.get()
        label, login_fn, _ = MODES[self.mode.get()]
        try:
            query, row = login_fn(self.conn, email, password)
        except Exception as e:  # синтаксис қатесі және т.б.
            self.login_status.config(text="Қате: %s" % e)
            self.set_text(self.login_sql, "(сұраныс орындалмады)")
            return
        self.set_text(self.login_sql, query)
        if row:
            self.user = row
            self.show_interface()
        else:
            self.login_status.config(text="Логин немесе пароль қате!")

    # ---------- 2-терезе: интерфейс ----------
    def show_interface(self):
        self.clear()
        label, _, _ = MODES[self.mode.get()]
        self.root.title("Жұмыспен қамту орталығы — интерфейс")
        user_id, full_name, email, role = self.user
        f = ttk.Frame(self.root, padding=20)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text="Жүйеге кіру сәтті орындалды!", font=("Arial", 16, "bold")).pack(anchor="w")
        ttk.Label(f, text="Пайдаланушы: %s (%s), рөлі: %s" % (full_name, email, role)).pack(anchor="w")
        ttk.Label(f, text="Режим: " + label, foreground="gray").pack(anchor="w", pady=(0, 10))

        row = ttk.Frame(f)
        row.pack(fill="x")
        ttk.Label(row, text="Вакансия атауы:").pack(side="left")
        self.search_entry = ttk.Entry(row, width=50)
        self.search_entry.pack(side="left", padx=8)
        ttk.Button(row, text="Іздеу", command=self.do_search).pack(side="left")
        self.search_entry.bind("<Return>", lambda e: self.do_search())

        cols = ("id", "title", "salary", "status")
        self.table = ttk.Treeview(f, columns=cols, show="headings", height=10)
        for c, w in zip(cols, (60, 360, 100, 100)):
            self.table.heading(c, text=c)
            self.table.column(c, width=w)
        self.table.pack(fill="both", expand=True, pady=10)

        self.search_status = ttk.Label(f, text="")
        self.search_status.pack(anchor="w")
        self.search_sql = tk.Text(f, height=3, wrap="word", state="disabled")
        self.search_sql.pack(fill="x", pady=(4, 8))

        ttk.Button(f, text="Шығу", command=self.show_login).pack(anchor="w")
        self.search_entry.focus_set()

    def do_search(self):
        text = self.search_entry.get()
        _, _, search_fn = MODES[self.mode.get()]
        for item in self.table.get_children():
            self.table.delete(item)
        try:
            query, rows = search_fn(self.conn, text)
        except Exception as e:
            self.search_status.config(text="Қате: %s" % e)
            self.set_text(self.search_sql, "(сұраныс орындалмады)")
            return
        self.set_text(self.search_sql, query)
        for r in rows:
            self.table.insert("", "end", values=r)
        self.search_status.config(text="Табылған жазба саны: %d" % len(rows))


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()

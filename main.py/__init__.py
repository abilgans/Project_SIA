import tkinter as tk
from ui.login_ui import LoginWindow
from ui.main_ui import MainApp
from database import init_db_if_needed


def start_main_app(email):
    """Dipanggil setelah login berhasil."""
    root = tk.Tk()
    app = MainApp(root, user_email=email)
    root.mainloop()


def main():
    # Pastikan database siap
    init_db_if_needed()

    root = tk.Tk()
    root.withdraw()  # Sembunyikan root, login di window terpisah

    def on_login_success(email):
        root.destroy()     # Tutup window login
        start_main_app(email)

    LoginWindow(root, on_login_success)
    root.mainloop()


if __name__ == "__main__":
    main()
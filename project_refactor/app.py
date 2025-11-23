from ui.main_window import MainApp
from core.db import DBHelper
from core.config import DB_FILENAME


def main():
    # Inisialisasi database
    try:
        db = DBHelper(DB_FILENAME)
        db.init_db_if_needed()
    except Exception as e:
        print("Database init error:", e)

    # Jalankan aplikasi
    app = MainApp("demo@local")
    app.mainloop()


if __name__ == "__main__":
    main()

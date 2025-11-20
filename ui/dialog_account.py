import tkinter as tk
from tkinter import ttk, messagebox


class AccountDialog(tk.Toplevel):
    def __init__(self, parent, initial=None, edit_mode=False):
        super().__init__(parent)
        self.title("Akun")
        self.geometry("420x240")
        self.configure(bg="#F8FAFC")

        self.result = None
        self.edit_mode = edit_mode

        ttk.Label(self, text="No Akun:").pack(anchor='w', padx=12, pady=6)
        self.e_no = ttk.Entry(self)
        self.e_no.pack(fill='x', padx=12)

        ttk.Label(self, text="Nama Akun:").pack(anchor='w', padx=12, pady=6)
        self.e_nama = ttk.Entry(self)
        self.e_nama.pack(fill='x', padx=12)

        ttk.Label(self, text="Tipe:").pack(anchor='w', padx=12, pady=6)
        self.combo = ttk.Combobox(self, values=[
            "Asset", "Liability", "Equity", "Revenue", "Expense"
        ])
        self.combo.pack(fill='x', padx=12)

        ttk.Button(self, text="Simpan", command=self.save).pack(pady=12)

        if initial:
            no, nama, tipe = initial
            self.e_no.insert(0, no)
            self.e_nama.insert(0, nama)
            self.combo.set(tipe)

            if edit_mode:
                self.e_no.config(state='disabled')

    def save(self):
        no = self.e_no.get().strip()
        nama = self.e_nama.get().strip()
        tipe = self.combo.get().strip()

        if not (no and nama and tipe):
            messagebox.showerror("Error", "Semua field wajib diisi")
            return

        self.result = (no, nama, tipe)
        self.destroy()

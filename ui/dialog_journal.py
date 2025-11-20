import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class JournalDialog(tk.Toplevel):
    def __init__(self, parent, accounts):
        super().__init__(parent)
        self.title("Tambah Jurnal")
        self.geometry("560x480")
        self.configure(bg="#F8FAFC")

        self.result = None

        ttk.Label(self, text="Tanggal (YYYY-MM-DD):").pack(anchor='w', padx=12, pady=6)
        self.e_date = ttk.Entry(self)
        self.e_date.pack(fill='x', padx=12)
        self.e_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(self, text="Akun Debit:").pack(anchor='w', padx=12, pady=6)
        self.combo_debit = ttk.Combobox(self,
            values=[f"{a[0]} - {a[1]}" for a in accounts])
        self.combo_debit.pack(fill='x', padx=12)

        ttk.Label(self, text="Akun Kredit:").pack(anchor='w', padx=12, pady=6)
        self.combo_credit = ttk.Combobox(self,
            values=[f"{a[0]} - {a[1]}" for a in accounts])
        self.combo_credit.pack(fill='x', padx=12)

        ttk.Label(self, text="Debit:").pack(anchor='w', padx=12, pady=6)
        self.e_debit = ttk.Entry(self)
        self.e_debit.pack(fill='x', padx=12)
        self.e_debit.insert(0, "0")

        ttk.Label(self, text="Kredit:").pack(anchor='w', padx=12, pady=6)
        self.e_kredit = ttk.Entry(self)
        self.e_kredit.pack(fill='x', padx=12)
        self.e_kredit.insert(0, "0")

        ttk.Label(self, text="Keterangan:").pack(anchor='w', padx=12, pady=6)
        self.e_ket = ttk.Entry(self)
        self.e_ket.pack(fill='x', padx=12)

        ttk.Button(self, text="Simpan", command=self.save).pack(pady=12)

    def save(self):
        try:
            tanggal = self.e_date.get().strip()
            adebit = self.combo_debit.get().split(" - ", 1)[0].strip()
            acredit = self.combo_credit.get().split(" - ", 1)[0].strip()

            debit_val = float(self.e_debit.get().replace(",", "") or 0)
            kredit_val = float(self.e_kredit.get().replace(",", "") or 0)

            datetime.strptime(tanggal, "%Y-%m-%d")

            if debit_val < 0 or kredit_val < 0:
                raise ValueError("Nilai tidak boleh negatif")

            if debit_val == 0 and kredit_val == 0:
                raise ValueError("Minimal debit / kredit harus diisi")

            self.result = (tanggal, adebit, acredit, debit_val, kredit_val, self.e_ket.get().strip())
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", str(e))

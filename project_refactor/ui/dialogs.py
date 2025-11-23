import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class ActivationDialog(tk.Toplevel):
    def __init__(self, parent, email):
        super().__init__(parent)
        self.title("Aktivasi Akun")
        self.geometry("420x180"); self.resizable(False, False)
        self.email = email
        ttk.Label(self, text=f"Masukkan kode OTP yang dikirim ke {email}").pack(padx=12, pady=(12,6))
        self.entry_otp = ttk.Entry(self); self.entry_otp.pack(fill='x', padx=12)
        ttk.Button(self, text="Aktivasi", command=self.do_activate).pack(pady=12)
        ttk.Button(self, text="Tutup", command=self.destroy).pack()

    def do_activate(self):
        otp = self.entry_otp.get().strip()
        if not otp:
            messagebox.showwarning("Peringatan","Masukkan OTP terlebih dahulu"); return
        ok, msg = verify_activation_otp(self.email, otp)
        if ok:
            messagebox.showinfo("Sukses", msg); self.destroy()
        else:
            messagebox.showerror("Error", msg)

class LoginWindow(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.overrideredirect(True)
        sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
        self.geometry(f"{sw}x{sh}+0+0"); self.configure(bg=WINDOW_BG)
        self.build()

    def build(self):
        frm = ttk.Frame(self, padding=20); frm.place(relx=0.5, rely=0.5, anchor='center')
        title = tk.Label(frm, text=APP_TITLE, font=("Segoe UI", 20, "bold"), fg=COLOR_PRIMARY, bg=WINDOW_BG)
        title.pack(pady=(0,12))
        nb = ttk.Notebook(frm)
        tab_login = ttk.Frame(nb); tab_reg = ttk.Frame(nb)
        nb.add(tab_login, text="Login"); nb.add(tab_reg, text="Register"); nb.pack(fill='both', expand=True)
        # Login
        ttk.Label(tab_login, text="Email:").pack(anchor='w', padx=8, pady=(8,2))
        self.login_email = ttk.Entry(tab_login, width=40); self.login_email.pack(padx=8)
        ttk.Label(tab_login, text="Password:").pack(anchor='w', padx=8, pady=(8,2))
        self.login_pass = ttk.Entry(tab_login, show='*', width=40); self.login_pass.pack(padx=8)
        ttk.Button(tab_login, text="Login", command=self.do_login).pack(pady=10)
        # Register
        ttk.Label(tab_reg, text="Email:").pack(anchor='w', padx=8, pady=(8,2))
        self.reg_email = ttk.Entry(tab_reg, width=40); self.reg_email.pack(padx=8)
        ttk.Label(tab_reg, text="Password:").pack(anchor='w', padx=8, pady=(8,2))
        self.reg_pass = ttk.Entry(tab_reg, show='*', width=40); self.reg_pass.pack(padx=8)
        ttk.Button(tab_reg, text="Register & Kirim OTP Aktivasi", command=self.do_register).pack(pady=10)
        ttk.Button(frm, text="Tutup (Esc)", command=self.quit_app).pack(pady=(8,0))
        self.bind("<Escape>", lambda e: self.quit_app())

    def do_register(self):
        email = self.reg_email.get().strip(); pw = self.reg_pass.get().strip()
        if not email or not pw:
            messagebox.showwarning("Peringatan","Email & password wajib diisi"); return
        ok, msg = register_user_with_otp(email, pw)
        if ok:
            messagebox.showinfo("Sukses", msg); ActivationDialog(self, email)
        else:
            messagebox.showerror("Error", msg)

    def do_login(self):
        email = self.login_email.get().strip(); pw = self.login_pass.get().strip()
        if not email or not pw:
            messagebox.showwarning("Peringatan","Email & password wajib diisi"); return
        ok, msg = verify_password_and_active(email, pw)
        if ok:
            self.destroy(); self.on_success(email)
        else:
            messagebox.showerror("Gagal login", msg)

    def quit_app(self):
        if messagebox.askyesno("Keluar", "Keluar aplikasi?"):
            self.master.destroy()

class AccountDialog(tk.Toplevel):
    def __init__(self, parent, initial=None, edit_mode=False):
        super().__init__(parent)
        self.title("Akun"); self.geometry("480x320"); self.configure(bg=WINDOW_BG)
        self.result = None; self.edit_mode = edit_mode
        ttk.Label(self, text="No Akun:").pack(anchor='w', padx=12, pady=6)
        self.e_no = ttk.Entry(self); self.e_no.pack(fill='x', padx=12)
        ttk.Label(self, text="Nama Akun:").pack(anchor='w', padx=12, pady=6)
        self.e_nama = ttk.Entry(self); self.e_nama.pack(fill='x', padx=12)
        ttk.Label(self, text="Tipe (Asset/Liability/Equity/Revenue/Expense):").pack(anchor='w', padx=12, pady=6)
        self.combo = ttk.Combobox(self, values=["Asset","Liability","Equity","Revenue","Expense"]); self.combo.pack(fill='x', padx=12)
        ttk.Label(self, text="Saldo Awal (angka, 0 jika tidak ada):").pack(anchor='w', padx=12, pady=6)
        self.e_sb = ttk.Entry(self); self.e_sb.pack(fill='x', padx=12); self.e_sb.insert(0, "0")
        ttk.Button(self, text="Simpan", command=self.save).pack(pady=12)
        if initial:
            no,nama,tipe,sb = initial
            self.e_no.insert(0,no); self.e_nama.insert(0,nama); self.combo.set(tipe); self.e_sb.delete(0,'end'); self.e_sb.insert(0,str(sb))
            if edit_mode: self.e_no.config(state='disabled')
    def save(self):
        no = self.e_no.get().strip(); nama = self.e_nama.get().strip(); tipe = self.combo.get().strip()
        sb = self.e_sb.get().strip()
        if not (no and nama and tipe):
            messagebox.showerror("Error","Semua field wajib diisi"); return
        try:
            sb_val = float(sb.replace(",","")) if sb else 0.0
        except Exception:
            messagebox.showerror("Error","Saldo Awal tidak valid"); return
        self.result = (no,nama,tipe,sb_val); self.destroy()

class JournalDialog(tk.Toplevel):
    def __init__(self, parent, accounts):
        super().__init__(parent)
        self.title("Tambah Jurnal"); self.geometry("560x480"); self.configure(bg=WINDOW_BG)
        self.result = None
        ttk.Label(self, text="Tanggal (YYYY-MM-DD):").pack(anchor='w', padx=12, pady=6)
        self.e_date = ttk.Entry(self); self.e_date.pack(fill='x', padx=12); self.e_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        ttk.Label(self, text="Akun Debit (no - nama):").pack(anchor='w', padx=12, pady=6)
        self.combo_debit = ttk.Combobox(self, values=[f"{a[0]} - {a[1]}" for a in accounts]); self.combo_debit.pack(fill='x', padx=12)
        ttk.Label(self, text="Akun Kredit (no - nama):").pack(anchor='w', padx=12, pady=6)
        self.combo_credit = ttk.Combobox(self, values=[f"{a[0]} - {a[1]}" for a in accounts]); self.combo_credit.pack(fill='x', padx=12)
        ttk.Label(self, text="Debit (angka, 0 jika tidak ada):").pack(anchor='w', padx=12, pady=6)
        self.e_debit = ttk.Entry(self); self.e_debit.pack(fill='x', padx=12); self.e_debit.insert(0,"0")
        ttk.Label(self, text="Kredit (angka, 0 jika tidak ada):").pack(anchor='w', padx=12, pady=6)
        self.e_kredit = ttk.Entry(self); self.e_kredit.pack(fill='x', padx=12); self.e_kredit.insert(0,"0")
        ttk.Label(self, text="Keterangan:").pack(anchor='w', padx=12, pady=6)
        self.e_ket = ttk.Entry(self); self.e_ket.pack(fill='x', padx=12)
        ttk.Button(self, text="Simpan", command=self.save).pack(pady=12)
    def save(self):
        tanggal = self.e_date.get().strip()
        dsel = self.combo_debit.get().strip(); csel = self.combo_credit.get().strip()
        debit = self.e_debit.get().strip(); kredit = self.e_kredit.get().strip(); ket = self.e_ket.get().strip()
        if not (tanggal and dsel and csel):
            messagebox.showerror("Error","Tanggal dan akun wajib diisi"); return
        try:
            debit_val = float(debit.replace(",","")) if debit else 0.0
            kredit_val = float(kredit.replace(",","")) if kredit else 0.0
            adebit = dsel.split(" - ",1)[0].strip(); acredit = csel.split(" - ",1)[0].strip()
            if debit_val < 0 or kredit_val < 0: raise ValueError("Nilai tidak boleh negatif")
            if debit_val == 0 and kredit_val == 0: raise ValueError("Isi debit atau kredit minimal satu")
            datetime.strptime(tanggal, "%Y-%m-%d")
            self.result = (tanggal, adebit, acredit, debit_val, kredit_val, ket)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

class AdjustDialog(tk.Toplevel):
    def __init__(self, parent, accounts):
        super().__init__(parent)
        self.title("Tambah Jurnal Penyesuaian"); self.geometry("560x480"); self.configure(bg=WINDOW_BG)
        self.result = None
        ttk.Label(self, text="Tanggal (YYYY-MM-DD):").pack(anchor='w', padx=12, pady=6)
        self.e_date = ttk.Entry(self); self.e_date.pack(fill='x', padx=12); self.e_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        ttk.Label(self, text="Akun Debit (no - nama):").pack(anchor='w', padx=12, pady=6)
        self.combo_debit = ttk.Combobox(self, values=[f"{a[0]} - {a[1]}" for a in accounts]); self.combo_debit.pack(fill='x', padx=12)
        ttk.Label(self, text="Akun Kredit (no - nama):").pack(anchor='w', padx=12, pady=6)
        self.combo_credit = ttk.Combobox(self, values=[f"{a[0]} - {a[1]}" for a in accounts]); self.combo_credit.pack(fill='x', padx=12)
        ttk.Label(self, text="Debit (angka, 0 jika tidak ada):").pack(anchor='w', padx=12, pady=6)
        self.e_debit = ttk.Entry(self); self.e_debit.pack(fill='x', padx=12); self.e_debit.insert(0,"0")
        ttk.Label(self, text="Kredit (angka, 0 jika tidak ada):").pack(anchor='w', padx=12, pady=6)
        self.e_kredit = ttk.Entry(self); self.e_kredit.pack(fill='x', padx=12); self.e_kredit.insert(0,"0")
        ttk.Label(self, text="Keterangan:").pack(anchor='w', padx=12, pady=6)
        self.e_ket = ttk.Entry(self); self.e_ket.pack(fill='x', padx=12)
        ttk.Button(self, text="Simpan Penyesuaian", command=self.save).pack(pady=12)
    def save(self):
        tanggal = self.e_date.get().strip()
        dsel = self.combo_debit.get().strip(); csel = self.combo_credit.get().strip()
        debit = self.e_debit.get().strip(); kredit = self.e_kredit.get().strip(); ket = self.e_ket.get().strip()
        if not (tanggal and dsel and csel):
            messagebox.showerror("Error","Tanggal dan akun wajib diisi"); return
        try:
            debit_val = float(debit.replace(",","")) if debit else 0.0
            kredit_val = float(kredit.replace(",","")) if kredit else 0.0
            adebit = dsel.split(" - ",1)[0].strip(); acredit = csel.split(" - ",1)[0].strip()
            if debit_val < 0 or kredit_val < 0: raise ValueError("Nilai tidak boleh negatif")
            if debit_val == 0 and kredit_val == 0: raise ValueError("Isi debit atau kredit minimal satu")
            datetime.strptime(tanggal, "%Y-%m-%d")
            self.result = (tanggal, adebit, acredit, debit_val, kredit_val, ket)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))



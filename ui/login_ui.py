import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from database import (
    register_user_with_otp,
    verify_activation_otp,
    verify_password_and_active
)


class ActivationDialog(tk.Toplevel):
    def __init__(self, parent, email):
        super().__init__(parent)
        self.title("Aktivasi Akun")
        self.geometry("420x180")
        self.resizable(False, False)
        self.email = email

        ttk.Label(self, text=f"Masukkan kode OTP yang dikirim ke {email}").pack(padx=12, pady=(12, 6))
        self.entry_otp = ttk.Entry(self)
        self.entry_otp.pack(fill='x', padx=12)

        ttk.Button(self, text="Aktivasi", command=self.do_activate).pack(pady=12)
        ttk.Button(self, text="Tutup", command=self.destroy).pack()

    def do_activate(self):
        otp = self.entry_otp.get().strip()
        if not otp:
            messagebox.showwarning("Peringatan", "Masukkan OTP terlebih dahulu")
            return

        ok, msg = verify_activation_otp(self.email, otp)
        if ok:
            messagebox.showinfo("Sukses", msg)
            self.destroy()
        else:
            messagebox.showerror("Error", msg)


class LoginWindow(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.overrideredirect(True)

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{sw}x{sh}+0+0")

        self.configure(bg="#F8FAFC")
        self.build()

    def build(self):
        frm = ttk.Frame(self, padding=20)
        frm.place(relx=0.5, rely=0.5, anchor='center')

        title = tk.Label(frm, text="Project SIA - Kelompok Ngapak",
                         font=("Segoe UI", 20, "bold"), fg="#0077B6", bg="#F8FAFC")
        title.pack(pady=(0, 12))

        nb = ttk.Notebook(frm)
        tab_login = ttk.Frame(nb)
        tab_reg = ttk.Frame(nb)

        nb.add(tab_login, text="Login")
        nb.add(tab_reg, text="Register")
        nb.pack(fill='both', expand=True)

        # Login
        ttk.Label(tab_login, text="Email:").pack(anchor='w', padx=8, pady=(8, 2))
        self.login_email = ttk.Entry(tab_login, width=40)
        self.login_email.pack(padx=8)

        ttk.Label(tab_login, text="Password:").pack(anchor='w', padx=8, pady=(8, 2))
        self.login_pass = ttk.Entry(tab_login, show='*', width=40)
        self.login_pass.pack(padx=8)

        ttk.Button(tab_login, text="Login", command=self.do_login).pack(pady=10)

        # Register
        ttk.Label(tab_reg, text="Email:").pack(anchor='w', padx=8, pady=(8, 2))
        self.reg_email = ttk.Entry(tab_reg, width=40)
        self.reg_email.pack(padx=8)

        ttk.Label(tab_reg, text="Password:").pack(anchor='w', padx=8, pady=(8, 2))
        self.reg_pass = ttk.Entry(tab_reg, show='*', width=40)
        self.reg_pass.pack(padx=8)

        ttk.Button(tab_reg, text="Register & Kirim OTP Aktivasi",
                   command=self.do_register).pack(pady=10)

        ttk.Button(frm, text="Tutup (Esc)", command=self.quit_app).pack(pady=(8, 0))
        self.bind("<Escape>", lambda e: self.quit_app())

    # ---------------------
    def do_register(self):
        email = self.reg_email.get().strip()
        pw = self.reg_pass.get().strip()

        if not email or not pw:
            messagebox.showwarning("Peringatan", "Email & password wajib diisi")
            return

        ok, msg = register_user_with_otp(email, pw)
        if ok:
            messagebox.showinfo("Sukses", msg)
            ActivationDialog(self, email)
        else:
            messagebox.showerror("Error", msg)

    def do_login(self):
        email = self.login_email.get().strip()
        pw = self.login_pass.get().strip()

        if not email or not pw:
            messagebox.showwarning("Peringatan", "Email & password wajib diisi")
            return

        ok, msg = verify_password_and_active(email, pw)
        if ok:
            self.destroy()
            self.on_success(email)
        else:
            messagebox.showerror("Gagal login", msg)

    def quit_app(self):
        if messagebox.askyesno("Keluar", "Keluar aplikasi?"):
            self.master.destroy()

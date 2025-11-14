# main.py
"""
Project SIA Kelompok Ngapak - Single-file desktop app
Requirements:
  pip install pandas matplotlib openpyxl reportlab
Run:
  python main.py
"""
import os
import sqlite3
import hashlib
from datetime import datetime
from decimal import Decimal, getcontext
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

# optional import checks
try:
    import pandas as pd
except Exception:
    pd = None

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt
except Exception:
    matplotlib = None
    FigureCanvasTkAgg = None
    plt = None

try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
except Exception:
    SimpleDocTemplate = None

from openpyxl import Workbook

# ---------- Config ----------
DB_FILENAME = "akuntansi.db"
APP_TITLE = "Project SIA Kelompok Ngapak"
WINDOW_BG = "#F8FAFC"
COLOR_PRIMARY = "#0077B6"   # biru laut
COLOR_ACCENT = "#00B4D8"    # biru elektrik
COLOR_TEXT = "#023E8A"
FONT = ("Segoe UI", 10)

getcontext().prec = 28

# ---------- Utility ----------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def to_decimal(x):
    try:
        return Decimal(str(x))
    except Exception:
        return Decimal('0')

def moneyfmt(x):
    try:
        d = to_decimal(x)
        return f"{d:,.2f}"
    except Exception:
        return str(x)

# ---------- Database helpers ----------
def init_db_if_needed():
    need_init = not os.path.exists(DB_FILENAME)
    conn = sqlite3.connect(DB_FILENAME)
    cur = conn.cursor()
    # create tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS akun (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            no_akun TEXT UNIQUE NOT NULL,
            nama_akun TEXT NOT NULL,
            tipe TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jurnal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT NOT NULL,
            akun_debit TEXT NOT NULL,
            akun_kredit TEXT NOT NULL,
            debit REAL DEFAULT 0,
            kredit REAL DEFAULT 0,
            keterangan TEXT
        )
    """)
    conn.commit()
    conn.close()
    return need_init

def ensure_default_data():
    conn = sqlite3.connect(DB_FILENAME)
    cur = conn.cursor()
    # default admin
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)",
                    ("admin@gmail.com", hash_password("admin123")))
    # example accounts if none
    cur.execute("SELECT COUNT(*) FROM akun")
    if cur.fetchone()[0] == 0:
        sample = [
            ("101","Kas","Asset"),
            ("102","Piutang Dagang","Asset"),
            ("201","Hutang Usaha","Liability"),
            ("301","Modal Pemilik","Equity"),
            ("401","Pendapatan Jasa","Revenue"),
            ("501","Beban Gaji","Expense"),
        ]
        for no,nm,tipe in sample:
            cur.execute("INSERT OR IGNORE INTO akun (no_akun, nama_akun, tipe) VALUES (?, ?, ?)", (no,nm,tipe))
    conn.commit(); conn.close()

def get_conn():
    if not os.path.exists(DB_FILENAME):
        init_db_if_needed()
    return sqlite3.connect(DB_FILENAME)

# ---------- CRUD: accounts ----------
def list_accounts():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT no_akun, nama_akun, tipe FROM akun ORDER BY no_akun")
    rows = cur.fetchall(); conn.close(); return rows

def add_account_db(no, nama, tipe):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO akun (no_akun, nama_akun, tipe) VALUES (?, ?, ?)", (no, nama, tipe))
    conn.commit(); conn.close()

def edit_account_db(no, nama, tipe):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("UPDATE akun SET nama_akun=?, tipe=? WHERE no_akun=?", (nama, tipe, no))
    conn.commit(); conn.close()

def delete_account_db(no):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM jurnal WHERE akun_debit=? OR akun_kredit=?", (no, no))
    if cur.fetchone()[0] > 0:
        conn.close(); raise ValueError("Tidak dapat menghapus akun yang memiliki transaksi.")
    cur.execute("DELETE FROM akun WHERE no_akun=?", (no,))
    conn.commit(); conn.close()

# ---------- CRUD: jurnal ----------
def add_journal_db(tanggal, akun_debit, akun_kredit, debit, kredit, keterangan):
    if float(debit) < 0 or float(kredit) < 0:
        raise ValueError("Debit/Kredit tidak boleh negatif.")
    if float(debit) == 0 and float(kredit) == 0:
        raise ValueError("Isi debit atau kredit minimal satu.")
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM akun WHERE no_akun=?", (akun_debit,))
    if cur.fetchone()[0] == 0:
        conn.close(); raise ValueError(f"Akun debit {akun_debit} tidak ditemukan")
    cur.execute("SELECT COUNT(*) FROM akun WHERE no_akun=?", (akun_kredit,))
    if cur.fetchone()[0] == 0:
        conn.close(); raise ValueError(f"Akun kredit {akun_kredit} tidak ditemukan")
    cur.execute("""INSERT INTO jurnal (tanggal, akun_debit, akun_kredit, debit, kredit, keterangan)
                   VALUES (?, ?, ?, ?, ?, ?)""", (tanggal, akun_debit, akun_kredit, float(debit), float(kredit), keterangan))
    conn.commit(); conn.close()

def list_journal_entries():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT id, tanggal, akun_debit, akun_kredit, debit, kredit, keterangan FROM jurnal ORDER BY tanggal, id")
    rows = cur.fetchall(); conn.close(); return rows

def delete_journal_db(_id):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM jurnal WHERE id=?", (_id,))
    conn.commit(); conn.close()

# ---------- Computations ----------
def compute_balances():
    accs = {}
    for no, nama, tipe in list_accounts():
        accs[no] = {'nama': nama, 'tipe': tipe, 'debit': to_decimal('0'), 'kredit': to_decimal('0')}
    for row in list_journal_entries():
        _id, tanggal, ad, ak, d, k, ket = row
        d = to_decimal(d); k = to_decimal(k)
        if ad not in accs:
            accs[ad] = {'nama': ad, 'tipe': 'Unknown', 'debit': to_decimal('0'), 'kredit': to_decimal('0')}
        if ak not in accs:
            accs[ak] = {'nama': ak, 'tipe': 'Unknown', 'debit': to_decimal('0'), 'kredit': to_decimal('0')}
        accs[ad]['debit'] += d
        accs[ak]['kredit'] += k
    return accs

def compute_trial_rows():
    bal = compute_balances()
    rows = []
    for no in sorted(bal.keys()):
        d = bal[no]['debit']; c = bal[no]['kredit']
        if d >= c:
            debit_bal = d - c; credit_bal = to_decimal('0')
        else:
            debit_bal = to_decimal('0'); credit_bal = c - d
        rows.append((no, bal[no]['nama'], bal[no]['tipe'], debit_bal, credit_bal))
    return rows

def prepare_balance_and_ratios():
    rows = compute_trial_rows()
    assets = to_decimal('0'); liabilities = to_decimal('0'); equity = to_decimal('0')
    for no,nm,tipe,d,c in rows:
        bal = d - c
        t = (tipe or "").lower()
        if t in ('asset','aset'):
            assets += max(bal, to_decimal('0'))
        elif t in ('liability','kewajiban','liab'):
            liabilities += max(-bal, to_decimal('0'))
        elif t in ('equity','ekuitas'):
            equity += max(-bal, to_decimal('0'))
    current_ratio = None
    debt_to_equity = None
    try:
        if liabilities != to_decimal('0'):
            current_ratio = assets / liabilities
    except Exception:
        current_ratio = None
    try:
        if equity != to_decimal('0'):
            debt_to_equity = liabilities / equity
    except Exception:
        debt_to_equity = None
    return {'assets': assets, 'liabilities': liabilities, 'equity': equity,
            'current_ratio': current_ratio, 'debt_to_equity': debt_to_equity}

# ---------- Export ----------
def export_trial_to_excel(path):
    rows = compute_trial_rows()
    wb = Workbook(); ws = wb.active; ws.title = "Neraca Saldo"
    ws.append(["No Akun","Nama","Tipe","Debit","Kredit"])
    for r in rows:
        ws.append([r[0], r[1], r[2], float(r[3]), float(r[4])])
    wb.save(path)

def export_journal_to_excel(path):
    rows = list_journal_entries()
    wb = Workbook(); ws = wb.active; ws.title = "Jurnal"
    ws.append(["ID","Tanggal","Akun Debit","Akun Kredit","Debit","Kredit","Keterangan"])
    for r in rows:
        ws.append([r[0], r[1], r[2], r[3], float(r[4]), float(r[5]), r[6]])
    wb.save(path)

def export_reports_to_pdf(path):
    if SimpleDocTemplate is None:
        raise RuntimeError("reportlab tidak terpasang")
    stats = prepare_balance_and_ratios()
    rows = compute_trial_rows()
    doc = SimpleDocTemplate(path, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    elems = []
    elems.append(Paragraph("Laporan Keuangan - Project SIA Kelompok Ngapak", styles['Title']))
    elems.append(Spacer(1,8))
    elems.append(Paragraph(f"Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elems.append(Spacer(1,8))
    elems.append(Paragraph("Neraca Saldo", styles['Heading2']))
    data = [["No Akun","Nama","Tipe","Debit","Kredit"]]
    for r in rows:
        data.append([r[0], r[1], r[2], f"{r[3]:,.2f}", f"{r[4]:,.2f}"])
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.gray),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),('GRID',(0,0),(-1,-1),0.5,colors.black)]))
    elems.append(t)
    elems.append(Spacer(1,12))
    elems.append(Paragraph("Ringkasan", styles['Heading2']))
    elems.append(Paragraph(f"Total Aset: {stats['assets']:,.2f}", styles['Normal']))
    elems.append(Paragraph(f"Total Liabilitas: {stats['liabilities']:,.2f}", styles['Normal']))
    elems.append(Paragraph(f"Total Ekuitas: {stats['equity']:,.2f}", styles['Normal']))
    cr = stats['current_ratio']; dte = stats['debt_to_equity']
    elems.append(Paragraph(f"Likuiditas (Current Ratio): {('N/A' if cr is None else f'{cr:.2f}')}", styles['Normal']))
    elems.append(Paragraph(f"Solvabilitas (Debt-to-Equity): {('N/A' if dte is None else f'{dte:.2f}')}", styles['Normal']))
    doc.build(elems)

# ---------- UI: Login / Main ----------
class LoginWindow(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.title("Login - " + APP_TITLE)
        self.configure(bg=WINDOW_BG)
        self.resizable(False, False)
        w = 480; h = 320
        sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
        x = (sw - w)//2; y = (sh - h)//2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.build()

    def build(self):
        frm = ttk.Frame(self); frm.pack(fill='both', expand=True, padx=18, pady=12)
        ttk.Label(frm, text=APP_TITLE, font=("Segoe UI", 16, "bold"), foreground=COLOR_PRIMARY).pack(pady=(0,12))
        ttk.Label(frm, text="Email:").pack(anchor='w')
        self.e_email = ttk.Entry(frm); self.e_email.pack(fill='x', pady=6)
        ttk.Label(frm, text="Password:").pack(anchor='w')
        self.e_pass = ttk.Entry(frm, show='*'); self.e_pass.pack(fill='x', pady=6)
        btnf = ttk.Frame(frm); btnf.pack(fill='x', pady=12)
        ttk.Button(btnf, text="Login", style='Accent.TButton', command=self.do_login).pack(side='left', padx=4)
        ttk.Button(btnf, text="Register", command=self.do_register).pack(side='left', padx=4)
        ttk.Button(btnf, text="Quit", command=self.quit_app).pack(side='right')
        self.lbl_info = ttk.Label(frm, text="", foreground='red'); self.lbl_info.pack(pady=6)

    def do_login(self):
        email = self.e_email.get().strip(); pw = self.e_pass.get().strip()
        if not email or not pw:
            self.lbl_info.config(text="Email & password wajib diisi"); return
        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT password_hash FROM users WHERE email=?", (email,))
        row = cur.fetchone(); conn.close()
        if not row:
            self.lbl_info.config(text="Email tidak terdaftar"); return
        if row[0] == hash_password(pw):
            self.destroy(); self.on_success(email)
        else:
            self.lbl_info.config(text="Password salah")

    def do_register(self):
        email = self.e_email.get().strip(); pw = self.e_pass.get().strip()
        if not email or not pw:
            self.lbl_info.config(text="Email & password wajib diisi"); return
        try:
            conn = get_conn(); cur = conn.cursor()
            cur.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, hash_password(pw)))
            conn.commit(); conn.close()
            messagebox.showinfo("Sukses", "Akun terdaftar. Silakan login.")
        except sqlite3.IntegrityError:
            self.lbl_info.config(text="Email sudah terdaftar.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def quit_app(self):
        self.master.destroy()

class MainApp(tk.Tk):
    def __init__(self, user_email):
        super().__init__()
        # borderless & fullscreen
        self.overrideredirect(True)
        sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
        self.geometry(f"{sw}x{sh}+0+0")
        self._is_fullscreen = True
        self._prev_geom = None

        self.configure(bg=WINDOW_BG)
        self.style = ttk.Style(self)
        try:
            self.style.theme_use('clam')
        except Exception:
            pass
        self.style.configure('TFrame', background=WINDOW_BG)
        self.style.configure('TLabel', background=WINDOW_BG, foreground=COLOR_TEXT, font=FONT)
        self.style.configure('Header.TLabel', font=("Segoe UI", 14, 'bold'), foreground=COLOR_PRIMARY, background=WINDOW_BG)
        self.style.configure('Accent.TButton', background=COLOR_ACCENT, foreground='white', font=("Segoe UI", 10, 'bold'))
        self.style.map('Accent.TButton', background=[('active', COLOR_PRIMARY)])

        self.user_email = user_email

        # header
        self.build_header()

        # tabs (notebook)
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill='both', expand=True, padx=18, pady=(12,18))

        # tabs
        self.tab_accounts = ttk.Frame(self.nb)
        self.tab_journal = ttk.Frame(self.nb)
        self.tab_ledger = ttk.Frame(self.nb)
        self.tab_trial = ttk.Frame(self.nb)
        self.tab_dashboard = ttk.Frame(self.nb)

        self.nb.add(self.tab_accounts, text="Akun")
        self.nb.add(self.tab_journal, text="Jurnal")
        self.nb.add(self.tab_ledger, text="Buku Besar")
        self.nb.add(self.tab_trial, text="Neraca Saldo")
        self.nb.add(self.tab_dashboard, text="Dashboard")

        # build
        self.build_accounts_tab(); self.build_journal_tab(); self.build_ledger_tab()
        self.build_trial_tab(); self.build_dashboard_tab()

        # initial refresh
        self.after(150, self.refresh_all)

        # key bindings
        self.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.bind("<Escape>", lambda e: self.exit_fullscreen_if_any())

    def build_header(self):
        hdr = tk.Frame(self, bg=COLOR_PRIMARY, height=52)
        hdr.pack(fill='x', side='top')
        lbl = tk.Label(hdr, text=APP_TITLE, bg=COLOR_PRIMARY, fg='white', font=("Segoe UI", 12, "bold"))
        lbl.pack(side='left', padx=12)
        # greeting
        short = self.user_email.split('@')[0] if self.user_email else ""
        self.lbl_greet = tk.Label(hdr, text=f"Selamat datang, {short}", bg=COLOR_PRIMARY, fg='white', font=("Segoe UI", 10))
        self.lbl_greet.pack(side='right', padx=12)
        btn_frame = tk.Frame(hdr, bg=COLOR_PRIMARY)
        btn_frame.pack(side='right', padx=6)
        btn_full = tk.Button(btn_frame, text="⛶", bg=COLOR_PRIMARY, fg='white', bd=0, command=self.toggle_fullscreen)
        btn_full.pack(side='left', padx=4)
        btn_logout = tk.Button(btn_frame, text="Logout", bg=COLOR_PRIMARY, fg='white', bd=0, command=self.logout)
        btn_logout.pack(side='left', padx=6)
        btn_close = tk.Button(btn_frame, text="✕", bg=COLOR_PRIMARY, fg='white', bd=0, command=self.quit_app)
        btn_close.pack(side='left', padx=4)
        hdr.bind("<ButtonPress-1>", self.start_move); hdr.bind("<ButtonRelease-1>", self.stop_move); hdr.bind("<B1-Motion>", self.do_move)
        self._offsetx = 0; self._offsety = 0

    def start_move(self, event):
        self._offsetx = event.x; self._offsety = event.y
    def stop_move(self, event):
        self._offsetx = 0; self._offsety = 0
    def do_move(self, event):
        if not self._is_fullscreen:
            x = self.winfo_x() + event.x - self._offsetx
            y = self.winfo_y() + event.y - self._offsety
            self.geometry(f"+{x}+{y}")

    def toggle_fullscreen(self):
        sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
        if not self._is_fullscreen:
            self._prev_geom = self.geometry()
            self.overrideredirect(True)
            self.geometry(f"{sw}x{sh}+0+0")
            self._is_fullscreen = True
        else:
            self.overrideredirect(False)
            if self._prev_geom:
                self.geometry(self._prev_geom)
            else:
                w, h = 1000, 650
                x = (sw - w)//2; y = (sh - h)//2
                self.geometry(f"{w}x{h}+{x}+{y}")
            self._is_fullscreen = False

    def exit_fullscreen_if_any(self):
        if self._is_fullscreen:
            self.toggle_fullscreen()

    def logout(self):
        if messagebox.askyesno("Logout", "Yakin ingin logout?"):
            self.destroy()
            main()

    def quit_app(self):
        if messagebox.askyesno("Keluar", "Keluar dari aplikasi?"):
            self.destroy()

    # ---------- Accounts tab ----------
    def build_accounts_tab(self):
        top = ttk.Frame(self.tab_accounts); top.pack(fill='x', pady=8)
        ttk.Label(top, text="Manajemen Akun", style='Header.TLabel').pack(side='left', padx=8)
        ttk.Button(top, text="Tambah Akun", style='Accent.TButton', command=self.ui_add_account).pack(side='right', padx=8)
        ttk.Button(top, text="Edit Akun", command=self.ui_edit_account).pack(side='right', padx=6)
        ttk.Button(top, text="Hapus Akun", command=self.ui_delete_account).pack(side='right', padx=6)
        cols = ("No Akun","Nama Akun","Tipe")
        self.tree_accounts = ttk.Treeview(self.tab_accounts, columns=cols, show='headings', height=18)
        for c in cols:
            self.tree_accounts.heading(c, text=c); self.tree_accounts.column(c, width=200 if c!="Nama Akun" else 420)
        self.tree_accounts.pack(fill='both', expand=True, padx=12, pady=8)

    def ui_add_account(self):
        d = AccountDialog(self)
        self.wait_window(d)
        if d.result:
            no,nama,tipe = d.result
            try:
                add_account_db(no,nama,tipe)
                messagebox.showinfo("Sukses","Akun ditambahkan")
                self.refresh_all()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def ui_edit_account(self):
        sel = self.tree_accounts.selection()
        if not sel:
            messagebox.showinfo("Info","Pilih akun untuk diedit"); return
        vals = self.tree_accounts.item(sel[0])['values']
        no = vals[0]
        d = AccountDialog(self, initial=vals, edit_mode=True)
        self.wait_window(d)
        if d.result:
            _, nama, tipe = d.result
            try:
                edit_account_db(no,nama,tipe)
                messagebox.showinfo("Sukses","Akun diupdate"); self.refresh_all()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def ui_delete_account(self):
        sel = self.tree_accounts.selection()
        if not sel:
            messagebox.showinfo("Info","Pilih akun untuk dihapus"); return
        vals = self.tree_accounts.item(sel[0])['values']; no = vals[0]
        if messagebox.askyesno("Konfirmasi", f"Hapus akun {no} - {vals[1]} ?"):
            try:
                delete_account_db(no); messagebox.showinfo("Sukses","Akun dihapus"); self.refresh_all()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ---------- Journal tab ----------
    def build_journal_tab(self):
        top = ttk.Frame(self.tab_journal); top.pack(fill='x', pady=6)
        ttk.Label(top, text="Jurnal Umum", style='Header.TLabel').pack(side='left', padx=8)
        ttk.Button(top, text="Tambah Jurnal", style='Accent.TButton', command=self.ui_add_journal).pack(side='right', padx=8)
        ttk.Button(top, text="Hapus Jurnal", command=self.ui_delete_journal).pack(side='right', padx=6)
        ttk.Button(top, text="Refresh", command=self.refresh_all).pack(side='right', padx=6)
        cols = ("ID","Tanggal","Akun Debit","Akun Kredit","Debit","Kredit","Keterangan")
        self.tree_journal = ttk.Treeview(self.tab_journal, columns=cols, show='headings', height=18)
        for c in cols:
            self.tree_journal.heading(c, text=c); self.tree_journal.column(c, width=120 if c!="Keterangan" else 360)
        self.tree_journal.pack(fill='both', expand=True, padx=12, pady=8)

    def ui_add_journal(self):
        accs = list_accounts()
        if not accs:
            messagebox.showinfo("Info","Tambahkan akun dulu"); return
        d = JournalDialog(self, accs)
        self.wait_window(d)
        if d.result:
            tanggal, debit_acc, credit_acc, debit_val, credit_val, ket = d.result
            try:
                add_journal_db(tanggal, debit_acc, credit_acc, debit_val, credit_val, ket)
                messagebox.showinfo("Sukses","Jurnal disimpan"); self.refresh_all()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def ui_delete_journal(self):
        sel = self.tree_journal.selection()
        if not sel:
            messagebox.showinfo("Info","Pilih jurnal untuk dihapus"); return
        ids = [self.tree_journal.item(s)['values'][0] for s in sel]
        for _id in ids:
            delete_journal_db(_id)
        messagebox.showinfo("Sukses", f"{len(ids)} jurnal dihapus")
        self.refresh_all()

    # ---------- Ledger tab ----------
    def build_ledger_tab(self):
        top = ttk.Frame(self.tab_ledger); top.pack(fill='x', pady=6)
        ttk.Label(top, text="Buku Besar (Pilih Akun)", style='Header.TLabel').pack(side='left', padx=8)
        self.combo_ledger_accounts = ttk.Combobox(top, values=[f"{a[0]} - {a[1]}" for a in list_accounts()], width=32)
        self.combo_ledger_accounts.pack(side='left', padx=8)
        ttk.Button(top, text="Tampilkan", command=self.refresh_ledger_for_account).pack(side='left', padx=6)
        ttk.Button(top, text="Refresh Akun", command=self.refresh_all).pack(side='right', padx=8)
        cols = ("Tanggal","Journal ID","Memo","Debit","Kredit","Saldo Berjalan")
        self.tree_ledger_account = ttk.Treeview(self.tab_ledger, columns=cols, show='headings', height=18)
        for c in cols:
            self.tree_ledger_account.heading(c, text=c); self.tree_ledger_account.column(c, width=140 if c!="Memo" else 360)
        self.tree_ledger_account.pack(fill='both', expand=True, padx=12, pady=8)

    def refresh_ledger_for_account(self):
        sel = self.combo_ledger_accounts.get()
        if not sel:
            messagebox.showinfo("Info","Pilih akun"); return
        no = sel.split(" - ",1)[0].strip()
        rows = []
        for r in list_journal_entries():
            _id,tanggal,ad,ak,d,k,ket = r
            if ad==no or ak==no:
                rows.append(r)
        for r in self.tree_ledger_account.get_children(): self.tree_ledger_account.delete(r)
        bal = to_decimal('0')
        for _id,tanggal,ad,ak,d,k,ket in rows:
            if ad == no:
                bal += to_decimal(d)
                debit = f"{d:,.2f}"; kredit = ""
            else:
                bal -= to_decimal(k)
                debit = ""; kredit = f"{k:,.2f}"
            self.tree_ledger_account.insert("", "end", values=(tanggal, _id, ket, debit, kredit, f"{bal:,.2f}"))

    # ---------- Trial tab ----------
    def build_trial_tab(self):
        top = ttk.Frame(self.tab_trial); top.pack(fill='x', pady=6)
        ttk.Label(top, text="Neraca Saldo", style='Header.TLabel').pack(side='left', padx=8)
        ttk.Button(top, text="Export Neraca ke Excel", command=self.export_trial_excel).pack(side='right', padx=8)
        cols = ("No Akun","Nama Akun","Tipe","Debit","Kredit")
        self.tree_trial = ttk.Treeview(self.tab_trial, columns=cols, show='headings', height=18)
        for c in cols:
            self.tree_trial.heading(c, text=c); self.tree_trial.column(c, width=140 if c!="Nama Akun" else 360)
        self.tree_trial.pack(fill='both', expand=True, padx=12, pady=8)

    # ---------- Dashboard ----------
    def build_dashboard_tab(self):
        top = ttk.Frame(self.tab_dashboard); top.pack(fill='x', pady=6)
        ttk.Label(top, text="Dashboard", style='Header.TLabel').pack(side='left', padx=8)
        ttk.Button(top, text="Refresh", command=self.refresh_all).pack(side='right', padx=8)
        if plt is None or FigureCanvasTkAgg is None:
            lbl = ttk.Label(self.tab_dashboard, text="matplotlib belum terpasang - grafik tidak tersedia")
            lbl.pack(padx=12, pady=12)
            self.fig = None; self.axes = None; self.canvas_dash = None
            return
        self.fig, self.axes = plt.subplots(1,3, figsize=(12,4))
        self.fig.tight_layout(pad=3.0)
        self.canvas_dash = FigureCanvasTkAgg(self.fig, master=self.tab_dashboard)
        self.canvas_dash.get_tk_widget().pack(fill='both', expand=True, padx=12, pady=12)

    # ---------- Refresh ----------
    def refresh_all(self):
        # accounts
        for r in self.tree_accounts.get_children(): self.tree_accounts.delete(r)
        for no,nama,tipe in list_accounts():
            self.tree_accounts.insert("", "end", values=(no,nama,tipe))
        # journal
        for r in self.tree_journal.get_children(): self.tree_journal.delete(r)
        for id_,tanggal,ad,ak,d,k,ket in list_journal_entries():
            self.tree_journal.insert("", "end", values=(id_, tanggal, ad, ak, f"{d:,.2f}", f"{k:,.2f}", ket))
        # trial
        for r in self.tree_trial.get_children(): self.tree_trial.delete(r)
        for no,nama,tipe,d,c in compute_trial_rows():
            self.tree_trial.insert("", "end", values=(no,nama,tipe, f"{d:,.2f}", f"{c:,.2f}"))
        # ledger combo values
        self.combo_ledger_accounts['values'] = [f"{a[0]} - {a[1]}" for a in list_accounts()]
        # dashboard draw
        self.draw_dashboard()

    def draw_dashboard(self):
        if plt is None or FigureCanvasTkAgg is None:
            return
        stats = prepare_balance_and_ratios()
        for ax in self.axes: ax.clear()
        aset = float(stats['assets']); liab = float(stats['liabilities'])
        self.axes[0].bar(['Aset','Kewajiban'], [aset, liab], color=[COLOR_PRIMARY, COLOR_ACCENT])
        self.axes[0].set_title("Aset vs Kewajiban")
        cr = stats['current_ratio']
        if cr is None:
            self.axes[1].text(0.5,0.5,"N/A", ha='center', va='center', fontsize=14)
            self.axes[1].set_title("Likuiditas (Current Ratio)")
        else:
            val = float(cr)
            self.axes[1].barh(['CR'], [val], color=COLOR_ACCENT)
            self.axes[1].set_xlim(0, max(1.5, val*1.2))
            self.axes[1].set_title(f"Likuiditas (CR): {val:.2f}")
        dte = stats['debt_to_equity']
        if dte is None:
            self.axes[2].text(0.5,0.5,"N/A", ha='center', va='center', fontsize=14)
            self.axes[2].set_title("Solvabilitas (D/E)")
        else:
            val = float(dte)
            self.axes[2].barh(['D/E'], [val], color=COLOR_PRIMARY)
            self.axes[2].set_xlim(0, max(1.5, val*1.2))
            self.axes[2].set_title(f"Solvabilitas (D/E): {val:.2f}")
        self.fig.tight_layout(); self.canvas_dash.draw()

    # ---------- Export handlers ----------
    def export_trial_excel(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
        if not path: return
        try:
            export_trial_to_excel(path)
            messagebox.showinfo("Sukses", "Neraca Saldo disimpan.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_journal_excel(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
        if not path: return
        try:
            export_journal_to_excel(path)
            messagebox.showinfo("Sukses", "Jurnal disimpan.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_reports_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")])
        if not path: return
        try:
            export_reports_to_pdf(path)
            messagebox.showinfo("Sukses", "Laporan PDF disimpan.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# ---------- Dialogs ----------
class AccountDialog(tk.Toplevel):
    def __init__(self, parent, initial=None, edit_mode=False):
        super().__init__(parent)
        self.title("Akun"); self.geometry("420x240"); self.configure(bg=WINDOW_BG)
        self.result = None; self.edit_mode = edit_mode
        ttk.Label(self, text="No Akun:").pack(anchor='w', padx=12, pady=6)
        self.e_no = ttk.Entry(self); self.e_no.pack(fill='x', padx=12)
        ttk.Label(self, text="Nama Akun:").pack(anchor='w', padx=12, pady=6)
        self.e_nama = ttk.Entry(self); self.e_nama.pack(fill='x', padx=12)
        ttk.Label(self, text="Tipe (Asset/Liability/Equity/Revenue/Expense):").pack(anchor='w', padx=12, pady=6)
        self.combo = ttk.Combobox(self, values=["Asset","Liability","Equity","Revenue","Expense"]); self.combo.pack(fill='x', padx=12)
        ttk.Button(self, text="Simpan", style='Accent.TButton', command=self.save).pack(pady=12)
        if initial:
            no,nama,tipe = initial; self.e_no.insert(0,no); self.e_nama.insert(0,nama); self.combo.set(tipe)
            if edit_mode: self.e_no.config(state='disabled')
    def save(self):
        no = self.e_no.get().strip(); nama = self.e_nama.get().strip(); tipe = self.combo.get().strip()
        if not (no and nama and tipe): messagebox.showerror("Error","Semua field wajib diisi"); return
        self.result = (no,nama,tipe); self.destroy()

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
        ttk.Button(self, text="Simpan", style='Accent.TButton', command=self.save).pack(pady=12)
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

# ---------- Program start ----------
def main():
    # init DB + defaults
    init_db_if_needed()
    ensure_default_data()

    # check optional libs
    missing = []
    if pd is None:
        missing.append("pandas")
    if matplotlib is None or plt is None:
        missing.append("matplotlib")
    if SimpleDocTemplate is None:
        missing.append("reportlab")
    if missing:
        msg = "Beberapa modul optional tidak terpasang: " + ", ".join(missing) + ".\nBeberapa fitur (grafik/PDF/Excel) mungkin tidak berfungsi.\n\nLanjutkan saja (OK) atau install modul dulu (Cancel)."
        if not messagebox.askokcancel("Dependency missing", msg):
            return

    root = tk.Tk(); root.withdraw()
    def on_success(email):
        root.destroy()
        app = MainApp(email)
        app.mainloop()
    login = LoginWindow(root, on_success)
    login.grab_set()
    root.mainloop()

if __name__ == "__main__":
    main()

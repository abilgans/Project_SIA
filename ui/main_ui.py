import tkinter as tk
from tkinter import ttk, messagebox

from datetime import datetime
from decimal import Decimal

# Import dari folder database
from database import (
    list_accounts,
    add_account_db,
    edit_account_db,
    delete_account_db,

    list_journal_entries,
    add_journal_db,
    delete_journal_db,

    list_adjusting_entries,
    add_adjusting_db,
    delete_adjusting_db,
    apply_adjustments,

    compute_trial_rows,
    compute_financial_statements,
    prepare_balance_and_ratios,
)

# Import dialog UI
from ui.dialog_account import AccountDialog
from ui.dialog_journal import JournalDialog
from ui.dialog_adjust import AdjustDialog


class MainApp(tk.Frame):
    def __init__(self, master, user_email):
        super().__init__(master)
        self.master = master
        self.master.title("Project SIA - Sistem Informasi Akuntansi")
        self.master.geometry("1280x720")
        self.master.configure(bg="#F8FAFC")

        self.user_email = user_email

        self.pack(fill="both", expand=True)
        self.create_menu()
        self.create_tabs()
        self.load_all_data()

    # ============================================================
    # MENU
    # ============================================================
    def create_menu(self):
        menubar = tk.Menu(self.master)

        # File
        m_file = tk.Menu(menubar, tearoff=0)
        m_file.add_command(label="Apply Adjustments", command=self.do_apply_adjustments)
        m_file.add_separator()
        m_file.add_command(label="Keluar", command=self.master.destroy)
        menubar.add_cascade(label="File", menu=m_file)

        # Help
        m_help = tk.Menu(menubar, tearoff=0)
        m_help.add_command(label="Tentang", command=lambda: messagebox.showinfo(
            "Tentang",
            "Project SIA - Sistem Informasi Akuntansi\nKelompok Ngapak"
        ))
        menubar.add_cascade(label="Help", menu=m_help)

        self.master.config(menu=menubar)

    # ============================================================
    # TAB CONTROL
    # ============================================================
    def create_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=12)

        self.tab_accounts = ttk.Frame(self.notebook)
        self.tab_journal = ttk.Frame(self.notebook)
        self.tab_adjust = ttk.Frame(self.notebook)
        self.tab_trial = ttk.Frame(self.notebook)
        self.tab_reports = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_accounts, text="Daftar Akun")
        self.notebook.add(self.tab_journal, text="Jurnal Umum")
        self.notebook.add(self.tab_adjust, text="Adjusting Entries")
        self.notebook.add(self.tab_trial, text="Neraca Saldo")
        self.notebook.add(self.tab_reports, text="Laporan Keuangan")

        self.build_accounts_tab()
        self.build_journal_tab()
        self.build_adjust_tab()
        self.build_trial_tab()
        self.build_report_tab()

    # ============================================================
    # TAB: DAFTAR AKUN
    # ============================================================
    def build_accounts_tab(self):
        frm_btn = ttk.Frame(self.tab_accounts)
        frm_btn.pack(anchor="w", pady=8)

        ttk.Button(frm_btn, text="Tambah", command=self.add_account).pack(side="left", padx=4)
        ttk.Button(frm_btn, text="Edit", command=self.edit_account).pack(side="left", padx=4)
        ttk.Button(frm_btn, text="Hapus", command=self.delete_account).pack(side="left", padx=4)

        self.tree_acc = ttk.Treeview(
            self.tab_accounts,
            columns=("no", "nama", "tipe"),
            show="headings",
            height=20
        )
        self.tree_acc.heading("no", text="No Akun")
        self.tree_acc.heading("nama", text="Nama Akun")
        self.tree_acc.heading("tipe", text="Tipe")

        self.tree_acc.column("no", width=100)
        self.tree_acc.column("nama", width=200)
        self.tree_acc.column("tipe", width=120)

        self.tree_acc.pack(fill="both", expand=True, padx=8, pady=8)

    def load_accounts(self):
        for i in self.tree_acc.get_children():
            self.tree_acc.delete(i)

        for no, nama, tipe in list_accounts():
            self.tree_acc.insert("", "end", values=(no, nama, tipe))

    def add_account(self):
        dlg = AccountDialog(self.master)
        self.master.wait_window(dlg)
        if dlg.result:
            no, nama, tipe = dlg.result
            try:
                add_account_db(no, nama, tipe)
                self.load_accounts()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def edit_account(self):
        sel = self.tree_acc.focus()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih akun terlebih dahulu")
            return

        no, nama, tipe = self.tree_acc.item(sel, "values")
        dlg = AccountDialog(self.master, initial=(no, nama, tipe), edit_mode=True)
        self.master.wait_window(dlg)

        if dlg.result:
            _no, _nama, _tipe = dlg.result
            try:
                edit_account_db(_no, _nama, _tipe)
                self.load_accounts()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_account(self):
        sel = self.tree_acc.focus()
        if not sel:
            messagebox.showwarning("Perhatian", "Pilih akun terlebih dahulu")
            return

        no, nama, tipe = self.tree_acc.item(sel, "values")

        if messagebox.askyesno("Konfirmasi", f"Hapus akun {no} - {nama}?"):
            try:
                delete_account_db(no)
                self.load_accounts()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ============================================================
    # TAB: JURNAL UMUM
    # ============================================================
    def build_journal_tab(self):
        frm_btn = ttk.Frame(self.tab_journal)
        frm_btn.pack(anchor="w", pady=8)

        ttk.Button(frm_btn, text="Tambah", command=self.add_journal).pack(side="left", padx=4)
        ttk.Button(frm_btn, text="Hapus", command=self.delete_journal).pack(side="left", padx=4)

        cols = ("id", "tanggal", "akun_debit", "akun_kredit", "debit", "kredit", "keterangan")
        self.tree_j = ttk.Treeview(self.tab_journal, columns=cols, show="headings", height=20)

        for c in cols:
            self.tree_j.heading(c, text=c.capitalize())
            self.tree_j.column(c, width=120)

        self.tree_j.column("keterangan", width=240)

        self.tree_j.pack(fill="both", expand=True, padx=8, pady=8)

    def load_journal(self):
        for i in self.tree_j.get_children():
            self.tree_j.delete(i)

        for row in list_journal_entries():
            self.tree_j.insert("", "end", values=row)

    def add_journal(self):
        accounts = list_accounts()
        dlg = JournalDialog(self.master, accounts)
        self.master.wait_window(dlg)

        if dlg.result:
            try:
                add_journal_db(*dlg.result)
                self.load_journal()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_journal(self):
        sel = self.tree_j.focus()
        if not sel:
            messagebox.showwarning("Perhatian", "Pilih entri jurnal terlebih dahulu")
            return

        _id = self.tree_j.item(sel, "values")[0]

        if messagebox.askyesno("Konfirmasi", "Hapus entri jurnal ini?"):
            delete_journal_db(_id)
            self.load_journal()

    # ============================================================
    # TAB: ADJUSTING ENTRIES
    # ============================================================
    def build_adjust_tab(self):
        frm_btn = ttk.Frame(self.tab_adjust)
        frm_btn.pack(anchor="w", pady=8)

        ttk.Button(frm_btn, text="Tambah", command=self.add_adjust).pack(side="left", padx=4)
        ttk.Button(frm_btn, text="Hapus", command=self.delete_adjust).pack(side="left", padx=4)

        cols = ("id", "tanggal", "ad", "ak", "debit", "kredit", "ket")
        self.tree_adj = ttk.Treeview(self.tab_adjust, columns=cols, show="headings", height=20)

        for c in cols:
            self.tree_adj.heading(c, text=c.capitalize())
            self.tree_adj.column(c, width=120)

        self.tree_adj.column("ket", width=240)

        self.tree_adj.pack(fill="both", expand=True, padx=8, pady=8)

    def load_adjust(self):
        for i in self.tree_adj.get_children():
            self.tree_adj.delete(i)

        for row in list_adjusting_entries():
            self.tree_adj.insert("", "end", values=row)

    def add_adjust(self):
        accounts = list_accounts()
        dlg = AdjustDialog(self.master, accounts)
        self.master.wait_window(dlg)

        if dlg.result:
            try:
                add_adjusting_db(*dlg.result)
                self.load_adjust()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_adjust(self):
        sel = self.tree_adj.focus()
        if not sel:
            messagebox.showwarning("Perhatian", "Pilih entri adjusting terlebih dahulu")
            return

        _id = self.tree_adj.item(sel, "values")[0]

        if messagebox.askyesno("Konfirmasi", "Hapus adjusting entry ini?"):
            delete_adjusting_db(_id)
            self.load_adjust()

    def do_apply_adjustments(self):
        count = apply_adjustments()
        if count > 0:
            messagebox.showinfo("Sukses", f"{count} adjusting entry berhasil diterapkan ke jurnal.")
            self.load_journal()
        else:
            messagebox.showinfo("Info", "Tidak ada adjusting entry yang perlu diterapkan.")

    # ============================================================
    # TAB: NERACA SALDO (TRIAL BALANCE)
    # ============================================================
    def build_trial_tab(self):
        frm_opt = ttk.Frame(self.tab_trial)
        frm_opt.pack(anchor="w", pady=8)

        self.var_inc_adj = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frm_opt, variable=self.var_inc_adj,
            text="Sertakan Adjusting Entries"
        ).pack(side="left", padx=4)

        ttk.Button(frm_opt, text="Refresh", command=self.load_trial).pack(side="left")

        cols = ("no", "nama", "tipe", "debit", "kredit")
        self.tree_trial = ttk.Treeview(
            self.tab_trial, columns=cols, show="headings", height=20
        )

        for c in cols:
            self.tree_trial.heading(c, text=c.capitalize())
            self.tree_trial.column(c, width=140)

        self.tree_trial.column("nama", width=260)

        self.tree_trial.pack(fill="both", expand=True, padx=8, pady=8)

    def load_trial(self):
        for i in self.tree_trial.get_children():
            self.tree_trial.delete(i)

        rows = compute_trial_rows(include_adjustments=self.var_inc_adj.get())

        for r in rows:
            no, nama, tipe, d, c = r
            self.tree_trial.insert(
                "", "end",
                values=(
                    no, nama, tipe,
                    f"{float(d):,.2f}",
                    f"{float(c):,.2f}"
                )
            )

    # ============================================================
    # TAB: LAPORAN KEUANGAN
    # ============================================================
    def build_report_tab(self):
        self.frm_report = ttk.Frame(self.tab_reports, padding=12)
        self.frm_report.pack(fill="both", expand=True)

        # Dropdown laporan
        self.rep_type = ttk.Combobox(
            self.frm_report,
            values=[
                "Laba Rugi",
                "Neraca",
                "Perubahan Ekuitas",
                "Dashboard"
            ],
            state="readonly",
            width=30
        )
        self.rep_type.set("Laba Rugi")
        self.rep_type.pack(anchor="w")

        ttk.Button(self.frm_report, text="Tampilkan", command=self.show_report).pack(anchor="w", pady=6)

        self.txt_rep = tk.Text(self.frm_report, height=30, bg="white")
        self.txt_rep.pack(fill="both", expand=True)

    def show_report(self):
        self.txt_rep.delete("1.0", "end")

        rep = self.rep_type.get()

        inc, neraca, equity = compute_financial_statements(include_adjustments=True)
        ratios = prepare_balance_and_ratios(include_adjustments=True)

        if rep == "Laba Rugi":
            self.show_income_statement(inc)

        elif rep == "Neraca":
            self.show_balance_sheet(neraca)

        elif rep == "Perubahan Ekuitas":
            self.show_equity_change(equity)

        elif rep == "Dashboard":
            self.show_dashboard(ratios)

    # ---------------- Dashboard ----------------
    def show_dashboard(self, r):
        t = self.txt_rep
        t.insert("end", "=== DASHBOARD KEUANGAN ===\n\n")
        t.insert("end", f"Total Aset       : {float(r['assets']):,.2f}\n")
        t.insert("end", f"Total Kewajiban  : {float(r['liabilities']):,.2f}\n")
        t.insert("end", f"Total Ekuitas    : {float(r['equity']):,.2f}\n\n")

        t.insert("end", "Rasio Keuangan:\n")
        t.insert("end", f"Current Ratio     : {r['current_ratio']}\n")
        t.insert("end", f"Debt to Equity    : {r['debt_to_equity']}\n")

    # ---------------- Income Statement ----------------
    def show_income_statement(self, inc):
        t = self.txt_rep
        t.insert("end", "=== LAPORAN LABA RUGI ===\n\n")

        t.insert("end", "Pendapatan:\n")
        for no, nama, amt in inc['revenues']:
            t.insert("end", f"- {nama} : {float(amt):,.2f}\n")

        t.insert("end", "\nBeban:\n")
        for no, nama, amt in inc['expenses']:
            t.insert("end", f"- {nama} : {float(amt):,.2f}\n")

        t.insert("end", f"\nTOTAL PENDAPATAN : {float(inc['total_revenue']):,.2f}\n")
        t.insert("end", f"TOTAL BEBAN      : {float(inc['total_expense']):,.2f}\n")
        t.insert("end", f"\nLABA BERSIH      : {float(inc['net_income']):,.2f}\n")

    # ---------------- Balance Sheet ----------------
    def show_balance_sheet(self, b):
        t = self.txt_rep
        t.insert("end", "=== NERACA ===\n\n")

        t.insert("end", "Aset:\n")
        for no, nm, amt in b['assets']:
            t.insert("end", f"- {nm} : {float(amt):,.2f}\n")

        t.insert("end", f"TOTAL ASET : {float(b['total_assets']):,.2f}\n\n")

        t.insert("end", "Kewajiban:\n")
        for no, nm, amt in b['liabilities']:
            t.insert("end", f"- {nm} : {float(amt):,.2f}\n")

        t.insert("end", f"TOTAL KEWAJIBAN : {float(b['total_liabilities']):,.2f}\n\n")

        t.insert("end", "Ekuitas:\n")
        for no, nm, amt in b['equity']:
            t.insert("end", f"- {nm} : {float(amt):,.2f}\n")

        t.insert("end", f"TOTAL EKUITAS : {float(b['total_equity']):,.2f}\n")

    # ---------------- Equity Change ----------------
    def show_equity_change(self, eq):
        t = self.txt_rep
        t.insert("end", "=== PERUBAHAN EKUITAS ===\n\n")

        for lbl, val in eq:
            t.insert("end", f"{lbl:<30} : {float(val):,.2f}\n")

    # ============================================================
    # LOAD SEMUA DATA
    # ============================================================
    def load_all_data(self):
        self.load_accounts()
        self.load_journal()
        self.load_adjust()
        self.load_trial()

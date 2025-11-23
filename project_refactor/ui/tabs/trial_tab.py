import tkinter as tk
from tkinter import ttk, messagebox


def build_tab(app, frame):
    top = ttk.Frame(self.tab_trial); top.pack(fill='x', pady=6)
    ttk.Label(top, text="Neraca Saldo (Sebelum Penyesuaian)", style='Header.TLabel').pack(side='left', padx=8)
    ttk.Button(top, text="Export Neraca ke Excel", command=lambda: self.export_trial_excel(False)).pack(side='right', padx=8)
    cols = ("No Akun","Nama Akun","Tipe","Debit","Kredit")
    self.tree_trial = ttk.Treeview(self.tab_trial, columns=cols, show='headings', height=18)
    for c in cols:
        self.tree_trial.heading(c, text=c); self.tree_trial.column(c, width=140 if c!="Nama Akun" else 360)
    self.tree_trial.pack(fill='both', expand=True, padx=12, pady=8)

    just tab (table for adjustments)
    build_adjust_tab(self):
    top = ttk.Frame(self.tab_adjust); top.pack(fill='x', pady=6)
    ttk.Label(top, text="Jurnal Penyesuaian", style='Header.TLabel').pack(side='left', padx=8)
    ttk.Button(top, text="Tambah Penyesuaian", command=self.ui_add_adjust).pack(side='right', padx=6)
    ttk.Button(top, text="Hapus Penyesuaian", command=self.ui_delete_adjust).pack(side='right', padx=6)
    ttk.Button(top, text="Apply Penyesuaian (copy ke Jurnal)", command=self.ui_apply_adjustments).pack(side='right', padx=6)
    ttk.Button(top, text="Export Penyesuaian ke Excel", command=self.export_adjust_excel).pack(side='right', padx=6)
    cols = ("ID","Tanggal","Akun Debit","Akun Kredit","Debit","Kredit","Keterangan","Applied")
    self.tree_adjust = ttk.Treeview(self.tab_adjust, columns=cols, show='headings', height=18)
    for c in cols:
        self.tree_adjust.heading(c, text=c); self.tree_adjust.column(c, width=120 if c not in ("Keterangan","Applied") else (360 if c=="Keterangan" else 80))
    self.tree_adjust.pack(fill='both', expand=True, padx=12, pady=8)

    ial adjusted tab
    build_trial_adj_tab(self):
    top = ttk.Frame(self.tab_trial_adj); top.pack(fill='x', pady=6)
    ttk.Label(top, text="Neraca Saldo Setelah Penyesuaian", style='Header.TLabel').pack(side='left', padx=8)
    ttk.Button(top, text="Export Neraca Penyesuaian ke Excel", command=lambda: self.export_trial_excel(True)).pack(side='right', padx=8)
    cols = ("No Akun","Nama Akun","Tipe","Debit","Kredit")
    self.tree_trial_adj = ttk.Treeview(self.tab_trial_adj, columns=cols, show='headings', height=18)
    for c in cols:
        self.tree_trial_adj.heading(c, text=c); self.tree_trial_adj.column(c, width=140 if c!="Nama Akun" else 360)
    self.tree_trial_adj.pack(fill='both', expand=True, padx=12, pady=8)

    ports
    build_reports_tab(self):
    top = ttk.Frame(self.tab_reports); top.pack(fill='x', pady=6)
    ttk.Label(top, text="Laporan Keuangan (Setelah Penyesuaian)", style='Header.TLabel').pack(side='left', padx=8)
    ttk.Button(top, text="Export Laporan ke Excel", command=self.export_reports_excel).pack(side='right', padx=6)
    ttk.Button(top, text="Export Laporan ke PDF", command=self.export_reports_pdf).pack(side='right', padx=6)
    frame = ttk.Frame(self.tab_reports); frame.pack(fill='both', expand=True, padx=12, pady=8)
    left = ttk.Frame(frame); left.pack(side='left', fill='both', expand=True, padx=6)
    mid = ttk.Frame(frame); mid.pack(side='left', fill='both', expand=True, padx=6)
    right = ttk.Frame(frame); right.pack(side='left', fill='both', expand=True, padx=6)
    ttk.Label(left, text="Laporan Laba Rugi", style='Header.TLabel').pack(anchor='nw')
    cols = ("Tipe","No Akun","Nama Akun","Jumlah")
    self.tree_income = ttk.Treeview(left, columns=cols, show='headings', height=12)
    for c in cols:
        self.tree_income.heading(c, text=c); self.tree_income.column(c, width=120 if c!="Nama Akun" else 220)
    self.tree_income.pack(fill='both', expand=True, pady=6)
    ttk.Label(mid, text="Perubahan Ekuitas (Rekonsiliasi)", style='Header.TLabel').pack(anchor='nw')
    cols2 = ("Keterangan","Jumlah")
    self.tree_equity = ttk.Treeview(mid, columns=cols2, show='headings', height=8)
    for c in cols2:
        self.tree_equity.heading(c, text=c); self.tree_equity.column(c, width=220)
    self.tree_equity.pack(fill='both', expand=True, pady=6)
    ttk.Label(right, text="Neraca (Balance Sheet)", style='Header.TLabel').pack(anchor='nw')
    cols3 = ("Sisi","No Akun","Nama Akun","Jumlah")
    self.tree_balance = ttk.Treeview(right, columns=cols3, show='headings', height=20)
    for c in cols3:
        self.tree_balance.heading(c, text=c); self.tree_balance.column(c, width=100 if c!="Nama Akun" else 200)
    self.tree_balance.pack(fill='both', expand=True, pady=6)

    shboard
    build_dashboard_tab(self):
    top = ttk.Frame(self.tab_dashboard); top.pack(fill='x', pady=6)
    ttk.Label(top, text="Dashboard", style='Header.TLabel').pack(side='left', padx=8)
    ttk.Button(top, text="Refresh", command=self.debounce_refresh).pack(side='right', padx=8)
    cards_frame = ttk.Frame(self.tab_dashboard); cards_frame.pack(fill='both', expand=True, padx=16, pady=12)
    self.card1 = tk.Frame(cards_frame, bg=CARD_BG, bd=1, relief='flat'); self.card1.pack(side='left', fill='both', expand=True, padx=8, pady=8)
    tk.Label(self.card1, text="Aset vs Kewajiban", bg=CARD_BG, fg=COLOR_PRIMARY, font=("Segoe UI", 12, "bold")).pack(anchor='nw', padx=12, pady=8)
    self.canvas1 = None
    self.card2 = tk.Frame(cards_frame, bg=CARD_BG, bd=1, relief='flat'); self.card2.pack(side='left', fill='both', expand=True, padx=8, pady=8)
    tk.Label(self.card2, text="Likuiditas (Current Ratio)", bg=CARD_BG, fg=COLOR_PRIMARY, font=("Segoe UI", 12, "bold")).pack(anchor='nw', padx=12, pady=8)
    self.canvas2 = None
    self.card3 = tk.Frame(cards_frame, bg=CARD_BG, bd=1, relief='flat'); self.card3.pack(side='left', fill='both', expand=True, padx=8, pady=8)
    tk.Label(self.card3, text="Solvabilitas (Debt-to-Equity)", bg=CARD_BG, fg=COLOR_PRIMARY, font=("Segoe UI", 12, "bold")).pack(anchor='nw', padx=12, pady=8)
    self.canvas3 = None
    if plt and FigureCanvasTkAgg:
        self.fig1 = plt.Figure(figsize=(4,2)); self.ax1 = self.fig1.add_subplot(111)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.card1); self.canvas1.get_tk_widget().pack(fill='both', expand=True, padx=8, pady=6)
        self.fig2 = plt.Figure(figsize=(4,2)); self.ax2 = self.fig2.add_subplot(111)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.card2); self.canvas2.get_tk_widget().pack(fill='both', expand=True, padx=8, pady=6)
        self.fig3 = plt.Figure(figsize=(4,2)); self.ax3 = self.fig3.add_subplot(111)
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=self.card3); self.canvas3.get_tk_widget().pack(fill='both', expand=True, padx=8, pady=6)
    else:
        tk.Label(self.card1, text="matplotlib tidak tersedia", bg=CARD_BG).pack()
        tk.Label(self.card2, text="matplotlib tidak tersedia", bg=CARD_BG).pack()
        tk.Label(self.card3, text="matplotlib tidak tersedia", bg=CARD_BG).pack()

    bounced refresh to avoid UI lag
    debounce_refresh(self, delay=0.15):
    if self._debounce_timer:
        self.after_cancel(self._debounce_timer)
    self._debounce_timer = self.after(int(delay*1000), self.refresh_all)

    fresh all (safe)
    refresh_all(self):
    with self._refresh_lock:
        try:
            # accounts
            for r in self.tree_accounts.get_children(): self.tree_accounts.delete(r)
            for no,nm,tipe,sb in list_accounts(): self.tree_accounts.insert("", "end", values=(no,nm,tipe, f"{to_decimal(sb):,.2f}"))
            # journal
            for r in self.tree_journal.get_children(): self.tree_journal.delete(r)
            for id_,tgl,ad,ak,d,k,ket in list_journal_entries(): self.tree_journal.insert("", "end", values=(id_, tgl, ad, ak, f"{d:,.2f}", f"{k:,.2f}", ket))
            # adjusting
            if hasattr(self, 'tree_adjust'):
                for r in self.tree_adjust.get_children(): self.tree_adjust.delete(r)
                for id_,tgl,ad,ak,d,k,ket,ap in list_adjusting_entries(include_applied=True):
                    self.tree_adjust.insert("", "end", values=(id_, tgl, ad, ak, f"{d:,.2f}", f"{k:,.2f}", ket, ap))
            # trial (before)
            for r in self.tree_trial.get_children(): self.tree_trial.delete(r)
            for no,nm,tipe,d,c in compute_trial_rows(): self.tree_trial.insert("", "end", values=(no,nm,tipe, f"{d:,.2f}", f"{c:,.2f}"))
            # trial adjusted (virtual)
            for r in self.tree_trial_adj.get_children(): self.tree_trial_adj.delete(r)
            for no,nm,tipe,d,c in compute_trial_rows(include_adjustments=True): self.tree_trial_adj.insert("", "end", values=(no,nm,tipe, f"{d:,.2f}", f"{c:,.2f}"))
            # ledger combo
            if hasattr(self, 'combo_ledger_accounts'):
                self.combo_ledger_accounts['values'] = [f"{a[0]} - {a[1]}" for a in list_accounts()]
            # reports
            self.refresh_reports()
            # dashboard
            self.draw_dashboard()
        except Exception as e:
            # UI should not crash
            print("Error during refresh_all:", e)

    refresh_reports(self):
    try:
        inc, bal, eqrec = compute_financial_statements(include_adjustments=True)
        # income
        for r in self.tree_income.get_children(): self.tree_income.delete(r)
        for no,nm,amt in inc['revenues']: self.tree_income.insert("", "end", values=("Pendapatan", no, nm, f"{amt:,.2f}"))
        self.tree_income.insert("", "end", values=("","", "Total Pendapatan", f"{inc['total_revenue']:,.2f}"))
        for no,nm,amt in inc['expenses']: self.tree_income.insert("", "end", values=("Beban", no, nm, f"{amt:,.2f}"))
        self.tree_income.insert("", "end", values=("","", "Total Beban", f"{inc['total_expense']:,.2f}"))
        self.tree_income.insert("", "end", values=("","", "Laba (Rugi) Bersih", f"{inc['net_income']:,.2f}"))
        # equity
        for r in self.tree_equity.get_children(): self.tree_equity.delete(r)
        for label, amt in eqrec: self.tree_equity.insert("", "end", values=(label, f"{amt:,.2f}"))
        # balance
        for r in self.tree_balance.get_children(): self.tree_balance.delete(r)
        for no,nm,amt in bal['assets']: self.tree_balance.insert("", "end", values=("Aset", no, nm, f"{amt:,.2f}"))
        self.tree_balance.insert("", "end", values=("", "", "Total Aset", f"{bal['total_assets']:,.2f}"))
        for no,nm,amt in bal['liabilities']: self.tree_balance.insert("", "end", values=("Kewajiban", no, nm, f"{amt:,.2f}"))
        for no,nm,amt in bal['equity']: self.tree_balance.insert("", "end", values=("Ekuitas", no, nm, f"{amt:,.2f}"))
        self.tree_balance.insert("", "end", values=("", "", "Total Kewajiban + Ekuitas", f"{(bal['total_liabilities'] + bal['total_equity']):,.2f}"))
    except Exception as e:
        print("Error refresh_reports:", e)

    draw_dashboard(self):
    try:
        stats = prepare_balance_and_ratios(include_adjustments=False)
        aset = float(stats['assets']); liab = float(stats['liabilities'])
        if self.canvas1:
            self.ax1.clear(); self.ax1.bar(['Aset','Kewajiban'], [aset, liab], color=[COLOR_PRIMARY, COLOR_ACCENT]); self.canvas1.draw()
        if self.canvas2:
            self.ax2.clear(); cr = stats['current_ratio']
            if cr is None: self.ax2.text(0.5,0.5,"N/A", ha='center', va='center', fontsize=14)
            else:
                val = float(cr); self.ax2.barh(['CR'], [val]); self.ax2.set_xlim(0, max(1.5, val*1.2))
            self.canvas2.draw()
        if self.canvas3:
            self.ax3.clear(); dte = stats['debt_to_equity']
            if dte is None: self.ax3.text(0.5,0.5,"N/A", ha='center', va='center', fontsize=14)
            else:
                val = float(dte); self.ax3.barh(['D/E'], [val]); self.ax3.set_xlim(0, max(1.5, val*1.2))
            self.canvas3.draw()
    except Exception as e:
        print("Error draw_dashboard:", e)

    port wrappers
    export_trial_excel(self, include_adjustments=False):
    path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
    if not path: return
    try:
        export_trial_to_excel(path, include_adjustments); messagebox.showinfo("Sukses","Neraca disimpan.")
    except Exception as e: messagebox.showerror("Error", str(e))

    export_journal_excel(self):
    path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
    if not path: return
    try:
        export_journal_to_excel(path); messagebox.showinfo("Sukses","Jurnal disimpan.")
    except Exception as e: messagebox.showerror("Error", str(e))

    export_adjust_excel(self):
    path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
    if not path: return
    try:
        export_adjusting_to_excel(path); messagebox.showinfo("Sukses","Penyesuaian disimpan.")
    except Exception as e: messagebox.showerror("Error", str(e))

    export_reports_pdf(self):
    path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")])
    if not path: return
    try:
        export_reports_to_pdf(path, include_adjustments=True); messagebox.showinfo("Sukses","Laporan PDF disimpan.")
    except Exception as e: messagebox.showerror("Error", str(e))

    export_reports_excel(self):
    path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
    if not path: return
    try:
        export_reports_to_excel(path, include_adjustments=True); messagebox.showinfo("Sukses","Laporan Excel disimpan.")
    except Exception as e: messagebox.showerror("Error", str(e))

    just UI actions
    ui_add_adjust(self):
    accs = list_accounts()
    if not accs:
        messagebox.showinfo("Info","Belum ada akun. Tambahkan akun dulu di tab Akun."); return
    d = AdjustDialog(self, accs); self.wait_window(d)
    if d.result:
        tanggal, debit_acc, credit_acc, debit_val, credit_val, ket = d.result
        try:
            add_adjusting_db(tanggal, debit_acc, credit_acc, debit_val, credit_val, ket)
            messagebox.showinfo("Sukses","Penyesuaian disimpan"); self.debounce_refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ui_delete_adjust(self):
    sel = self.tree_adjust.selection()
    if not sel: messagebox.showinfo("Info","Pilih penyesuaian untuk dihapus"); return
    ids = [self.tree_adjust.item(s)['values'][0] for s in sel]
    for _id in ids:
        delete_adjusting_db(_id)
    messagebox.showinfo("Sukses", f"{len(ids)} penyesuaian dihapus"); self.debounce_refresh()

    ui_apply_adjustments(self):
    # run apply in background to keep UI responsive
    def worker():
        try:
            applied = apply_adjustments()
            self.debounce_refresh()
            messagebox.showinfo("Selesai", f"{applied} penyesuaian diterapkan ke jurnal (tanggal hari ini).")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    threading.Thread(target=worker, daemon=True).start()

    tomation: run_cycle
    run_cycle(self):
    if messagebox.askyesno("Jalankan Siklus", "Jalankan siklus: terapkan semua penyesuaian ke jurnal dan refresh laporan?"):
        self.ui_apply_adjustments()

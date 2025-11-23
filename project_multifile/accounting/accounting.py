# ---------------- Akun & Jurnal CRUD ----------------
def list_accounts():
    # returns list of tuples (no_akun, nama_akun, tipe, starting_balance)
    rows = db.fetchall("SELECT no_akun, nama_akun, tipe, IFNULL(starting_balance,0) FROM akun ORDER BY no_akun")
    return rows

def add_account_db(no, nama, tipe, starting_balance=0):
    db.execute("INSERT INTO akun (no_akun, nama_akun, tipe, starting_balance) VALUES (?, ?, ?, ?)",
               (no, nama, tipe, float(starting_balance)), commit=True)

def edit_account_db(no, nama, tipe, starting_balance=0):
    db.execute("UPDATE akun SET nama_akun=?, tipe=?, starting_balance=? WHERE no_akun=?",
               (nama, tipe, float(starting_balance), no), commit=True)

def delete_account_db(no):
    cnt = db.fetchone("SELECT COUNT(*) FROM jurnal WHERE akun_debit=? OR akun_kredit=?", (no, no))[0]
    if cnt > 0:
        raise ValueError("Tidak dapat menghapus akun yang memiliki transaksi.")
    db.execute("DELETE FROM akun WHERE no_akun=?", (no,), commit=True)

def add_journal_db(tanggal, akun_debit, akun_kredit, debit, kredit, keterangan):
    if float(debit) < 0 or float(kredit) < 0:
        raise ValueError("Debit/Kredit tidak boleh negatif.")
    if float(debit) == 0 and float(kredit) == 0:
        raise ValueError("Isi debit atau kredit minimal satu.")
    # ensure accounts exist
    cnt = db.fetchone("SELECT COUNT(*) FROM akun WHERE no_akun=?", (akun_debit,))[0]
    if cnt == 0:
        raise ValueError(f"Akun debit {akun_debit} tidak ditemukan")
    cnt = db.fetchone("SELECT COUNT(*) FROM akun WHERE no_akun=?", (akun_kredit,))[0]
    if cnt == 0:
        raise ValueError(f"Akun kredit {akun_kredit} tidak ditemukan")
    db.execute("""INSERT INTO jurnal (tanggal, akun_debit, akun_kredit, debit, kredit, keterangan)
                  VALUES (?, ?, ?, ?, ?, ?)""", (tanggal, akun_debit, akun_kredit, float(debit), float(kredit), keterangan), commit=True)

def list_journal_entries():
    return db.fetchall("SELECT id, tanggal, akun_debit, akun_kredit, debit, kredit, keterangan FROM jurnal ORDER BY tanggal, id")

def delete_journal_db(_id):
    db.execute("DELETE FROM jurnal WHERE id=?", (_id,), commit=True)

# Adjusting CRUD
def add_adjusting_db(tanggal, akun_debit, akun_kredit, debit, kredit, keterangan):
    db.execute("""INSERT INTO adjusting (tanggal, akun_debit, akun_kredit, debit, kredit, keterangan, applied)
                  VALUES (?, ?, ?, ?, ?, ?, 0)""", (tanggal, akun_debit, akun_kredit, float(debit), float(kredit), keterangan), commit=True)

def list_adjusting_entries(include_applied=False):
    if include_applied:
        return db.fetchall("SELECT id, tanggal, akun_debit, akun_kredit, debit, kredit, keterangan, applied FROM adjusting ORDER BY tanggal, id")
    else:
        return db.fetchall("SELECT id, tanggal, akun_debit, akun_kredit, debit, kredit, keterangan, applied FROM adjusting WHERE applied=0 ORDER BY tanggal, id")

def delete_adjusting_db(_id):
    db.execute("DELETE FROM adjusting WHERE id=?", (_id,), commit=True)

def apply_adjustments():
    """
    Apply adjusting entries that are not yet applied, copy them into jurnal with today's date,
    and mark them as applied. Use transaction (single connection) for atomicity.
    """
    backoff = DB_RETRY_BACKOFF
    for attempt in range(1, DB_MAX_RETRIES + 1):
        try:
            conn = db.connect()
            cur = conn.cursor()
            cur.execute("BEGIN")
            cur.execute("SELECT id, tanggal, akun_debit, akun_kredit, debit, kredit, keterangan FROM adjusting WHERE applied=0")
            rows = cur.fetchall()
            if not rows:
                cur.execute("COMMIT")
                conn.close()
                return 0
            today = datetime.now().strftime("%Y-%m-%d")
            applied = 0
            for _id, tanggal, ad, ak, d, k, ket in rows:
                note = f"{ket} (Penyesuaian from {tanggal})" if ket else f"Penyesuaian from {tanggal}"
                cur.execute("""INSERT INTO jurnal (tanggal, akun_debit, akun_kredit, debit, kredit, keterangan)
                               VALUES (?, ?, ?, ?, ?, ?)""", (today, ad, ak, float(d), float(k), note))
                cur.execute("UPDATE adjusting SET applied=1 WHERE id=?", (_id,))
                applied += 1
            cur.execute("COMMIT")
            conn.close()
            return applied
        except sqlite3.OperationalError as e:
            try:
                conn.rollback()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass
            if "locked" in str(e).lower() and attempt < DB_MAX_RETRIES:
                time.sleep(backoff)
                backoff *= 1.8
                continue
            raise
    return 0

# ---------------- Accounting computations ----------------
def compute_balances(include_adjustments=False):
    """
    include_adjustments: if True, include adjusting entries amounts (without applying).
    starting_balance from akun is taken into account:
      - for Asset/Expense: starting_balance treated as initial debit
      - for Liability/Equity/Revenue: starting_balance treated as initial credit
    """
    accs = {}
    # load accounts + starting balance
    for no, nama, tipe, sb in list_accounts():
        sb_dec = to_decimal(sb)
        debit = to_decimal('0'); kredit = to_decimal('0')
        t = (tipe or "").lower()
        if t in ('asset', 'aset', 'expense', 'beban', 'cost'):
            debit += sb_dec
        else:
            kredit += sb_dec
        accs[no] = {'nama': nama, 'tipe': tipe, 'debit': debit, 'kredit': kredit}
    # base jurnal
    for _id, tanggal, ad, ak, d, k, ket in list_journal_entries():
        d = to_decimal(d); k = to_decimal(k)
        if ad not in accs:
            accs[ad] = {'nama': ad, 'tipe': 'Unknown', 'debit': to_decimal('0'), 'kredit': to_decimal('0')}
        if ak not in accs:
            accs[ak] = {'nama': ak, 'tipe': 'Unknown', 'debit': to_decimal('0'), 'kredit': to_decimal('0')}
        accs[ad]['debit'] += d
        accs[ak]['kredit'] += k
    if include_adjustments:
        adj_rows = db.fetchall("SELECT id, tanggal, akun_debit, akun_kredit, debit, kredit, keterangan FROM adjusting")
        for _id, tanggal, ad, ak, d, k, ket in adj_rows:
            d = to_decimal(d); k = to_decimal(k)
            if ad not in accs:
                accs[ad] = {'nama': ad, 'tipe': 'Unknown', 'debit': to_decimal('0'), 'kredit': to_decimal('0')}
            if ak not in accs:
                accs[ak] = {'nama': ak, 'tipe': 'Unknown', 'debit': to_decimal('0'), 'kredit': to_decimal('0')}
            accs[ad]['debit'] += d
            accs[ak]['kredit'] += k
    return accs

def compute_trial_rows(include_adjustments=False):
    bal = compute_balances(include_adjustments=include_adjustments)
    rows = []
    for no in sorted(bal.keys()):
        d = bal[no]['debit']; c = bal[no]['kredit']
        if d >= c:
            debit_bal = d - c; credit_bal = to_decimal('0')
        else:
            debit_bal = to_decimal('0'); credit_bal = c - d
        rows.append((no, bal[no]['nama'], bal[no]['tipe'], debit_bal, credit_bal))
    return rows

def prepare_balance_and_ratios(include_adjustments=False):
    rows = compute_trial_rows(include_adjustments=include_adjustments)
    assets = to_decimal('0'); liabilities = to_decimal('0'); equity = to_decimal('0')
    for no, nm, tipe, d, c in rows:
        bal = d - c
        t = (tipe or "").lower()
        if t in ('asset', 'aset'):
            assets += max(bal, to_decimal('0'))
        elif t in ('liability', 'kewajiban', 'liab'):
            liabilities += max(-bal, to_decimal('0'))
        elif t in ('equity', 'ekuitas'):
            equity += max(-bal, to_decimal('0'))
    current_ratio = None; debt_to_equity = None
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

# ---------------- Financial statements ----------------
def compute_financial_statements(include_adjustments=False):
    balances = compute_balances(include_adjustments=include_adjustments)
    revenues = []; expenses = []
    for no, info in balances.items():
        t = (info['tipe'] or "").lower()
        d = info['debit']; c = info['kredit']
        bal = d - c
        if t in ('revenue','pendapatan','income'):
            rev_amt = max(to_decimal('0'), -bal)
            if rev_amt != 0: revenues.append((no, info['nama'], rev_amt))
        elif t in ('expense','beban','cost'):
            exp_amt = max(to_decimal('0'), bal)
            if exp_amt != 0: expenses.append((no, info['nama'], exp_amt))
    total_revenue = sum((r[2] for r in revenues), to_decimal('0'))
    total_expense = sum((e[2] for e in expenses), to_decimal('0'))
    net_income = total_revenue - total_expense

    assets = []; liabilities = []; equity_lst = []
    for no, info in balances.items():
        t = (info['tipe'] or "").lower()
        d = info['debit']; c = info['kredit']
        bal = d - c
        if t in ('asset','aset'):
            amt = max(bal, to_decimal('0'))
            if amt != 0: assets.append((no, info['nama'], amt))
        elif t in ('liability','kewajiban','liab'):
            amt = max(-bal, to_decimal('0'))
            if amt != 0: liabilities.append((no, info['nama'], amt))
        elif t in ('equity','ekuitas'):
            amt = max(-bal, to_decimal('0'))
            if amt != 0: equity_lst.append((no, info['nama'], amt))

    total_equity_end = sum((e[2] for e in equity_lst), to_decimal('0'))
    total_equity_begin = total_equity_end - net_income
    equity_reconciliation = [
        ("Beginning Equity (approx)", total_equity_begin),
        ("Net Income (Laba/Rugi)", net_income),
        ("Ending Equity", total_equity_end)
    ]
    income_statement = {'revenues': revenues, 'expenses': expenses, 'total_revenue': total_revenue, 'total_expense': total_expense, 'net_income': net_income}
    balance_sheet = {'assets': assets, 'liabilities': liabilities, 'equity': equity_lst, 'total_assets': sum((a[2] for a in assets), to_decimal('0')), 'total_liabilities': sum((l[2] for l in liabilities), to_decimal('0')), 'total_equity': total_equity_end}
    return income_statement, balance_sheet, equity_reconciliation


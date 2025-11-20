from decimal import Decimal, getcontext
from .db_accounts import list_accounts
from .db_jurnal import list_journal_entries
from .db_adjust import list_adjusting_entries

getcontext().prec = 28


# ---------------- Utility ----------------
def to_decimal(x):
    try:
        return Decimal(str(x))
    except Exception:
        return Decimal('0')


# ---------------- Compute Balances ----------------
def compute_balances(include_adjustments=False):
    """
    Menghasilkan saldo setiap akun dari jurnal dan penyesuaian (opsional).
    Return: dict {no_akun: {nama, tipe, debit, kredit}}
    """
    accs = {}

    # Inisialisasi semua akun
    for no, nama, tipe in list_accounts():
        accs[no] = {
            'nama': nama,
            'tipe': tipe,
            'debit': to_decimal('0'),
            'kredit': to_decimal('0'),
        }

    # Masukkan jurnal umum
    for row in list_journal_entries():
        _id, tanggal, ad, ak, d, k, ket = row
        d = to_decimal(d)
        k = to_decimal(k)

        if ad not in accs:
            accs[ad] = {'nama': ad, 'tipe': 'Unknown', 'debit': to_decimal('0'), 'kredit': to_decimal('0')}
        if ak not in accs:
            accs[ak] = {'nama': ak, 'tipe': 'Unknown', 'debit': to_decimal('0'), 'kredit': to_decimal('0')}

        accs[ad]['debit'] += d
        accs[ak]['kredit'] += k

    # Tambahkan adjusting entry (jika diminta)
    if include_adjustments:
        for row in list_adjusting_entries():
            _id, tanggal, ad, ak, d, k, ket = row
            d = to_decimal(d)
            k = to_decimal(k)

            if ad not in accs:
                accs[ad] = {'nama': ad, 'tipe': 'Unknown', 'debit': to_decimal('0'), 'kredit': to_decimal('0')}
            if ak not in accs:
                accs[ak] = {'nama': ak, 'tipe': 'Unknown', 'debit': to_decimal('0'), 'kredit': to_decimal('0')}

            accs[ad]['debit'] += d
            accs[ak]['kredit'] += k

    return accs


# ---------------- Trial Balance ----------------
def compute_trial_rows(include_adjustments=False):
    bal = compute_balances(include_adjustments=include_adjustments)
    rows = []

    for no in sorted(bal.keys()):
        d = bal[no]['debit']
        c = bal[no]['kredit']

        if d >= c:
            debit_bal = d - c
            credit_bal = to_decimal('0')
        else:
            debit_bal = to_decimal('0')
            credit_bal = c - d

        rows.append((no, bal[no]['nama'], bal[no]['tipe'], debit_bal, credit_bal))

    return rows


# ---------------- Dashboard Stats ----------------
def prepare_balance_and_ratios(include_adjustments=False):
    rows = compute_trial_rows(include_adjustments=include_adjustments)

    assets = to_decimal('0')
    liabilities = to_decimal('0')
    equity = to_decimal('0')

    for no, nm, tipe, d, c in rows:
        bal = d - c
        t = (tipe or "").lower()

        if t in ('asset', 'aset'):
            assets += max(bal, to_decimal('0'))

        elif t in ('liability', 'kewajiban', 'liab'):
            liabilities += max(-bal, to_decimal('0'))

        elif t in ('equity', 'ekuitas'):
            equity += max(-bal, to_decimal('0'))

    # Rasio keuangan
    try:
        current_ratio = assets / liabilities if liabilities != 0 else None
    except Exception:
        current_ratio = None

    try:
        debt_to_equity = liabilities / equity if equity != 0 else None
    except Exception:
        debt_to_equity = None

    return {
        'assets': assets,
        'liabilities': liabilities,
        'equity': equity,
        'current_ratio': current_ratio,
        'debt_to_equity': debt_to_equity
    }


# ---------------- Financial Statements ----------------
def compute_financial_statements(include_adjustments=False):
    balances = compute_balances(include_adjustments=include_adjustments)

    revenues = []
    expenses = []

    # Kelompokkan pendapatan & beban
    for no, info in balances.items():
        t = (info['tipe'] or "").lower()
        d = info['debit']
        c = info['kredit']
        bal = d - c

        if t in ('revenue', 'pendapatan', 'income'):
            amt = max(to_decimal('0'), -bal)
            if amt != 0:
                revenues.append((no, info['nama'], amt))

        elif t in ('expense', 'beban', 'cost'):
            amt = max(to_decimal('0'), bal)
            if amt != 0:
                expenses.append((no, info['nama'], amt))

    total_revenue = sum((x[2] for x in revenues), to_decimal('0'))
    total_expense = sum((x[2] for x in expenses), to_decimal('0'))
    net_income = total_revenue - total_expense

    # ---------------- Neraca ----------------
    assets = []
    liabilities = []
    equity_list = []

    for no, info in balances.items():
        t = (info['tipe'] or "").lower()
        d = info['debit']
        c = info['kredit']
        bal = d - c

        if t in ('asset', 'aset'):
            amt = max(bal, to_decimal('0'))
            if amt != 0:
                assets.append((no, info['nama'], amt))

        elif t in ('liability', 'kewajiban', 'liab'):
            amt = max(-bal, to_decimal('0'))
            if amt != 0:
                liabilities.append((no, info['nama'], amt))

        elif t in ('equity', 'ekuitas'):
            amt = max(-bal, to_decimal('0'))
            if amt != 0:
                equity_list.append((no, info['nama'], amt))

    total_equity_end = sum((e[2] for e in equity_list), to_decimal('0'))
    total_equity_begin = total_equity_end - net_income

    equity_reconciliation = [
        ("Beginning Equity (approx)", total_equity_begin),
        ("Net Income (Laba/Rugi)", net_income),
        ("Ending Equity", total_equity_end),
    ]

    income_statement = {
        'revenues': revenues,
        'expenses': expenses,
        'total_revenue': total_revenue,
        'total_expense': total_expense,
        'net_income': net_income,
    }

    balance_sheet = {
        'assets': assets,
        'liabilities': liabilities,
        'equity': equity_list,
        'total_assets': sum((a[2] for a in assets), to_decimal('0')),
        'total_liabilities': sum((l[2] for l in liabilities), to_decimal('0')),
        'total_equity': total_equity_end,
    }

    return income_statement, balance_sheet, equity_reconciliation

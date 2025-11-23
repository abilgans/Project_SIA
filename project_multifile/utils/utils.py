# ---------------- Utilities ----------------
def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode('utf-8')).hexdigest()

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


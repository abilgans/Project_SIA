from datetime import datetime
from .db_init import get_conn

def list_adjusting_entries():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, tanggal, akun_debit, akun_kredit, debit, kredit, keterangan
        FROM adjusting ORDER BY tanggal, id
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def add_adjusting_db(tanggal, akun_debit, akun_kredit, debit, kredit, keterangan):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO adjusting (tanggal, akun_debit, akun_kredit, debit, kredit, keterangan)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (tanggal, akun_debit, akun_kredit, float(debit), float(kredit), keterangan))

    conn.commit()
    conn.close()


def delete_adjusting_db(_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM adjusting WHERE id=?", (_id,))
    conn.commit()
    conn.close()


def apply_adjustments():
    adj = list_adjusting_entries()
    if not adj:
        return 0

    today = datetime.now().strftime("%Y-%m-%d")
    applied = 0

    conn = get_conn()
    cur = conn.cursor()

    for _id, tanggal, ad, ak, d, k, ket in adj:
        note = f"{ket} (Penyesuaian from {tanggal})"
        cur.execute("""
            INSERT INTO jurnal (tanggal, akun_debit, akun_kredit, debit, kredit, keterangan)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (today, ad, ak, float(d), float(k), note))
        applied += 1

    conn.commit()
    conn.close()
    return applied

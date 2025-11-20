from .db_init import get_conn

def list_journal_entries():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, tanggal, akun_debit, akun_kredit, debit, kredit, keterangan
        FROM jurnal ORDER BY tanggal, id
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def add_journal_db(tanggal, akun_debit, akun_kredit, debit, kredit, keterangan):
    conn = get_conn()
    cur = conn.cursor()

    # cek akun debit
    cur.execute("SELECT COUNT(*) FROM akun WHERE no_akun=?", (akun_debit,))
    if cur.fetchone()[0] == 0:
        conn.close()
        raise ValueError(f"Akun debit {akun_debit} tidak ditemukan")

    # cek akun kredit
    cur.execute("SELECT COUNT(*) FROM akun WHERE no_akun=?", (akun_kredit,))
    if cur.fetchone()[0] == 0:
        conn.close()
        raise ValueError(f"Akun kredit {akun_kredit} tidak ditemukan")

    cur.execute("""
        INSERT INTO jurnal (tanggal, akun_debit, akun_kredit, debit, kredit, keterangan)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (tanggal, akun_debit, akun_kredit, float(debit), float(kredit), keterangan))

    conn.commit()
    conn.close()


def delete_journal_db(_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM jurnal WHERE id=?", (_id,))
    conn.commit()
    conn.close()

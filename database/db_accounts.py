from .db_init import get_conn

def list_accounts():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT no_akun, nama_akun, tipe FROM akun ORDER BY no_akun")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_account_db(no, nama, tipe):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO akun (no_akun, nama_akun, tipe) VALUES (?, ?, ?)", (no, nama, tipe))
    conn.commit()
    conn.close()


def edit_account_db(no, nama, tipe):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE akun SET nama_akun=?, tipe=? WHERE no_akun=?", (nama, tipe, no))
    conn.commit()
    conn.close()


def delete_account_db(no):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM jurnal WHERE akun_debit=? OR akun_kredit=?", (no, no))
    if cur.fetchone()[0] > 0:
        conn.close()
        raise ValueError("Tidak dapat menghapus akun yang memiliki transaksi.")

    cur.execute("DELETE FROM akun WHERE no_akun=?", (no,))
    conn.commit()
    conn.close()

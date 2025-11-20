import sqlite3
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

from .db_init import get_conn
from .db_init import DB_FILENAME   # jika ingin akses path DB
from hashlib import sha256

# Sesuaikan dengan konfigurasi kamu
SMTP_EMAIL = "siangapak@gmail.com"
SMTP_PASSWORD = "pwwc mdza lbtu mvtz"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
OTP_TTL_SECONDS = 600


# ---------------- Utility ----------------
def hash_password(pw: str) -> str:
    return sha256(pw.encode("utf-8")).hexdigest()


# ---------------- USER EXIST ----------------
def user_exists(email: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email=?", (email,))
    r = cur.fetchone()
    conn.close()
    return r is not None


# ---------------- SEND OTP EMAIL ----------------
def send_activation_otp_email(to_email, otp):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        return False, "SMTP belum dikonfigurasi."

    try:
        body = f"Kode OTP aktivasi akun Anda: {otp}"
        msg = MIMEText(body)
        msg["Subject"] = "OTP Aktivasi"
        msg["From"] = SMTP_EMAIL
        msg["To"] = to_email

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, [to_email], msg.as_string())
        server.quit()
        return True, "OTP terkirim."
    except Exception as e:
        return False, str(e)


# ---------------- REGISTER USER ----------------
def register_user_with_otp(email, password):
    if user_exists(email):
        return False, "Email sudah terdaftar."

    ph = hash_password(password)
    otp = f"{random.randint(100000, 999999)}"
    expiry = (datetime.now() + timedelta(seconds=OTP_TTL_SECONDS)).isoformat()

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (email, password_hash, otp, otp_expiry, is_active)
        VALUES (?, ?, ?, ?, 0)
    """, (email, ph, otp, expiry))
    conn.commit()
    conn.close()

    sent, msg = send_activation_otp_email(email, otp)
    if sent:
        return True, "Terdaftar. OTP terkirim ke email."
    else:
        print(f"[DEBUG] OTP untuk {email}: {otp} (expiry {expiry})")
        return True, f"Terdaftar. Gagal kirim email: {msg}. OTP ditampilkan di console."


# ---------------- VERIFY ACTIVATION ----------------
def verify_activation_otp(email, otp_input):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT otp, otp_expiry FROM users WHERE email=?", (email,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return False, "Email tidak ditemukan."

    otp, expiry = row
    expiry_dt = datetime.fromisoformat(expiry)

    if datetime.now() > expiry_dt:
        conn.close()
        return False, "OTP kadaluarsa."

    if otp_input != otp:
        conn.close()
        return False, "OTP salah."

    cur.execute("UPDATE users SET is_active=1 WHERE email=?", (email,))
    conn.commit()
    conn.close()

    return True, "Akun berhasil diaktivasi."


# ---------------- VERIFY LOGIN ----------------
def verify_password_and_active(email, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT password_hash, is_active FROM users WHERE email=?", (email,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return False, "Email tidak ditemukan."

    stored_hash, is_active = row
    if hash_password(password) != stored_hash:
        conn.close()
        return False, "Password salah."

    if not is_active:
        conn.close()
        return False, "Akun belum diaktivasi."

    conn.close()
    return True, "Login berhasil."

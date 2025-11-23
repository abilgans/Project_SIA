# ---------------- User / Auth (activation OTP) ----------------
def user_exists(email):
    r = db.fetchone("SELECT id FROM users WHERE email=?", (email,))
    return r is not None

def register_user_with_otp(email, password):
    if user_exists(email):
        return False, "Email sudah terdaftar."
    ph = hash_password(password)
    otp = f"{random.randint(100000,999999)}"
    expiry = (datetime.now() + timedelta(seconds=OTP_TTL_SECONDS)).isoformat()
    db.execute("INSERT INTO users (email, password_hash, is_active, otp, otp_expiry) VALUES (?, ?, 0, ?, ?)",
               (email, ph, otp, expiry), commit=True)
    sent, msg = send_activation_otp_email(email, otp)
    if sent:
        return True, "Terdaftar. OTP aktivasi terkirim ke email."
    else:
        # for convenience in dev mode
        print(f"[DEBUG] OTP for {email}: {otp} (expiry {expiry})")
        return True, f"Terdaftar. Gagal kirim email ({msg}), OTP ditampilkan di console untuk testing."

def send_activation_otp_email(to_email, otp):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        return False, "SMTP belum dikonfigurasi."
    try:
        body = f"Kode OTP aktivasi akun Anda: {otp}\nBerlaku selama {OTP_TTL_SECONDS//60} menit."
        msg = MIMEText(body)
        msg['Subject'] = "OTP Aktivasi Akun - Project SIA"
        msg['From'] = SMTP_EMAIL
        msg['To'] = to_email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, [to_email], msg.as_string())
        server.quit()
        return True, "Terkirim"
    except Exception as e:
        return False, str(e)

def verify_activation_otp(email, otp_input):
    row = db.fetchone("SELECT otp, otp_expiry FROM users WHERE email=?", (email,))
    if not row:
        return False, "Email tidak ditemukan."
    otp, expiry = row
    if not otp:
        return False, "Tidak ada OTP tersimpan."
    try:
        exp_dt = datetime.fromisoformat(expiry)
    except Exception:
        exp_dt = datetime.now() - timedelta(seconds=1)
    if datetime.now() > exp_dt:
        return False, "OTP sudah kadaluarsa."
    if str(otp_input).strip() != str(otp).strip():
        return False, "OTP salah."
    db.execute("UPDATE users SET is_active=1, otp=NULL, otp_expiry=NULL WHERE email=?", (email,), commit=True)
    return True, "Akun berhasil diaktifkan."

def verify_password_and_active(email, password):
    row = db.fetchone("SELECT password_hash, is_active FROM users WHERE email=?", (email,))
    if not row:
        return False, "Email tidak terdaftar."
    phash, is_active = row
    if phash != hash_password(password):
        return False, "Password salah."
    if is_active != 1:
        return False, "Akun belum aktif. Silakan cek email untuk OTP aktivasi."
    return True, "Login berhasil."


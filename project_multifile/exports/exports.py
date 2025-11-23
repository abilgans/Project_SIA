# ---------------- Export helpers ----------------
def export_trial_to_excel(path, include_adjustments=False):
    if Workbook is None:
        raise RuntimeError("openpyxl tidak terpasang")
    rows = compute_trial_rows(include_adjustments)
    wb = Workbook(); ws = wb.active; ws.title = "Neraca Saldo"
    ws.append(["No Akun","Nama","Tipe","Debit","Kredit"])
    for r in rows:
        ws.append([r[0], r[1], r[2], float(r[3]), float(r[4])])
    wb.save(path)

def export_journal_to_excel(path):
    if Workbook is None:
        raise RuntimeError("openpyxl tidak terpasang")
    rows = list_journal_entries()
    wb = Workbook(); ws = wb.active; ws.title = "Jurnal"
    ws.append(["ID","Tanggal","Akun Debit","Akun Kredit","Debit","Kredit","Keterangan"])
    for r in rows:
        ws.append([r[0], r[1], r[2], r[3], float(r[4]), float(r[5]), r[6]])
    wb.save(path)

def export_adjusting_to_excel(path):
    if Workbook is None:
        raise RuntimeError("openpyxl tidak terpasang")
    rows = db.fetchall("SELECT id, tanggal, akun_debit, akun_kredit, debit, kredit, keterangan, applied FROM adjusting ORDER BY tanggal, id")
    wb = Workbook(); ws = wb.active; ws.title = "Penyesuaian"
    ws.append(["ID","Tanggal","Akun Debit","Akun Kredit","Debit","Kredit","Keterangan","Applied"])
    for r in rows:
        ws.append([r[0], r[1], r[2], r[3], float(r[4]), float(r[5]), r[6], r[7]])
    wb.save(path)

def export_reports_to_pdf(path, include_adjustments=True):
    if SimpleDocTemplate is None:
        raise RuntimeError("reportlab tidak terpasang")
    income, balance, eq_rec = compute_financial_statements(include_adjustments=include_adjustments)
    doc = SimpleDocTemplate(path, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("Laporan Keuangan", styles['Title'])); story.append(Spacer(1,12))
    # Laporan Laba Rugi
    story.append(Paragraph("Laporan Laba Rugi", styles['Heading2']))
    data = [["Jenis", "No Akun", "Nama Akun", "Jumlah"]]
    for no,nm,amt in income['revenues']:
        data.append(["Pendapatan", no, nm, f"{float(amt):,.2f}"])
    data.append(["", "", "Total Pendapatan", f"{float(income['total_revenue']):,.2f}"])
    for no,nm,amt in income['expenses']:
        data.append(["Beban", no, nm, f"{float(amt):,.2f}"])
    data.append(["", "", "Total Beban", f"{float(income['total_expense']):,.2f}"])
    data.append(["", "", "Laba (Rugi) Bersih", f"{float(income['net_income']):,.2f}"])
    t = Table(data, colWidths=[80,80,220,100])
    t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.grey), ('BACKGROUND',(0,0),(-1,0),colors.lightblue), ('ALIGN',(-1,0),(-1,-1),'RIGHT')]))
    story.append(t); story.append(Spacer(1,12))
    # Equity reconciliation
    story.append(Paragraph("Perubahan Ekuitas (Rekonsiliasi sederhana)", styles['Heading2']))
    data = [["Keterangan", "Jumlah"]]
    for label, amt in eq_rec:
        data.append([label, f"{float(amt):,.2f}"])
    t2 = Table(data, colWidths=[400,120])
    t2.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.grey), ('BACKGROUND',(0,0),(-1,0),colors.lightblue), ('ALIGN',(-1,0),(-1,-1),'RIGHT')]))
    story.append(t2); story.append(Spacer(1,12))
    # Balance sheet
    story.append(Paragraph("Neraca (Balance Sheet)", styles['Heading2']))
    data = [["Sisi", "No Akun", "Nama Akun", "Jumlah"]]
    for no,nm,amt in balance['assets']:
        data.append(["Aset", no, nm, f"{float(amt):,.2f}"])
    data.append(["", "", "Total Aset", f"{float(balance['total_assets']):,.2f}"])
    for no,nm,amt in balance['liabilities']:
        data.append(["Kewajiban", no, nm, f"{float(amt):,.2f}"])
    for no,nm,amt in balance['equity']:
        data.append(["Ekuitas", no, nm, f"{float(amt):,.2f}"])
    data.append(["", "", "Total Kewajiban + Ekuitas", f"{float(balance['total_liabilities'] + balance['total_equity']):,.2f}"])
    t3 = Table(data, colWidths=[80,80,220,100])
    t3.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.grey), ('BACKGROUND',(0,0),(-1,0),colors.lightblue), ('ALIGN',(-1,0),(-1,-1),'RIGHT')]))
    story.append(t3)
    doc.build(story)

def export_reports_to_excel(path, include_adjustments=True):
    if Workbook is None:
        raise RuntimeError("openpyxl tidak terpasang")
    income, balance, eq_rec = compute_financial_statements(include_adjustments=include_adjustments)
    wb = Workbook()
    ws1 = wb.active; ws1.title = "Laba Rugi"
    ws1.append(["Jenis","No Akun","Nama Akun","Jumlah"])
    for no,nm,amt in income['revenues']:
        ws1.append(["Pendapatan", no, nm, float(amt)])
    ws1.append(["","", "Total Pendapatan", float(income['total_revenue'])])
    for no,nm,amt in income['expenses']:
        ws1.append(["Beban", no, nm, float(amt)])
    ws1.append(["","", "Total Beban", float(income['total_expense'])])
    ws1.append(["","", "Laba (Rugi) Bersih", float(income['net_income'])])
    ws2 = wb.create_sheet("Perubahan Ekuitas"); ws2.append(["Keterangan","Jumlah"])
    for label, amt in eq_rec:
        ws2.append([label, float(amt)])
    ws3 = wb.create_sheet("Neraca"); ws3.append(["Sisi","No Akun","Nama Akun","Jumlah"])
    for no,nm,amt in balance['assets']:
        ws3.append(["Aset", no, nm, float(amt)])
    ws3.append(["","", "Total Aset", float(balance['total_assets'])])
    for no,nm,amt in balance['liabilities']:
        ws3.append(["Kewajiban", no, nm, float(amt)])
    for no,nm,amt in balance['equity']:
        ws3.append(["Ekuitas", no, nm, float(amt)])
    ws3.append(["","", "Total Kewajiban + Ekuitas", float(balance['total_liabilities'] + balance['total_equity'])])
    wb.save(path)


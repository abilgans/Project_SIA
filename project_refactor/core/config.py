import os
import sqlite3
import hashlib
import smtplib
import random
import threading
import time
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from decimal import Decimal, getcontext

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

import pandas as pd
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from openpyxl import Workbook

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


DB_FILENAME = "akuntansi.db"
APP_TITLE = "SAM POO KONG xlim go" 

WINDOW_BG = "#FFF0F0"         # Background putih-kemerahan
COLOR_PRIMARY = "#C00000"     # Merah klenteng pekat
COLOR_ACCENT = "#E6A700"      # Emas lebih tua
COLOR_TEXT = "#5A0000"        # Merah gelap untuk teks
CARD_BG = "#FFFFFF"           # Putih netral
FONT = ("Segoe UI", 10)

# SMTP (untuk OTP)
SMTP_EMAIL = ""
SMTP_PASSWORD = ""
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
OTP_TTL_SECONDS = 600

# DB retry
DB_MAX_RETRIES = 5
DB_RETRY_BACKOFF = 0.12

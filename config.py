# config.py

import os

# --- KONFIGURASI BOT TELEGRAM ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "BOT_TOKEN_PLACEHOLDER")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "ADMIN_ID_PLACEHOLDER"))
ADMIN_USERNAME = os.getenv("ADMIN_TELEGRAM_USERNAME", "hokagelegend1")

# --- KONFIGURASI DATABASE ---
DB_FILE = 'bot_database.sqlite'

# --- KONFIGURASI TRIPAY SANDBOX ---
TRIPAY_API_KEY_SANDBOX = "DEV-74qgIcPmK16lbtU6Dzv8qzFfW0EsvQaSf2eV0Cdj"
TRIPAY_PRIVATE_KEY_SANDBOX = "QK2gt-0rRmb-SiN7u-8h4y9-4Bmc7"
TRIPAY_MERCHANT_CODE_SANDBOX = "T38562"
TRIPAY_API_URL_SANDBOX = "https://tripay.co.id/api-sandbox/transaction/create"


# config.py
WEBHOOK_CALLBACK_URL = "http://ujicoba.hokagelegend.web.id:81/tripay-callback"

# --- KONFIGURASI API LAINNYA ---
KMSP_API_KEY = os.getenv("XL_API_KEY", "c7d49152-51a3-4cf4-b696-af8bd60ad2d8")
HESDA_API_KEY = os.getenv("HESDA_API_KEY", "2iB0Qvvqaw85lCOvCy")
HESDA_USERNAME = os.getenv("HESDA_USERNAME", "ikbal192817@gmail.com")
HESDA_PASSWORD = os.getenv("HESDA_PASSWORD", "ayomasuk123")

# --- PENGATURAN BOT ---
MIN_TOP_UP_AMOUNT = 10000 # Minimal top up untuk Tripay

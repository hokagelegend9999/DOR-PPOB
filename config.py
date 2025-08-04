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

# --- URL WEBHOOK (SESUAIKAN DENGAN DOMAIN ANDA) ---
WEBHOOK_CALLBACK_URL = "http://ujicoba.hokagelegend.web.id:81/tripay-callback"

# --- KONFIGURASI API LAINNYA ---
KMSP_API_KEY = os.getenv("XL_API_KEY", "c7d49152-51a3-4cf4-b696-af8bd60ad2d8")
HESDA_API_KEY = os.getenv("HESDA_API_KEY", "2iB0Qvvqaw85lCOvCy")
HESDA_USERNAME = os.getenv("HESDA_USERNAME", "ikbal192817@gmail.com")
HESDA_PASSWORD = os.getenv("HESDA_PASSWORD", "ayomasuk123")

# --- PENGATURAN BOT ---
MIN_TOP_UP_AMOUNT = 10000 # Minimal top up untuk Tripay
MIN_BALANCE_FOR_PURCHASE = 5000

# --- DEFINISI DAFTAR PAKET ---
CUSTOM_PACKAGE_PRICES = {
    "XL_XC1PLUS1DISC_EWALLET": {"price_bot": 5000, "display_name": "XC 1+1GB DANA"},
    "XLUNLITURBOTIKTOK_DANA": {"price_bot": 200, "display_name": "ADD ON TIKTOK (DANA)"},
    "XLUNLITURBOVIU_DANA": {"price_bot": 200, "display_name": "ADD ON VIU (DANA)"},
    "XLUNLITURBOJOOXXC": {"price_bot": 200, "display_name": "ADD ON JOOX (DANA)"},
    "XLUNLITURBONETFLIXXC": {"price_bot": 200, "display_name": "ADD ON NETFLIX (DANA)"},
    "XLUNLITURBOHPREMIUM7H": {"price_bot": 200, "display_name": "PREMIUM 7H (DANA)"},
    "XLUNLITURBOHSUPER7H": {"price_bot": 200, "display_name": "SUPER 7H (DANA)"},
    "XLUNLITURBOHBASIC7H": {"price_bot": 200, "display_name": "BASIC 7H (DANA)"},
    "XLUNLITURBOHSTANDARD7H": {"price_bot": 200, "display_name": "STANDAR 7H (DANA)"},
    "XLUNLITURBOPREMIUMXC": {"price_bot": 200, "display_name": "ADD ON PREMIUM (DANA)"},
    "XLUNLITURBOSUPERXC": {"price_bot": 200, "display_name": "ADD ON SUPER (DANA)"},
    "XLUNLITURBOBASICXC": {"price_bot": 200, "display_name": "ADD ON BASIC (DANA)"},
    "XLUNLITURBOSTANDARDXC": {"price_bot": 200, "display_name": "ADD ON STANDAR (DANA)"},
    "WjNMaVEyR0NoNG5SdUhHYWFLbU9RUQ": {"price_bot": 200, "display_name": "BYPAS BASIC"},
    "aCtmMVl2YldLZDcvRzhJNlQraTNZdw": {"price_bot": 200, "display_name": "BYPAS STANDARD"},
    "eUxzZE9Wa0dmdTdDT1RDeVFyOWJyZw": {"price_bot": 200, "display_name": "BYPAS SUPER"},
    "UzhmQk5zam53SUZReWJ3c0poZ0xaQQ": {"price_bot": 200, "display_name": "BYPAS PREMIUM"},
    "VlNxbzdGbDRtVnZHUmdwb284R2wzdw": {"price_bot": 200, "display_name": "BYPAS JOOX"},
    "SDNuUmJBbWEvMnZSVFRCcEtzQlBFZw": {"price_bot": 200, "display_name": "BYPAS YOUTUBE"},
    "MnFpMjJHaXhpU2pweUZ2WWRRM0tYZw": {"price_bot": 200, "display_name": "BYPAS NETFLIX"},
    "dlZJSi9kRC85U2tuc3ZaQkVmc1lkQQ": {"price_bot": 200, "display_name": "BYPAS TIKTOK"},
    "Tm8vcWtGQ01Kc3h1dlFFdGZqQ3FzUQ": {"price_bot": 200, "display_name": "BYPAS VIU"},
    "bStlR1JhcUkrZzlhYmdURWRMNUlaQQ": {"price_bot": 200, "display_name": "BYPAS BASIC 7H"},
    "VWM1ZWF0Nk1GQW9MRTEyajJnWFcrdw": {"price_bot": 200, "display_name": "BYPAS STANDARD 7H"},
    "N3IvV0NHUEtNUzV6ZlNYR0l0MTNuUQ": {"price_bot": 200, "display_name": "BYPAS PREMIUM 7H"},
    "c03be70fb3523ac2ac440966d3a5920e": {"price_bot": 5000, "display_name": "XCP 8GB DANA"},
    "bdb392a7aa12b21851960b7e7d54af2c": {"price_bot": 5000, "display_name": "XCP 8GB PULSA"},
    "XL_XC1PLUS1DISC_PULSA": {"price_bot": 5000, "display_name": "XC 1+1GB PULSA"},
    "XL_XC1PLUS1DISC_QRIS": {"price_bot": 5000, "display_name": "XC 1+1GB QRIS"},
    "c03be70fb3523ac2ac440966d3a5920e_QRIS": {"price_bot": 5000, "display_name": "XCP 8GB QRIS"},
    "XLUNLITURBOPREMIUMXC_PULSA": {"price_bot": 200, "display_name": "ADD ON PREMIUM (PULSA)"},
    "XLUNLITURBOSUPERXC_PULSA": {"price_bot": 200, "display_name": "ADD ON SUPER (PULSA)"},
    "XLUNLITURBOBASICXC_PULSA": {"price_bot": 200, "display_name": "ADD ON BASIC (PULSA)"},
    "XLUNLITURBOSTANDARDXC_PULSA": {"price_bot": 200, "display_name": "ADD ON STANDAR (PULSA)"},
    "XLUNLITURBOVIU_PULSA": {"price_bot": 200, "display_name": "ADD ON VIU (PULSA)"},
    "XLUNLITURBOTIKTOK_PULSA": {"price_bot": 200, "display_name": "ADD ON TIKTOK (PULSA)"},
    "XLUNLITURBONETFLIXXC_PULSA": {"price_bot": 200, "display_name": "ADD ON NETFLIX (PULSA)"},
    "XLUNLITURBOYOUTUBEXC_PULSA": {"price_bot": 200, "display_name": "ADD ON YOUTUBE (PULSA)"},
    "XLUNLITURBOJOOXXC_PULSA": {"price_bot": 200, "display_name": "ADD ON JOOX (PULSA)"},
    "XLUNLITURBOHPREMIUM7H_P": {"price_bot": 200, "display_name": "PREMIUM 7H (PULSA)"},
    "XLUNLITURBOHSUPER7H_P": {"price_bot": 200, "display_name": "SUPER 7H (PULSA)"},
    "XLUNLITURBOHBASIC7H_P": {"price_bot": 200, "display_name": "BASIC 7H (PULSA)"},
    "XLUNLITURBOHSTANDARD7H_P": {"price_bot": 200, "display_name": "STANDAR 7H (PULSA)"},
    "XLUNLITURBOVIDIO_PULSA": {"price_bot": 3000, "display_name": "VIDIO XL (PULSA)"},
    "XLUNLITURBOVIDIO_QRIS": {"price_bot": 3000, "display_name": "VIDIO XL (QRIS)"},
    "XLUNLITURBOVIDIO_DANA": {"price_bot": 3000, "display_name": "VIDIO XL (DANA)"},
    "XLUNLITURBOIFLIXXC_DANA": {"price_bot": 3000, "display_name": "IFLIX XL (DANA)"},
    "XLUNLITURBOIFLIXXC_PULSA": {"price_bot": 3000, "display_name": "IFLIX XL (PULSA)"},
    "XLUNLITURBOIFLIXXC_QRIS": {"price_bot": 3000, "display_name": "IFLIX XL (QRIS)"},
}

ADD_ON_SEQUENCE = [
    {"code": "XLUNLITURBOPREMIUMXC_PULSA", "name": "ADD ON PREMIUM"},
    {"code": "XLUNLITURBOSUPERXC_PULSA", "name": "ADD ON SUPER"},
    {"code": "XLUNLITURBOBASICXC_PULSA", "name": "ADD ON BASIC"},
    {"code": "XLUNLITURBOSTANDARDXC_PULSA", "name": "ADD ON STANDAR"},
    {"code": "XLUNLITURBOTIKTOK_PULSA", "name": "ADD ON TIKTOK"},
    {"code": "XLUNLITURBOVIU_PULSA", "name": "ADD ON VIU"},
    {"code": "XLUNLITURBOJOOXXC_PULSA", "name": "ADD ON JOX"},
    {"code": "XLUNLITURBONETFLIXXC_PULSA", "name": "ADD ON NETFLIX"},
    {"code": "XLUNLITURBOYOUTUBEXC_PULSA", "name": "ADD ON YOUTUBE"},
    {"code": "XLUNLITURBOHPREMIUM7H_P", "name": "PREMIUM 7H"},
    {"code": "XLUNLITURBOHSUPER7H_P", "name": "SUPER 7H"},
    {"code": "XLUNLITURBOHBASIC7H_P", "name": "BASIC 7H"},
    {"code": "XLUNLITURBOHSTANDARD7H_P", "name": "STANDAR 7H"},
]

XCP_8GB_PACKAGE = {"code": "c03be70fb3523ac2ac440966d3a5920e", "name": "XCP 8GB"}
XCP_8GB_PULSA_PACKAGE = {"code": "bdb392a7aa12b21851960b7e7d54af2c", "name": "XCP 8GB PULSA"}

HESDA_PACKAGES = [
    {"id": "WjNMaVEyR0NoNG5SdUhHYWFLbU9RUQ", "name": "BASIC", "price_bot": 200},
    {"id": "aCtmMVl2YldLZDcvRzhJNlQraTNZdw", "name": "STANDARD", "price_bot": 200},
    {"id": "eUxzZE9Wa0dmdTdDT1RDeVFyOWJyZw", "name": "SUPER", "price_bot": 200},
    {"id": "UzhmQk5zam53SUZReWJ3c0poZ0xaQQ", "name": "PREMIUM", "price_bot": 200},
    {"id": "VlNxbzdGbDRtVnZHUmdwb284R2wzdw", "name": "JOOX", "price_bot": 200},
    {"id": "SDNuUmJBbWEvMnZSVFRCcEtzQlBFZw", "name": "YOUTUBE", "price_bot": 200},
    {"id": "MnFpMjJHaXhpU2pweUZ2WWRRM0tYZw", "name": "NETFLIX", "price_bot": 200},
    {"id": "dlZJSi9kRC85U2tuc3ZaQkVmc1lkQQ", "name": "TIKTOK", "price_bot": 200},
    {"id": "Tm8vcWtGQ01Kc3h1dlFFdGZqQ3FzUQ", "name": "VIU", "price_bot": 200},
    {"id": "bStlR1JhcUkrZzlhYmdURWRMNUlaQQ", "name": "BASIC 7H", "price_bot": 200},
    {"id": "VWM1ZWF0Nk1GQW9MRTEyajJnWFcrdw", "name": "STANDARD 7H", "price_bot": 200},
    {"id": "N3IvV0NHUEtNUzV6ZlNYR0l0MTNuUQ", "name": "PREMIUM 7H", "price_bot": 200},
]

THIRTY_H_PACKAGES = [
    {"id": "XLUNLITURBOPREMIUMXC_PULSA", "name": "PREMIUM 30H", "price_bot": 200},
    {"id": "XLUNLITURBOSUPERXC_PULSA", "name": "SUPER 30H", "price_bot": 250},
    {"id": "XLUNLITURBOBASICXC_PULSA", "name": "BASIC 30H", "price_bot": 200},
    {"id": "XLUNLITURBOSTANDARDXC_PULSA", "name": "STANDARD 30H", "price_bot": 200},
    {"id": "XLUNLITURBONETFLIXXC_PULSA", "name": "NETFLIX", "price_bot": 200},
    {"id": "XLUNLITURBOTIKTOK_PULSA", "name": "TIKTOK", "price_bot": 200},
    {"id": "XLUNLITURBOJOOXXC_PULSA", "name": "JOOX", "price_bot": 200},
    {"id": "XLUNLITURBOVIU_PULSA", "name": "VIU", "price_bot": 200},
    {"id": "XLUNLITURBOYOUTUBEXC_PULSA", "name": "YOUTUBE", "price_bot": 200},
    {"id": "XLUNLITURBOHPREMIUM7H_P", "name": "PREMIUM 7H", "price_bot": 200},
    {"id": "XLUNLITURBOHSUPER7H_P", "name": "SUPER 7H", "price_bot": 200},
    {"id": "XLUNLITURBOHBASIC7H_P", "name": "BASIC 7H", "price_bot": 200},
    {"id": "XLUNLITURBOHSTANDARD7H_P", "name": "STANDARD 7H", "price_bot": 200},
]

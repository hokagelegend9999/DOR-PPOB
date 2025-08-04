# keyboards.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import ADMIN_USERNAME

def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔮 LOGIN OTP", callback_data='show_login_options'),
         InlineKeyboardButton("🆔 NOMOR SAYA", callback_data="akun_saya")],
        [InlineKeyboardButton("⚡ Tembak Paket", callback_data='tembak_paket')],
        [InlineKeyboardButton("👾 XL VIDIO", callback_data='vidio_xl_menu'),
         InlineKeyboardButton("🍇 XL IFLIX", callback_data='iflix_xl_menu')],
        [InlineKeyboardButton("📶 Cek Kuota", callback_data='cek_kuota'),
         InlineKeyboardButton("💰 Cek Saldo", callback_data='cek_saldo')],
        [InlineKeyboardButton("📚 Tutorial Beli", callback_data='tutorial_beli'),
         InlineKeyboardButton("💸 Top Up Saldo", callback_data='top_up_saldo')],
        [InlineKeyboardButton("📦 Paket Lainnya", callback_data='show_custom_packages')],
        [InlineKeyboardButton("💜 Kontak Admin", url=f"https://t.me/{ADMIN_USERNAME}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_login_options_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔐 LOGIN OTP", callback_data='login_kmsp')],
        [InlineKeyboardButton("🔑 LOGIN OTP BYPASS", callback_data='login_hesda')],
        [InlineKeyboardButton("🏠 Kembali ke Menu Utama", callback_data='back_to_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("➕ Tambah Saldo", callback_data='admin_add_balance'),
         InlineKeyboardButton("➖ Kurangi Saldo", callback_data='admin_deduct_balance')],
        [InlineKeyboardButton("💰 Cek Saldo User", callback_data='admin_check_user_balances')],
        [InlineKeyboardButton("👥 Daftar User", callback_data='admin_list_users')],
        [InlineKeyboardButton("🚫 Blokir", callback_data='admin_block_user_menu'),
         InlineKeyboardButton("✅ Un-Blokir", callback_data='admin_unblock_user_menu')],
        [InlineKeyboardButton("🔍 Cari User", callback_data='admin_search_user_menu'),
         InlineKeyboardButton("🧾 Riwayat User", callback_data='admin_check_user_transactions_menu')],
        [InlineKeyboardButton("📢 Broadcast Pesan", callback_data='admin_broadcast')],
        [InlineKeyboardButton("🏠 Kembali ke Menu User", callback_data='back_to_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

# ... Tambahkan semua fungsi lain yang membuat keyboard di sini ...
# Contoh: get_tembak_paket_keyboard(), get_tutorial_keyboard(), dll.

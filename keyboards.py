# keyboards.py (Versi Final)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import ADMIN_USERNAME
from database import user_data

def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔮 LOGIN OTP", callback_data='show_login_options')],
        [InlineKeyboardButton("🆔 NOMOR SAYA", callback_data="akun_saya")],
        [InlineKeyboardButton("⚡ Tembak Paket", callback_data='tembak_paket')],
        [InlineKeyboardButton("👾 XL VIDIO", callback_data='vidio_xl_menu'),
         InlineKeyboardButton("🍇 XL IFLIX", callback_data='iflix_xl_menu')],
        [InlineKeyboardButton("📶 Cek Kuota", callback_data='cek_kuota'),
         InlineKeyboardButton("💰 Cek Saldo", callback_data='cek_saldo')],
        [InlineKeyboardButton("📚 Tutorial Beli", callback_data='tutorial_beli')],
        [InlineKeyboardButton("💸 Top Up Saldo", callback_data='top_up_saldo')],
        [InlineKeyboardButton("📦 Paket Lainnya", callback_data='show_custom_packages')],
        [InlineKeyboardButton("💜 Kontak Admin", url=f"https://t.me/{ADMIN_USERNAME}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_tutorial_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("❗ Syarat Pembelian", callback_data='syarat_pembelian')],
        [InlineKeyboardButton("📖 Tutorial XCS ADD-ONS", callback_data='tutorial_xcs_addons')],
        [InlineKeyboardButton("📖 Tutorial XUTS", callback_data='tutorial_uts')],
        [InlineKeyboardButton("🏠 Kembali ke Menu Utama", callback_data='back_to_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_custom_packages_keyboard():
    # Placeholder - Anda dapat mengembangkan ini nanti dengan data dari database
    buttons = [
        [InlineKeyboardButton("Belum ada paket lain yang tersedia saat ini.", callback_data="no_op")],
        [InlineKeyboardButton("🏠 Kembali ke Menu Utama", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_login_options_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔐 LOGIN OTP", callback_data='login_kmsp')],
        [InlineKeyboardButton("🔑 LOGIN OTP BYPASS", callback_data='login_hesda')],
        [InlineKeyboardButton("🏠 Kembali ke Menu Utama", callback_data='back_to_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_tembak_paket_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ XUTS", callback_data="menu_uts_nested")],
        [InlineKeyboardButton("🌟 XUTP", callback_data="xutp_menu")],
        [InlineKeyboardButton("⚡ XCS ADD ON", callback_data="xcp_addon")],
        [InlineKeyboardButton("🏠 Kembali ke Menu Utama", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

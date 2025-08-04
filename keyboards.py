# keyboards.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import (ADMIN_USERNAME, HESDA_PACKAGES, THIRTY_H_PACKAGES, 
                    ADD_ON_SEQUENCE, XCP_8GB_PACKAGE, XCP_8GB_PULSA_PACKAGE, 
                    CUSTOM_PACKAGE_PRICES)

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

def get_tembak_paket_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ XUTS", callback_data="menu_uts_nested")],
        [InlineKeyboardButton("🌟 XUTP", callback_data="xutp_menu")],
        [InlineKeyboardButton("⚡ XCS ADD ON", callback_data="xcp_addon")],
        [InlineKeyboardButton("🏠 Kembali ke Menu Utama", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_uts_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("OTOMATIS 🤖", callback_data="automatic_purchase_flow")],
        [InlineKeyboardButton("MANUAL ✍️", callback_data="manual_uts_selection_menu")],
        [InlineKeyboardButton("🔙 Kembali ke Tembak Paket", callback_data="tembak_paket")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_automatic_method_selection_keyboard():
    keyboard = [
        [InlineKeyboardButton("DANA", callback_data="automatic_method_dana")],
        [InlineKeyboardButton("PULSA (Saldo Bot)", callback_data="automatic_method_pulsa")],
        [InlineKeyboardButton("QRIS", callback_data="automatic_method_qris")],
        [InlineKeyboardButton("🔙 Kembali ke Menu XUTS", callback_data="menu_uts_nested")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_manual_uts_selection_keyboard():
    keyboard = [
        [InlineKeyboardButton("XUTS (Wajib Pertama)", callback_data="buy_uts_pulsa_gandengan")],
        [InlineKeyboardButton("XC 1+1GB DANA", callback_data="buy_uts_1gb")],
        [InlineKeyboardButton("XC 1+1GB PULSA", callback_data="buy_uts_1gb_pulsa")],
        [InlineKeyboardButton("XC 1+1GB QRIS", callback_data="buy_uts_1gb_qris")],
        [InlineKeyboardButton("🔙 Kembali ke Pilihan Mode", callback_data="menu_uts_nested")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_xutp_method_selection_keyboard():
    keyboard = [
        [InlineKeyboardButton("DANA", callback_data="xutp_method_dana")],
        [InlineKeyboardButton("PULSA (Saldo Bot)", callback_data="xutp_method_pulsa")],
        [InlineKeyboardButton("QRIS", callback_data="xutp_method_qris")],
        [InlineKeyboardButton("🔙 Kembali ke Menu Tembak Paket", callback_data="tembak_paket")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_xcp_addon_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("OTOMATIS 🤖", callback_data="automatic_xcs_addon_flow")],
        [InlineKeyboardButton("MANUAL ✍️", callback_data="manual_xcs_addon_selection_menu")],
        [InlineKeyboardButton("🔙 Kembali ke Tembak Paket", callback_data="tembak_paket")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_manual_xcs_addon_selection_keyboard():
    keyboard = [
        [InlineKeyboardButton("BYPAS V1 (Pilih Paket)", callback_data="menu_bypass_nested")],
        [InlineKeyboardButton("BYPAS V2 (Pilih Paket)", callback_data="menu_30h_nested")],
        [InlineKeyboardButton("XCP 8GB DANA", callback_data=f"xcp_{XCP_8GB_PACKAGE['code']}")],
        [InlineKeyboardButton("XCP 8GB PULSA", callback_data=f"xcp_{XCP_8GB_PULSA_PACKAGE['code']}")],
        [InlineKeyboardButton("XCP 8GB QRIS", callback_data=f"xcp_{XCP_8GB_PACKAGE['code']}_QRIS")],
        [InlineKeyboardButton("🔙 Kembali ke Pilihan Mode XCS", callback_data="xcp_addon")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_automatic_xcs_addon_method_selection_keyboard():
    keyboard = [
        [InlineKeyboardButton("DANA", callback_data="auto_xcs_method_dana")],
        [InlineKeyboardButton("PULSA (Saldo Bot)", callback_data="auto_xcs_method_pulsa")],
        [InlineKeyboardButton("QRIS", callback_data="auto_xcs_method_qris")],
        [InlineKeyboardButton("🔙 Kembali ke Pilihan Mode XCS", callback_data="xcp_addon")]
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
        [InlineKeyboardButton("🏠 Kembali ke Menu User", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

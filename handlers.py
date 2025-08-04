# handlers.py

import logging
import requests
import json
from datetime import datetime, timezone, timedelta
import hashlib
import time
import os
import re
import asyncio
import math
import html
import base64
import traceback
import uuid
import random
import sqlite3

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

# Import dari file-file lain di proyek Anda
import keyboards
from database import user_data, simpan_data_ke_db
from config import *

logger = logging.getLogger(__name__)

# --- FUNGSI TRIPAY ---
def buat_transaksi_tripay(user_id, amount):
    merchant_ref = f"TOPUP-{user_id}-{int(time.time())}"
    method = 'QRISC'
    signature_string = f"{TRIPAY_MERCHANT_CODE_SANDBOX}{merchant_ref}{amount}{TRIPAY_PRIVATE_KEY_SANDBOX}"
    signature = hashlib.sha256(signature_string.encode()).hexdigest()
    payload = {
        'method': method, 'merchant_ref': merchant_ref, 'amount': amount,
        'customer_name': f'User {user_id}', 'customer_email': f'user{user_id}@example.com',
        'customer_phone': '081234567890',
        'order_items': [{'sku': 'TOPUP', 'name': 'Top Up Saldo Bot', 'price': amount, 'quantity': 1}],
        'callback_url': WEBHOOK_CALLBACK_URL, 'return_url': f'https://t.me/{ADMIN_USERNAME}',
        'signature': signature
    }
    headers = {'Authorization': f'Bearer {TRIPAY_API_KEY_SANDBOX}'}
    try:
        response = requests.post(TRIPAY_API_URL_SANDBOX, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('success'):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO tripay_transactions (merchant_ref, user_id, amount, status) VALUES (?, ?, ?, ?)",
                    (merchant_ref, user_id, amount, 'PENDING')
                )
                conn.commit()
                conn.close()
                return response_data['data']
    except requests.exceptions.RequestException as e:
        logger.error(f"Koneksi ke Tripay gagal: {e}")
        return None
    logger.error(f"Error saat membuat transaksi Tripay: {response.text}")
    return None

# --- HANDLER UTAMA ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id_str = str(user.id)
    user_first_name = user.first_name or "N/A"
    user_username = user.username or "N/A"
    
    is_new_user = user_id_str not in user_data["registered_users"]
    user_details = user_data["registered_users"].setdefault(user_id_str, {
        "accounts": {}, "balance": 0, "transactions": [], "selected_hesdapkg_ids": [],
        "selected_30h_pkg_ids": []
    })
    user_details['first_name'] = user_first_name
    user_details['username'] = user_username
    if is_new_user:
        logging.info(f"User baru terdaftar: ID={user_id_str}, Nama={user_first_name}, Username=@{user_username}")
    
    simpan_data_ke_db()
    await send_main_menu(update, context)

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_first_name = update.effective_user.first_name
    user_balance = user_data.get("registered_users", {}).get(str(user_id), {}).get("balance", 0)
    total_users = len(user_data.get("registered_users", {}))
    
    uptime_delta = datetime.now() - context.application.bot_data.get("bot_start_time", datetime.now())
    days, remainder = divmod(uptime_delta.seconds, 3600)
    hours, _ = divmod(remainder, 60)
    minutes = (uptime_delta.seconds % 3600) // 60
    uptime_str = f"{days}d:{hours}j:{minutes}m"

    stats_block = (
        f"💜 D O R  X L  H O K A G E  L E G E N D  S T O R E 💜\n"
        f"╔══════════════════════════════╗\n"
        f"║ 🪪 *Nama* : {escape_markdown(user_first_name)}\n"
        f"║ 🆔 *ID User* : `{user_id}`\n"
        f"║ 💰 *Saldo Anda* : `Rp{user_balance:,}`\n"
        f"╠══════════════════════════════╣\n"
        f"║ 📊 *S T A T I S T I K  B O T*\n"
        f"╠══════════════════════════════╣\n"
        f"║ 👥 *Total Pengguna* : {total_users} user\n"
        f"║ ⏱️ *Uptime Bot* : {uptime_str}\n"
        f"╚══════════════════════════════╝\n\n"
        f"🌸 *~ Selamat Berbelanja Di Hokage Legend ~* 🌸"
    )
    
    reply_markup = keyboards.get_main_menu_keyboard()
    
    if update.callback_query:
        await update.callback_query.edit_message_text(stats_block, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(stats_block, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_top_up_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        top_up_amount = int(update.message.text.strip())
        
        if top_up_amount < MIN_TOP_UP_AMOUNT:
            await update.message.reply_text(f"Minimal top up adalah Rp {MIN_TOP_UP_AMOUNT:,}.")
            context.user_data['next'] = 'handle_top_up_amount'
            return

        status_msg = await update.message.reply_text("⏳ Sedang membuat kode pembayaran, harap tunggu...")
        tripay_data = buat_transaksi_tripay(user_id, top_up_amount)
        await status_msg.delete()

        if tripay_data:
            qris_url = tripay_data.get('qr_url')
            checkout_url = tripay_data.get('checkout_url')
            pesan = (
                f"Silakan selesaikan pembayaran Anda sebesar *Rp{top_up_amount:,}*.\n\n"
                f"Scan QRIS ini atau buka link di bawah untuk melihat simulator pembayaran (mode sandbox).\n\n"
                f"[Buka Halaman Pembayaran]({checkout_url})"
            )
            await context.bot.send_photo(chat_id=user_id, photo=qris_url, caption=pesan, parse_mode="Markdown")
        else:
            await update.message.reply_text("Maaf, gagal membuat link pembayaran. Coba lagi nanti.")
            await send_main_menu(update, context)
    except ValueError:
        await update.message.reply_text("Nominal tidak valid. Masukkan angka saja.")
        context.user_data['next'] = 'handle_top_up_amount'

# --- HANDLER UNTUK SEMUA INTERAKSI TOMBOL ---
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'back_to_menu':
        await send_main_menu(update, context)
    
    elif data == 'top_up_saldo':
        await query.edit_message_text(f"Masukkan nominal top up (minimal Rp{MIN_TOP_UP_AMOUNT:,}):",
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Kembali", callback_data="back_to_menu")]]))
        context.user_data['next'] = 'handle_top_up_amount'

    elif data == 'tembak_paket':
        reply_markup = keyboards.get_tembak_paket_keyboard()
        await query.edit_message_text("Silakan pilih jenis paket yang ingin ditembak:", reply_markup=reply_markup)

    # --- ALUR XUTS ---
    elif data == 'menu_uts_nested':
        await send_uts_menu(update, context)
    elif data == 'manual_uts_selection_menu':
        await send_manual_uts_selection_menu(update, context)
    elif data == 'automatic_purchase_flow':
        reply_markup = keyboards.get_automatic_method_selection_keyboard()
        await query.edit_message_text(
            "Anda memilih mode Otomatis. Silakan pilih metode pembayaran untuk paket *XC 1+1GB*:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    elif data.startswith('automatic_method_'):
        # ... (Logika untuk handle automatic_method)
        pass # Akan ditangani di handle_text setelah user input nomor
        
    # --- ALUR XUTP ---
    elif data == 'xutp_menu':
        await send_xutp_method_selection_menu(update, context)
        
    # --- ALUR XCS ADD ON ---
    elif data == 'xcp_addon':
        await send_xcp_addon_menu(update, context)
    elif data == 'manual_xcs_addon_selection_menu':
        await send_manual_xcs_addon_selection_menu(update, context)
    elif data == 'automatic_xcs_addon_flow':
        await send_automatic_xcs_addon_method_selection_menu(update, context)
        
    else:
        await query.edit_message_text("Fitur ini sedang dalam pengembangan.")

# --- HANDLER UNTUK SEMUA PESAN TEKS ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'next' in context.user_data:
        next_step = context.user_data.pop('next')
        if next_step == 'handle_top_up_amount':
            await handle_top_up_amount(update, context)
        # ... Tambahkan semua logika 'next' Anda yang lain di sini
    else:
        pass

# --- FUNGSI MENU-MENU ---
async def send_uts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*Pilih Mode Pembelian XUTS*\n\n"
        "1. *Mode Otomatis*: Beli XUTS & XC 1+1GB secara berurutan.\n"
        "2. *Mode Manual*: Beli paket satu per satu."
    )
    reply_markup = keyboards.get_uts_menu_keyboard()
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def send_manual_uts_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "⚠️ *PENTING*: Beli **XUTS** terlebih dahulu sebelum membeli XC 1+1GB."
    reply_markup = keyboards.get_manual_uts_selection_keyboard()
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def send_xutp_method_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Pilih metode pembayaran untuk alur pembelian XUTP otomatis:"
    reply_markup = keyboards.get_xutp_method_selection_keyboard()
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def send_xcp_addon_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Pilih mode pembelian untuk XCS ADD ON:"
    reply_markup = keyboards.get_xcp_addon_menu_keyboard()
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    
async def send_manual_xcs_addon_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Pilih paket secara manual:"
    reply_markup = keyboards.get_manual_xcs_addon_selection_keyboard()
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def send_automatic_xcs_addon_method_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Pilih metode pembayaran untuk alur pembelian XCS ADD ON Otomatis:"
    reply_markup = keyboards.get_automatic_xcs_addon_method_selection_keyboard()
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)

# --- FUNGSI ADMIN DAN LAIN-LAIN ---
# (Salin semua fungsi sisanya dari skrip lama Anda di sini,
# seperti `admin_menu`, `akun_saya_command_handler`, dll.
# Pastikan untuk menyesuaikan panggilan keyboard-nya)

# handlers.py

# ... (kode handlers.py yang sudah ada sebelumnya ada di sini) ...

# 剪═══════════════════════════════════════════════════════════════
# █ FUNGSI ADMIN DAN LAIN-LAIN
# 剪═══════════════════════════════════════════════════════════════

async def check_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        return True
    if user_id in database.user_data.get("blocked_users", []):
        await update.effective_message.reply_text("Anda telah diblokir. Hubungi admin.")
        return False
    return True

async def akun_saya_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update, context):
        return
    user_id = update.effective_user.id
    akun_list = database.user_data.get("registered_users", {}).get(str(user_id), {}).get("accounts", {})
    
    text_parts = ["*Akun Nomor HP Terdaftar:*\n"]
    if not akun_list:
        text_parts.append("_Anda belum login dengan nomor manapun._")
    else:
        for nomor, details in akun_list.items():
            kmsp_status = "✅" if details.get("kmsp", {}).get("access_token") else "❌"
            hesda_status = "✅" if details.get("hesda", {}).get("access_token") else "❌"
            text_parts.append(f"• `{nomor}` (LOGIN: {kmsp_status} | BYPAS: {hesda_status})")
    
    keyboard = [
        [InlineKeyboardButton("🏠 Kembali ke Menu Utama", callback_data="back_to_menu")]
    ]
    
    if update.callback_query:
        await update.callback_query.edit_message_text("\n".join(text_parts), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("\n".join(text_parts), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        if update.message:
            await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    total_users = len(database.user_data.get("registered_users", {}))
    
    header_text = (
        f"📊 *Statistik Bot*\n"
        f"👥 Total Pengguna: *{total_users}*\n\n"
        "👑 *Panel Admin*\n"
        "Pilih tindakan yang ingin Anda lakukan:"
    )
    reply_markup = keyboards.get_admin_menu_keyboard()
    
    if update.callback_query:
         await update.callback_query.edit_message_text(
            header_text, parse_mode="Markdown", reply_markup=reply_markup
        )
    elif update.message:
         await update.message.reply_text(
            header_text, parse_mode="Markdown", reply_markup=reply_markup
        )

async def admin_handle_add_balance_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        parts = update.message.text.split()
        target_user_id = int(parts[0])
        amount = int(parts[1])

        target_user_str = str(target_user_id)
        if target_user_str not in database.user_data["registered_users"]:
            await update.message.reply_text(f"User ID `{target_user_id}` tidak ditemukan.")
            return

        database.user_data["registered_users"][target_user_str]["balance"] += amount
        database.simpan_data_ke_db()
        
        new_balance = database.user_data["registered_users"][target_user_str]["balance"]
        await update.message.reply_text(f"✅ Saldo user `{target_user_id}` berhasil ditambah Rp{amount:,}.\nSaldo baru: Rp{new_balance:,}.", parse_mode="Markdown")
        
        try:
            await context.bot.send_message(target_user_id, f"💰 Saldo Anda telah ditambahkan sebesar *Rp{amount:,}* oleh admin.", parse_mode="Markdown")
        except Exception as e:
            logger.warning(f"Gagal kirim notifikasi ke user {target_user_id}: {e}")

    except (ValueError, IndexError):
        await update.message.reply_text("Format salah. Gunakan: `ID_User Jumlah_Saldo`")
    finally:
        await admin_menu(update, context)

# (Tambahkan fungsi admin lainnya seperti admin_handle_deduct_balance, block, unblock, search, dll. di sini)
# ...

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    next_step = context.user_data.pop('next', None)

    if not next_step:
        return

    # Admin actions
    if user_id == ADMIN_ID:
        if next_step == 'admin_handle_add_balance_input':
            await admin_handle_add_balance_input(update, context)
            return
        # ... (tambahkan elif untuk handler admin lainnya)

    # User actions
    if next_step == 'handle_top_up_amount':
        await handle_top_up_amount(update, context)
    # ... (tambahkan elif untuk handler user lainnya)

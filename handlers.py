# handlers.py

import logging
import requests
import json
from datetime import datetime
import hashlib
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

# Import dari file lain di proyek Anda
import keyboards # Mengimpor semua fungsi keyboard
from database import user_data, simpan_data_ke_db # Mengimpor data dan fungsi DB
from config import * # Mengimpor semua konfigurasi

logger = logging.getLogger(__name__)

# --- FUNGSI TRIPAY BARU ---
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
    # ... (logika pendaftaran user baru Anda) ...
    simpan_data_ke_db()
    await send_main_menu(update, context)

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_first_name = update.effective_user.first_name
    user_balance = user_data.get("registered_users", {}).get(str(user_id), {}).get("balance", 0)
    
    # ... (logika pembuatan teks menu utama Anda) ...
    text = f"Selamat datang {user_first_name}!\nSaldo Anda: Rp{user_balance:,}" # Contoh teks
    
    reply_markup = keyboards.get_main_menu_keyboard() # Memanggil dari keyboards.py
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

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
            
            await context.bot.send_photo(
                chat_id=user_id, photo=qris_url, caption=pesan, parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("Maaf, gagal membuat link pembayaran. Coba lagi nanti.")
            await send_main_menu(update, context)

    except ValueError:
        await update.message.reply_text("Nominal tidak valid. Masukkan angka saja.")
        context.user_data['next'] = 'handle_top_up_amount'

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'top_up_saldo':
        await query.edit_message_text(f"Masukkan nominal top up (minimal Rp{MIN_TOP_UP_AMOUNT:,}):")
        context.user_data['next'] = 'handle_top_up_amount'
    elif query.data == 'back_to_menu':
        await send_main_menu(update, context)
    # ... (tambahkan semua logika callback query Anda yang lain di sini) ...

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'next' in context.user_data:
        next_step = context.user_data.pop('next')
        if next_step == 'handle_top_up_amount':
            await handle_top_up_amount(update, context)
        # ... (tambahkan semua logika 'next' Anda yang lain di sini) ...

# ... (Salin semua fungsi handler Anda yang lain ke sini) ...
# Contoh: admin_menu, check_access, run_automatic_flow, dll.
# Pastikan untuk mengganti pembuatan keyboard dengan memanggil fungsi dari keyboards.py
# Contoh: reply_markup = keyboards.get_admin_menu_keyboard()

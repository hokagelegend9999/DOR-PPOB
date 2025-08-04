# purchase_flows.py

import logging, requests, json, time, hashlib, sqlite3, asyncio, re
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

from database import user_data, simpan_data_ke_db
from config import *
import main_handlers # Untuk memanggil send_main_menu

logger = logging.getLogger(__name__)

async def handle_top_up_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        top_up_amount = int(update.message.text.strip())
        if top_up_amount < MIN_TOP_UP_AMOUNT:
            await update.message.reply_text(f"Minimal top up adalah Rp {MIN_TOP_UP_AMOUNT:,}.")
            context.user_data['next'] = 'handle_top_up_amount'
            return

        status_msg = await update.message.reply_text("⏳ Sedang membuat kode pembayaran...")
        tripay_data = main_handlers.buat_transaksi_tripay(user_id, top_up_amount)
        await status_msg.delete()

        if tripay_data:
            qris_url = tripay_data.get('qr_url')
            checkout_url = tripay_data.get('checkout_url')
            pesan = (f"Silakan bayar *Rp{top_up_amount:,}*.\n\n[Buka Halaman Pembayaran]({checkout_url})")
            await context.bot.send_photo(chat_id=user_id, photo=qris_url, caption=pesan, parse_mode="Markdown")
        else:
            await update.message.reply_text("Gagal membuat pembayaran. Coba lagi nanti.")
    except ValueError:
        await update.message.reply_text("Nominal tidak valid. Masukkan angka.")
        context.user_data['next'] = 'handle_top_up_amount'

async def handle_automatic_purchase_phone_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (Salin fungsi lengkap `handle_automatic_purchase_phone_input` dari jawaban saya sebelumnya)
    pass

async def run_automatic_purchase_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (Salin fungsi lengkap `run_automatic_purchase_flow` dari skrip asli Anda)
    pass
    
# ... (Salin SEMUA fungsi lain yang berhubungan dengan pembelian:
# execute_automatic_xuts_purchase, execute_automatic_xc_purchase,
# run_automatic_xutp_flow, run_automatic_xcs_addon_flow, dll. ke sini)

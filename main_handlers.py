# main_handlers.py
import requests 
import re       
import html      
import logging, re, html
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, error
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from datetime import datetime

# Impor dari file lain di proyek Anda
import keyboards
import purchase_flows
import admin_handlers
from database import user_data, simpan_data_ke_db
from config import *

logger = logging.getLogger(__name__)

# --- FUNGSI HELPER ---
async def safe_edit_message(query, text, **kwargs):
    try:
        if query and query.message:
            await query.edit_message_text(text=text, **kwargs)
    except error.BadRequest as e:
        if "Message is not modified" in str(e) or "Message to edit not found" in str(e):
            logger.warning(f"Ignored expected BadRequest error: {e}")
        else:
            logger.error(f"Unhandled BadRequest error: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Failed to edit message, sending new one: {e}", exc_info=True)
        if query and query.message:
            try: await query.message.delete()
            except Exception: pass
            await query.message.reply_text(text, **kwargs)

# --- HANDLER UTAMA ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id_str = str(user.id)
    user_details = user_data["registered_users"].setdefault(user_id_str, {
        "accounts": {}, "balance": 0, "transactions": [], "selected_hesdapkg_ids": [], "selected_30h_pkg_ids": []
    })
    user_details['first_name'] = user.first_name or "N/A"
    user_details['username'] = user.username or "N/A"
    simpan_data_ke_db()
    await send_main_menu(update, context)

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_first_name = update.effective_user.first_name
    user_balance = user_data.get("registered_users", {}).get(str(user_id), {}).get("balance", 0)
    total_users = len(user_data.get("registered_users", {}))
    uptime_delta = datetime.now() - context.application.bot_data.get("bot_start_time", datetime.now())
    days, remainder = divmod(uptime_delta.seconds, 3600)
    hours, minutes = divmod(remainder, 60)
    uptime_str = f"{days}d:{hours}j:{minutes}m"
    stats_block = (
        f"💜 *DOR XL HOKAGE LEGEND STORE* 💜\n"
        f"══════════════════════\n"
        f"👤 *Nama*: {escape_markdown(user_first_name)}\n"
        f"🆔 *ID User*: `{user_id}`\n"
        f"💰 *Saldo Anda*: `Rp{user_balance:,}`\n"
        f"══════════════════════\n"
        f"📊 *STATISTIK BOT*\n"
        f"👥 *Total Pengguna*: {total_users} user\n"
        f"⏱️ *Uptime Bot*: {uptime_str}\n"
    )
    reply_markup = keyboards.get_main_menu_keyboard()
    if update.callback_query:
        await safe_edit_message(update.callback_query, stats_block, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.message:
        await update.message.reply_text(stats_block, reply_markup=reply_markup, parse_mode="Markdown")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith('admin_'):
        await admin_handlers.admin_callback_handler(update, context)
        return

    # User Handlers
    if data == 'back_to_menu':
        await send_main_menu(update, context)
    elif data == 'show_login_options':
        await safe_edit_message(query, text="Silakan pilih jenis login:", reply_markup=keyboards.get_login_options_keyboard())
    elif data == 'login_kmsp':
        await safe_edit_message(query, text="Masukkan nomor HP untuk login (LOGIN):")
        context.user_data['next'] = 'handle_phone_for_login'
        context.user_data['current_login_provider'] = 'kmsp'
    elif data == 'login_hesda':
        await safe_edit_message(query, text="Masukkan nomor HP untuk login (BYPAS):")
        context.user_data['next'] = 'handle_phone_for_login'
        context.user_data['current_login_provider'] = 'hesda'
    elif data == 'tembak_paket':
        await safe_edit_message(query, text="Silakan pilih jenis paket yang ingin ditembak:", reply_markup=keyboards.get_tembak_paket_keyboard())
    elif data == 'top_up_saldo':
        await safe_edit_message(query, text=f"Masukkan nominal top up (minimal Rp{MIN_TOP_UP_AMOUNT:,}):",
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Kembali", callback_data="back_to_menu")]]))
        context.user_data['next'] = 'handle_top_up_amount'
    elif data == 'cek_saldo':
        balance = user_data.get("registered_users", {}).get(str(user_id), {}).get("balance", 0)
        await query.answer(f"💰 Saldo Anda saat ini: Rp{balance:,}", show_alert=True)
    elif data == 'cek_kuota':
        await safe_edit_message(query, text="Masukkan nomor HP XL/Axis yang ingin dicek (contoh: `0878...`):",
                                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Kembali", callback_data="back_to_menu")]]))
        context.user_data['next'] = 'handle_cek_kuota_input'
    elif data == 'menu_uts_nested':
        await send_uts_menu(update, context)
    elif data == 'automatic_purchase_flow':
         await safe_edit_message(query,
            text="Anda memilih mode Otomatis. Silakan pilih metode pembayaran untuk paket *XC 1+1GB*:",
            reply_markup=keyboards.get_automatic_method_selection_keyboard()
        )
    elif data.startswith('automatic_method_'):
        payment_method_for_auto = data.replace('automatic_method_', '').upper()
        if payment_method_for_auto == "PULSA":
            context.user_data['automatic_purchase_payment_method'] = "BALANCE"
            display_method_name = "PULSA (Saldo Bot)"
        else:
            context.user_data['automatic_purchase_payment_method'] = payment_method_for_auto
            display_method_name = payment_method_for_auto
        await safe_edit_message(query,
            text=f"Mode Otomatis XUTS dipilih dengan pembayaran *{display_method_name}*.\nMasukkan nomor HP untuk memulai proses:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali", callback_data="automatic_purchase_flow")]])
        )
        context.user_data['next'] = 'handle_automatic_purchase_phone_input'
    else:
        await query.answer("Fitur ini belum diimplementasikan.", show_alert=True)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_step = context.user_data.pop('next', None)
    if not next_step: return

    # User actions
    if next_step == 'handle_top_up_amount':
        await purchase_flows.handle_top_up_amount(update, context)
    elif next_step == 'handle_phone_for_login':
        await purchase_flows.handle_phone_for_login(update, context)
    elif next_step == 'handle_login_otp_input':
        await purchase_flows.handle_login_otp_input(update, context)
    elif next_step == 'handle_cek_kuota_input':
        await jalankan_cek_kuota_baru(update, context)
    elif next_step == 'handle_automatic_purchase_phone_input':
        await purchase_flows.handle_automatic_purchase_phone_input(update, context)
    
    # Admin actions
    elif next_step.startswith('admin_'):
        await admin_handlers.admin_handle_text(update, context, next_step)

async def send_uts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "*Pilih Mode Pembelian XUTS*\n\n1. *Mode Otomatis*\n2. *Mode Manual*"
    await safe_edit_message(update.callback_query, text, reply_markup=keyboards.get_uts_menu_keyboard())

async def jalankan_cek_kuota_baru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    nomor_input = update.message.text.strip()

    if not re.match(r'^(08|62)\d{8,12}$', nomor_input):
        await update.message.reply_text('Format nomor salah. Coba lagi.')
        context.user_data['next'] = 'handle_cek_kuota_input'
        return

    nomor = '62' + nomor_input[1:] if nomor_input.startswith('08') else nomor_input
    status_msg = await update.message.reply_text("🔍 Sedang mengecek kuota, harap tunggu...")

    try:
        url = f"https://apigw.kmsp-store.com/sidompul/v4/cek_kuota?msisdn={nomor}&isJSON=true"
        headers = { "Authorization": "Basic c2lkb21wdWxhcGk6YXBpZ3drbXNw", "X-API-Key": "60ef29aa-a648-4668-90ae-20951ef90c55", "X-App-Version": "4.0.0" }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response_json = response.json()
        
        await status_msg.delete()

        if response_json.get('status'):
            hasil_kotor = response_json.get("data", {}).get("hasil", "Tidak ada data.")
            hasil_bersih = html.unescape(hasil_kotor).replace('<br>', '\n').replace('MSISDN', 'NOMOR')
            final_text = f"✅ *Hasil Cek Kuota {nomor}*\n\n```{hasil_bersih}```"
            await context.bot.send_message(user_id, final_text, parse_mode="Markdown")
        else:
            error_text = response_json.get("message", "Gagal mengambil data.")
            await context.bot.send_message(user_id, f"❌ Terjadi kesalahan: `{error_text}`", parse_mode="Markdown")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error Cek Kuota: {e}")
        await status_msg.delete()
        await context.bot.send_message(user_id, "❌ Gagal terhubung ke server pengecekan kuota.")
    finally:
        await send_main_menu(update, context)

async def check_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        return True
    if user_id in user_data.get("blocked_users", []):
        await update.effective_message.reply_text("Anda telah diblokir.")
        return False
    return True

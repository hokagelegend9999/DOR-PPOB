# main_handlers.py (Versi Final dengan Perbaikan Tombol Cek Saldo)

import logging, re, html
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, error
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

import keyboards
import purchase_flows
import admin_handlers
from database import user_data, simpan_data_ke_db
from config import *

logger = logging.getLogger(__name__)

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
        logger.error(f"Failed to edit message: {e}", exc_info=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id_str = str(user.id)
    user_details = user_data["registered_users"].setdefault(user_id_str, {"balance": 0, "accounts": {}})
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

    if data == 'back_to_menu':
        await send_main_menu(update, context)

    # --- PERBAIKAN LOGIKA CEK SALDO ---
    elif data == 'cek_saldo':
        balance = user_data.get("registered_users", {}).get(str(user_id), {}).get("balance", 0)
        text = f"💰 Saldo Anda saat ini adalah: *Rp{balance:,}*"
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali ke Menu Utama", callback_data="back_to_menu")]])
        await safe_edit_message(query, text, reply_markup=reply_markup, parse_mode="Markdown")

    elif data == 'tutorial_beli':
        await send_tutorial_menu(update, context)
    elif data == 'show_custom_packages':
        await show_custom_packages_for_user(update, context)
    elif data.startswith('syarat_') or data.startswith('tutorial_'):
        await send_tutorial_detail(update, context)
    elif data == 'show_login_options':
        await safe_edit_message(query, text="Silakan pilih jenis login:", reply_markup=keyboards.get_login_options_keyboard())
    elif data == 'login_kmsp':
        await safe_edit_message(query, text="Masukkan nomor HP untuk login (LOGIN):")
        context.user_data['next'] = 'handle_phone_for_login'
        context.user_data['current_login_provider'] = 'kmsp'
    elif data == 'tembak_paket':
        await safe_edit_message(query, text="Silakan pilih jenis paket yang ingin ditembak:", reply_markup=keyboards.get_tembak_paket_keyboard())
    elif data == 'top_up_saldo':
        await safe_edit_message(query, text=f"Masukkan nominal top up (minimal Rp{MIN_TOP_UP_AMOUNT:,}):",
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Kembali", callback_data="back_to_menu")]]))
        context.user_data['next'] = 'handle_top_up_amount'
    elif data == 'cek_kuota':
        await safe_edit_message(query, text="Masukkan nomor HP XL/Axis (contoh: `0878...`):",
                                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Kembali", callback_data="back_to_menu")]]))
        context.user_data['next'] = 'handle_cek_kuota_input'
    else:
        await query.answer(f"Callback '{data}' belum memiliki fungsi.", show_alert=True)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_step = context.user_data.pop('next', None)
    if not next_step: return

    if next_step == 'handle_cek_kuota_input':
        await jalankan_cek_kuota_baru(update, context)
    elif next_step.startswith('admin_'):
        pass # Delegasi ke admin_handlers
    else:
        if hasattr(purchase_flows, next_step):
            handler_func = getattr(purchase_flows, next_step)
            await handler_func(update, context)
        else:
            logger.warning(f"No handler found for next_step: {next_step}")

async def send_tutorial_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Silakan pilih tutorial yang ingin Anda lihat:"
    await safe_edit_message(update.callback_query, text, reply_markup=keyboards.get_tutorial_menu_keyboard())

async def show_custom_packages_for_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Berikut adalah daftar paket lainnya yang tersedia:"
    await safe_edit_message(update.callback_query, text, reply_markup=keyboards.get_custom_packages_keyboard())

async def send_tutorial_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    text = ""
    if data == 'syarat_pembelian':
        text = "Syarat Pembelian:\n1. Sudah Login OTP\n2. Tidak ada paket Xtra Combo\n3. Kartu tidak dalam masa tenggang."
    elif data == 'tutorial_xcs_addons':
        text = "Tutorial Pembelian XCS ADD-ONS:\n1. Pilih mode Otomatis\n2. Masukkan nomor\n3. Lakukan pembayaran."
    elif data == 'tutorial_uts':
        text = "Tutorial Pembelian XUTS:\n1. Beli XUTS dulu\n2. Setelah berhasil, baru beli XC 1+1GB."
    await safe_edit_message(update.callback_query, text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali ke Tutorial", callback_data='tutorial_beli')]]))

async def jalankan_cek_kuota_baru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    nomor_input = update.message.text.strip()
    if not re.match(r'^(08|62)\d{8,12}$', nomor_input):
        await update.message.reply_text('Format nomor salah. Coba lagi.')
        context.user_data['next'] = 'handle_cek_kuota_input'
        return
    nomor = '62' + nomor_input[1:] if nomor_input.startswith('08') else nomor_input
    status_msg = await update.message.reply_text("🔍 Sedang mengecek kuota...")
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
    if user_id == ADMIN_ID: return True
    if user_id in user_data.get("blocked_users", []):
        if update.callback_query: await update.callback_query.answer("Anda telah diblokir.", show_alert=True)
        elif update.message: await update.message.reply_text("Anda telah diblokir.")
        return False
    return True

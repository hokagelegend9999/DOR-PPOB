# main_handlers.py

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, error
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from datetime import datetime

# Impor dari file lain di proyek Anda
import keyboards
import purchase_flows  # Kita akan memanggil fungsi dari sini
import admin_handlers  # Kita akan memanggil fungsi dari sini
from database import user_data, simpan_data_ke_db
from config import *

logger = logging.getLogger(__name__)

# --- FUNGSI HELPER ---
async def safe_edit_message(query: Update.callback_query, text: str, **kwargs):
    try:
        await query.edit_message_text(text=text, **kwargs)
    except error.BadRequest as e:
        if "Message is not modified" in str(e) or "Message to edit not found" in str(e):
            logger.warning(f"Ignored expected BadRequest error: {e}")
        else:
            logger.error(f"Unhandled BadRequest error: {e}", exc_info=True)
            raise
    except Exception as e:
        logger.error(f"Failed to edit message, sending new one: {e}", exc_info=True)
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.reply_text(text, **kwargs)

# --- HANDLER UTAMA ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id_str = str(user.id)
    is_new_user = user_id_str not in user_data["registered_users"]
    user_details = user_data["registered_users"].setdefault(user_id_str, {
        "accounts": {}, "balance": 0, "transactions": [], "selected_hesdapkg_ids": [],
        "selected_30h_pkg_ids": []
    })
    user_details['first_name'] = user.first_name or "N/A"
    user_details['username'] = user.username or "N/A"
    if is_new_user:
        logger.info(f"User baru terdaftar: ID={user_id_str}, Nama={user.first_name}, Username=@{user.username}")
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
        await safe_edit_message(update.callback_query, stats_block, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(stats_block, reply_markup=reply_markup, parse_mode="Markdown")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith('admin_'):
        await admin_handlers.admin_callback_handler(update, context)
        return

    # User Handlers
    if data == 'back_to_menu':
        await send_main_menu(update, context)
    elif data == 'tembak_paket':
        await safe_edit_message(query, "Silakan pilih jenis paket:", reply_markup=keyboards.get_tembak_paket_keyboard())
    elif data == 'top_up_saldo':
        await safe_edit_message(query, f"Masukkan nominal top up (minimal Rp{MIN_TOP_UP_AMOUNT:,}):",
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Kembali", callback_data="back_to_menu")]]))
        context.user_data['next'] = 'handle_top_up_amount'
    elif data == 'menu_uts_nested':
        await send_uts_menu(update, context)
    elif data == 'automatic_purchase_flow':
        await safe_edit_message(query, "Pilih metode pembayaran untuk paket XC 1+1GB:",
                                 reply_markup=keyboards.get_automatic_method_selection_keyboard())
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
        await query.answer("Fitur ini belum diimplementasikan di main_handlers.", show_alert=True)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_step = context.user_data.pop('next', None)
    if not next_step:
        return

    if next_step == 'handle_top_up_amount':
        await purchase_flows.handle_top_up_amount(update, context)
    elif next_step == 'handle_automatic_purchase_phone_input':
        await purchase_flows.handle_automatic_purchase_phone_input(update, context)
    elif next_step.startswith('admin_'):
        await admin_handlers.admin_handle_text(update, context, next_step)
    # ...tambahkan handler teks lainnya jika ada

# --- Fungsi Menu Sederhana ---
async def send_uts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "*Pilih Mode Pembelian XUTS*\n\n1. *Mode Otomatis*\n2. *Mode Manual*"
    await safe_edit_message(update.callback_query, text, keyboards.get_uts_menu_keyboard())

# ... (tambahkan fungsi menu sederhana lainnya di sini jika perlu)

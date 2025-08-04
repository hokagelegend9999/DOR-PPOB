# admin_handlers.py

import logging
from telegram import Update
from telegram.ext import ContextTypes

import keyboards
from database import user_data, simpan_data_ke_db
from config import *

logger = logging.getLogger(__name__)

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # (Kode fungsi admin_menu dari skrip asli Anda, disesuaikan)
    if update.effective_user.id != ADMIN_ID:
        return
    
    total_users = len(user_data.get("registered_users", {}))
    header_text = (
        f"📊 *Statistik Bot*\n"
        f"👥 Total Pengguna: *{total_users}*\n\n"
        "👑 *Panel Admin*"
    )
    reply_markup = keyboards.get_admin_menu_keyboard()
    
    if update.callback_query:
        await main_handlers.safe_edit_message(update.callback_query, header_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(header_text, reply_markup=reply_markup, parse_mode="Markdown")


async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == 'admin_add_balance':
        await main_handlers.safe_edit_message(query, "Masukkan: `ID_USER JUMLAH`")
        context.user_data['next'] = 'admin_handle_add_balance_input'
    # ... (Tambahkan elif untuk semua tombol admin lainnya)
    else:
        await query.answer("Tombol admin belum diimplementasikan.", show_alert=True)

async def admin_handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE, next_step: str):
    if next_step == 'admin_handle_add_balance_input':
        try:
            _, target_user_id, amount = update.message.text.split()
            target_user_id = int(target_user_id)
            amount = int(amount)
            
            user_data["registered_users"][str(target_user_id)]["balance"] += amount
            simpan_data_ke_db()
            
            new_balance = user_data["registered_users"][str(target_user_id)]["balance"]
            await update.message.reply_text(f"Saldo user `{target_user_id}` ditambah Rp{amount:,}. Saldo baru: Rp{new_balance:,}.")
            
            await context.bot.send_message(target_user_id, f"Saldo Anda ditambah Rp{amount:,} oleh Admin.")
        except Exception as e:
            await update.message.reply_text(f"Format salah atau user tidak ada. Error: {e}")
    # ... (Tambahkan elif untuk semua input teks admin lainnya)

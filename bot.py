# bot.py

import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import threading
from datetime import datetime

import database
import main_handlers    # Impor file handler utama
import admin_handlers   # Impor file handler admin
from config import BOT_TOKEN

def main():
    database.inisialisasi_database()
    database.muat_data_dari_db()

    # (Jalankan webhook server di sini jika Anda menggunakannya)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.bot_data["bot_start_time"] = datetime.now()

    # Daftarkan handler dari file-file yang berbeda
    app.add_handler(CommandHandler("start", main_handlers.start))
    app.add_handler(CommandHandler("admin", admin_handlers.admin_menu))
    app.add_handler(CallbackQueryHandler(main_handlers.button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, main_handlers.handle_text))

    logging.info("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

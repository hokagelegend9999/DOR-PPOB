# bot.py

import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import threading
from datetime import datetime

import database
import main_handlers
import admin_handlers
from config import BOT_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    database.inisialisasi_database()
    database.muat_data_dari_db()

    # Jalankan webhook di thread terpisah (jika Anda pakai)
    # webhook_thread = threading.Thread(target=lambda: webhook_server.app.run(port=5000, host='0.0.0.0'))
    # webhook_thread.daemon = True
    # webhook_thread.start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.bot_data["bot_start_time"] = datetime.now()

    # Daftarkan handler dari file-file yang berbeda
    app.add_handler(CommandHandler("start", main_handlers.start))
    app.add_handler(CommandHandler("admin", admin_handlers.admin_menu))
    app.add_handler(CallbackQueryHandler(main_handlers.button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, main_handlers.handle_text))

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

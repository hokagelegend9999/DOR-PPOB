# bot.py

import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import threading
from datetime import datetime

import database
import handlers
import webhook_server
from config import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    database.inisialisasi_database()
    database.muat_data_dari_db()

    webhook_thread = threading.Thread(target=lambda: webhook_server.app.run(port=5000, host='0.0.0.0'))
    webhook_thread.daemon = True
    webhook_thread.start()
    logger.info("Webhook server started on port 5000 in a background thread.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Simpan waktu mulai bot
    app.bot_data["bot_start_time"] = datetime.now()

    # Daftarkan semua handler dari file handlers.py
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("menu", handlers.start)) # Alias untuk start
    app.add_handler(CommandHandler("admin", handlers.admin_menu))
    app.add_handler(CommandHandler("akun", handlers.akun_saya_command_handler))
    
    app.add_handler(CallbackQueryHandler(handlers.button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_text))

    logger.info("Telegram bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

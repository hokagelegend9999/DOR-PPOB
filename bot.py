# bot.py

import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import threading

# Import dari file-file lain
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
    # 1. Inisialisasi dan muat data dari database
    database.inisialisasi_database()
    database.muat_data_dari_db()

    # 2. Setup dan jalankan server webhook di thread terpisah
    # Ini penting agar bot telegram dan server webhook bisa berjalan bersamaan
    webhook_thread = threading.Thread(target=lambda: webhook_server.app.run(port=5000))
    webhook_thread.daemon = True
    webhook_thread.start()
    logger.info("Webhook server started on port 5000 in a background thread.")

    # 3. Bangun aplikasi bot Telegram
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # 4. Daftarkan semua handler dari file handlers.py
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("admin", handlers.admin_menu)) # Contoh
    app.add_handler(CallbackQueryHandler(handlers.button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_text))

    # 5. Jalankan bot
    logger.info("Telegram bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

# purchase_flows.py (Versi Final Lengkap - 4 Agustus 2025)

import logging, requests, json, time, hashlib, sqlite3, asyncio, re, base64
from telegram import Update, error
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from datetime import datetime
# Impor dari file-file lain dalam proyek Anda
import main_handlers
import keyboards
from database import user_data, simpan_data_ke_db
from config import *

logger = logging.getLogger(__name__)
import logging, requests, json, time, hashlib, sqlite3, asyncio, re, base64
from telegram import Update, error, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

from database import user_data, simpan_data_ke_db
from config import *
import main_handlers

logger = logging.getLogger(__name__)

# --- FUNGSI PEMBELIAN VIDIO / IFLIX ---
async def handle_vidio_iflix_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    package_type, payment_method_selected = "", ""
    if data.startswith('buy_vidio_xl_package_'):
        package_type = "vidio"
        payment_method_selected = data.replace('buy_vidio_xl_package_', '')
    elif data.startswith('buy_iflix_xl_package_'):
        package_type = "iflix"
        payment_method_selected = data.replace('buy_iflix_xl_package_', '')

    # --- BAGIAN YANG DIPERBAIKI ---
    price_key_base = ""
    if package_type == 'vidio':
        price_key_base = "XLUNLITURBOVIDIO"
    elif package_type == 'iflix':
        price_key_base = "XLUNLITURBOIFLIXXC"

    price_key = f"{price_key_base}_{payment_method_selected}"
    # --- AKHIR PERBAIKAN ---

    price_info = CUSTOM_PACKAGE_PRICES.get(price_key)
    if not price_info:
        logger.error(f"Harga tidak ditemukan untuk kunci: {price_key}")
        await query.answer("Terjadi kesalahan: Harga untuk paket ini tidak ditemukan.", show_alert=True)
        return

    required_balance = price_info.get('price_bot', 0)
    user_balance = user_data.get("registered_users", {}).get(str(user_id), {}).get("balance", 0)

    if user_balance < required_balance:
        await query.answer(f"Saldo Anda tidak cukup (butuh Rp{required_balance:,})", show_alert=True)
        return

    context.user_data['selected_package_info'] = price_info
    context.user_data['next'] = 'handle_beli_vidio_iflix_package'

    await main_handlers.safe_edit_message(
        query,
        text=f"Anda memilih: *{price_info.get('display_name')}*.\nMasukkan nomor HP untuk pembelian:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali", callback_data=f"{package_type}_xl_menu")]])
    )

async def handle_beli_vidio_iflix_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    phone_raw = update.message.text.strip()
    phone = '62' + phone_raw[1:] if phone_raw.startswith('08') else phone_raw

    if not re.match(r'^628\d{9,12}$', phone):
        await update.message.reply_text("Format nomor HP salah.")
        context.user_data['next'] = 'handle_beli_vidio_iflix_package'
        return

    package_info = context.user_data.pop('selected_package_info', None)
    if not package_info:
        await update.message.reply_text("Sesi pembelian tidak valid, silakan ulangi.")
        return

    await update.message.reply_text(
        f"Memproses pembelian *{package_info.get('display_name')}* untuk nomor `{phone}`...\n"
        f"(Logika API untuk pembelian ini belum diimplementasikan)",
        parse_mode="Markdown"
    )
# --- FUNGSI TRIPAY ---
def buat_transaksi_tripay(user_id, amount):
    merchant_ref = f"TOPUP-{user_id}-{int(time.time())}"
    method = 'QRISC'
    signature_string = f"{TRIPAY_MERCHANT_CODE_SANDBOX}{merchant_ref}{amount}{TRIPAY_PRIVATE_KEY_SANDBOX}"
    signature = hashlib.sha256(signature_string.encode()).hexdigest()
    payload = {
        'method': method, 'merchant_ref': merchant_ref, 'amount': amount,
        'customer_name': f'User {user_id}', 'customer_email': f'user{user_id}@example.com',
        'order_items': [{'sku': 'TOPUP', 'name': 'Top Up Saldo Bot', 'price': amount, 'quantity': 1}],
        'callback_url': WEBHOOK_CALLBACK_URL, 'return_url': f'https://t.me/{ADMIN_USERNAME}',
        'signature': signature
    }
    headers = {'Authorization': f'Bearer {TRIPAY_API_KEY_SANDBOX}'}
    try:
        response = requests.post(TRIPAY_API_URL_SANDBOX, headers=headers, json=payload, timeout=20)
        if response.status_code == 200 and response.json().get('success'):
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tripay_transactions (merchant_ref, user_id, amount, status) VALUES (?, ?, ?, ?)", (merchant_ref, user_id, amount, 'PENDING'))
            conn.commit()
            conn.close()
            return response.json()['data']
    except requests.exceptions.RequestException as e:
        logger.error(f"Koneksi ke Tripay gagal: {e}")
    logger.error(f"Error saat membuat transaksi Tripay: {response.text if 'response' in locals() else 'Request Failed'}")
    return None

async def handle_top_up_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        top_up_amount = int(update.message.text.strip())
        if top_up_amount < MIN_TOP_UP_AMOUNT:
            await update.message.reply_text(f"Minimal top up adalah Rp {MIN_TOP_UP_AMOUNT:,}.")
            context.user_data['next'] = 'handle_top_up_amount'
            return

        status_msg = await update.message.reply_text("⏳ Sedang membuat kode pembayaran...")
        tripay_data = buat_transaksi_tripay(user_id, top_up_amount)
        if status_msg: await status_msg.delete()

        if tripay_data:
            qris_url = tripay_data.get('qr_url')
            checkout_url = tripay_data.get('checkout_url')
            pesan = (f"Silakan bayar *Rp{top_up_amount:,}*.\n\n[Buka Halaman Pembayaran]({checkout_url})")
            await context.bot.send_photo(chat_id=user_id, photo=qris_url, caption=pesan, parse_mode="Markdown")
        else:
            await update.message.reply_text("Gagal membuat pembayaran. Coba lagi nanti.")
    except (ValueError, TypeError):
        await update.message.reply_text("Nominal tidak valid. Masukkan angka.")
        context.user_data['next'] = 'handle_top_up_amount'

# --- FUNGSI LOGIN & OTP ---
async def handle_phone_for_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    phone_raw = update.message.text.strip()
    phone = '62' + phone_raw[1:] if phone_raw.startswith('08') else phone_raw

    if not re.match(r'^628\d{9,12}$', phone):
        await update.message.reply_text("Format nomor HP salah. Coba lagi.")
        context.user_data['next'] = 'handle_phone_for_login'
        return

    context.user_data['temp_phone_for_login'] = phone
    login_provider = context.user_data.get('current_login_provider', 'kmsp')

    if login_provider == 'kmsp':
        await request_otp_and_prompt_kmsp(update, context, phone)
    elif login_provider == 'hesda':
        await request_otp_and_prompt_hesda(update, context, phone)

async def request_otp_and_prompt_kmsp(update: Update, context: ContextTypes.DEFAULT_TYPE, phone: str):
    user_id = update.effective_user.id
    await context.bot.send_message(user_id, f"⏳ Meminta OTP LOGIN untuk nomor `{phone}`...", parse_mode="Markdown")
    try:
        url = f"https://golang-openapi-reqotp-xltembakservice.kmsp-store.com/v1?api_key={KMSP_API_KEY}&phone={phone}&method=OTP"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        result = response.json()
        auth_id = result.get('data', {}).get('auth_id')

        if not auth_id: raise ValueError(result.get("message", "Auth ID tidak ditemukan."))

        # Memastikan struktur data ada sebelum diisi
        user_data["registered_users"].setdefault(str(user_id), {}).setdefault('accounts', {}).setdefault(phone, {}).setdefault('kmsp', {})['auth_id'] = auth_id
        simpan_data_ke_db()

        await context.bot.send_message(user_id, "✅ OTP Terkirim! Silakan masukkan kode OTP yang Anda terima.")
        context.user_data['next'] = 'handle_login_otp_input'
    except Exception as e:
        logger.error(f"Gagal request OTP KMSP: {e}")
        await context.bot.send_message(user_id, f"Gagal meminta OTP: {e}")

async def request_otp_and_prompt_hesda(update: Update, context: ContextTypes.DEFAULT_TYPE, phone: str):
    await context.bot.send_message(user_id, "Fitur login BYPAS (Hesda) belum diimplementasikan.")

async def handle_login_otp_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    otp_input = update.message.text.strip()
    phone = context.user_data.get('temp_phone_for_login')
    provider = context.user_data.get('current_login_provider')

    if not all([otp_input.isdigit(), phone, provider]):
        await update.message.reply_text("Sesi login tidak valid atau OTP bukan angka. Silakan mulai ulang.")
        return

    auth_id = user_data.get("registered_users",{}).get(str(user_id),{}).get('accounts',{}).get(phone, {}).get(provider, {}).get('auth_id')
    if not auth_id:
        await update.message.reply_text("Gagal menemukan Auth ID. Silakan coba minta OTP lagi.")
        return

    await context.bot.send_message(user_id, "Memverifikasi OTP...")
    try:
        if provider == 'kmsp':
            url = f"https://golang-openapi-login-xltembakservice.kmsp-store.com/v1?api_key={KMSP_API_KEY}&phone={phone}&method=OTP&auth_id={auth_id}&otp={otp_input}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            result = response.json()
            data_login = result.get('data')

            if not data_login or 'access_token' not in data_login:
                error_message_from_api = result.get("message", "OTP salah atau tidak valid.")
                raise ValueError(error_message_from_api)

            access_token = data_login['access_token']
            user_data["registered_users"][str(user_id)]['accounts'][phone]['kmsp']['access_token'] = access_token
            user_data["registered_users"][str(user_id)]['accounts'][phone]['kmsp']['login_timestamp'] = datetime.now().isoformat()
            simpan_data_ke_db()

            await context.bot.send_message(user_id, f"✅ *Login Berhasil!* Nomor *{phone}* telah terhubung.", parse_mode="Markdown")
            await main_handlers.send_main_menu(update, context)

    except requests.exceptions.ReadTimeout:
        logger.error(f"Gagal verifikasi OTP {provider} untuk {phone}: Read Timeout")
        user_friendly_message = "⚠️ Server provider sedang sibuk dan tidak merespon. Silakan coba lagi dalam beberapa saat."
        await context.bot.send_message(user_id, user_friendly_message)
        context.user_data['next'] = 'handle_login_otp_input'
    except Exception as e:
        logger.error(f"Gagal verifikasi OTP {provider} untuk {phone}: {e}")
        user_friendly_message = f"Gagal memverifikasi OTP.\n\nPesan: *{str(e)}*\n\nSilakan periksa kembali kode Anda dan coba lagi."
        await context.bot.send_message(user_id, user_friendly_message, parse_mode="Markdown")
        context.user_data['next'] = 'handle_login_otp_input'
# --- FUNGSI ALUR PEMBELIAN OTOMATIS ---
async def handle_automatic_purchase_phone_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    phone_raw = update.message.text.strip()
    phone = '62' + phone_raw[1:] if phone_raw.startswith('08') else phone_raw

    if not re.match(r'^628\d{9,12}$', phone):
        await update.message.reply_text("Format nomor HP salah. Gunakan `08xxxxxxxxxx`.", parse_mode="Markdown")
        context.user_data['next'] = 'handle_automatic_purchase_phone_input'
        return

    token_data = user_data.get("registered_users", {}).get(str(user_id), {}).get("accounts", {}).get(phone, {})
    access_token_kmsp = token_data.get("kmsp", {}).get("access_token")

    if not access_token_kmsp:
        await update.message.reply_text(f"Token LOGIN tidak ditemukan untuk nomor `{phone}`. Silakan login terlebih dahulu untuk nomor ini.")
        # Di sini kita tidak memanggil send_main_menu agar user bisa langsung klik tombol login jika ada
        return

    context.user_data['automatic_purchase_phone'] = phone
    context.user_data['automatic_purchase_token'] = access_token_kmsp
    
    if 'automatic_flow_state' in user_data.get("registered_users", {}).get(str(user_id), {}).get('accounts', {}).get(phone, {}):
        del user_data["registered_users"][str(user_id)]['accounts'][phone]['automatic_flow_state']
    simpan_data_ke_db()

    await context.bot.send_message(user_id, f"Memulai alur Otomatis untuk *{phone}*...", parse_mode="Markdown")
    asyncio.create_task(run_automatic_purchase_flow(update, context))

async def run_automatic_purchase_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ini adalah contoh placeholder. Anda harus menggantinya dengan logika lengkap dari skrip lama Anda.
    user_id = update.effective_user.id
    logger.info(f"Fungsi 'run_automatic_purchase_flow' untuk user {user_id} telah dipanggil.")
    await context.bot.send_message(user_id, "✅ Alur pembelian otomatis dimulai!\n(Logika pembelian detail belum diimplementasikan di file ini)")
    # Contoh alur yang seharusnya ada di sini:
    # 1. Panggil execute_automatic_xuts_purchase(...)
    # 2. Jika sukses, panggil execute_automatic_xc_purchase(...)
    # 3. Kirim hasil akhir ke user.

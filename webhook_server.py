# webhook_server.py

from flask import Flask, request, jsonify
import hashlib
import json
import requests
import sqlite3
import os
from datetime import datetime

# Mengambil konfigurasi dari file config.py
# Pastikan file config.py ada di folder yang sama
from config import DB_FILE, TRIPAY_PRIVATE_KEY_SANDBOX, BOT_TOKEN

app = Flask(__name__)

def send_telegram_message(chat_id, text):
    """Fungsi helper untuk mengirim pesan dari webhook ke user."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, json=payload, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Gagal mengirim pesan ke Telegram: {e}")

@app.route('/tripay-callback', methods=['POST'])
def tripay_callback():
    data = request.json
    signature_from_tripay = request.headers.get('X-Callback-Signature')

    # Verifikasi signature
    json_string = json.dumps(data)
    local_signature = hashlib.sha256((TRIPAY_PRIVATE_KEY_SANDBOX + json_string).encode()).hexdigest()

    if signature_from_tripay != local_signature:
        print(f"Signature tidak valid! Diterima: {signature_from_tripay}, Diharapkan: {local_signature}")
        return jsonify({'success': False, 'message': 'Invalid Signature'}), 403

    # Proses notifikasi jika signature valid
    merchant_ref = data.get('merchant_ref')
    status = data.get('status')

    print(f"Callback diterima untuk {merchant_ref} dengan status {status}")

    if status == 'PAID':
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute("SELECT user_id, amount, status FROM tripay_transactions WHERE merchant_ref = ?", (merchant_ref,))
            transaction = cursor.fetchone()

            if not transaction:
                print(f"Transaksi {merchant_ref} tidak ditemukan di DB.")
                return jsonify({'success': False, 'message': 'Transaction not found'})

            user_id, amount, db_status = transaction

            if db_status == 'PENDING':
                cursor.execute("UPDATE tripay_transactions SET status = 'SUCCESS' WHERE merchant_ref = ?", (merchant_ref,))
                cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_id))

                cursor.execute("SELECT transactions, balance FROM users WHERE id = ?", (user_id,))
                user_row = cursor.fetchone()
                current_transactions = json.loads(user_row[0] or '[]')
                new_balance = user_row[1]

                new_tx = {
                    "type": "Top Up (Tripay)", "amount": amount, 
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "Berhasil", "reference": merchant_ref,
                    "balance_after_tx": new_balance
                }
                current_transactions.append(new_tx)
                cursor.execute("UPDATE users SET transactions = ? WHERE id = ?", (json.dumps(current_transactions), user_id))

                conn.commit()
                print(f"Sukses: Saldo user {user_id} ditambah sebesar {amount}")

                pesan_sukses = f"✅ Top up Anda sebesar *Rp{amount:,}* telah berhasil dikonfirmasi!"
                send_telegram_message(user_id, pesan_sukses)
            else:
                print(f"Transaksi {merchant_ref} sudah diproses sebelumnya (status: {db_status}).")

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            if conn: conn.rollback()
            return jsonify({'success': False, 'message': 'Database error'}), 500
        finally:
            if conn: conn.close()

    return jsonify({'success': True})

if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        print(f"Error: File database '{DB_FILE}' tidak ditemukan. Jalankan bot.py terlebih dahulu.")
    else:
        print("Webhook server siap di port 5000...")
        app.run(host='0.0.0.0', port=5000)

# database.py

import sqlite3
import json
import logging
from config import DB_FILE

# Variabel global untuk data yang dimuat
user_data = {"registered_users": {}, "blocked_users": [], "custom_packages": {}}

def inisialisasi_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, first_name TEXT, username TEXT,
        balance INTEGER DEFAULT 0, accounts TEXT DEFAULT '{}',
        transactions TEXT DEFAULT '[]', selected_hesdapkg_ids TEXT DEFAULT '[]',
        selected_30h_pkg_ids TEXT DEFAULT '[]', is_admin INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0, phone_number TEXT
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS custom_packages (
        code TEXT PRIMARY KEY, name TEXT, price INTEGER, description TEXT,
        payment_methods TEXT, ewallet_fee INTEGER DEFAULT 0
    )''')
    cursor.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS blocked_users (user_id INTEGER PRIMARY KEY)')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tripay_transactions (
        merchant_ref TEXT PRIMARY KEY,
        user_id INTEGER,
        amount INTEGER,
        status TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()
    logging.info("Database SQLite berhasil diinisialisasi (dengan tabel Tripay).")

def simpan_data_ke_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for user_id_str, details in user_data["registered_users"].items():
        cursor.execute('''
        INSERT OR REPLACE INTO users (id, first_name, username, balance, accounts, transactions, selected_hesdapkg_ids, selected_30h_pkg_ids)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            int(user_id_str), details.get('first_name'), details.get('username'),
            details.get('balance', 0), json.dumps(details.get('accounts', {})),
            json.dumps(details.get('transactions', [])), json.dumps(details.get('selected_hesdapkg_ids', [])),
            json.dumps(details.get('selected_30h_pkg_ids', []))
        ))
    cursor.execute("DELETE FROM blocked_users")
    if user_data.get("blocked_users"):
        cursor.executemany("INSERT INTO blocked_users (user_id) VALUES (?)", [(uid,) for uid in user_data["blocked_users"]])
    conn.commit()
    conn.close()
    logging.info("Data berhasil disimpan ke SQLite.")

def muat_data_dari_db():
    global user_data
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, first_name, username, balance, accounts, transactions, selected_hesdapkg_ids, selected_30h_pkg_ids FROM users")
    for row in cursor.fetchall():
        user_id_str = str(row[0])
        user_data["registered_users"][user_id_str] = {
            "first_name": row[1], "username": row[2], "balance": row[3],
            "accounts": json.loads(row[4] or '{}'),
            "transactions": json.loads(row[5] or '[]'),
            "selected_hesdapkg_ids": json.loads(row[6] or '[]'),
            "selected_30h_pkg_ids": json.loads(row[7] or '[]')
        }
    cursor.execute("SELECT user_id FROM blocked_users")
    user_data["blocked_users"] = [row[0] for row in cursor.fetchall()]
    # Anda bisa menambahkan load data custom_packages di sini jika perlu
    conn.close()
    logging.info(f"Data dari SQLite berhasil dimuat. Total {len(user_data['registered_users'])} user.")

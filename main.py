import requests
import sqlite3
import os
from datetime import datetime

API_TOKEN = os.getenv("API_TOKEN", "")  # Pegamos do ambiente (seguro no Actions)

# Caminho do banco no repositório
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "historico.db")


def connect_db():
    """Connect to the SQLite database and ensure schema exists."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            codein TEXT,
            name TEXT,
            high REAL,
            low REAL,
            varBid REAL,
            pctChange REAL,
            bid REAL,
            ask REAL,
            timestamp INTEGER UNIQUE,
            create_date TEXT
        )
    """)
    conn.commit()
    return conn


def fetch_historical_data(code, days=30):
    """Fetch historical data for the last N days."""
    url = f"https://economia.awesomeapi.com.br/json/daily/{code}/{days}?token={API_TOKEN}"
    response = requests.get(url, timeout=10)
    return response.json() if response.status_code == 200 else []


def insert_quote(cursor, quote):
    """Insert a single quote if it doesn't exist."""
    cursor.execute("SELECT 1 FROM quotes WHERE timestamp = ?", (int(quote["timestamp"]),))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO quotes (code, codein, name, high, low, varBid, pctChange, bid, ask, timestamp, create_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            quote["code"],
            quote["codein"],
            quote["name"],
            float(quote["high"]),
            float(quote["low"]),
            float(quote["varBid"]),
            float(quote["pctChange"]),
            float(quote["bid"]),
            float(quote["ask"]),
            int(quote["timestamp"]),
            quote["create_date"]
        ))


def populate_historical_data():
    """Populate historical data for main currencies."""
    codes = {
        "USD-BRL": ("USD", "BRL", "Dólar Americano/Real Brasileiro"),
        "EUR-BRL": ("EUR", "BRL", "Euro/Real Brasileiro"),
        "GBP-BRL": ("GBP", "BRL", "Libra Esterlina/Real Brasileiro"),
        "JPY-BRL": ("JPY", "BRL", "Iene Japonês/Real Brasileiro"),
        "AUD-BRL": ("AUD", "BRL", "Dólar Australiano/Real Brasileiro"),
    }

    conn = connect_db()
    cursor = conn.cursor()

    for code, (c, c_in, name) in codes.items():
        hist_data = fetch_historical_data(code, days=30)
        for quote in hist_data:
            quote["code"] = c
            quote["codein"] = c_in
            quote["name"] = name
            quote["create_date"] = datetime.fromtimestamp(
                int(quote["timestamp"])
            ).strftime("%Y-%m-%d %H:%M:%S")
            insert_quote(cursor, quote)

    conn.commit()
    conn.close()


def fetch_current_rates():
    """Fetch current rates."""
    url = f"https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,GBP-BRL,JPY-BRL,AUD-BRL?token={API_TOKEN}"
    response = requests.get(url, timeout=10)
    return response.json() if response.status_code == 200 else {}


def update_current_rates():
    """Update database with latest quotes."""
    data = fetch_current_rates()
    if not data:
        return

    conn = connect_db()
    cursor = conn.cursor()

    for _, quote in data.items():
        if "code" in quote:
            quote["create_date"] = datetime.fromtimestamp(
                int(quote["timestamp"])
            ).strftime("%Y-%m-%d %H:%M:%S")
            insert_quote(cursor, quote)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    populate_historical_data()
    update_current_rates()
    print("✅ Atualização concluída com sucesso!")

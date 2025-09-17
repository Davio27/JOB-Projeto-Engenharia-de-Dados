import requests
import sqlite3
import os
import time
from datetime import datetime, timedelta

API_TOKEN = os.get(`API_TOKEN`)  # Option 1: Hardcode (less secure, use for testing)


# Definir o caminho para o banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'historico.db')

def connect_db():
    """Connect to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    return conn

def fetch_historical_data(code, days=30):
    """Fetch historical data for the last N days."""
    url = f"https://economia.awesomeapi.com.br/json/daily/{code}/{days}?token={API_TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching historical data for {code}: {response.status_code}")
        return []

def insert_quote(cursor, quote):
    """Insert a single quote into the database if it doesn't exist."""
    cursor.execute("""
        SELECT id FROM quotes WHERE timestamp = ?
    """, (int(quote['timestamp']),))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO quotes (code, codein, name, high, low, varBid, pctChange, bid, ask, timestamp, create_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            quote['code'],
            quote['codein'],
            quote['name'],
            float(quote['high']),
            float(quote['low']),
            float(quote['varBid']),
            float(quote['pctChange']),
            float(quote['bid']),
            float(quote['ask']),
            int(quote['timestamp']),
            quote['create_date']
        ))

def populate_historical_data():
    """Populate historical data for USD and EUR for the last 30 days."""
    codes = {
    'USD-BRL': ("USD", "BRL", "Dólar Americano/Real Brasileiro"),
    'EUR-BRL': ("EUR", "BRL", "Euro/Real Brasileiro"),
    'GBP-BRL': ("GBP", "BRL", "Libra Esterlina/Real Brasileiro"),
    'JPY-BRL': ("JPY", "BRL", "Iene Japonês/Real Brasileiro"),
    'AUD-BRL': ("AUD", "BRL", "Dólar Australiano/Real Brasileiro")
    }
    conn = connect_db()
    cursor = conn.cursor()
    
    for code, (c, c_in, name) in codes.items():
        hist_data = fetch_historical_data(code, days=30)
        for quote in hist_data:
            # Adiciona campos que faltam no histórico
            quote['code'] = c
            quote['codein'] = c_in
            quote['name'] = name
            quote['create_date'] = datetime.fromtimestamp(int(quote['timestamp'])).strftime("%Y-%m-%d %H:%M:%S")
            
            insert_quote(cursor, quote)
    
    conn.commit()
    conn.close()
    print("dados historicos populados com sucesso.")

def fetch_current_rates():
    """Fetch current rates from the API."""
    url = f"https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,GBP-BRL,JPY-BRL,AUD-BRL?token={API_TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching current rates: {response.status_code}")
        return {}

def update_current_rates():
    data = fetch_current_rates()
    if not data:
        return
    
    conn = connect_db()
    cursor = conn.cursor()
    
    for key, quote in data.items():
        # Garantia extra: só insere se tiver 'code'
        if "code" in quote:
            insert_quote(cursor, quote)
    
    conn.commit()
    conn.close()
    print("atualizacao realizada.")

if __name__ == '__main__':
    populate_historical_data()
    while True:
        update_current_rates()
        print("Aguardando 25 minutos para próxima atualização...")

        time.sleep(1500)  # 25 min

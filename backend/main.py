import requests
import sqlite3
import os
from datetime import datetime

API_TOKEN = os.getenv("API_TOKEN", "")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'historico.db')

def connect_db():
    return sqlite3.connect(DB_PATH)

def insert_quote(cursor, quote):
    cursor.execute("SELECT id FROM quotes WHERE timestamp = ?", (int(quote['timestamp']),))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO quotes (code, codein, name, high, low, varBid, pctChange, bid, ask, timestamp, create_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            quote['code'], quote['codein'], quote['name'],
            float(quote['high']), float(quote['low']), float(quote['varBid']),
            float(quote['pctChange']), float(quote['bid']), float(quote['ask']),
            int(quote['timestamp']), quote['create_date']
        ))

def update_current_rates():
    url = f"https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,GBP-BRL,JPY-BRL,AUD-BRL?token={API_TOKEN}"
    res = requests.get(url)
    if res.status_code != 200:
        print("Erro ao buscar taxas atuais")
        return

    data = res.json()
    conn = connect_db()
    cursor = conn.cursor()

    for key, quote in data.items():
        quote['create_date'] = datetime.fromtimestamp(int(quote['timestamp'])).strftime("%Y-%m-%d %H:%M:%S")
        insert_quote(cursor, quote)

    conn.commit()
    conn.close()
    print("Atualização realizada.")
    
def pegar_realtime(moeda='USD-BRL', quantidade=60):
    """
    Retorna os últimos 'quantidade' minutos da cotação da moeda selecionada.
    Retorna duas listas: labels (HH:MM) e bids (valor).
    """
    url = f"https://economia.awesomeapi.com.br/{moeda}/{quantidade}"
    res = requests.get(url)
    if res.status_code != 200:
        print(f"Erro ao buscar dados em tempo real da moeda {moeda}")
        return [], []

    data = res.json()
    labels = []
    bids = []
    for item in data:
        dt = datetime.fromtimestamp(int(item['timestamp']))
        labels.append(dt.strftime('%H:%M'))
        bids.append(float(item['bid']))
    return labels, bids

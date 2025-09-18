import requests
import sqlite3
from datetime import datetime, timedelta

# Conexão com o banco
conn = sqlite3.connect('historico.db')
cursor = conn.cursor()

# Criar tabela quotes se não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    codein TEXT NOT NULL,
    name TEXT NOT NULL,
    high REAL,
    low REAL,
    varBid REAL,
    pctChange REAL,
    bid REAL,
    ask REAL,
    timestamp INTEGER,
    create_date TEXT,
    UNIQUE(code, timestamp)
)
''')

# Função para pegar histórico da API
def pegar_historico(moeda='USD-BRL', dias=90):
    url = f"https://economia.awesomeapi.com.br/json/daily/{moeda}/{dias}"
    res = requests.get(url)
    if res.status_code != 200:
        print(f"Erro ao buscar histórico da moeda {moeda}")
        return []
    return res.json()

# Buscar histórico das moedas
historico_usd = pegar_historico('USD-BRL', 90)
historico_eur = pegar_historico('EUR-BRL', 90)
historico_gbp = pegar_historico('GBP-BRL', 90)

# Inserir dados no banco
for i in range(len(historico_usd)):
    date = datetime.fromtimestamp(int(historico_usd[i]['timestamp'])).strftime('%Y-%m-%d')
    
    for moeda, historico in [('USD', historico_usd), ('EUR', historico_eur), ('GBP', historico_gbp)]:
        bid = float(historico[i]['bid'])
        high = float(historico[i]['high'])
        low = float(historico[i]['low'])
        pctChange = float(historico[i]['pctChange'])
        varBid = high - low
        timestamp = int(historico[i]['timestamp'])
        create_date = date
        code = moeda
        codein = 'BRL'
        name = f"{moeda}/BRL"
        ask = bid  # se não tiver ask, repetir o bid

        print(f"Inserindo {code} - {create_date}")

        cursor.execute('''
        INSERT INTO quotes (code, codein, name, high, low, varBid, pctChange, bid, ask, timestamp, create_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(code, timestamp) DO UPDATE SET
            high=excluded.high,
            low=excluded.low,
            varBid=excluded.varBid,
            pctChange=excluded.pctChange,
            bid=excluded.bid,
            ask=excluded.ask,
            create_date=excluded.create_date
        ''', (code, codein, name, high, low, varBid, pctChange, bid, ask, timestamp, create_date))

# Salvar e fechar
conn.commit()
conn.close()

print("historico.db populado com sucesso com 90 dias de dados reais da API!")

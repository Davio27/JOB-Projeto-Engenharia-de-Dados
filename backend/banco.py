import sqlite3
import os

# Definir o caminho para o banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'historico.db')

# Conectar ao banco de dados
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Criar tabela para armazenar cotações
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
        create_date TEXT
    )
''')

# Salvar alterações
conn.commit()

# Fechar conexão
conn.close()

print("Banco 'historico.db' e tabela 'quotes' criados com sucesso!")
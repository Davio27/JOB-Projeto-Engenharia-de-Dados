from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from backend.main import update_current_rates, pegar_realtime
import sqlite3
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = 'your-secret-key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'historico.db')

users = {'admin': 'password123'}

def connect_db():
    return sqlite3.connect(DB_PATH)

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_current_rates, 'interval', minutes=25)
    scheduler.start()
def parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.strptime(s, "%Y-%m-%d")
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username in users and users[username] == password:
        session['username'] = username
        return redirect(url_for('dashboard'))
    return render_template('login.html', error='Usuário ou senha inválidos')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT bid, create_date FROM quotes WHERE code='USD' ORDER BY timestamp DESC LIMIT 1")
    usd_row = cursor.fetchone()
    usd_value = round(float(usd_row[0]), 3) if usd_row else 5.25
    usd_update = usd_row[1] if usd_row else datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    cursor.execute("SELECT bid FROM quotes WHERE code='EUR' ORDER BY timestamp DESC LIMIT 1")
    eur_row = cursor.fetchone()
    eur_value = round(float(eur_row[0]), 3) if eur_row else 5.68
    conn.close()
    return render_template('dashboard.html', usd_value=usd_value, eur_value=eur_value, last_update=usd_update)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/api/realtime-data-short')
def get_realtime_data():
    conn = connect_db()
    cursor = conn.cursor()

    # Função auxiliar para tratar datas com ou sem hora
    def parse_date(s):
        from datetime import datetime
        try:
            return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.strptime(s, "%Y-%m-%d")

    # Pega últimos 60 registros USD
    cursor.execute("""
        SELECT create_date, bid
        FROM quotes
        WHERE code='USD'
        ORDER BY timestamp DESC
        LIMIT 60
    """)
    usd_rows = cursor.fetchall()
    labels_usd = [parse_date(r[0]).strftime('%H:%M') for r in reversed(usd_rows)]
    bids_usd = [round(float(r[1]), 3) for r in reversed(usd_rows)]

    # Pega últimos 60 registros EUR
    cursor.execute("""
        SELECT create_date, bid
        FROM quotes
        WHERE code='EUR'
        ORDER BY timestamp DESC
        LIMIT 60
    """)
    eur_rows = cursor.fetchall()
    labels_eur = [parse_date(r[0]).strftime('%H:%M') for r in reversed(eur_rows)]
    bids_eur = [round(float(r[1]), 3) for r in reversed(eur_rows)]

    conn.close()

    # Retorna JSON para o frontend
    return jsonify({
        'labels': labels_usd,  # assumimos mesmos horários para USD e EUR
        'usd': bids_usd,
        'eur': bids_eur
    })

@app.route('/api/realtime-data')
def realtime_data():
    conn = connect_db()
    cursor = conn.cursor()

    # Pega os últimos 60 registros de USD
    cursor.execute("""
        SELECT bid, create_date 
        FROM quotes 
        WHERE code='USD'
        ORDER BY timestamp DESC
        LIMIT 60
    """)
    usd_rows = cursor.fetchall()
    labels_usd = [datetime.strptime(r[1], "%Y-%m-%d").strftime('%H:%M') for r in reversed(usd_rows)]
    bids_usd = [float(r[0]) for r in reversed(usd_rows)]

    # Pega os últimos 60 registros de EUR
    cursor.execute("""
        SELECT bid, create_date 
        FROM quotes 
        WHERE code='EUR'
        ORDER BY timestamp DESC
        LIMIT 60
    """)
    eur_rows = cursor.fetchall()
    labels_eur = [datetime.strptime(r[1], "%Y-%m-%d").strftime('%H:%M') for r in reversed(eur_rows)]
    bids_eur = [float(r[0]) for r in reversed(eur_rows)]

    conn.close()

    # Retorna JSON para o frontend
    return jsonify({
        'labels': labels_usd,  # assume mesmo horário para USD e EUR
        'usd': bids_usd,
        'eur': bids_eur
    })
@app.route('/api/currency-data')
def currency_data():
    conn = connect_db()
    cursor = conn.cursor()

    # Pega os últimos 30 dias de cada moeda
    cursor.execute("""
        SELECT code, bid, create_date 
        FROM quotes 
        WHERE code IN ('USD','EUR','GBP')
        AND DATE(create_date) >= DATE('now','-30 days')
        ORDER BY create_date ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    # Organizar dados por moeda
    usd = [float(r[1]) for r in rows if r[0]=='USD']
    eur = [float(r[1]) for r in rows if r[0]=='EUR']
    gbp = [float(r[1]) for r in rows if r[0]=='GBP']
    labels30 = [parse_date(r[2]).strftime("%d/%m") for r in rows if r[0]=='USD']
    # Variação % últimos 15 dias para USD
    variation15 = []
    for i in range(1, min(16, len(usd))):
        delta = ((usd[-i] - usd[-i-1]) / usd[-i-1]) * 100
        variation15.append(round(delta, 2))
    variation15 = variation15[::-1]  # inverter para ficar cronológico

    # Últimos 10 dias
    labels10 = labels30[-10:]
    usd10 = usd[-10:]
    eur10 = eur[-10:]
    gbp10 = gbp[-10:]
    brl10 = [1]*len(usd10)

    return jsonify({
        "labels30": labels30,
        "usd30": usd,
        "eur30": eur,
        "gbp30": gbp,
        "labels15": labels30[-15:],
        "variation15": variation15,
        "labels10": labels10,
        "usd10": usd10,
        "eur10": eur10,
        "gbp10": gbp10,
        "brl10": brl10
    })

if __name__ == '__main__':
    start_scheduler()


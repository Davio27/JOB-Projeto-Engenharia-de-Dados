from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random
from apscheduler.schedulers.background import BackgroundScheduler
from backend.main import update_current_rates
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure key in production

# Definir o caminho para o banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'historico.db')

# Mock user for demonstration (replace with proper database in production)
users = {
    'admin': 'password123'
}

def connect_db():
    """Connect to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    return conn

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_current_rates, 'interval', minutes=25)
    scheduler.start()
    
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
    else:
        return render_template('login.html', error='Invalid username or password')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Get latest USD value and last update
    cursor.execute("""
        SELECT bid, create_date FROM quotes 
        WHERE code = 'USD' ORDER BY timestamp DESC LIMIT 1
    """)
    usd_row = cursor.fetchone()
    usd_value = round(float(usd_row[0]), 3) if usd_row else 5.25
    usd_update = usd_row[1] if usd_row else datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    # Get latest EUR value
    cursor.execute("""
        SELECT bid FROM quotes 
        WHERE code = 'EUR' ORDER BY timestamp DESC LIMIT 1
    """)
    eur_row = cursor.fetchone()
    eur_value = round(float(eur_row[0]), 3) if eur_row else 5.68
    
    conn.close()
    
    # Simulate slight variation for demo (optional, remove in production)
    usd_value += (random.random() - 0.5) * 0.001
    eur_value += (random.random() - 0.5) * 0.001
    
    return render_template('dashboard.html', 
                        usd_value=usd_value,
                        eur_value=eur_value,
                        last_update=usd_update)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/api/currency-data')
def get_currency_data():
    conn = connect_db()
    cursor = conn.cursor()
    
    # 30 days USD
    cursor.execute("""
        SELECT strftime('%d/%m', create_date) as label, bid, pctChange 
        FROM quotes WHERE code = 'USD' ORDER BY timestamp DESC LIMIT 30
    """)
    usd30_rows = cursor.fetchall()
    labels30 = [row[0] for row in reversed(usd30_rows)]
    usd30 = [round(float(row[1]), 3) for row in reversed(usd30_rows)]
    
    # 30 days EUR
    cursor.execute("""
        SELECT bid FROM quotes WHERE code = 'EUR' ORDER BY timestamp DESC LIMIT 30
    """)
    eur30_rows = cursor.fetchall()
    eur30 = [round(float(row[0]), 3) for row in reversed(eur30_rows)]
    
    # 15 days variation (pctChange for USD)
    cursor.execute("""
        SELECT strftime('%d/%m', create_date) as label, pctChange 
        FROM quotes WHERE code = 'USD' ORDER BY timestamp DESC LIMIT 15
    """)
    var15_rows = cursor.fetchall()
    labels15 = [row[0] for row in reversed(var15_rows)]
    variation15 = [round(float(row[1]), 2) for row in reversed(var15_rows)]
    
    # 10 days USD
    cursor.execute("""
        SELECT bid FROM quotes WHERE code = 'USD' ORDER BY timestamp DESC LIMIT 10
    """)
    usd10_rows = cursor.fetchall()
    usd10 = [round(float(row[0]), 3) for row in reversed(usd10_rows)]
    
    # 30 dias GBP
    cursor.execute("SELECT bid FROM quotes WHERE code = 'GBP' ORDER BY timestamp DESC LIMIT 30")
    gbp30_rows = cursor.fetchall()
    gbp30 = [round(float(row[0]),3) for row in reversed(gbp30_rows)]

    # 10 dias GBP
    cursor.execute("SELECT bid FROM quotes WHERE code = 'GBP' ORDER BY timestamp DESC LIMIT 10")
    gbp10_rows = cursor.fetchall()
    gbp10 = [round(float(row[0]),3) for row in reversed(gbp10_rows)]
    
    # 10 days EUR
    cursor.execute("""
        SELECT bid FROM quotes WHERE code = 'EUR' ORDER BY timestamp DESC LIMIT 10
    """)
    eur10_rows = cursor.fetchall()
    eur10 = [round(float(row[0]), 3) for row in reversed(eur10_rows)]
    
    # BRL as base (static 1.0)
    brl10 = [1.00 for _ in range(10)]
    labels10 = [f"{i+1:02d}/09" for i in range(10)]  # Simplified, adjust based on actual dates if needed
    
    conn.close()
    
    return jsonify({
        'labels30': labels30,
        'usd30': usd30,
        'eur30': eur30,
        'labels15': labels15,
        'variation15': variation15,
        'labels10': labels10,
        'usd10': usd10,
        'eur10': eur10,
        'gbp30': gbp30,
        'gbp10': gbp10,
        'brl10': brl10
    })

if __name__ == '__main__':
    start_scheduler()
    app.run(debug=True)
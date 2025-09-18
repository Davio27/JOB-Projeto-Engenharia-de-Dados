# Projeto de Engenharia de Dados: Monitoramento de Câmbio (USD, EUR, GBP, JPY, AUD)

Este projeto é um pipeline de engenharia de dados completo para captura, armazenamento e visualização de taxas de câmbio de moedas em relação ao Real Brasileiro (BRL). Ele combina coleta de dados via API, armazenamento em banco SQLite, atualização automática com GitHub Actions e visualização em tempo real em um dashboard web construído com Flask e Chart.js.

---

## 🚀 Objetivos do Projeto

- Capturar dados históricos e em tempo real de moedas: USD, EUR, GBP, JPY e AUD.
- Armazenar as informações em um banco de dados **SQLite (`historico.db`)**.
- Atualizar continuamente os dados utilizando **GitHub Actions**.
- Disponibilizar visualizações interativas e modernas em um **dashboard web** com Flask + Chart.js.
- Permitir monitoramento de variações percentuais, tendências de curto e médio prazo e comparativos entre moedas.

---

## 🛠 Estrutura do Pipeline

1. **Coleta de Dados (ETL)**
   - O script `populate.py` busca:
     - **Histórico dos últimos 10 dias** de cada moeda.
     - **Cotação atual** em tempo real.
   - API utilizada: [AwesomeAPI](https://docs.awesomeapi.com.br/api-de-moedas)
   - Cada registro inclui:
     - Código da moeda (`USD`, `EUR`, etc.)
     - Código de conversão (`BRL`)
     - Nome da moeda
     - Máxima e mínima do dia (`high` / `low`)
     - Valor de abertura e fechamento (`bid` / `ask`)
     - Variação percentual (`pctChange`)
     - Variação de preço (`varBid`)
     - Timestamp
     - Data formatada (`create_date`)

2. **Banco de Dados**
   - SQLite (`historico.db`) localizado em `backend/`.
   - Tabela `quotes` criada automaticamente com o seguinte schema:
     ```sql
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
     ```
   - O script garante **inserção incremental**, evitando duplicação e atualizando os dados existentes.

3. **Atualização Automática**
   - O job `update_current_rates()` atualiza as cotações atuais periodicamente.
   - Pode ser agendado para execução contínua via **GitHub Actions**:
     - Busca dados atuais.
     - Atualiza a tabela `quotes` automaticamente.
     - Mantém o histórico atualizado.

4. **Dashboard Web**
   - Desenvolvido com **Flask**.
   - Frontend com **Chart.js** para visualização de:
     - Histórico dos últimos 30 dias (USD, EUR, GBP)
     - Comparativo USD x EUR
     - Resumo de 10 dias
     - Gráfico em tempo real (últimos 60 minutos)
     - Variação percentual dos últimos 15 dias
   - Recursos adicionais:
     - Tema claro / escuro
     - Cards de valor e variação em tempo real

---

## 📁 Estrutura de Pastas

````

projeto\_api/
│
├── backend/
│   ├── historico.db         # Banco de dados SQLite
│   ├── main.py              # Funções de ETL e atualização de dados
│   └── populate.py          # Script para popular histórico
│
├── templates/
│   ├── login.html
│   └── dashboard.html
│
├── static/
│   ├── script.js            # Script para gráficos e frontend
│
├── app.py                   # Aplicação Flask
└── README.md

````

---

## ⚙️ Instalação e Uso

1. **Clonar o repositório**
```bash
git clone <repo-url>
cd projeto_api
````

2. **Criar ambiente virtual e instalar dependências**

```bash
python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. **Configurar token da API**

```bash
export API_TOKEN="SEU_TOKEN_AQUI"  # Linux / macOS
set API_TOKEN=SEU_TOKEN_AQUI       # Windows
```

4. **Rodar aplicação**

```bash
python app.py
```

* Acesse o dashboard em `http://127.0.0.1:5000`.
* Login: `admin` / `password123`.

---

## ⚡ GitHub Actions

Um workflow pode ser configurado para rodar o script automaticamente, garantindo que o `historico.db` esteja sempre atualizado:

```yaml
name: Atualizar Cotações

on:
  schedule:
    - cron: "0 * * * *"  # A cada hora
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Configurar Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Instalar dependências
        run: pip install requests
      - name: Executar atualização
        run: python backend/populate.py
        env:
          API_TOKEN: ${{ secrets.API_TOKEN }}
      - name: Commit database atualizado
        run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add backend/historico.db
          git commit -m "Atualização automática do histórico"
          git push
```

---

## 💡 Observações

* O banco **SQLite** foi escolhido por simplicidade e facilidade de versionamento junto ao Git.
* O dashboard suporta **gráficos modernos e responsivos** via Chart.js.
* Todos os dados são armazenados com timestamp, garantindo histórico consistente.
* Atualizações contínuas via GitHub Actions permitem histórico sempre atualizado sem intervenção manual.

---

## 🛠 Tecnologias Utilizadas

* **Python 3.12**
* **Flask** (Web Framework)
* **SQLite** (Banco de Dados)
* **Requests** (API)
* **Chart.js** (Visualização)
* **GitHub Actions** (Automação)

---

## 📈 Próximos Passos

* Adicionar alertas de variação significativa de moedas.
* Implementar autenticação mais robusta no dashboard.
* Migrar banco para PostgreSQL para suportar volumes maiores de dados.
* Melhorar a estética dos gráficos com temas interativos.

---

✅ Projeto completo de **engenharia de dados** com coleta, transformação, armazenamento e visualização de cotações.

```


Quer que eu faça isso?
```

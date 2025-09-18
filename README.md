# 💱 Projeto de Monitoramento de Câmbio (USD, EUR, GBP, JPY, AUD)

![Python](https://img.shields.io/badge/python-3.12-blue)
![Flask](https://img.shields.io/badge/flask-2.3-green)
![SQLite](https://img.shields.io/badge/sqlite-3.41-orange)
![GitHub Actions](https://img.shields.io/badge/github--actions-automated-purple)

Pipeline de **engenharia de dados** para coleta, armazenamento e visualização de taxas de câmbio em relação ao Real Brasileiro (BRL), com dashboard web em tempo real.

---

## 🔹 Funcionalidades

- Captura de **dados históricos (10 dias)** e **atualizações em tempo real** via [AwesomeAPI](https://docs.awesomeapi.com.br/api-de-moedas)
- Armazenamento em **SQLite (`historico.db`)** com prevenção de duplicação
- Dashboard interativo com **Chart.js**:
  - Histórico de 30 dias
  - Comparativo USD x EUR
  - Resumo de 10 dias
  - Gráfico em tempo real
  - Variação percentual dos últimos 15 dias
- **Tema claro / escuro** e cards de valor atual

---

## 📊 Visual do Dashboard

**Histórico USD/BRL e EUR/BRL**  

![Histórico 30 dias](docs/hitorico30.png)

**Comparativo de moedas**  

![Comparativo](docs/Captura de tela 2025-09-17 221656.png)

**Resumo de 10 dias**  

![Resumo 10 dias](docs/Captura de tela 2025-09-17 221715.png)

**Variação percentual 15 dias**  

![Variação 15 dias](docs/Captura de tela 2025-09-17 221706.png)

> Obs: você pode gerar GIFs mostrando os gráficos em tempo real para colocar aqui também.

---

## ⚙️ Tecnologias

- Python 3.12
- Flask
- SQLite
- Chart.js
- Requests
- GitHub Actions para automação

---

## 📁 Estrutura do Projeto

```

projeto\_api/
├── backend/
│   ├── historico.db
│   ├── main.py
│   ├── count.py
│   └── databases.py
├── templates/
│   ├── login.html
│   └── dashboard.html
├── static/
│   └── script.js
│   └── styles.css
├── app.py
└── README.md

````

---

## 🚀 Instalação e Execução

```bash
git clone <repo-url>
cd projeto_api

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/macOS

pip install -r requirements.txt

# Configurar token da API
set API_TOKEN=SEU_TOKEN     # Windows
export API_TOKEN=SEU_TOKEN  # Linux/macOS

# Rodar dashboard
python app.py
````

Acesse o dashboard em [http://127.0.0.1:5000](http://127.0.0.1:5000)
Login: `admin` / `password123`

---

## ⚡ Automação com GitHub Actions

O workflow garante que o banco `historico.db` esteja sempre atualizado:

```yaml
name: Update Quotes DB

permissions:
  contents: write  # permite push no repositório

on:
  schedule:
    - cron: "*/1 * * * *"  # a cada 30 minutos
  workflow_dispatch:        # também pode rodar manualmente

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install requests

      - name: Run update script
        env:
          API_TOKEN: ${{ secrets.API_TOKEN }}
        run: python scheduler.py

      - name: Commit and push updated DB
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add backend/historico.db
          git commit -m "Update historico.db [skip ci]" || echo "No changes to commit"
          git push https://x-access-token:${GITHUB_TOKEN}@github.com/${{ github.repository }}.git HEAD:${{ github.ref }}
```

---

## 📊 Pipeline de Dados

1. **ETL (populate.py / main.py)**: coleta histórico e cotações em tempo real.
2. **Banco SQLite**: armazena dados estruturados, previne duplicação e mantém timestamps.
3. **Atualização automática**: via GitHub Actions ou agendamento local.
4. **Dashboard web**: gráficos interativos, tema escuro/claro, cards de valor e variação.

---

## 🌟 Próximos Passos

* Alertas de variação significativa de moedas
* Migração para PostgreSQL para maior escalabilidade
* Gráficos interativos avançados e análise preditiva

---

✅ Projeto completo de **engenharia de dados**: coleta, transformação, armazenamento e visualização de cotações em tempo real.

```


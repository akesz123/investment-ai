# AI Investment Assistant

This project implements an AI-powered investment assistant that scans US stocks and ETFs, ranks opportunities, and provides probability-based investment research. It is built with FastAPI, Streamlit, SQLAlchemy, and a modern ML stack.

## Features

- Daily market scanner across major indices and ETFs
- Technical indicators (RSI, MACD, EMAs, Bollinger Bands, and more)
- Fundamental metrics, analyst ratings, and macro snapshot storage
- Explainable AI score (0–100) with per-ticker explanations
- 30-day positive-return probability and expected return range (ML models)
- Portfolio tracking with positions, performance, risk, and diversification
- Backtesting utilities against SPY/QQQ/S&P 500
- Dark-themed Streamlit dashboard: Overview, Top Stocks, Top ETFs (more pages coming)

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/akesz123/investment-ai.git
cd investment-ai
```

### 2. Create environment file

Copy the example environment file and adjust values as needed:

```bash
cp .env.example .env
```

You can keep the default SQLite database for local development. To use PostgreSQL, set `DATABASE_URL` accordingly in `.env`.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run with Docker Compose (recommended)

```bash
docker compose up --build
```

This starts:

- FastAPI backend at http://localhost:8000
- Streamlit frontend at http://localhost:8501

### 5. First steps in the UI

1. Open the Streamlit app in your browser.
2. Go to the **Overview** page and check backend health.
3. Click **Run market scan** to load initial ETFs and assets.
4. Explore **Top Stocks** and **Top ETFs** pages (AI scores will be populated as the ML pipeline is implemented).

## Development

- Backend entrypoint: `backend/api/main.py`
- API routes: `backend/api/routes.py`
- Database models: `backend/database/models.py`
- Configuration: `backend/config/settings.py`
- Frontend app: `frontend/app.py`

Run tests locally with:

```bash
pytest -q
```

## Roadmap

The following features are being implemented next:

- Full technical indicator computation and storage
- Fundamental, analyst rating, and macro data ingestion from multiple free APIs
- Machine learning models (Random Forest, Gradient Boosting, XGBoost, LightGBM) with model selection
- Portfolio analytics, backtesting, and export (CSV, Excel, JSON, PDF)
- Additional Streamlit pages (Portfolio, Market News, AI Analysis, Backtesting, Settings)

Contributions and issues are welcome.

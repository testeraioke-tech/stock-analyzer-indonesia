# 📈 Stock Analyzer Indonesia

Tools analisa saham Indonesia super lengkap dengan Technical Analysis, Fundamental Analysis, News Sentiment, Geopolitical Analysis, dan Scalping Tools.

## 🚀 Live Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## ✨ Features

- 📊 **Quote & Chart** - Real-time quotes & interactive charts
- 📈 **Technical Analysis** - RSI, MACD, Bollinger, Support/Resistance
- 💰 **Fundamental Analysis** - Financial statements, scoring, recommendations
- 📰 **News & Sentiment** - Stock news with sentiment analysis
- 🌍 **Geopolitical Analysis** - Global markets, commodities, currencies
- ⚡ **Scalping Tools** - Short-term trading indicators & signals

## 🛠️ Installation

```bash
# Clone repository
git clone https://github.com/yourusername/stock-analyzer-indonesia.git
cd stock-analyzer-indonesia

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py
```

## 📦 Dependencies

- Python 3.8+
- Streamlit
- yfinance
- plotly
- pandas
- ta (Technical Analysis)
- textblob (Sentiment Analysis)

## 🌐 Deploy to Streamlit Cloud

1. Push to GitHub
2. Go to https://share.streamlit.io
3. Sign in with GitHub
4. Click "New app"
5. Select repository and `app.py`
6. Click "Deploy"

## 📁 Project Structure

```
├── app.py                 # Main Streamlit app
├── cli.py                 # CLI interface
├── config.py              # Configuration
├── data_fetcher.py        # Data fetching module
├── technical_analysis.py  # Technical analysis
├── fundamental_analysis.py # Fundamental analysis
├── news_fetcher.py        # News & sentiment
├── geopolitical.py        # Geopolitical analysis
├── scalping.py            # Scalping tools
├── requirements.txt       # Dependencies
└── .streamlit/
    └── config.toml        # Streamlit config
```

## ⚠️ Disclaimer

Tool ini untuk edukasi. Selalu lakukan riset sendiri sebelum investasi.

## 📄 License

MIT License

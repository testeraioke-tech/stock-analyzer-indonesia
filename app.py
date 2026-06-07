import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_fetcher import StockDataFetcher
from technical_analysis import TechnicalAnalyzer
from fundamental_analysis import FundamentalAnalyzer
from news_fetcher import NewsFetcher
from geopolitical import GeopoliticalAnalyzer
from scalping import ScalpingAnalyzer
from config import IDX_STOCKS

st.set_page_config(
    page_title="StockVerse - Analisa Saham Indonesia",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PASSWORD PROTECTION ---
def check_password():
    def password_entered():
        if st.session_state.get("password_input") == st.secrets.get("password", "Masuk1234_"):
            st.session_state["authenticated"] = True
        else:
            st.session_state["authenticated"] = False

    if "authenticated" not in st.session_state:
        st.markdown("""
        <style>
        .login-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem;
            border-radius: 20px;
            text-align: center;
            margin-top: 5rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .login-title {
            color: white;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .login-subtitle {
            color: rgba(255,255,255,0.8);
            font-size: 1.1rem;
        }
        </style>
        <div class="login-container">
            <div style="font-size: 4rem;">🚀</div>
            <div class="login-title">StockVerse</div>
            <div class="login-subtitle">Analisa Saham Indonesia - Masuk untuk melanjutkan</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.text_input("🔑 Password", type="password", on_change=password_entered, key="password_input")
        return False
    elif not st.session_state["authenticated"]:
        st.error("❌ Password salah!")
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.text_input("🔑 Password", type="password", on_change=password_entered, key="password_input")
        return False
    else:
        return True

if not check_password():
    st.stop()

# --- MODERN CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Main Background */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    border-right: 1px solid rgba(255,255,255,0.1);
}

section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] label {
    color: #ffffff !important;
}

/* Sidebar Selectbox */
section[data-testid="stSidebar"] [data-baseweb="select"] {
    background-color: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.2) !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] span {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] [data-baseweb="input"] {
    background-color: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.2) !important;
}

section[data-testid="stSidebar"] [data-baseweb="input"] input {
    color: #ffffff !important;
}

/* Header */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3rem;
    font-weight: 800;
    text-align: center;
    padding: 1rem;
    letter-spacing: -1px;
}

.sub-header {
    color: #a0a0a0;
    text-align: center;
    font-size: 1rem;
    margin-top: -1rem;
    margin-bottom: 2rem;
}

/* Cards */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.2rem;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

div[data-testid="stMetric"]:hover {
    border-color: #667eea;
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
}

div[data-testid="stMetric"] label {
    color: #a0a0a0 !important;
    font-weight: 500 !important;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 5px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 10px 20px;
    color: #a0a0a0 !important;
    font-weight: 500;
    transition: all 0.3s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
}

/* Select Boxes */
div[data-baseweb="select"] {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}

div[data-baseweb="select"] span {
    color: #ffffff !important;
}

/* Expander */
streamlit-expanderHeader {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
}

/* Info/Success/Warning Boxes */
.stAlert {
    border-radius: 12px !important;
    backdrop-filter: blur(10px) !important;
}

/* Text Colors */
h1, h2, h3, h4, h5, h6, p, span, label {
    color: #ffffff !important;
}

/* Section Headers */
.section-header {
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid rgba(102, 126, 234, 0.5);
}

/* Glass Card */
.glass-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 1.5rem;
    backdrop-filter: blur(10px);
    margin-bottom: 1rem;
}

/* Signal Cards */
.signal-buy {
    background: linear-gradient(135deg, rgba(0, 255, 136, 0.2) 0%, rgba(0, 200, 100, 0.1) 100%);
    border: 1px solid rgba(0, 255, 136, 0.3);
    border-radius: 12px;
    padding: 1rem;
}

.signal-sell {
    background: linear-gradient(135deg, rgba(255, 71, 87, 0.2) 0%, rgba(200, 50, 70, 0.1) 100%);
    border: 1px solid rgba(255, 71, 87, 0.3);
    border-radius: 12px;
    padding: 1rem;
}

/* Trend Indicator */
.trend-bullish {
    color: #00ff88 !important;
    font-weight: 800;
    text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
}

.trend-bearish {
    color: #ff4757 !important;
    font-weight: 800;
    text-shadow: 0 0 20px rgba(255, 71, 87, 0.5);
}

.trend-neutral {
    color: #ffa502 !important;
    font-weight: 800;
    text-shadow: 0 0 20px rgba(255, 165, 2, 0.5);
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255,255,255,0.05);
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 4px;
}

/* Dataframe */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="main-header">🚀 StockVerse</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analisa Saham Indonesia - Real-time, Technical, Fundamental & Scalping</div>', unsafe_allow_html=True)

# --- STOCK SELECTOR (MAIN AREA) ---
stock_list = list(IDX_STOCKS.keys())

col_search, col_select = st.columns([1, 3])

with col_search:
    search_query = st.text_input("🔍 Cari Saham", placeholder="Ketik nama/simbol...", key="main_search")

if search_query:
    filtered = [s for s in stock_list if search_query.upper() in s or search_query.upper() in IDX_STOCKS.get(s, '').upper()]
    options = filtered if filtered else stock_list[:20]
    if not filtered:
        st.warning("Saham tidak ditemukan, menampilkan daftar populer")
    selected_stock = st.selectbox("📋 Pilih Saham", options, format_func=lambda x: f"{x} - {IDX_STOCKS.get(x, '')}", key="main_stock_select")
else:
    selected_stock = st.selectbox("📋 Pilih Saham", stock_list, format_func=lambda x: f"{x} - {IDX_STOCKS.get(x, '')}", key="main_stock_select")

st.markdown("---")

# --- RESOURCES ---
@st.cache_resource
def get_fetcher():
    return StockDataFetcher()

@st.cache_resource
def get_news_fetcher():
    return NewsFetcher()

@st.cache_resource
def get_geopolitical_analyzer():
    return GeopoliticalAnalyzer()

fetcher = get_fetcher()
news_fetcher = get_news_fetcher()
geo_analyzer = get_geopolitical_analyzer()

# --- SIDEBAR (INFO SAJA) ---
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <div style="font-size: 3rem;">📊</div>
        <h2 style="color: white; margin: 0;">StockVerse</h2>
        <p style="color: #a0a0a0;">v2.0 - Super Lengkap</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.info("📋 Pilih saham di bagian atas halaman utama")
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.8rem;">
        Made with ❤️ for Indonesian Investors
    </div>
    """, unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏠 Beranda",
    "📈 Teknikal",
    "💰 Fundamental",
    "📰 Berita",
    "🌍 Global",
    "⚡ Scalping",
    "🔍 Full Analisa"
])

# --- TAB 1: BERANDA ---
with tab1:
    st.markdown(f'<div class="section-header">📊 {IDX_STOCKS.get(selected_stock, selected_stock)} ({selected_stock})</div>', unsafe_allow_html=True)
    
    try:
        with st.spinner(f"Memuat data {selected_stock}..."):
            quote = fetcher.get_realtime_quote(selected_stock)
            df = fetcher.get_stock_data(selected_stock, '6mo')
        
        if quote:
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.metric("💰 Harga", f"Rp {quote['price']:,.0f}", f"{quote['change']:+,.0f} ({quote['change_percent']:+.2f}%)")
            with col_b:
                st.metric("📦 Volume", f"{quote['volume']:,}")
            with col_c:
                st.metric("🏦 Market Cap", f"Rp {quote['market_cap']/1e9:,.0f}B" if quote['market_cap'] else "N/A")
            with col_d:
                st.metric("📊 PE Ratio", f"{quote['pe_ratio']:.1f}" if quote['pe_ratio'] else "N/A")
            
            if not df.empty:
                analyzer = TechnicalAnalyzer(df)
                fig = analyzer.create_candlestick_chart(last_n_days=60)
                st.plotly_chart(fig, width='stretch', key="chart_beranda")
            else:
                st.warning("⚠️ Data chart tidak tersedia")
        else:
            st.error(f"❌ Tidak dapat mengambil data untuk {selected_stock}")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# --- TAB 2: TEKNIKAL ---
with tab2:
    st.markdown('<div class="section-header">📈 Analisa Teknikal</div>', unsafe_allow_html=True)
    
    period = st.selectbox("📅 Periode", ['1mo', '3mo', '6mo', '1y', '2y', '5y'], index=2, key="tech_period")
    
    if selected_stock:
        with st.spinner(f"Menganalisa {selected_stock}..."):
            df = fetcher.get_stock_data(selected_stock, period)
        
        if not df.empty:
            analyzer = TechnicalAnalyzer(df)
            summary = analyzer.get_summary()
            
            # Trend
            trend = summary['trend']
            trend_class = 'trend-bullish' if trend['overall'] == 'BULLISH' else 'trend-bearish' if trend['overall'] == 'BEARISH' else 'trend-neutral'
            trend_icon = "🟢" if trend['overall'] == 'BULLISH' else "🔴" if trend['overall'] == 'BEARISH' else "🟡"
            
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 3rem;">{trend_icon}</div>
                <div class="{trend_class}" style="font-size: 2rem;">{trend['overall']}</div>
                <div style="color: #a0a0a0;">Bullish: {trend['bullish_count']} | Bearish: {trend['bearish_count']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = analyzer.create_candlestick_chart(last_n_days=90)
                st.plotly_chart(fig, width='stretch', key="chart_teknikal")
            
            with col2:
                st.markdown('<div class="section-header">🎯 Indikator</div>', unsafe_allow_html=True)
                
                indicators = [
                    ("RSI (14)", summary['rsi'], 30, 70),
                    ("MACD", summary['macd'], None, None),
                    ("Volatility", summary['volatility'], None, None),
                ]
                
                for name, value, low, high in indicators:
                    if value:
                        if low and high:
                            status = "🟢 Oversold" if value < low else "🔴 Overbought" if value > high else "⚪ Normal"
                        else:
                            status = ""
                        st.markdown(f"""
                        <div class="glass-card">
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: #a0a0a0;">{name}</span>
                                <span style="color: #fff; font-weight: 600;">{value:.2f}</span>
                            </div>
                            <div style="color: #666; font-size: 0.85rem;">{status}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown('<div class="section-header">🎯 Signals</div>', unsafe_allow_html=True)
                
                for sig in summary['signals'][:5]:
                    if sig['type'] == 'BUY':
                        st.markdown(f"""
                        <div class="signal-buy">
                            <div style="color: #00ff88; font-weight: 700;">🟢 {sig['type']}</div>
                            <div style="color: #ccc;">{sig['indicator']} ({sig['strength']})</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="signal-sell">
                            <div style="color: #ff4757; font-weight: 700;">🔴 {sig['type']}</div>
                            <div style="color: #ccc;">{sig['indicator']} ({sig['strength']})</div>
                        </div>
                        """, unsafe_allow_html=True)

# --- TAB 3: FUNDAMENTAL ---
with tab3:
    st.markdown('<div class="section-header">💰 Analisa Fundamental</div>', unsafe_allow_html=True)
    
    if selected_stock:
        with st.spinner(f"Mengambil data fundamental {selected_stock}..."):
            company = fetcher.get_company_info(selected_stock)
            financials = fetcher.get_financial_statements(selected_stock)
            metrics = fetcher.get_key_metrics(selected_stock)
        
        if company and metrics:
            st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="font-size: 3rem;">🏢</div>
                    <div>
                        <h2 style="margin: 0; color: #fff;">{company['name']}</h2>
                        <p style="margin: 0; color: #a0a0a0;">{company['sector']} | {company['industry']}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="section-header">📊 Key Metrics</div>', unsafe_allow_html=True)
                key_display = ['Trailing PE', 'Price to Book', 'ROE', 'ROA', 'Dividend Yield', 'Profit Margin', 'Revenue', 'Market Cap']
                for k in key_display:
                    if k in metrics and metrics[k] != 'N/A':
                        st.markdown(f"""
                        <div class="glass-card" style="display: flex; justify-content: space-between; padding: 0.8rem 1.2rem;">
                            <span style="color: #a0a0a0;">{k}</span>
                            <span style="color: #fff; font-weight: 600;">{metrics[k]}</span>
                        </div>
                        """, unsafe_allow_html=True)
            
            with col2:
                if financials:
                    fund_analyzer = FundamentalAnalyzer(financials, metrics, company)
                    scores = fund_analyzer.get_overall_score()
                    rec = fund_analyzer.get_investment_recommendation()
                    
                    rec_color = "#00ff88" if "BUY" in rec['recommendation'] else "#ff4757" if "SELL" in rec['recommendation'] else "#ffa502"
                    rec_icon = "🟢" if "BUY" in rec['recommendation'] else "🔴" if "SELL" in rec['recommendation'] else "🟡"
                    
                    st.markdown(f"""
                    <div class="glass-card" style="text-align: center;">
                        <div style="font-size: 3rem;">{rec_icon}</div>
                        <div style="color: {rec_color}; font-size: 1.8rem; font-weight: 800;">{rec['recommendation']}</div>
                        <div style="color: #a0a0a0;">Confidence: {rec['confidence']}</div>
                        <div style="color: #fff; font-size: 2rem; font-weight: 700; margin-top: 1rem;">{scores['overall']:.0f}/100</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    scores_data = {k: v for k, v in scores['breakdown'].items() if v is not None}
                    if scores_data:
                        fig = go.Figure(data=go.Bar(
                            x=list(scores_data.keys()),
                            y=list(scores_data.values()),
                            marker_color=['#00ff88' if v >= 60 else '#ffa502' if v >= 40 else '#ff4757' for v in scores_data.values()],
                            text=[f"{v:.0f}" for v in scores_data.values()],
                            textposition='auto',
                        ))
                        fig.update_layout(
                            template='plotly_dark',
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=0, r=0, t=30, b=0),
                            yaxis_range=[0, 100]
                        )
                        st.plotly_chart(fig, width='stretch', key="chart_fundamental_scores")

# --- TAB 4: BERITA ---
with tab4:
    st.markdown('<div class="section-header">📰 Berita & Sentiment</div>', unsafe_allow_html=True)
    
    max_news = st.slider("Jumlah berita:", 5, 30, 10)
    
    if selected_stock:
        with st.spinner(f"Mengambil berita {selected_stock}..."):
            stock_news = news_fetcher.fetch_stock_news(selected_stock, max_items=max_news)
            summary = news_fetcher.get_news_sentiment_summary(stock_news)
        
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("📰 Total", summary['total_news'])
        with col_b:
            st.metric("📊 Sentiment", summary['sentiment_score'])
        with col_c:
            st.metric("🟢 Positive", summary['positive_count'])
        with col_d:
            st.metric("🔴 Negative", summary['negative_count'])
        
        if stock_news:
            formatted = news_fetcher.format_news_for_display(stock_news[:max_news])
            
            for news in formatted:
                sentiment_color = "#00ff88" if news['sentiment'] == 'Positive' else "#ff4757" if news['sentiment'] == 'Negative' else "#ffa502"
                
                with st.expander(f"{news['icon']} {news['title'][:80]}..."):
                    st.markdown(f"""
                    <div class="glass-card">
                        <div style="display: flex; gap: 1rem; margin-bottom: 0.5rem;">
                            <span style="color: {sentiment_color}; font-weight: 600;">{news['sentiment']}</span>
                            <span style="color: #666;">|</span>
                            <span style="color: #a0a0a0;">Score: {news['sentiment_score']}</span>
                            <span style="color: #666;">|</span>
                            <span style="color: #a0a0a0;">Relevance: {news['relevance']}</span>
                        </div>
                        <div style="color: #888; font-size: 0.9rem;">Source: {news['source']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if news['link'] != '#':
                        st.markdown(f"[🔗 Baca Selengkapnya]({news['link']})")

# --- TAB 5: GLOBAL ---
with tab5:
    st.markdown('<div class="section-header">🌍 Geopolitik & Pasar Global</div>', unsafe_allow_html=True)
    
    with st.spinner("Memuat data global..."):
        commodities = geo_analyzer.get_commodity_prices()
        currencies = geo_analyzer.get_currency_rates()
        indices = geo_analyzer.get_global_indices()
        fear_greed = geo_analyzer.get_fear_greed_index()
    
    if fear_greed:
        vix_color = "#00ff88" if fear_greed['vix'] < 20 else "#ff4757" if fear_greed['vix'] > 25 else "#ffa502"
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 2rem;">📊 Fear & Greed Index</div>
            <div style="color: {vix_color}; font-size: 3rem; font-weight: 800;">VIX: {fear_greed['vix']:.1f}</div>
            <div style="color: {vix_color}; font-size: 1.2rem;">{fear_greed['sentiment']}</div>
            <div style="color: #a0a0a0; margin-top: 0.5rem;">{fear_greed['interpretation']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if commodities:
            st.markdown('<div class="section-header">🛢️ Commodities</div>', unsafe_allow_html=True)
            for name, data in list(commodities.items())[:6]:
                color = "#00ff88" if data['change_pct'] > 0 else "#ff4757"
                st.markdown(f"""
                <div class="glass-card" style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #a0a0a0;">{name}</span>
                    <span style="color: #fff; font-weight: 600;">{data['price']:.2f}</span>
                    <span style="color: {color}; font-weight: 600;">{data['change_pct']:+.2f}%</span>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        if currencies:
            st.markdown('<div class="section-header">💱 Currencies</div>', unsafe_allow_html=True)
            for name, data in list(currencies.items())[:6]:
                color = "#00ff88" if data['change_pct'] > 0 else "#ff4757"
                st.markdown(f"""
                <div class="glass-card" style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #a0a0a0;">{name}</span>
                    <span style="color: #fff; font-weight: 600;">{data['rate']:.4f}</span>
                    <span style="color: {color}; font-weight: 600;">{data['change_pct']:+.2f}%</span>
                </div>
                """, unsafe_allow_html=True)
    
    if indices:
        st.markdown('<div class="section-header">📈 Global Indices</div>', unsafe_allow_html=True)
        cols = st.columns(4)
        for i, (name, data) in enumerate(list(indices.items())[:8]):
            with cols[i % 4]:
                color = "#00ff88" if data['change_pct'] > 0 else "#ff4757"
                st.markdown(f"""
                <div class="glass-card" style="text-align: center;">
                    <div style="color: #a0a0a0; font-size: 0.85rem;">{name}</div>
                    <div style="color: #fff; font-weight: 700;">{data['price']:,.0f}</div>
                    <div style="color: {color}; font-weight: 600;">{data['change_pct']:+.2f}%</div>
                </div>
                """, unsafe_allow_html=True)

# --- TAB 6: SCALPING ---
with tab6:
    st.markdown('<div class="section-header">⚡ Scalping Tools</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        interval = st.selectbox("⏱️ Interval", ['1m', '5m', '15m', '30m'], index=1)
        scalping_period = st.selectbox("📅 Periode", ['1d', '5d', '1mo'], index=1, key="scalping_period")
    
    with col1:
        if selected_stock:
            with st.spinner(f"Menganalisa scalping {selected_stock}..."):
                scalping_analyzer = ScalpingAnalyzer(selected_stock, period=scalping_period, interval=interval)
            
            if not scalping_analyzer.df.empty:
                metrics = scalping_analyzer.get_scalping_metrics()
                
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("💰 Harga", f"Rp {metrics['current_price']:,.0f}")
                with col_b:
                    vol_color = "normal" if metrics['volume_ratio'] > 1 else "inverse"
                    st.metric("📦 Volume", f"{metrics['volume_ratio']:.1f}x")
                with col_c:
                    rsi_color = "inverse" if metrics['rsi_7'] < 30 or metrics['rsi_7'] > 70 else "normal"
                    st.metric("📊 RSI", f"{metrics['rsi_7']:.0f}")
                with col_d:
                    mom_color = "normal" if metrics['momentum'] > 0 else "inverse"
                    st.metric("🚀 Momentum", f"{metrics['momentum']:+.2f}%")
                
                fig = scalping_analyzer.create_scalping_chart(last_n_bars=100)
                if fig:
                    st.plotly_chart(fig, width='stretch', key="chart_scalping")
                
                zones = scalping_analyzer.get_scalping_zones()
                if zones:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("""
                        <div class="glass-card" style="border-left: 3px solid #00ff88;">
                            <div style="color: #00ff88; font-weight: 700;">🟢 Support</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"**Immediate:** Rp {zones['immediate_support']:,.0f}")
                        st.markdown(f"**Strong:** Rp {zones['strong_support']:,.0f}")
                    with col2:
                        st.markdown("""
                        <div class="glass-card" style="border-left: 3px solid #ff4757;">
                            <div style="color: #ff4757; font-weight: 700;">🔴 Resistance</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"**Immediate:** Rp {zones['immediate_resistance']:,.0f}")
                        st.markdown(f"**Strong:** Rp {zones['strong_resistance']:,.0f}")
                    with col3:
                        st.markdown("""
                        <div class="glass-card" style="border-left: 3px solid #667eea;">
                            <div style="color: #667eea; font-weight: 700;">📐 Risk Management</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"**ATR:** {zones['atr']:,.0f}")
                        st.markdown(f"**SL:** {zones['stop_loss_distance']:,.0f}")
                
                signals = scalping_analyzer.get_scalping_signals()
                if signals:
                    st.markdown('<div class="section-header">🎯 Scalping Signals</div>', unsafe_allow_html=True)
                    for sig in signals:
                        color = "#00ff88" if sig['type'] == 'BUY' else "#ff4757"
                        with st.expander(f"{'🟢' if sig['type'] == 'BUY' else '🔴'} {sig['type']} - {sig['indicator']}"):
                            st.markdown(f"""
                            <div class="glass-card">
                                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                                    <div>
                                        <div style="color: #a0a0a0;">Entry</div>
                                        <div style="color: #fff; font-weight: 600;">Rp {sig['entry']:,.0f}</div>
                                    </div>
                                    <div>
                                        <div style="color: #a0a0a0;">Stop Loss</div>
                                        <div style="color: #ff4757; font-weight: 600;">Rp {sig['stop_loss']:,.0f}</div>
                                    </div>
                                    <div>
                                        <div style="color: #a0a0a0;">Target</div>
                                        <div style="color: #00ff88; font-weight: 600;">Rp {sig['target']:,.0f}</div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Tidak ada data untuk scalping")

# --- TAB 7: FULL ANALISA ---
with tab7:
    st.markdown('<div class="section-header">🔍 Analisa Lengkap</div>', unsafe_allow_html=True)
    
    with st.spinner(f"Menganalisa {selected_stock} secara menyeluruh..."):
        df = fetcher.get_stock_data(selected_stock, '6mo')
        company = fetcher.get_company_info(selected_stock)
        financials = fetcher.get_financial_statements(selected_stock)
        metrics = fetcher.get_key_metrics(selected_stock)
    
    if not df.empty:
        tech_analyzer = TechnicalAnalyzer(df)
        tech_summary = tech_analyzer.get_summary()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            fig = tech_analyzer.create_candlestick_chart(last_n_days=60)
            st.plotly_chart(fig, width='stretch', key="chart_full")
        
        with col2:
            trend = tech_summary['trend']
            trend_class = 'trend-bullish' if trend['overall'] == 'BULLISH' else 'trend-bearish' if trend['overall'] == 'BEARISH' else 'trend-neutral'
            
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <div class="{trend_class}" style="font-size: 1.8rem;">{trend['overall']}</div>
                <div style="color: #fff; font-size: 2rem; font-weight: 700;">Rp {tech_summary['current_price']:,.0f}</div>
                <div style="color: {'#00ff88' if tech_summary['change_pct'] > 0 else '#ff4757'}; font-weight: 600;">{tech_summary['change_pct']:+.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        if company and metrics:
            st.markdown('<div class="section-header">📋 Ringkasan Fundamental</div>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="glass-card">
                    <div style="color: #a0a0a0;">Sektor</div>
                    <div style="color: #fff; font-weight: 600;">{company['sector']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                pe = metrics.get('Trailing PE', 'N/A')
                st.markdown(f"""
                <div class="glass-card">
                    <div style="color: #a0a0a0;">PE Ratio</div>
                    <div style="color: #fff; font-weight: 600;">{pe}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                roe = metrics.get('ROE', 'N/A')
                st.markdown(f"""
                <div class="glass-card">
                    <div style="color: #a0a0a0;">ROE</div>
                    <div style="color: #fff; font-weight: 600;">{roe}</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                div = metrics.get('Dividend Yield', 'N/A')
                st.markdown(f"""
                <div class="glass-card">
                    <div style="color: #a0a0a0;">Dividend</div>
                    <div style="color: #fff; font-weight: 600;">{div}</div>
                </div>
                """, unsafe_allow_html=True)
            
            if financials:
                fund_analyzer = FundamentalAnalyzer(financials, metrics, company)
                rec = fund_analyzer.get_investment_recommendation()
                scores = fund_analyzer.get_overall_score()
                
                rec_color = "#00ff88" if "BUY" in rec['recommendation'] else "#ff4757" if "SELL" in rec['recommendation'] else "#ffa502"
                
                st.markdown(f"""
                <div class="glass-card" style="text-align: center;">
                    <div style="color: {rec_color}; font-size: 2rem; font-weight: 800;">{rec['recommendation']}</div>
                    <div style="color: #a0a0a0;">Confidence: {rec['confidence']} | Score: {scores['overall']:.0f}/100</div>
                </div>
                """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🚀 StockVerse v2.0 | Made with ❤️ for Indonesian Investors</p>
    <p style="font-size: 0.8rem;">⚠️ Tool ini untuk edukasi. Selalu lakukan riset sendiri sebelum investasi.</p>
</div>
""", unsafe_allow_html=True)

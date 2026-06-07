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
    page_title="Stock Analyzer Indonesia",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PASSWORD PROTECTION ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets.get("password", "Masuk1234_"):
            st.session_state["authenticated"] = True
            del st.session_state["password"]
        else:
            st.session_state["authenticated"] = False

    if "authenticated" not in st.session_state:
        st.markdown("""
        <div style="text-align:center; padding: 2rem;">
            <h1>🔒 Stock Analyzer Indonesia</h1>
            <p>Masukkan password untuk mengakses tools</p>
        </div>
        """, unsafe_allow_html=True)
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["authenticated"]:
        st.error("Password salah! Silakan coba lagi.")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    else:
        return True

if not check_password():
    st.stop()

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .bullish { color: #00ff00; font-weight: bold; }
    .bearish { color: #ff0000; font-weight: bold; }
    .neutral { color: #ffff00; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📈 Tools Analisa Saham Indonesia - Super Lengkap</div>', unsafe_allow_html=True)

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

st.sidebar.header("🔧 Pengaturan")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 Quote & Chart",
    "📈 Analisa Teknikal",
    "💰 Analisa Fundamental",
    "🔍 Analisa Lengkap",
    "📰 Berita & Sentiment",
    "🌍 Geopolitik & Pasar Global",
    "⚡ Scalping Tools",
    "📋 Daftar Saham"
])

with tab1:
    st.header("Quote & Chart")

    col1, col2 = st.columns([2, 1])

    with col2:
        st.subheader("Pilih Saham")
        search_query = st.text_input("Cari saham (nama/simbol):", "")
        stock_list = list(IDX_STOCKS.keys())

        if search_query:
            filtered = [s for s in stock_list if search_query.upper() in s or search_query.upper() in IDX_STOCKS[s].upper()]
            if filtered:
                selected_stock = st.selectbox("Hasil pencarian:", filtered, format_func=lambda x: f"{x} - {IDX_STOCKS[x]}")
            else:
                st.warning("Tidak ditemukan")
                selected_stock = st.selectbox("Pilih saham:", stock_list, format_func=lambda x: f"{x} - {IDX_STOCKS[x]}")
        else:
            selected_stock = st.selectbox("Pilih saham:", stock_list, format_func=lambda x: f"{x} - {IDX_STOCKS[x]}")

        period = st.selectbox("Periode:", ['1mo', '3mo', '6mo', '1y', '2y', '5y'], index=2)

    with col1:
        if selected_stock:
            with st.spinner(f"Mengambil data {selected_stock}..."):
                quote = fetcher.get_realtime_quote(selected_stock)
                df = fetcher.get_stock_data(selected_stock, period)

            if quote:
                st.subheader(f"{quote['name']} ({selected_stock})")

                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Harga", f"Rp {quote['price']:,.0f}", f"{quote['change']:+,.0f} ({quote['change_percent']:+.2f}%)")
                with col_b:
                    st.metric("Volume", f"{quote['volume']:,}")
                with col_c:
                    st.metric("Market Cap", f"Rp {quote['market_cap']/1e9:,.2f}B" if quote['market_cap'] else "N/A")
                with col_d:
                    st.metric("PE Ratio", f"{quote['pe_ratio']:.2f}" if quote['pe_ratio'] else "N/A")

            if not df.empty:
                analyzer = TechnicalAnalyzer(df)
                fig = analyzer.create_candlestick_chart(last_n_days=60)
                st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Analisa Teknikal")

    if 'selected_stock' not in locals():
        selected_stock = st.selectbox("Pilih saham:", list(IDX_STOCKS.keys()), key="tech_stock", format_func=lambda x: f"{x} - {IDX_STOCKS[x]}")
        period = st.selectbox("Periode:", ['1mo', '3mo', '6mo', '1y', '2y', '5y'], index=2, key="tech_period")

    if selected_stock:
        with st.spinner(f"Menganalisa {selected_stock}..."):
            df = fetcher.get_stock_data(selected_stock, period)

        if not df.empty:
            analyzer = TechnicalAnalyzer(df)
            summary = analyzer.get_summary()

            col1, col2 = st.columns([2, 1])

            with col1:
                fig = analyzer.create_candlestick_chart(last_n_days=90)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                trend = summary['trend']
                trend_class = 'bullish' if trend['overall'] == 'BULLISH' else 'bearish' if trend['overall'] == 'BEARISH' else 'neutral'

                st.markdown(f"### Trend: <span class='{trend_class}'>{trend['overall']}</span>", unsafe_allow_html=True)
                st.write(f"Bullish: {trend['bullish_count']} | Bearish: {trend['bearish_count']}")

                st.subheader("Indikator")
                indicators = {
                    'RSI (14)': f"{summary['rsi']:.2f}" if summary['rsi'] else 'N/A',
                    'MACD': f"{summary['macd']:.4f}" if summary['macd'] else 'N/A',
                    'MACD Signal': f"{summary['macd_signal']:.4f}" if summary['macd_signal'] else 'N/A',
                    'Volatility': f"{summary['volatility']:.2%}" if summary['volatility'] else 'N/A',
                }
                for k, v in indicators.items():
                    st.write(f"**{k}:** {v}")

            st.subheader("Signals")
            signals = summary['signals']
            if signals:
                for sig in signals:
                    icon = "🟢" if sig['type'] == 'BUY' else "🔴"
                    st.write(f"{icon} **{sig['type']}** - {sig['indicator']} ({sig['strength']})")
            else:
                st.info("Tidak ada signal saat ini")

            st.subheader("Support & Resistance")
            sr = summary['support_resistance']
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Resistance:**")
                for r in sr['resistance'][:3]:
                    st.write(f"- Rp {r['price']:,.0f}")
            with col2:
                st.write("**Support:**")
                for s in sr['support'][:3]:
                    st.write(f"- Rp {s['price']:,.0f}")

with tab3:
    st.header("Analisa Fundamental")

    selected_stock_fund = st.selectbox("Pilih saham:", list(IDX_STOCKS.keys()), key="fund_stock", format_func=lambda x: f"{x} - {IDX_STOCKS[x]}")

    if selected_stock_fund:
        with st.spinner(f"Mengambil data fundamental {selected_stock_fund}..."):
            company = fetcher.get_company_info(selected_stock_fund)
            financials = fetcher.get_financial_statements(selected_stock_fund)
            metrics = fetcher.get_key_metrics(selected_stock_fund)

        if company and metrics:
            st.subheader(company['name'])
            st.write(f"**Sektor:** {company['sector']} | **Industri:** {company['industry']}")
            st.write(f"**CEO:** {company['ceo']}")
            if company['description'] != 'N/A':
                st.write(company['description'][:500] + "..." if len(company['description']) > 500 else company['description'])

            st.subheader("Key Metrics")
            metrics_df = pd.DataFrame(list(metrics.items()), columns=['Metric', 'Value'])
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)

            if financials:
                analyzer = FundamentalAnalyzer(financials, metrics, company)
                scores = analyzer.get_overall_score()
                rec = analyzer.get_investment_recommendation()

                st.subheader("Skor Analisa")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if scores['overall']:
                        st.metric("Overall Score", f"{scores['overall']:.1f}/100")
                with col2:
                    rec_color = "normal" if 'HOLD' in rec['recommendation'] else "inverse"
                    st.metric("Rekomendasi", rec['recommendation'])
                with col3:
                    st.metric("Confidence", rec['confidence'])

                st.subheader("Detail Skor")
                scores_data = {k: v for k, v in scores['breakdown'].items() if v is not None}
                if scores_data:
                    fig = go.Figure(data=go.Bar(
                        x=list(scores_data.keys()),
                        y=list(scores_data.values()),
                        marker_color=['#00ff00' if v >= 60 else '#ffff00' if v >= 40 else '#ff0000' for v in scores_data.values()]
                    ))
                    fig.update_layout(
                        title="Skor per Kategori",
                        yaxis_title="Skor",
                        yaxis_range=[0, 100],
                        template='plotly_dark'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                st.subheader("Keuangan")
                if financials.get('income_statement') is not None:
                    st.write("**Income Statement:**")
                    st.dataframe(financials['income_statement'].head(), use_container_width=True)

                if financials.get('balance_sheet') is not None:
                    st.write("**Balance Sheet:**")
                    st.dataframe(financials['balance_sheet'].head(), use_container_width=True)

                if financials.get('cash_flow') is not None:
                    st.write("**Cash Flow:**")
                    st.dataframe(financials['cash_flow'].head(), use_container_width=True)

with tab4:
    st.header("Analisa Lengkap")

    selected_stock_full = st.selectbox("Pilih saham:", list(IDX_STOCKS.keys()), key="full_stock", format_func=lambda x: f"{x} - {IDX_STOCKS[x]}")
    period_full = st.selectbox("Periode:", ['1mo', '3mo', '6mo', '1y', '2y', '5y'], index=2, key="full_period")

    if selected_stock_full:
        with st.spinner(f"Menganalisa {selected_stock_full} secara lengkap..."):
            df = fetcher.get_stock_data(selected_stock_full, period_full)
            company = fetcher.get_company_info(selected_stock_full)
            financials = fetcher.get_financial_statements(selected_stock_full)
            metrics = fetcher.get_key_metrics(selected_stock_full)

        if not df.empty:
            tech_analyzer = TechnicalAnalyzer(df)
            tech_summary = tech_analyzer.get_summary()

            col1, col2 = st.columns([3, 1])

            with col1:
                fig = tech_analyzer.create_candlestick_chart(last_n_days=60)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Ringkasan")
                trend = tech_summary['trend']
                trend_class = 'bullish' if trend['overall'] == 'BULLISH' else 'bearish' if trend['overall'] == 'BEARISH' else 'neutral'

                st.markdown(f"**Trend:** <span class='{trend_class}'>{trend['overall']}</span>", unsafe_allow_html=True)
                st.write(f"**Harga:** Rp {tech_summary['current_price']:,.0f}")
                st.write(f"**Change:** {tech_summary['change_pct']:+.2f}%")
                st.write(f"**RSI:** {tech_summary['rsi']:.2f}" if tech_summary['rsi'] else "**RSI:** N/A")

                st.subheader("Signals")
                for sig in tech_summary['signals'][:5]:
                    icon = "🟢" if sig['type'] == 'BUY' else "🔴"
                    st.write(f"{icon} {sig['type']} - {sig['indicator']}")

            if company and metrics:
                st.subheader("Fundamental")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Sektor:** {company['sector']}")
                    st.write(f"**PE:** {metrics.get('Trailing PE', 'N/A')}")
                with col2:
                    st.write(f"**ROE:** {metrics.get('ROE', 'N/A')}")
                    st.write(f"**PB:** {metrics.get('Price to Book', 'N/A')}")
                with col3:
                    st.write(f"**Div Yield:** {metrics.get('Dividend Yield', 'N/A')}")
                    st.write(f"**Profit Margin:** {metrics.get('Profit Margin', 'N/A')}")

                if financials:
                    fund_analyzer = FundamentalAnalyzer(financials, metrics, company)
                    rec = fund_analyzer.get_investment_recommendation()
                    scores = fund_analyzer.get_overall_score()

                    rec_color = "normal" if 'HOLD' in rec['recommendation'] else "inverse"
                    st.success(f"**Rekomendasi: {rec['recommendation']}** (Confidence: {rec['confidence']})")
                    if scores['overall']:
                        st.info(f"**Overall Score: {scores['overall']:.1f}/100**")

with tab5:
    st.header("📰 Berita & Sentiment Analysis")

    col1, col2 = st.columns([2, 1])

    with col2:
        st.subheader("Pilih Saham untuk Berita")
        news_stock = st.selectbox("Pilih saham:", list(IDX_STOCKS.keys()), key="news_stock", format_func=lambda x: f"{x} - {IDX_STOCKS[x]}")
        max_news = st.slider("Jumlah berita:", 5, 30, 10)

    with col1:
        if news_stock:
            with st.spinner(f"Mengambil berita {news_stock}..."):
                stock_news = news_fetcher.fetch_stock_news(news_stock, max_items=max_news)
                summary = news_fetcher.get_news_sentiment_summary(stock_news)

            st.subheader(f"Berita: {news_stock}")

            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.metric("Total Berita", summary['total_news'])
            with col_b:
                st.metric("Sentiment", summary['sentiment_score'])
            with col_c:
                st.metric("Positive", f"{summary['positive_count']}")
            with col_d:
                st.metric("Negative", f"{summary['negative_count']}")

            if stock_news:
                st.subheader("Daftar Berita")
                formatted = news_fetcher.format_news_for_display(stock_news[:max_news])

                for news in formatted:
                    with st.expander(f"{news['icon']} {news['title'][:80]}..."):
                        st.write(f"**Sentiment:** {news['sentiment']} ({news['sentiment_score']})")
                        st.write(f"**Source:** {news['source']}")
                        st.write(f"**Relevance:** {news['relevance']}")
                        if news['link'] != '#':
                            st.markdown(f"[Baca Selengkapnya]({news['link']})")
            else:
                st.info("Tidak ada berita ditemukan")

with tab6:
    st.header("🌍 Geopolitik & Pasar Global")

    subtab1, subtab2, subtab3 = st.tabs(["📊 Global Markets", "⚠️ Risk Factors", "🔗 Korelasi"])

    with subtab1:
        st.subheader("Global Market Overview")

        with st.spinner("Mengambil data pasar global..."):
            commodities = geo_analyzer.get_commodity_prices()
            currencies = geo_analyzer.get_currency_rates()
            indices = geo_analyzer.get_global_indices()
            bonds = geo_analyzer.get_bond_yields()
            fear_greed = geo_analyzer.get_fear_greed_index()

        if fear_greed:
            st.subheader("Market Sentiment (VIX)")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("VIX", f"{fear_greed['vix']:.2f}")
            with col2:
                st.metric("Sentiment", fear_greed['sentiment'])
            with col3:
                st.metric("Avg VIX", f"{fear_greed['avg_vix']:.2f}")

            st.info(fear_greed['interpretation'])

        col1, col2 = st.columns(2)

        with col1:
            if commodities:
                st.subheader("Commodities")
                df_comm = pd.DataFrame(commodities).T
                st.dataframe(df_comm, use_container_width=True)

        with col2:
            if currencies:
                st.subheader("Currencies")
                df_curr = pd.DataFrame(currencies).T
                st.dataframe(df_curr, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            if indices:
                st.subheader("Global Indices")
                df_idx = pd.DataFrame(indices).T
                st.dataframe(df_idx, use_container_width=True)

        with col2:
            if bonds:
                st.subheader("Bond Yields")
                df_bonds = pd.DataFrame(bonds).T
                st.dataframe(df_bonds, use_container_width=True)

    with subtab2:
        st.subheader("Indonesia Risk Factors")

        with st.spinner("Menganalisa risk factors..."):
            risks = geo_analyzer.get_indonesia_risk_factors()

        if risks:
            for risk in risks:
                color = "🔴" if risk['impact'] == 'Negative' else "🟢" if risk['impact'] == 'Positive' else "🟡"
                with st.expander(f"{color} {risk['factor']} - {risk['severity']}"):
                    st.write(f"**Impact:** {risk['impact']}")
                    st.write(f"**Detail:** {risk['detail']}")
        else:
            st.info("Tidak ada risk factors signifikan")

    with subtab3:
        st.subheader("Korelasi Saham dengan Pasar Global")

        corr_stock = st.selectbox("Pilih saham:", list(IDX_STOCKS.keys()), key="corr_stock", format_func=lambda x: f"{x} - {IDX_STOCKS[x]}")

        if corr_stock:
            with st.spinner(f"Menghitung korelasi {corr_stock}..."):
                correlations = geo_analyzer.get_market_correlation(corr_stock)

            if correlations:
                df_corr = pd.DataFrame(list(correlations.items()), columns=['Benchmark', 'Correlation'])
                df_corr['Interpretation'] = df_corr['Correlation'].apply(
                    lambda x: 'Strong Positive' if x > 0.7 else
                              'Moderate Positive' if x > 0.3 else
                              'Weak' if x > -0.3 else
                              'Moderate Negative' if x > -0.7 else
                              'Strong Negative'
                )
                st.dataframe(df_corr, use_container_width=True, hide_index=True)

                fig = go.Figure(data=go.Bar(
                    x=df_corr['Benchmark'],
                    y=df_corr['Correlation'],
                    marker_color=['green' if c > 0 else 'red' for c in df_corr['Correlation']]
                ))
                fig.update_layout(
                    title=f"Korelasi {corr_stock} dengan Pasar Global",
                    yaxis_title="Correlation",
                    template='plotly_dark'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Tidak dapat menghitung korelasi")

with tab7:
    st.header("⚡ Scalping Tools")

    col1, col2 = st.columns([2, 1])

    with col2:
        st.subheader("Pengaturan Scalping")
        scalping_stock = st.selectbox("Pilih saham:", list(IDX_STOCKS.keys()), key="scalping_stock", format_func=lambda x: f"{x} - {IDX_STOCKS[x]}")

        col_a, col_b = st.columns(2)
        with col_a:
            interval = st.selectbox("Interval:", ['1m', '5m', '15m', '30m'], index=1)
        with col_b:
            period = st.selectbox("Periode:", ['1d', '5d', '1mo'], index=1)

    with col1:
        if scalping_stock:
            with st.spinner(f"Menganalisa scalping {scalping_stock}..."):
                scalping_analyzer = ScalpingAnalyzer(scalping_stock, period=period, interval=interval)

            if not scalping_analyzer.df.empty:
                metrics = scalping_analyzer.get_scalping_metrics()

                st.subheader(f"Scalping Analysis: {scalping_stock}")

                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Harga", f"Rp {metrics['current_price']:,.0f}")
                with col_b:
                    st.metric("Volume Ratio", f"{metrics['volume_ratio']:.2f}x")
                with col_c:
                    rsi_color = "normal" if 30 < metrics['rsi_7'] < 70 else "inverse"
                    st.metric("RSI (7)", f"{metrics['rsi_7']:.1f}")
                with col_d:
                    st.metric("Momentum", f"{metrics['momentum']:.2f}%")

                fig = scalping_analyzer.create_scalping_chart(last_n_bars=100)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                zones = scalping_analyzer.get_scalping_zones()
                if zones:
                    st.subheader("Scalping Zones")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write("**Support:**")
                        st.write(f"- Immediate: Rp {zones['immediate_support']:,.0f}")
                        st.write(f"- Strong: Rp {zones['strong_support']:,.0f}")
                    with col2:
                        st.write("**Resistance:**")
                        st.write(f"- Immediate: Rp {zones['immediate_resistance']:,.0f}")
                        st.write(f"- Strong: Rp {zones['strong_resistance']:,.0f}")
                    with col3:
                        st.write("**Risk Management:**")
                        st.write(f"- ATR: {zones['atr']:,.0f}")
                        st.write(f"- SL Distance: {zones['stop_loss_distance']:,.0f}")
                        st.write(f"- TP Distance: {zones['target_distance']:,.0f}")

                signals = scalping_analyzer.get_scalping_signals()
                if signals:
                    st.subheader("Scalping Signals")
                    for sig in signals:
                        color = "🟢" if sig['type'] == 'BUY' else "🔴"
                        with st.expander(f"{color} {sig['type']} - {sig['indicator']} ({sig['strength']})"):
                            st.write(f"**Entry:** Rp {sig['entry']:,.0f}")
                            st.write(f"**Stop Loss:** Rp {sig['stop_loss']:,.0f}")
                            st.write(f"**Target:** Rp {sig['target']:,.0f}")
                            st.write(f"**Timeframe:** {sig['timeframe']}")
                else:
                    st.info("Tidak ada scalping signal saat ini")

                plan = scalping_analyzer.get_scalping_plan()
                if plan.get('scalping_checklist'):
                    st.subheader("Scalping Checklist")
                    for item in plan['scalping_checklist']:
                        st.write(item)
            else:
                st.warning("Tidak ada data untuk scalping")

with tab8:
    st.header("Daftar Saham Indonesia")

    st.subheader(f"Total: {len(IDX_STOCKS)} Saham")

    search = st.text_input("Cari saham:", "", key="search_list")

    if search:
        filtered = {k: v for k, v in IDX_STOCKS.items() if search.upper() in k or search.upper() in v.upper()}
    else:
        filtered = IDX_STOCKS

    stocks_df = pd.DataFrame(list(filtered.items()), columns=['Symbol', 'Nama Perusahaan'])
    stocks_df.index = range(1, len(stocks_df) + 1)
    st.dataframe(stocks_df, use_container_width=True)

    if st.button("Load Semua Data Real-time"):
        with st.spinner("Mengambil data real-time..."):
            progress = st.progress(0)
            results = []
            for i, symbol in enumerate(filtered.keys()):
                quote = fetcher.get_realtime_quote(symbol)
                if quote:
                    results.append(quote)
                progress.progress((i + 1) / len(filtered))

            if results:
                df_results = pd.DataFrame(results)
                st.dataframe(df_results, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### Tentang")
st.sidebar.markdown("""
**Tools Analisa Saham Indonesia**
- 📊 Technical & Fundamental Analysis
- 📰 News & Sentiment Analysis
- 🌍 Geopolitical Analysis
- ⚡ Scalping Tools
- Real-time quotes
- Interactive charts
""")
st.sidebar.markdown("---")
st.sidebar.markdown("**Disclaimer:** Tool ini untuk edukasi. Selalu lakukan riset sendiri sebelum investasi.")

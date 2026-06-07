import click
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.columns import Columns
from rich import box
from data_fetcher import StockDataFetcher
from technical_analysis import TechnicalAnalyzer
from fundamental_analysis import FundamentalAnalyzer
from news_fetcher import NewsFetcher
from geopolitical import GeopoliticalAnalyzer
from scalping import ScalpingAnalyzer
from config import IDX_STOCKS

console = Console()

def format_number(num):
    if num is None:
        return 'N/A'
    if abs(num) >= 1e12:
        return f"Rp {num/1e12:.2f} T"
    elif abs(num) >= 1e9:
        return f"Rp {num/1e9:.2f} B"
    elif abs(num) >= 1e6:
        return f"Rp {num/1e6:.2f} M"
    else:
        return f"Rp {num:,.0f}"

def format_percent(num):
    if num is None:
        return 'N/A'
    return f"{num:.2f}%"

@click.group()
def cli():
    """Tools Analisa Saham Indonesia - Super Lengkap"""
    pass

@cli.command()
@click.argument('symbol')
@click.option('--period', '-p', default='1y', help='Periode data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y)')
def quote(symbol, period):
    """Dapatkan quote real-time untuk saham"""
    fetcher = StockDataFetcher()

    with console.status(f"Mengambil data {symbol}..."):
        data = fetcher.get_realtime_quote(symbol)

    if data:
        table = Table(title=f"Quote: {data['name']} ({symbol})", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Harga", format_number(data['price']))
        table.add_row("Perubahan", f"{format_number(data['change'])} ({format_percent(data['change_percent'])})")
        table.add_row("Volume", f"{data['volume']:,}")
        table.add_row("Market Cap", format_number(data['market_cap']))
        table.add_row("PE Ratio", f"{data['pe_ratio']:.2f}" if data['pe_ratio'] else 'N/A')
        table.add_row("PB Ratio", f"{data['pb_ratio']:.2f}" if data['pb_ratio'] else 'N/A')
        table.add_row("Dividend Yield", format_percent(data['dividend_yield'] * 100 if data['dividend_yield'] else None))
        table.add_row("52W High", format_number(data['high_52w']))
        table.add_row("52W Low", format_number(data['low_52w']))

        console.print(table)
    else:
        console.print(f"[red]Tidak dapat mengambil data untuk {symbol}[/red]")

@cli.command()
@click.argument('symbol')
@click.option('--period', '-p', default='1y', help='Periode data')
@click.option('--days', '-d', default=60, help='Jumlah hari untuk chart')
def technical(symbol, period, days):
    """Analisa teknikal lengkap"""
    fetcher = StockDataFetcher()

    with console.status(f"Mengambil data {symbol}..."):
        df = fetcher.get_stock_data(symbol, period)

    if df.empty:
        console.print(f"[red]Tidak ada data untuk {symbol}[/red]")
        return

    analyzer = TechnicalAnalyzer(df)
    summary = analyzer.get_summary()

    console.print(f"\n[bold blue]=== ANALISA TEKNIKAL: {symbol} ===[/bold blue]\n")

    price_table = Table(title="Harga Saat Ini", box=box.SIMPLE)
    price_table.add_column("Metric", style="cyan")
    price_table.add_column("Value", style="green")

    price_table.add_row("Harga", format_number(summary['current_price']))
    price_table.add_row("Perubahan", f"{format_number(summary['change'])} ({format_percent(summary['change_pct'])})")
    price_table.add_row("Volume", f"{summary['volume']:,}")
    price_table.add_row("High Hari", format_number(summary['high_today']))
    price_table.add_row("Low Hari", format_number(summary['low_today']))

    console.print(price_table)

    trend = summary['trend']
    trend_color = 'green' if trend['overall'] == 'BULLISH' else 'red' if trend['overall'] == 'BEARISH' else 'yellow'

    console.print(f"\n[bold {trend_color}]TREND: {trend['overall']}[/bold {trend_color}]")
    console.print(f"Bullish Signals: {trend['bullish_count']} | Bearish Signals: {trend['bearish_count']}\n")

    signal_table = Table(title="Indikator Teknikal", box=box.ROUNDED)
    signal_table.add_column("Indikator", style="cyan")
    signal_table.add_column("Nilai", style="green")
    signal_table.add_column("Status", style="yellow")

    if summary['rsi']:
        rsi_status = "Overbought" if summary['rsi'] > 70 else "Oversold" if summary['rsi'] < 30 else "Normal"
        signal_table.add_row("RSI (14)", f"{summary['rsi']:.2f}", rsi_status)

    if summary['macd']:
        macd_status = "Bullish" if summary['macd'] > summary['macd_signal'] else "Bearish"
        signal_table.add_row("MACD", f"{summary['macd']:.4f}", macd_status)

    if summary['volatility']:
        signal_table.add_row("Volatility (20)", f"{summary['volatility']:.2%}", "Annualized")

    console.print(signal_table)

    signals = summary['signals']
    if signals:
        console.print("\n[bold yellow]=== SIGNAL ===[/bold yellow]")
        for sig in signals:
            color = 'green' if sig['type'] == 'BUY' else 'red'
            console.print(f"[{color}]{sig['type']}[/] - {sig['indicator']} ({sig['strength']})")

    sr = summary['support_resistance']
    if sr['support'] or sr['resistance']:
        console.print("\n[bold yellow]=== SUPPORT & RESISTANCE ===[/bold yellow]")
        if sr['resistance']:
            console.print("Resistance:")
            for r in sr['resistance'][:3]:
                console.print(f"  - {format_number(r['price'])}")
        if sr['support']:
            console.print("Support:")
            for s in sr['support'][:3]:
                console.print(f"  - {format_number(s['price'])}")

@cli.command()
@click.argument('symbol')
def fundamental(symbol):
    """Analisa fundamental lengkap"""
    fetcher = StockDataFetcher()

    with console.status(f"Mengambil data {symbol}..."):
        company = fetcher.get_company_info(symbol)
        financials = fetcher.get_financial_statements(symbol)
        metrics = fetcher.get_key_metrics(symbol)

    if not company or not metrics:
        console.print(f"[red]Tidak dapat mengambil data untuk {symbol}[/red]")
        return

    console.print(f"\n[bold blue]=== ANALISA FUNDAMENTAL: {company['name']} ({symbol}) ===[/bold blue]\n")

    info_table = Table(title="Informasi Perusahaan", box=box.ROUNDED)
    info_table.add_column("Field", style="cyan")
    info_table.add_column("Value", style="green")

    info_table.add_row("Nama", company['name'])
    info_table.add_row("Sektor", company['sector'])
    info_table.add_row("Industri", company['industry'])
    info_table.add_row("Website", company['website'])
    info_table.add_row("CEO", company['ceo'])

    console.print(info_table)

    metrics_table = Table(title="Key Metrics", box=box.ROUNDED)
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", style="green")

    for key, value in metrics.items():
        if value != 'N/A':
            metrics_table.add_row(key, str(value))

    console.print(metrics_table)

    if financials:
        analyzer = FundamentalAnalyzer(financials, metrics, company)
        scores = analyzer.get_overall_score()
        rec = analyzer.get_investment_recommendation()

        score_table = Table(title="Skor Analisa", box=box.ROUNDED)
        score_table.add_column("Kategori", style="cyan")
        score_table.add_column("Skor", style="green")

        for category, score in scores['breakdown'].items():
            if score is not None:
                score_table.add_row(category, f"{score:.1f}/100")
            else:
                score_table.add_row(category, "N/A")

        if scores['overall']:
            score_table.add_row("OVERALL", f"{scores['overall']:.1f}/100")

        console.print(score_table)

        rec_color = 'green' if 'BUY' in rec['recommendation'] else 'red' if 'SELL' in rec['recommendation'] else 'yellow'
        console.print(f"\n[bold {rec_color}]REKOMENDASI: {rec['recommendation']}[/bold {rec_color}]")
        console.print(f"Confidence: {rec['confidence']}")

@cli.command()
@click.argument('symbols', nargs=-1)
@click.option('--period', '-p', default='6mo', help='Periode data')
def compare(symbols, period):
    """Bandingkan beberapa saham"""
    if not symbols:
        console.print("[red]Masukkan minimal 1 simbol saham[/red]")
        return

    fetcher = StockDataFetcher()

    console.print(f"\n[bold blue]=== PERBANDINGAN SAHAM ===[/bold blue]\n")

    table = Table(title="Perbandingan", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")

    all_data = {}
    for symbol in symbols:
        table.add_column(symbol.upper(), style="green")
        with console.status(f"Mengambil data {symbol}..."):
            quote_data = fetcher.get_realtime_quote(symbol)
            if quote_data:
                all_data[symbol.upper()] = quote_data

    if all_data:
        metrics = ['price', 'change_percent', 'pe_ratio', 'pb_ratio', 'dividend_yield', 'market_cap']
        metric_names = ['Harga', 'Change %', 'PE Ratio', 'PB Ratio', 'Div Yield', 'Market Cap']

        for metric, name in zip(metrics, metric_names):
            row = [name]
            for symbol in symbols:
                data = all_data.get(symbol.upper(), {})
                value = data.get(metric)
                if value is None:
                    row.append('N/A')
                elif metric == 'price' or metric == 'market_cap':
                    row.append(format_number(value))
                elif metric == 'dividend_yield':
                    row.append(format_percent(value * 100 if value else None))
                elif metric == 'change_percent':
                    row.append(format_percent(value))
                else:
                    row.append(f"{value:.2f}" if isinstance(value, (int, float)) else 'N/A')
            table.add_row(*row)

        console.print(table)

@cli.command()
@click.argument('query')
def search(query):
    """Cari saham berdasarkan nama atau simbol"""
    fetcher = StockDataFetcher()
    results = fetcher.search_stock(query)

    if results:
        table = Table(title=f"Hasil Pencarian: {query}", box=box.ROUNDED)
        table.add_column("Symbol", style="cyan")
        table.add_column("Nama", style="green")

        for r in results:
            table.add_row(r['symbol'], r['name'])

        console.print(table)
    else:
        console.print(f"[yellow]Tidak ditemukan saham dengan query '{query}'[/yellow]")

@cli.command()
def list_stocks():
    """Daftar semua saham Indonesia yang tersedia"""
    table = Table(title="Daftar Saham Indonesia", box=box.ROUNDED)
    table.add_column("No", style="dim")
    table.add_column("Symbol", style="cyan")
    table.add_column("Nama", style="green")

    for i, (symbol, name) in enumerate(IDX_STOCKS.items(), 1):
        table.add_row(str(i), symbol, name)

    console.print(table)

@cli.command()
@click.argument('symbol')
@click.option('--period', '-p', default='1y', help='Periode data')
def full(symbol, period):
    """Analisa lengkap (Technical + Fundamental)"""
    console.print(f"\n[bold blue]{'='*60}[/bold blue]")
    console.print(f"[bold blue]    ANALISA LENGKAP: {symbol.upper()}[/bold blue]")
    console.print(f"[bold blue]{'='*60}[/bold blue]\n")

    fetcher = StockDataFetcher()

    with console.status(f"Mengambil data {symbol}..."):
        df = fetcher.get_stock_data(symbol, period)
        company = fetcher.get_company_info(symbol)
        financials = fetcher.get_financial_statements(symbol)
        metrics = fetcher.get_key_metrics(symbol)

    if df.empty:
        console.print(f"[red]Tidak ada data teknikal untuk {symbol}[/red]")
        return

    tech_analyzer = TechnicalAnalyzer(df)
    tech_summary = tech_analyzer.get_summary()

    console.print(f"[bold cyan]1. INFORMASI PERUSAHAAN[/bold cyan]")
    if company:
        console.print(f"   Nama: {company['name']}")
        console.print(f"   Sektor: {company['sector']}")
        console.print(f"   Industri: {company['industry']}")
    console.print()

    console.print(f"[bold cyan]2. HARGA SAAT INI[/bold cyan]")
    console.print(f"   Harga: {format_number(tech_summary['current_price'])}")
    console.print(f"   Perubahan: {format_number(tech_summary['change'])} ({format_percent(tech_summary['change_pct'])})")
    console.print(f"   Volume: {tech_summary['volume']:,}")
    console.print()

    console.print(f"[bold cyan]3. ANALISA TEKNIKAL[/bold cyan]")
    trend = tech_summary['trend']
    trend_color = 'green' if trend['overall'] == 'BULLISH' else 'red' if trend['overall'] == 'BEARISH' else 'yellow'
    console.print(f"   Trend: [bold {trend_color}]{trend['overall']}[/bold {trend_color}]")
    console.print(f"   RSI: {tech_summary['rsi']:.2f}" if tech_summary['rsi'] else "   RSI: N/A")
    console.print(f"   MACD: {'Bullish' if tech_summary['macd'] > tech_summary['macd_signal'] else 'Bearish'}" if tech_summary['macd'] else "   MACD: N/A")
    console.print()

    if metrics:
        console.print(f"[bold cyan]4. FUNDAMENTAL[/bold cyan]")
        key_metrics = ['Trailing PE', 'Price to Book', 'ROE', 'ROA', 'Dividend Yield', 'Profit Margin']
        for m in key_metrics:
            if m in metrics and metrics[m] != 'N/A':
                console.print(f"   {m}: {metrics[m]}")
        console.print()

    if financials and metrics and company:
        fund_analyzer = FundamentalAnalyzer(financials, metrics, company)
        rec = fund_analyzer.get_investment_recommendation()
        scores = fund_analyzer.get_overall_score()

        console.print(f"[bold cyan]5. REKOMENDASI[/bold cyan]")
        rec_color = 'green' if 'BUY' in rec['recommendation'] else 'red' if 'SELL' in rec['recommendation'] else 'yellow'
        console.print(f"   [bold {rec_color}]Rekomendasi: {rec['recommendation']}[/bold {rec_color}]")
        console.print(f"   Confidence: {rec['confidence']}")
        if scores['overall']:
            console.print(f"   Overall Score: {scores['overall']:.1f}/100")
        console.print()

    console.print(f"[bold cyan]6. SIGNAL TEKNIKAL[/bold cyan]")
    for sig in tech_summary['signals'][:5]:
        color = 'green' if sig['type'] == 'BUY' else 'red'
        console.print(f"   [{color}]{sig['type']}[/] - {sig['indicator']} ({sig['strength']})")

    console.print(f"\n[bold blue]{'='*60}[/bold blue]")

@cli.command()
@click.argument('symbol')
@click.option('--max-items', '-n', default=10, help='Jumlah berita')
def news(symbol, max_items):
    """Lihat berita terbaru untuk saham"""
    fetcher = NewsFetcher()

    with console.status(f"Mengambil berita {symbol}..."):
        news_list = fetcher.fetch_stock_news(symbol, max_items=max_items)
        summary = fetcher.get_news_sentiment_summary(news_list)

    console.print(f"\n[bold blue]=== BERITA: {symbol.upper()} ===[/bold blue]\n")

    sentiment_table = Table(title="Sentiment Summary", box=box.ROUNDED)
    sentiment_table.add_column("Metric", style="cyan")
    sentiment_table.add_column("Value", style="green")

    sentiment_table.add_row("Total Berita", str(summary['total_news']))
    sentiment_table.add_row("Avg Sentiment", f"{summary['avg_sentiment']:.3f}")
    sentiment_table.add_row("Sentiment Score", summary['sentiment_score'])
    sentiment_table.add_row("Positive", f"{summary['positive_count']} ({summary['sentiment_distribution']['positive']:.1f}%)")
    sentiment_table.add_row("Negative", f"{summary['negative_count']} ({summary['sentiment_distribution']['negative']:.1f}%)")
    sentiment_table.add_row("Neutral", f"{summary['neutral_count']} ({summary['sentiment_distribution']['neutral']:.1f}%)")

    console.print(sentiment_table)

    if news_list:
        console.print("\n[bold yellow]=== BERITA TERBARU ===[/bold yellow]\n")
        formatted = fetcher.format_news_for_display(news_list[:max_items])

        for i, news in enumerate(formatted, 1):
            console.print(f"{news['icon']} [bold]{news['title']}[/bold]")
            console.print(f"   Sentiment: {news['sentiment']} ({news['sentiment_score']}) | Source: {news['source']}")
            console.print()

@cli.command()
@click.option('--max-items', '-n', default=15, help='Jumlah berita')
def market_news(max_items):
    """Lihat berita pasar/ekonomi Indonesia"""
    fetcher = NewsFetcher()

    with console.status("Mengambil berita pasar..."):
        news_list = fetcher.fetch_market_news(max_items=max_items)
        summary = fetcher.get_news_sentiment_summary(news_list)

    console.print(f"\n[bold blue]=== BERITA PASAR INDONESIA ===[/bold blue]\n")

    sentiment_table = Table(title="Market Sentiment", box=box.ROUNDED)
    sentiment_table.add_column("Metric", style="cyan")
    sentiment_table.add_column("Value", style="green")

    sentiment_table.add_row("Total Berita", str(summary['total_news']))
    sentiment_table.add_row("Sentiment Score", summary['sentiment_score'])
    sentiment_table.add_row("Avg Sentiment", f"{summary['avg_sentiment']:.3f}")

    console.print(sentiment_table)

    if news_list:
        console.print("\n[bold yellow]=== BERITA TERBARU ===[/bold yellow]\n")
        formatted = fetcher.format_news_for_display(news_list[:max_items])

        for news in formatted:
            console.print(f"{news['icon']} [bold]{news['title']}[/bold]")
            console.print(f"   Sentiment: {news['sentiment']} | Source: {news['source']}")
            console.print()

@cli.command()
@click.option('--max-items', '-n', default=15, help='Jumlah berita')
def geopolitics(max_items):
    """Lihat berita dan analisa geopolitik"""
    fetcher = NewsFetcher()
    geo_analyzer = GeopoliticalAnalyzer()

    with console.status("Mengambil data geopolitik..."):
        news_list = fetcher.fetch_geopolitical_news(max_items=max_items)
        risks = geo_analyzer.get_indonesia_risk_factors()
        fear_greed = geo_analyzer.get_fear_greed_index()

    console.print(f"\n[bold blue]=== GEOPOLITICAL ANALYSIS ===[/bold blue]\n")

    if fear_greed:
        fg_table = Table(title="Market Sentiment (VIX)", box=box.ROUNDED)
        fg_table.add_column("Metric", style="cyan")
        fg_table.add_column("Value", style="green")

        fg_table.add_row("VIX", f"{fear_greed['vix']:.2f}")
        fg_table.add_row("Sentiment", fear_greed['sentiment'])
        fg_table.add_row("Avg VIX (1M)", f"{fear_greed['avg_vix']:.2f}")
        fg_table.add_row("Interpretation", fear_greed['interpretation'])

        console.print(fg_table)

    if risks:
        console.print("\n[bold yellow]=== RISK FACTORS ===[/bold yellow]\n")
        risk_table = Table(title="Indonesia Risk Factors", box=box.ROUNDED)
        risk_table.add_column("Factor", style="cyan")
        risk_table.add_column("Impact", style="green")
        risk_table.add_column("Detail", style="yellow")
        risk_table.add_column("Severity", style="red")

        for risk in risks:
            risk_table.add_row(risk['factor'], risk['impact'], risk['detail'], risk['severity'])

        console.print(risk_table)

    if news_list:
        console.print("\n[bold yellow]=== GEOPOLITICAL NEWS ===[/bold yellow]\n")
        formatted = fetcher.format_news_for_display(news_list[:max_items])

        for news in formatted:
            console.print(f"{news['icon']} [bold]{news['title']}[/bold]")
            console.print(f"   Sentiment: {news['sentiment']} | Source: {news['source']}")
            console.print()

@cli.command()
@click.argument('symbol')
@click.option('--interval', '-i', default='5m', help='Interval data (1m, 5m, 15m, 30m)')
@click.option('--period', '-p', default='5d', help='Periode data (1d, 5d, 1mo)')
def scalping(symbol, interval, period):
    """Analisa scalping untuk trading jangka pendek"""
    with console.status(f"Mengambil data scalping {symbol}..."):
        analyzer = ScalpingAnalyzer(symbol, period=period, interval=interval)

    if analyzer.df.empty:
        console.print(f"[red]Tidak ada data untuk {symbol}[/red]")
        return

    console.print(f"\n[bold blue]=== SCALPING ANALYSIS: {symbol.upper()} ===[/bold blue]\n")

    metrics = analyzer.get_scalping_metrics()

    price_table = Table(title="Current Metrics", box=box.ROUNDED)
    price_table.add_column("Metric", style="cyan")
    price_table.add_column("Value", style="green")
    price_table.add_column("Status", style="yellow")

    price_table.add_row("Harga", f"Rp {metrics['current_price']:,.0f}", "")
    price_table.add_row("Spread", f"{metrics['spread']:,.0f}", metrics['volume_status'])
    price_table.add_row("Volume", f"{metrics['volume']:,}", metrics['volume_status'])
    price_table.add_row("Volume Ratio", f"{metrics['volume_ratio']:.2f}x", "High" if metrics['volume_ratio'] > 1.5 else "Normal")
    price_table.add_row("RSI (7)", f"{metrics['rsi_7']:.1f}", "Oversold" if metrics['rsi_7'] < 30 else "Overbought" if metrics['rsi_7'] > 70 else "Neutral")
    price_table.add_row("Stochastic K", f"{metrics['stoch_k']:.1f}", "Oversold" if metrics['stoch_k'] < 20 else "Overbought" if metrics['stoch_k'] > 80 else "Neutral")
    price_table.add_row("MFI", f"{metrics['mfi']:.1f}", "Oversold" if metrics['mfi'] < 20 else "Overbought" if metrics['mfi'] > 80 else "Neutral")
    price_table.add_row("ATR", f"{metrics['atr']:,.0f}", "")
    price_table.add_row("Momentum", f"{metrics['momentum']:.2f}%", "Bullish" if metrics['momentum'] > 0 else "Bearish")

    console.print(price_table)

    zones = analyzer.get_scalping_zones()
    if zones:
        console.print("\n[bold yellow]=== SCALPING ZONES ===[/bold yellow]\n")
        zone_table = Table(title="Support & Resistance", box=box.ROUNDED)
        zone_table.add_column("Level", style="cyan")
        zone_table.add_column("Price", style="green")

        zone_table.add_row("Current Price", f"Rp {zones['current_price']:,.0f}")
        zone_table.add_row("Immediate Support", f"Rp {zones['immediate_support']:,.0f}")
        zone_table.add_row("Strong Support", f"Rp {zones['strong_support']:,.0f}")
        zone_table.add_row("Immediate Resistance", f"Rp {zones['immediate_resistance']:,.0f}")
        zone_table.add_row("Strong Resistance", f"Rp {zones['strong_resistance']:,.0f}")
        zone_table.add_row("ATR", f"{zones['atr']:,.0f}")

        console.print(zone_table)

    signals = analyzer.get_scalping_signals()
    if signals:
        console.print("\n[bold yellow]=== SCALPING SIGNALS ===[/bold yellow]\n")
        for sig in signals:
            color = 'green' if sig['type'] == 'BUY' else 'red'
            console.print(f"[{color}]{sig['type']}[/] - {sig['indicator']} ({sig['strength']})")
            console.print(f"   Entry: Rp {sig['entry']:,.0f}")
            console.print(f"   Stop Loss: Rp {sig['stop_loss']:,.0f}")
            console.print(f"   Target: Rp {sig['target']:,.0f}")
            console.print()

    plan = analyzer.get_scalping_plan()
    if plan.get('scalping_checklist'):
        console.print("\n[bold yellow]=== SCALPING CHECKLIST ===[/bold yellow]\n")
        for item in plan['scalping_checklist']:
            console.print(f"  {item}")

@cli.command()
@click.argument('symbol')
@click.option('--interval', '-i', default='5m', help='Interval data')
@click.option('--period', '-p', default='5d', help='Periode data')
def scalping_chart(symbol, interval, period):
    """Tampilkan chart scalping"""
    analyzer = ScalpingAnalyzer(symbol, period=period, interval=interval)

    if analyzer.df.empty:
        console.print(f"[red]Tidak ada data untuk {symbol}[/red]")
        return

    fig = analyzer.create_scalping_chart(last_n_bars=100)
    if fig:
        fig.show()
        console.print("[green]Chart打开 di browser[/green]")

@cli.command()
def global_markets():
    """Lihat kondisi pasar global"""
    analyzer = GeopoliticalAnalyzer()

    with console.status("Mengambil data pasar global..."):
        commodities = analyzer.get_commodity_prices()
        currencies = analyzer.get_currency_rates()
        indices = analyzer.get_global_indices()
        bonds = analyzer.get_bond_yields()
        fear_greed = analyzer.get_fear_greed_index()

    console.print(f"\n[bold blue]=== GLOBAL MARKETS ===[/bold blue]\n")

    if fear_greed:
        fg_color = 'green' if fear_greed['vix'] < 20 else 'red' if fear_greed['vix'] > 25 else 'yellow'
        console.print(f"[bold {fg_color}]VIX: {fear_greed['vix']:.2f} ({fear_greed['sentiment']})[/bold {fg_color}]")
        console.print(f"{fear_greed['interpretation']}\n")

    if commodities:
        console.print("[bold cyan]COMMODITIES[/bold cyan]")
        table = Table(box=box.SIMPLE)
        table.add_column("Name", style="cyan")
        table.add_column("Price", style="green")
        table.add_column("Change %", style="yellow")

        for name, data in commodities.items():
            color = 'green' if data['change_pct'] > 0 else 'red'
            table.add_row(name, f"{data['price']:.2f}", f"[{color}]{data['change_pct']:+.2f}%[/]")

        console.print(table)

    if currencies:
        console.print("\n[bold cyan]CURRENCIES[/bold cyan]")
        table = Table(box=box.SIMPLE)
        table.add_column("Pair", style="cyan")
        table.add_column("Rate", style="green")
        table.add_column("Change %", style="yellow")

        for name, data in currencies.items():
            color = 'green' if data['change_pct'] > 0 else 'red'
            table.add_row(name, f"{data['rate']:.4f}", f"[{color}]{data['change_pct']:+.2f}%[/]")

        console.print(table)

    if indices:
        console.print("\n[bold cyan]GLOBAL INDICES[/bold cyan]")
        table = Table(box=box.SIMPLE)
        table.add_column("Index", style="cyan")
        table.add_column("Price", style="green")
        table.add_column("Change %", style="yellow")

        for name, data in indices.items():
            color = 'green' if data['change_pct'] > 0 else 'red'
            table.add_row(name, f"{data['price']:,.2f}", f"[{color}]{data['change_pct']:+.2f}%[/]")

        console.print(table)

    if bonds:
        console.print("\n[bold cyan]BOND YIELDS[/bold cyan]")
        table = Table(box=box.SIMPLE)
        table.add_column("Bond", style="cyan")
        table.add_column("Yield", style="green")
        table.add_column("Change", style="yellow")

        for name, data in bonds.items():
            color = 'green' if data['change'] > 0 else 'red'
            table.add_row(name, f"{data['yield']:.3f}%", f"[{color}]{data['change']:+.3f}[/]")

        console.print(table)

@cli.command()
@click.argument('symbol')
def correlation(symbol):
    """Lihat korelasi saham dengan pasar global"""
    analyzer = GeopoliticalAnalyzer()

    with console.status(f"Menghitung korelasi {symbol}..."):
        correlations = analyzer.get_market_correlation(symbol)

    if correlations:
        console.print(f"\n[bold blue]=== KORELASI: {symbol.upper()} ===[/bold blue]\n")

        table = Table(title="Market Correlation", box=box.ROUNDED)
        table.add_column("Benchmark", style="cyan")
        table.add_column("Correlation", style="green")
        table.add_column("Interpretation", style="yellow")

        for bench, corr in correlations.items():
            if corr > 0.7:
                interp = "Strong Positive"
            elif corr > 0.3:
                interp = "Moderate Positive"
            elif corr > -0.3:
                interp = "Weak/No Correlation"
            elif corr > -0.7:
                interp = "Moderate Negative"
            else:
                interp = "Strong Negative"

            table.add_row(bench, f"{corr:.3f}", interp)

        console.print(table)
    else:
        console.print(f"[yellow]Tidak dapat menghitung korelasi untuk {symbol}[/yellow]")

if __name__ == '__main__':
    cli()

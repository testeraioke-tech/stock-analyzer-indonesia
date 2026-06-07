import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class GeopoliticalAnalyzer:
    def __init__(self):
        self.commodities = {
            'Crude Oil (WTI)': 'CL=F',
            'Brent Oil': 'BZ=F',
            'Gold': 'GC=F',
            'Silver': 'SI=F',
            'Copper': 'HG=F',
            'Aluminum': 'ALI=F',
            'Nickel': 'NIDY.L',
            'Natural Gas': 'NG=F',
        }

        self.currencies = {
            'USD/IDR': 'USDIDR=X',
            'EUR/IDR': 'EURIDR=X',
            'USD/JPY': 'USDJPY=X',
            'USD/CNY': 'USDCNY=X',
            'EUR/USD': 'EURUSD=X',
            'GBP/USD': 'GBPUSD=X',
            'DXY (Dollar Index)': 'DX-Y.NYB',
        }

        self.global_indices = {
            'S&P 500': '^GSPC',
            'Nasdaq': '^IXIC',
            'Dow Jones': '^DJI',
            'Nikkei 225': '^N225',
            'Hang Seng': '^HSI',
            'Shanghai Composite': '000001.SS',
            'FTSE 100': '^FTSE',
            'DAX': '^GDAXI',
        }

        self.bonds = {
            'US 10Y Treasury': '^TNX',
            'US 2Y Treasury': '^IRX',
            'US 30Y Treasury': '^TYX',
        }

    def get_commodity_prices(self):
        data = {}

        for name, ticker in self.commodities.items():
            try:
                commodity = yf.Ticker(ticker)
                hist = commodity.history(period='5d')

                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                    change = current - prev
                    change_pct = (change / prev * 100) if prev != 0 else 0

                    data[name] = {
                        'price': current,
                        'change': change,
                        'change_pct': change_pct,
                        'high_5d': hist['High'].max(),
                        'low_5d': hist['Low'].min(),
                        'volume': hist['Volume'].sum() if 'Volume' in hist else 0
                    }
            except Exception as e:
                continue

        return data

    def get_currency_rates(self):
        data = {}

        for name, ticker in self.currencies.items():
            try:
                currency = yf.Ticker(ticker)
                hist = currency.history(period='5d')

                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                    change = current - prev
                    change_pct = (change / prev * 100) if prev != 0 else 0

                    data[name] = {
                        'rate': current,
                        'change': change,
                        'change_pct': change_pct,
                        'high_5d': hist['High'].max(),
                        'low_5d': hist['Low'].min()
                    }
            except Exception as e:
                continue

        return data

    def get_global_indices(self):
        data = {}

        for name, ticker in self.global_indices.items():
            try:
                index = yf.Ticker(ticker)
                hist = index.history(period='5d')

                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                    change = current - prev
                    change_pct = (change / prev * 100) if prev != 0 else 0

                    data[name] = {
                        'price': current,
                        'change': change,
                        'change_pct': change_pct,
                        'high_5d': hist['High'].max(),
                        'low_5d': hist['Low'].min()
                    }
            except Exception as e:
                continue

        return data

    def get_bond_yields(self):
        data = {}

        for name, ticker in self.bonds.items():
            try:
                bond = yf.Ticker(ticker)
                hist = bond.history(period='1mo')

                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                    change = current - prev

                    data[name] = {
                        'yield': current,
                        'change': change,
                        'high_1m': hist['High'].max(),
                        'low_1m': hist['Low'].min()
                    }
            except Exception as e:
                continue

        return data

    def get_fear_greed_index(self):
        try:
            vix = yf.Ticker('^VIX')
            hist = vix.history(period='1mo')

            if not hist.empty:
                current_vix = hist['Close'].iloc[-1]
                avg_vix = hist['Close'].mean()
                max_vix = hist['Close'].max()
                min_vix = hist['Close'].min()

                if current_vix < 15:
                    sentiment = 'Extreme Greed'
                    color = 'green'
                elif current_vix < 20:
                    sentiment = 'Greed'
                    color = 'lightgreen'
                elif current_vix < 25:
                    sentiment = 'Neutral'
                    color = 'yellow'
                elif current_vix < 30:
                    sentiment = 'Fear'
                    color = 'orange'
                else:
                    sentiment = 'Extreme Fear'
                    color = 'red'

                return {
                    'vix': current_vix,
                    'avg_vix': avg_vix,
                    'max_vix': max_vix,
                    'min_vix': min_vix,
                    'sentiment': sentiment,
                    'color': color,
                    'interpretation': self._interpret_vix(current_vix)
                }
        except Exception as e:
            pass

        return None

    def _interpret_vix(self, vix):
        if vix < 12:
            return "VIX sangat rendah - pasar sangat tenang, potensi kurang volatilitas"
        elif vix < 15:
            return "VIX rendah - pasar stabil, kondisi normal"
        elif vix < 20:
            return "VIX moderat - sedikit kekhawatiran di pasar"
        elif vix < 25:
            return "VIX meningkat - ketidakpastian mulai naik"
        elif vix < 30:
            return "VIX tinggi - kekhawatiran signifikan di pasar"
        else:
            return "VIX sangat tinggi - panik di pasar, potensi peluang contrarian"

    def get_indonesia_risk_factors(self):
        factors = []

        try:
            usd_idr = yf.Ticker('USDIDR=X')
            hist = usd_idr.history(period='1mo')
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                month_ago = hist['Close'].iloc[0]
                idr_change = ((current - month_ago) / month_ago) * 100

                if idr_change > 3:
                    factors.append({
                        'factor': 'Rupiah Melemah',
                        'impact': 'Negative',
                        'detail': f'IDR melemah {idr_change:.2f}% terhadap USD dalam 1 bulan',
                        'severity': 'High'
                    })
                elif idr_change < -3:
                    factors.append({
                        'factor': 'Rupiah Menguat',
                        'impact': 'Positive',
                        'detail': f'IDR menguat {abs(idr_change):.2f}% terhadap USD dalam 1 bulan',
                        'severity': 'Medium'
                    })
        except:
            pass

        try:
            oil = yf.Ticker('CL=F')
            hist = oil.history(period='1mo')
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                month_ago = hist['Close'].iloc[0]
                oil_change = ((current - month_ago) / month_ago) * 100

                if oil_change > 10:
                    factors.append({
                        'factor': 'Harga Minyak Naik',
                        'impact': 'Mixed',
                        'detail': f'Oil naik {oil_change:.2f}% - positif untuk ADRO/PTBA, negatif untuk consumer',
                        'severity': 'Medium'
                    })
                elif oil_change < -10:
                    factors.append({
                        'factor': 'Harga Minyak Turun',
                        'impact': 'Mixed',
                        'detail': f'Oil turun {oil_change:.2f}% - negatif untuk mining, positif untuk consumer',
                        'severity': 'Medium'
                    })
        except:
            pass

        try:
            nickel = yf.Ticker('NIDY.L')
            hist = nickel.history(period='1mo')
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                month_ago = hist['Close'].iloc[0]
                ni_change = ((current - month_ago) / month_ago) * 100

                if ni_change > 10:
                    factors.append({
                        'factor': 'Harga Nikel Naik',
                        'impact': 'Positive',
                        'detail': f'Nickel naik {ni_change:.2f}% - positif untuk ANTm, INCO',
                        'severity': 'Medium'
                    })
                elif ni_change < -10:
                    factors.append({
                        'factor': 'Harga Nikel Turun',
                        'impact': 'Negative',
                        'detail': f'Nickel turun {ni_change:.2f}% - negatif untuk ANTm, INCO',
                        'severity': 'Medium'
                    })
        except:
            pass

        try:
            gold = yf.Ticker('GC=F')
            hist = gold.history(period='1mo')
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                month_ago = hist['Close'].iloc[0]
                gold_change = ((current - month_ago) / month_ago) * 100

                if gold_change > 5:
                    factors.append({
                        'factor': 'Harga Emas Naik',
                        'impact': 'Positive',
                        'detail': f'Gold naik {gold_change:.2f}% - safe haven demand tinggi',
                        'severity': 'Low'
                    })
        except:
            pass

        try:
            snp = yf.Ticker('^GSPC')
            hist = snp.history(period='1wk')
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                week_ago = hist['Close'].iloc[0]
                sp_change = ((current - week_ago) / week_ago) * 100

                if sp_change < -3:
                    factors.append({
                        'factor': 'S&P 500 Turun Tajam',
                        'impact': 'Negative',
                        'detail': f'S&P turun {sp_change:.2f}% minggu ini - risk off global',
                        'severity': 'High'
                    })
                elif sp_change > 3:
                    factors.append({
                        'factor': 'S&P 500 Naik Tajam',
                        'impact': 'Positive',
                        'detail': f'S&P naik {sp_change:.2f}% minggu ini - risk on global',
                        'severity': 'Medium'
                    })
        except:
            pass

        return factors

    def get_market_correlation(self, symbol):
        try:
            stock = yf.Ticker(f"{symbol}.JK")
            stock_hist = stock.history(period='3mo')

            correlations = {}

            benchmarks = {
                'IHSG': '^JKSE',
                'S&P 500': '^GSPC',
                'USD/IDR': 'USDIDR=X',
                'Oil': 'CL=F',
                'Gold': 'GC=F'
            }

            for bench_name, bench_ticker in benchmarks.items():
                try:
                    bench = yf.Ticker(bench_ticker)
                    bench_hist = bench.history(period='3mo')

                    if not stock_hist.empty and not bench_hist.empty:
                        common_dates = stock_hist.index.intersection(bench_hist.index)
                        if len(common_dates) > 10:
                            stock_returns = stock_hist.loc[common_dates, 'Close'].pct_change().dropna()
                            bench_returns = bench_hist.loc[common_dates, 'Close'].pct_change().dropna()

                            correlation = stock_returns.corr(bench_returns)
                            correlations[bench_name] = round(correlation, 3)
                except:
                    continue

            return correlations

        except Exception as e:
            return {}

    def create_geopolitical_dashboard(self):
        commodities = self.get_commodity_prices()
        currencies = self.get_currency_rates()
        indices = self.get_global_indices()
        bonds = self.get_bond_yields()
        fear_greed = self.get_fear_greed_index()

        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Commodities', 'Currencies',
                'Global Indices', 'Bond Yields',
                'Market Sentiment', 'Risk Factors'
            ),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}],
                   [{"type": "indicator"}, {"type": "table"}]]
        )

        if commodities:
            commodity_names = list(commodities.keys())[:6]
            commodity_changes = [commodities[c]['change_pct'] for c in commodity_names]
            colors = ['green' if c > 0 else 'red' for c in commodity_changes]

            fig.add_trace(go.Bar(
                x=commodity_names,
                y=commodity_changes,
                marker_color=colors,
                name='Commodities'
            ), row=1, col=1)

        if currencies:
            curr_names = list(currencies.keys())[:6]
            curr_changes = [currencies[c]['change_pct'] for c in curr_names]
            colors = ['green' if c > 0 else 'red' for c in curr_changes]

            fig.add_trace(go.Bar(
                x=curr_names,
                y=curr_changes,
                marker_color=colors,
                name='Currencies'
            ), row=1, col=2)

        if indices:
            idx_names = list(indices.keys())[:6]
            idx_changes = [indices[i]['change_pct'] for i in idx_names]
            colors = ['green' if c > 0 else 'red' for c in idx_changes]

            fig.add_trace(go.Bar(
                x=idx_names,
                y=idx_changes,
                marker_color=colors,
                name='Indices'
            ), row=2, col=1)

        if bonds:
            bond_names = list(bonds.keys())[:3]
            bond_changes = [bonds[b]['change'] for b in bond_names]
            colors = ['green' if c > 0 else 'red' for c in bond_changes]

            fig.add_trace(go.Bar(
                x=bond_names,
                y=bond_changes,
                marker_color=colors,
                name='Bonds'
            ), row=2, col=2)

        if fear_greed:
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=fear_greed['vix'],
                title={'text': "VIX (Fear Index)"},
                gauge={
                    'axis': {'range': [0, 50]},
                    'bar': {'color': fear_greed['color']},
                    'steps': [
                        {'range': [0, 15], 'color': 'green'},
                        {'range': [15, 25], 'color': 'yellow'},
                        {'range': [25, 50], 'color': 'red'}
                    ],
                    'threshold': {
                        'line': {'color': 'white', 'width': 4},
                        'thickness': 0.75,
                        'value': fear_greed['vix']
                    }
                }
            ), row=3, col=1)

        fig.update_layout(
            height=1000,
            showlegend=False,
            template='plotly_dark',
            title_text="Global Market Dashboard"
        )

        return fig

    def get_full_analysis(self):
        return {
            'commodities': self.get_commodity_prices(),
            'currencies': self.get_currency_rates(),
            'global_indices': self.get_global_indices(),
            'bonds': self.get_bond_yields(),
            'fear_greed': self.get_fear_greed_index(),
            'indonesia_risks': self.get_indonesia_risk_factors()
        }

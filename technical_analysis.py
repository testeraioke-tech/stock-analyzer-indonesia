import pandas as pd
import numpy as np
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class TechnicalAnalyzer:
    def __init__(self, df):
        self.df = df.copy()
        self._calculate_all_indicators()

    def _calculate_all_indicators(self):
        df = self.df

        df['SMA_20'] = ta.trend.sma_indicator(df['close'], window=20)
        df['SMA_50'] = ta.trend.sma_indicator(df['close'], window=50)
        df['SMA_200'] = ta.trend.sma_indicator(df['close'], window=200)

        df['EMA_12'] = ta.trend.ema_indicator(df['close'], window=12)
        df['EMA_26'] = ta.trend.ema_indicator(df['close'], window=26)

        macd = ta.trend.MACD(df['close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()

        df['RSI_14'] = ta.momentum.rsi(df['close'], window=14)
        df['Stoch_K'] = ta.momentum.stoch(df['high'], df['low'], df['close'])
        df['Stoch_D'] = ta.momentum.stoch_signal(df['high'], df['low'], df['close'])

        bb = ta.volatility.BollingerBands(df['close'])
        df['BB_Upper'] = bb.bollinger_hband()
        df['BB_Middle'] = bb.bollinger_mavg()
        df['BB_Lower'] = bb.bollinger_lband()
        df['BB_Width'] = bb.bollinger_wband()

        df['ATR_14'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)

        adx = ta.trend.ADXIndicator(df['high'], df['low'], df['close'])
        df['ADX_14'] = adx.adx()
        df['DI_Plus'] = adx.adx_pos()
        df['DI_Minus'] = adx.adx_neg()

        df['OBV'] = ta.volume.on_balance_volume(df['close'], df['volume'])

        df['VWAP'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()

        df['Williams_R'] = ta.momentum.williams_r(df['high'], df['low'], df['close'])

        df['CCI'] = ta.trend.cci(df['high'], df['low'], df['close'])

        df['ROC'] = ta.momentum.roc(df['close'])

        df['Daily_Return'] = df['close'].pct_change()
        df['Volatility_20'] = df['Daily_Return'].rolling(window=20).std() * np.sqrt(252)

        self.df = df

    def get_support_resistance(self, window=20):
        df = self.df
        highs = df['high'].rolling(window=window, center=True).max()
        lows = df['low'].rolling(window=window, center=True).min()

        resistance_levels = []
        support_levels = []

        for i in range(window, len(df) - window):
            if df['high'].iloc[i] == highs.iloc[i]:
                resistance_levels.append({
                    'price': df['high'].iloc[i],
                    'date': df.index[i]
                })
            if df['low'].iloc[i] == lows.iloc[i]:
                support_levels.append({
                    'price': df['low'].iloc[i],
                    'date': df.index[i]
                })

        return {
            'resistance': sorted(resistance_levels, key=lambda x: x['price'], reverse=True)[:5],
            'support': sorted(support_levels, key=lambda x: x['price'])[:5]
        }

    def get_trend(self):
        df = self.df
        latest = df.iloc[-1]

        trend_signals = []

        if pd.notna(latest.get('SMA_20')) and pd.notna(latest.get('SMA_50')):
            if latest['SMA_20'] > latest['SMA_50']:
                trend_signals.append('Golden Cross (SMA20 > SMA50)')
            else:
                trend_signals.append('Death Cross (SMA20 < SMA50)')

        if pd.notna(latest.get('SMA_50')) and pd.notna(latest.get('SMA_200')):
            if latest['SMA_50'] > latest['SMA_200']:
                trend_signals.append('Uptrend (SMA50 > SMA200)')
            else:
                trend_signals.append('Downtrend (SMA50 < SMA200)')

        if pd.notna(latest.get('MACD')) and pd.notna(latest.get('MACD_Signal')):
            if latest['MACD'] > latest['MACD_Signal']:
                trend_signals.append('MACD Bullish')
            else:
                trend_signals.append('MACD Bearish')

        if pd.notna(latest.get('ADX_14')):
            if latest['ADX_14'] > 25:
                trend_signals.append(f"Strong Trend (ADX: {latest['ADX_14']:.1f})")
            else:
                trend_signals.append(f"Weak Trend (ADX: {latest['ADX_14']:.1f})")

        if pd.notna(latest.get('RSI_14')):
            if latest['RSI_14'] > 70:
                trend_signals.append('Overbought (RSI > 70)')
            elif latest['RSI_14'] < 30:
                trend_signals.append('Oversold (RSI < 30)')
            else:
                trend_signals.append(f"Neutral (RSI: {latest['RSI_14']:.1f})")

        bullish_count = sum(1 for s in trend_signals if any(w in s for w in ['Golden', 'Uptrend', 'Bullish', 'Oversold']))
        bearish_count = sum(1 for s in trend_signals if any(w in s for w in ['Death', 'Downtrend', 'Bearish', 'Overbought']))

        if bullish_count > bearish_count:
            overall = 'BULLISH'
        elif bearish_count > bullish_count:
            overall = 'BEARISH'
        else:
            overall = 'NEUTRAL'

        return {
            'overall': overall,
            'signals': trend_signals,
            'bullish_count': bullish_count,
            'bearish_count': bearish_count
        }

    def get_signals(self):
        df = self.df
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest

        signals = []

        if pd.notna(latest.get('RSI_14')) and pd.notna(prev.get('RSI_14')):
            if prev['RSI_14'] < 30 and latest['RSI_14'] >= 30:
                signals.append({'type': 'BUY', 'indicator': 'RSI', 'strength': 'Strong'})
            elif prev['RSI_14'] > 70 and latest['RSI_14'] <= 70:
                signals.append({'type': 'SELL', 'indicator': 'RSI', 'strength': 'Strong'})
            elif latest['RSI_14'] < 30:
                signals.append({'type': 'BUY', 'indicator': 'RSI', 'strength': 'Medium'})
            elif latest['RSI_14'] > 70:
                signals.append({'type': 'SELL', 'indicator': 'RSI', 'strength': 'Medium'})

        if pd.notna(latest.get('MACD')) and pd.notna(latest.get('MACD_Signal')):
            if prev['MACD'] < prev['MACD_Signal'] and latest['MACD'] >= latest['MACD_Signal']:
                signals.append({'type': 'BUY', 'indicator': 'MACD Crossover', 'strength': 'Strong'})
            elif prev['MACD'] > prev['MACD_Signal'] and latest['MACD'] <= latest['MACD_Signal']:
                signals.append({'type': 'SELL', 'indicator': 'MACD Crossover', 'strength': 'Strong'})

        if pd.notna(latest.get('close')) and pd.notna(latest.get('BB_Upper')) and pd.notna(latest.get('BB_Lower')):
            if latest['close'] <= latest['BB_Lower']:
                signals.append({'type': 'BUY', 'indicator': 'Bollinger Band', 'strength': 'Medium'})
            elif latest['close'] >= latest['BB_Upper']:
                signals.append({'type': 'SELL', 'indicator': 'Bollinger Band', 'strength': 'Medium'})

        if pd.notna(latest.get('Stoch_K')) and pd.notna(latest.get('Stoch_D')):
            if prev['Stoch_K'] < prev['Stoch_D'] and latest['Stoch_K'] >= latest['Stoch_D'] and latest['Stoch_K'] < 20:
                signals.append({'type': 'BUY', 'indicator': 'Stochastic', 'strength': 'Strong'})
            elif prev['Stoch_K'] > prev['Stoch_D'] and latest['Stoch_K'] <= latest['Stoch_D'] and latest['Stoch_K'] > 80:
                signals.append({'type': 'SELL', 'indicator': 'Stochastic', 'strength': 'Strong'})

        if pd.notna(latest.get('close')) and pd.notna(latest.get('SMA_20')) and pd.notna(latest.get('SMA_50')):
            if prev['close'] < prev['SMA_20'] and latest['close'] >= latest['SMA_20']:
                signals.append({'type': 'BUY', indicator: 'Price Cross SMA20', 'strength': 'Medium'})
            elif prev['close'] > prev['SMA_20'] and latest['close'] <= latest['SMA_20']:
                signals.append({'type': 'SELL', indicator: 'Price Cross SMA20', 'strength': 'Medium'})

        return signals

    def create_candlestick_chart(self, last_n_days=60):
        df = self.df.tail(last_n_days)

        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.5, 0.15, 0.15, 0.2],
            subplot_titles=('Candlestick & Moving Averages', 'Volume', 'RSI', 'MACD')
        )

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='OHLC',
            increasing_line_color='#00ff00',
            decreasing_line_color='#ff0000'
        ), row=1, col=1)

        if 'SMA_20' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['SMA_20'],
                name='SMA 20', line=dict(color='blue', width=1)
            ), row=1, col=1)

        if 'SMA_50' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['SMA_50'],
                name='SMA 50', line=dict(color='orange', width=1)
            ), row=1, col=1)

        if 'BB_Upper' in df.columns and 'BB_Lower' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['BB_Upper'],
                name='BB Upper', line=dict(color='gray', width=1, dash='dash')
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df.index, y=df['BB_Lower'],
                name='BB Lower', line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty', fillcolor='rgba(128,128,128,0.1)'
            ), row=1, col=1)

        colors = ['green' if row['close'] >= row['open'] else 'red' for idx, row in df.iterrows()]
        fig.add_trace(go.Bar(
            x=df.index, y=df['volume'],
            name='Volume', marker_color=colors
        ), row=2, col=1)

        if 'RSI_14' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['RSI_14'],
                name='RSI', line=dict(color='purple', width=1.5)
            ), row=3, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

        if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MACD'],
                name='MACD', line=dict(color='blue', width=1.5)
            ), row=4, col=1)
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MACD_Signal'],
                name='Signal', line=dict(color='orange', width=1.5)
            ), row=4, col=1)
            macd_colors = ['green' if v >= 0 else 'red' for v in df['MACD_Hist']]
            fig.add_trace(go.Bar(
                x=df.index, y=df['MACD_Hist'],
                name='MACD Hist', marker_color=macd_colors
            ), row=4, col=1)

        fig.update_layout(
            height=800,
            xaxis_rangeslider_visible=False,
            showlegend=True,
            template='plotly_dark',
            title_text="Technical Analysis Chart"
        )

        return fig

    def get_summary(self):
        df = self.df
        latest = df.iloc[-1]

        trend = self.get_trend()
        signals = self.get_signals()
        sr = self.get_support_resistance()

        summary = {
            'current_price': latest['close'],
            'change': latest['close'] - df['close'].iloc[-2] if len(df) > 1 else 0,
            'change_pct': ((latest['close'] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100) if len(df) > 1 else 0,
            'volume': latest['volume'],
            'high_today': latest['high'],
            'low_today': latest['low'],
            'rsi': latest.get('RSI_14', None),
            'macd': latest.get('MACD', None),
            'macd_signal': latest.get('MACD_Signal', None),
            'trend': trend,
            'signals': signals,
            'support_resistance': sr,
            'volatility': latest.get('Volatility_20', None),
        }

        return summary

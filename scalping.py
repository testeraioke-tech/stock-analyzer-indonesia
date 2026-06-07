import pandas as pd
import numpy as np
import yfinance as yf
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

class ScalpingAnalyzer:
    def __init__(self, symbol, period='5d', interval='5m'):
        self.symbol = symbol
        self.period = period
        self.interval = interval
        self.df = self._fetch_data()

        if not self.df.empty:
            self._calculate_scalping_indicators()

    def _fetch_data(self):
        try:
            ticker = f"{self.symbol}.JK"
            stock = yf.Ticker(ticker)
            df = stock.history(period=self.period, interval=self.interval)

            if df.empty:
                raise ValueError(f"No data for {self.symbol}")

            df.columns = [col.lower().replace(' ', '_') for col in df.columns]
            return df
        except Exception as e:
            print(f"Error: {e}")
            return pd.DataFrame()

    def _calculate_scalping_indicators(self):
        df = self.df

        df['EMA_5'] = ta.trend.ema_indicator(df['close'], window=5)
        df['EMA_8'] = ta.trend.ema_indicator(df['close'], window=8)
        df['EMA_13'] = ta.trend.ema_indicator(df['close'], window=13)
        df['EMA_21'] = ta.trend.ema_indicator(df['close'], window=21)

        df['SMA_9'] = ta.trend.sma_indicator(df['close'], window=9)
        df['SMA_20'] = ta.trend.sma_indicator(df['close'], window=20)

        macd = ta.trend.MACD(df['close'], window_slow=26, window_fast=12, window_sign=9)
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()

        df['RSI_7'] = ta.momentum.rsi(df['close'], window=7)
        df['RSI_14'] = ta.momentum.rsi(df['close'], window=14)

        stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'], window=14, smooth_window=3)
        df['Stoch_K'] = stoch.stoch()
        df['Stoch_D'] = stoch.stoch_signal()

        df['Williams_R'] = ta.momentum.williams_r(df['high'], df['low'], df['close'], lbp=14)

        df['CCI'] = ta.trend.cci(df['high'], df['low'], df['close'], window=20)

        df['MFI'] = ta.volume.money_flow_index(df['high'], df['low'], df['close'], df['volume'], window=14)

        bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
        df['BB_Upper'] = bb.bollinger_hband()
        df['BB_Middle'] = bb.bollinger_mavg()
        df['BB_Lower'] = bb.bollinger_lband()
        df['BB_Width'] = bb.bollinger_wband()

        df['ATR_14'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)

        df['VWAP'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()

        df['OBV'] = ta.volume.on_balance_volume(df['close'], df['volume'])

        df['ROC'] = ta.momentum.roc(df['close'], window=10)

        df['Daily_Return'] = df['close'].pct_change()
        df['Volatility'] = df['Daily_Return'].rolling(window=20).std() * np.sqrt(252)

        df['Price_Change'] = df['close'].pct_change()
        df['Volume_Change'] = df['volume'].pct_change()

        df['Range'] = df['high'] - df['low']
        df['Avg_Range'] = df['Range'].rolling(window=20).mean()

        self.df = df

    def get_scalping_signals(self):
        if self.df.empty:
            return []

        df = self.df
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest

        signals = []

        if pd.notna(latest.get('EMA_5')) and pd.notna(latest.get('EMA_13')):
            if prev['EMA_5'] < prev['EMA_13'] and latest['EMA_5'] >= latest['EMA_13']:
                signals.append({
                    'type': 'BUY',
                    'indicator': 'EMA Crossover (5/13)',
                    'strength': 'Strong',
                    'entry': latest['close'],
                    'stop_loss': latest['close'] - (latest['ATR_14'] * 1.5) if pd.notna(latest.get('ATR_14')) else latest['close'] * 0.98,
                    'target': latest['close'] + (latest['ATR_14'] * 2) if pd.notna(latest.get('ATR_14')) else latest['close'] * 1.02,
                    'timeframe': '5m'
                })
            elif prev['EMA_5'] > prev['EMA_13'] and latest['EMA_5'] <= latest['EMA_13']:
                signals.append({
                    'type': 'SELL',
                    'indicator': 'EMA Crossover (5/13)',
                    'strength': 'Strong',
                    'entry': latest['close'],
                    'stop_loss': latest['close'] + (latest['ATR_14'] * 1.5) if pd.notna(latest.get('ATR_14')) else latest['close'] * 1.02,
                    'target': latest['close'] - (latest['ATR_14'] * 2) if pd.notna(latest.get('ATR_14')) else latest['close'] * 0.98,
                    'timeframe': '5m'
                })

        if pd.notna(latest.get('RSI_7')):
            if prev['RSI_7'] < 30 and latest['RSI_7'] >= 30:
                signals.append({
                    'type': 'BUY',
                    'indicator': 'RSI 7 Oversold Bounce',
                    'strength': 'Medium',
                    'entry': latest['close'],
                    'stop_loss': latest['close'] - (latest['ATR_14'] * 1) if pd.notna(latest.get('ATR_14')) else latest['close'] * 0.99,
                    'target': latest['close'] + (latest['ATR_14'] * 1.5) if pd.notna(latest.get('ATR_14')) else latest['close'] * 1.01,
                    'timeframe': '5m'
                })
            elif prev['RSI_7'] > 70 and latest['RSI_7'] <= 70:
                signals.append({
                    'type': 'SELL',
                    'indicator': 'RSI 7 Overbought Reversal',
                    'strength': 'Medium',
                    'entry': latest['close'],
                    'stop_loss': latest['close'] + (latest['ATR_14'] * 1) if pd.notna(latest.get('ATR_14')) else latest['close'] * 1.01,
                    'target': latest['close'] - (latest['ATR_14'] * 1.5) if pd.notna(latest.get('ATR_14')) else latest['close'] * 0.99,
                    'timeframe': '5m'
                })

        if pd.notna(latest.get('close')) and pd.notna(latest.get('BB_Lower')) and pd.notna(latest.get('BB_Upper')):
            bb_position = (latest['close'] - latest['BB_Lower']) / (latest['BB_Upper'] - latest['BB_Lower'])

            if bb_position < 0.1:
                signals.append({
                    'type': 'BUY',
                    'indicator': 'Bollinger Band Lower Touch',
                    'strength': 'Medium',
                    'entry': latest['close'],
                    'stop_loss': latest['BB_Lower'] - (latest['ATR_14'] * 0.5) if pd.notna(latest.get('ATR_14')) else latest['BB_Lower'] * 0.99,
                    'target': latest['BB_Middle'],
                    'timeframe': '5m'
                })
            elif bb_position > 0.9:
                signals.append({
                    'type': 'SELL',
                    'indicator': 'Bollinger Band Upper Touch',
                    'strength': 'Medium',
                    'entry': latest['close'],
                    'stop_loss': latest['BB_Upper'] + (latest['ATR_14'] * 0.5) if pd.notna(latest.get('ATR_14')) else latest['BB_Upper'] * 1.01,
                    'target': latest['BB_Middle'],
                    'timeframe': '5m'
                })

        if pd.notna(latest.get('Stoch_K')) and pd.notna(latest.get('Stoch_D')):
            if prev['Stoch_K'] < prev['Stoch_D'] and latest['Stoch_K'] >= latest['Stoch_D'] and latest['Stoch_K'] < 20:
                signals.append({
                    'type': 'BUY',
                    'indicator': 'Stochastic Bullish Crossover (Oversold)',
                    'strength': 'Strong',
                    'entry': latest['close'],
                    'stop_loss': latest['close'] - (latest['ATR_14'] * 1.5) if pd.notna(latest.get('ATR_14')) else latest['close'] * 0.98,
                    'target': latest['close'] + (latest['ATR_14'] * 2) if pd.notna(latest.get('ATR_14')) else latest['close'] * 1.02,
                    'timeframe': '5m'
                })
            elif prev['Stoch_K'] > prev['Stoch_D'] and latest['Stoch_K'] <= latest['Stoch_D'] and latest['Stoch_K'] > 80:
                signals.append({
                    'type': 'SELL',
                    'indicator': 'Stochastic Bearish Crossover (Overbought)',
                    'strength': 'Strong',
                    'entry': latest['close'],
                    'stop_loss': latest['close'] + (latest['ATR_14'] * 1.5) if pd.notna(latest.get('ATR_14')) else latest['close'] * 1.02,
                    'target': latest['close'] - (latest['ATR_14'] * 2) if pd.notna(latest.get('ATR_14')) else latest['close'] * 0.98,
                    'timeframe': '5m'
                })

        if pd.notna(latest.get('MFI')):
            if latest['MFI'] < 20:
                signals.append({
                    'type': 'BUY',
                    'indicator': 'MFI Oversold',
                    'strength': 'Medium',
                    'entry': latest['close'],
                    'stop_loss': latest['close'] - (latest['ATR_14'] * 1) if pd.notna(latest.get('ATR_14')) else latest['close'] * 0.99,
                    'target': latest['close'] + (latest['ATR_14'] * 1.5) if pd.notna(latest.get('ATR_14')) else latest['close'] * 1.01,
                    'timeframe': '5m'
                })
            elif latest['MFI'] > 80:
                signals.append({
                    'type': 'SELL',
                    'indicator': 'MFI Overbought',
                    'strength': 'Medium',
                    'entry': latest['close'],
                    'stop_loss': latest['close'] + (latest['ATR_14'] * 1) if pd.notna(latest.get('ATR_14')) else latest['close'] * 1.01,
                    'target': latest['close'] - (latest['ATR_14'] * 1.5) if pd.notna(latest.get('ATR_14')) else latest['close'] * 0.99,
                    'timeframe': '5m'
                })

        if pd.notna(latest.get('close')) and pd.notna(latest.get('VWAP')):
            if prev['close'] < prev['VWAP'] and latest['close'] >= latest['VWAP']:
                signals.append({
                    'type': 'BUY',
                    'indicator': 'VWAP Breakout',
                    'strength': 'Medium',
                    'entry': latest['close'],
                    'stop_loss': latest['VWAP'] - (latest['ATR_14'] * 0.5) if pd.notna(latest.get('ATR_14')) else latest['VWAP'] * 0.99,
                    'target': latest['close'] + (latest['ATR_14'] * 2) if pd.notna(latest.get('ATR_14')) else latest['close'] * 1.02,
                    'timeframe': '5m'
                })
            elif prev['close'] > prev['VWAP'] and latest['close'] <= latest['VWAP']:
                signals.append({
                    'type': 'SELL',
                    'indicator': 'VWAP Breakdown',
                    'strength': 'Medium',
                    'entry': latest['close'],
                    'stop_loss': latest['VWAP'] + (latest['ATR_14'] * 0.5) if pd.notna(latest.get('ATR_14')) else latest['VWAP'] * 1.01,
                    'target': latest['close'] - (latest['ATR_14'] * 2) if pd.notna(latest.get('ATR_14')) else latest['close'] * 0.98,
                    'timeframe': '5m'
                })

        if pd.notna(latest.get('close')) and pd.notna(latest.get('SMA_9')):
            if prev['close'] < prev['SMA_9'] and latest['close'] >= latest['SMA_9'] and latest.get('volume', 0) > df['volume'].rolling(20).mean().iloc[-1] * 1.5:
                signals.append({
                    'type': 'BUY',
                    'indicator': 'Price Cross SMA9 + Volume Spike',
                    'strength': 'Strong',
                    'entry': latest['close'],
                    'stop_loss': latest['SMA_9'] - (latest['ATR_14'] * 0.5) if pd.notna(latest.get('ATR_14')) else latest['SMA_9'] * 0.99,
                    'target': latest['close'] + (latest['ATR_14'] * 2.5) if pd.notna(latest.get('ATR_14')) else latest['close'] * 1.025,
                    'timeframe': '5m'
                })

        return signals

    def get_scalping_zones(self):
        if self.df.empty:
            return {}

        df = self.df.tail(50)
        latest = df.iloc[-1]

        support_levels = []
        resistance_levels = []

        for i in range(2, len(df) - 2):
            if df['low'].iloc[i] < df['low'].iloc[i-1] and df['low'].iloc[i] < df['low'].iloc[i-2] and \
               df['low'].iloc[i] < df['low'].iloc[i+1] and df['low'].iloc[i] < df['low'].iloc[i+2]:
                support_levels.append(df['low'].iloc[i])

            if df['high'].iloc[i] > df['high'].iloc[i-1] and df['high'].iloc[i] > df['high'].iloc[i-2] and \
               df['high'].iloc[i] > df['high'].iloc[i+1] and df['high'].iloc[i] > df['high'].iloc[i+2]:
                resistance_levels.append(df['high'].iloc[i])

        support_levels = sorted(set([round(s, 2) for s in support_levels if s < latest['close']]))[-3:]
        resistance_levels = sorted(set([round(r, 2) for r in resistance_levels if r > latest['close']]))[:3]

        atr = latest.get('ATR_14', latest['close'] * 0.01)

        return {
            'current_price': latest['close'],
            'immediate_support': support_levels[-1] if support_levels else latest['close'] - atr,
            'immediate_resistance': resistance_levels[0] if resistance_levels else latest['close'] + atr,
            'strong_support': support_levels[-2] if len(support_levels) > 1 else latest['close'] - (atr * 2),
            'strong_resistance': resistance_levels[1] if len(resistance_levels) > 1 else latest['close'] + (atr * 2),
            'all_supports': support_levels,
            'all_resistances': resistance_levels,
            'atr': atr,
            'stop_loss_distance': atr * 1.5,
            'target_distance': atr * 2
        }

    def get_scalping_metrics(self):
        if self.df.empty:
            return {}

        df = self.df
        latest = df.iloc[-1]

        spread = latest['high'] - latest['low']
        avg_spread = df['Range'].rolling(20).mean().iloc[-1] if 'Range' in df else spread

        volume_avg = df['volume'].rolling(20).mean().iloc[-1]
        volume_ratio = latest['volume'] / volume_avg if volume_avg > 0 else 1

        price_position = (latest['close'] - df['low'].rolling(20).min().iloc[-1]) / \
                         (df['high'].rolling(20).max().iloc[-1] - df['low'].rolling(20).min().iloc[-1])

        momentum = latest.get('ROC', 0)

        return {
            'current_price': latest['close'],
            'spread': spread,
            'avg_spread': avg_spread,
            'spread_ratio': spread / avg_spread if avg_spread > 0 else 1,
            'volume': latest['volume'],
            'volume_avg': volume_avg,
            'volume_ratio': volume_ratio,
            'volume_status': 'High' if volume_ratio > 1.5 else 'Normal' if volume_ratio > 0.7 else 'Low',
            'price_position': price_position,
            'momentum': momentum,
            'atr': latest.get('ATR_14', 0),
            'volatility': latest.get('Volatility', 0),
            'rsi_7': latest.get('RSI_7', 50),
            'rsi_14': latest.get('RSI_14', 50),
            'stoch_k': latest.get('Stoch_K', 50),
            'stoch_d': latest.get('Stoch_D', 50),
            'mfi': latest.get('MFI', 50),
        }

    def create_scalping_chart(self, last_n_bars=100):
        if self.df.empty:
            return None

        df = self.df.tail(last_n_bars)

        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.4, 0.15, 0.15, 0.3],
            subplot_titles=('Price & EMAs', 'Volume', 'RSI', 'Stochastic')
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

        if 'EMA_5' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_5'], name='EMA 5',
                                     line=dict(color='cyan', width=1)), row=1, col=1)
        if 'EMA_13' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_13'], name='EMA 13',
                                     line=dict(color='yellow', width=1)), row=1, col=1)
        if 'EMA_21' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], name='EMA 21',
                                     line=dict(color='orange', width=1)), row=1, col=1)

        if 'BB_Upper' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper',
                                     line=dict(color='gray', width=1, dash='dash')), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower',
                                     line=dict(color='gray', width=1, dash='dash'),
                                     fill='tonexty', fillcolor='rgba(128,128,128,0.1)'), row=1, col=1)

        if 'VWAP' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], name='VWAP',
                                     line=dict(color='magenta', width=2)), row=1, col=1)

        colors = ['green' if row['close'] >= row['open'] else 'red' for idx, row in df.iterrows()]
        fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='Volume',
                             marker_color=colors), row=2, col=1)

        if 'RSI_7' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['RSI_7'], name='RSI 7',
                                     line=dict(color='cyan', width=1.5)), row=3, col=1)
        if 'RSI_14' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['RSI_14'], name='RSI 14',
                                     line=dict(color='yellow', width=1.5)), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

        if 'Stoch_K' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['Stoch_K'], name='Stoch K',
                                     line=dict(color='cyan', width=1.5)), row=4, col=1)
        if 'Stoch_D' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['Stoch_D'], name='Stoch D',
                                     line=dict(color='orange', width=1.5)), row=4, col=1)
        fig.add_hline(y=80, line_dash="dash", line_color="red", row=4, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="green", row=4, col=1)

        fig.update_layout(
            height=800,
            xaxis_rangeslider_visible=False,
            showlegend=True,
            template='plotly_dark',
            title_text=f"Scalping Chart - {self.symbol}"
        )

        return fig

    def get_scalping_plan(self):
        signals = self.get_scalping_signals()
        zones = self.get_scalping_zones()
        metrics = self.get_scalping_metrics()

        plan = {
            'symbol': self.symbol,
            'current_price': zones.get('current_price', 0),
            'signals': signals,
            'zones': zones,
            'metrics': metrics,
            'risk_management': {
                'max_loss_per_trade': '1-2% of capital',
                'recommended_position_size': self._calculate_position_size(zones, metrics),
                'stop_loss': zones.get('immediate_support', 0),
                'take_profit_1': zones.get('immediate_resistance', 0),
                'take_profit_2': zones.get('strong_resistance', 0),
                'risk_reward_ratio': '1:2 minimum'
            },
            'scalping_checklist': self._create_checklist(metrics, signals)
        }

        return plan

    def _calculate_position_size(self, zones, metrics):
        atr = zones.get('atr', 0)
        current_price = zones.get('current_price', 0)

        if atr > 0 and current_price > 0:
            risk_per_share = atr * 1.5
            position_size = f"Max {int(10000 / risk_per_share)} shares per Rp 10,000 risk"
            return position_size

        return "Calculate based on ATR"

    def _create_checklist(self, metrics, signals):
        checklist = []

        rsi = metrics.get('rsi_7', 50)
        if rsi < 30:
            checklist.append("✅ RSI Oversold - Potential Buy")
        elif rsi > 70:
            checklist.append("🔴 RSI Overbought - Potential Sell")
        else:
            checklist.append("⚪ RSI Neutral")

        vol_ratio = metrics.get('volume_ratio', 1)
        if vol_ratio > 1.5:
            checklist.append("✅ High Volume - Good Liquidity")
        elif vol_ratio < 0.5:
            checklist.append("⚠️ Low Volume - Be Careful")
        else:
            checklist.append("⚪ Normal Volume")

        stoch_k = metrics.get('stoch_k', 50)
        if stoch_k < 20:
            checklist.append("✅ Stochastic Oversold")
        elif stoch_k > 80:
            checklist.append("🔴 Stochastic Overbought")
        else:
            checklist.append("⚪ Stochastic Neutral")

        spread_ratio = metrics.get('spread_ratio', 1)
        if spread_ratio > 2:
            checklist.append("⚠️ Wide Spread - Avoid Scalping")
        else:
            checklist.append("✅ Normal Spread")

        if any(s['type'] == 'BUY' for s in signals):
            checklist.append("✅ BUY Signal Detected")
        elif any(s['type'] == 'SELL' for s in signals):
            checklist.append("🔴 SELL Signal Detected")
        else:
            checklist.append("⚪ No Clear Signal")

        return checklist

import pandas as pd
import numpy as np
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.techindicators import TechIndicators
import yfinance as yf
from datetime import datetime, timedelta
import time

# Import config
try:
    from config import ALPHA_VANTAGE_API_KEY, IDX_SUFFIX, IDX_STOCKS
except ImportError:
    ALPHA_VANTAGE_API_KEY = 'demo'
    IDX_SUFFIX = '.JK'
    IDX_STOCKS = {}

class StockDataFetcher:
    def __init__(self):
        self.av_api_key = ALPHA_VANTAGE_API_KEY
        self.ts = TimeSeries(key=self.av_api_key, output_format='pandas')
        self.fd = FundamentalData(key=self.av_api_key, output_format='pandas')
        self.ti = TechIndicators(key=self.av_api_key, output_format='pandas')
        self.cache = {}
        self.last_request_time = 0
        self.min_interval = 12.5

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

    def get_stock_data(self, symbol, period='1y', interval='daily'):
        cache_key = f"{symbol}_{period}_{interval}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        ticker = f"{symbol}{IDX_SUFFIX}"
        stock = yf.Ticker(ticker)

        period_map = {
            '1d': '1d', '5d': '5d', '1mo': '1mo',
            '3mo': '3mo', '6mo': '6mo', '1y': '1y',
            '2y': '2y', '5y': '5y', '10y': '10y', 'max': 'max'
        }

        # Try multiple attempts
        for attempt in range(3):
            try:
                df = stock.history(period=period_map.get(period, '1y'))

                if not df.empty:
                    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
                    self.cache[cache_key] = df
                    return df
            except Exception as e:
                print(f"Attempt {attempt+1} failed for {symbol}: {e}")
                time.sleep(1)

        # Fallback: try shorter period
        try:
            df = stock.history(period='1mo')
            if not df.empty:
                df.columns = [col.lower().replace(' ', '_') for col in df.columns]
                self.cache[cache_key] = df
                return df
        except:
            pass

        return pd.DataFrame()

    def get_realtime_quote(self, symbol):
        try:
            ticker = f"{symbol}{IDX_SUFFIX}"
            stock = yf.Ticker(ticker)
            
            # Try to get info with retry
            info = None
            for attempt in range(3):
                try:
                    info = stock.info
                    if info and 'regularMarketPrice' in info:
                        break
                except:
                    time.sleep(1)
            
            if not info or 'regularMarketPrice' not in info:
                # Fallback: try to get price from history
                try:
                    hist = stock.history(period='1d')
                    if not hist.empty:
                        last_price = hist['Close'].iloc[-1]
                        prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else last_price
                        return {
                            'symbol': symbol,
                            'name': IDX_STOCKS.get(symbol, symbol),
                            'price': float(last_price),
                            'change': float(last_price - prev_price),
                            'change_percent': float((last_price - prev_price) / prev_price * 100) if prev_price else 0,
                            'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0,
                            'market_cap': 0,
                            'pe_ratio': None,
                            'pb_ratio': None,
                            'dividend_yield': None,
                            'high_52w': float(hist['High'].max()),
                            'low_52w': float(hist['Low'].min()),
                        }
                except:
                    pass
                
                # Last resort: return minimal data
                return {
                    'symbol': symbol,
                    'name': IDX_STOCKS.get(symbol, symbol),
                    'price': 0,
                    'change': 0,
                    'change_percent': 0,
                    'volume': 0,
                    'market_cap': 0,
                    'pe_ratio': None,
                    'pb_ratio': None,
                    'dividend_yield': None,
                    'high_52w': None,
                    'low_52w': None,
                }
            
            return {
                'symbol': symbol,
                'name': info.get('longName', IDX_STOCKS.get(symbol, symbol)),
                'price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'change': info.get('regularMarketChange', 0),
                'change_percent': info.get('regularMarketChangePercent', 0),
                'volume': info.get('volume', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', None),
                'pb_ratio': info.get('priceToBook', None),
                'dividend_yield': info.get('dividendYield', None),
                'high_52w': info.get('fiftyTwoWeekHigh', None),
                'low_52w': info.get('fiftyTwoWeekLow', None),
            }
        except Exception as e:
            print(f"Error getting quote for {symbol}: {e}")
            return {
                'symbol': symbol,
                'name': IDX_STOCKS.get(symbol, symbol),
                'price': 0,
                'change': 0,
                'change_percent': 0,
                'volume': 0,
                'market_cap': 0,
                'pe_ratio': None,
                'pb_ratio': None,
                'dividend_yield': None,
                'high_52w': None,
                'low_52w': None,
            }

    def get_company_info(self, symbol):
        try:
            ticker = f"{symbol}{IDX_SUFFIX}"
            stock = yf.Ticker(ticker)
            info = stock.info

            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'description': info.get('longBusinessSummary', 'N/A'),
                'website': info.get('website', 'N/A'),
                'employees': info.get('fullTimeEmployees', 'N/A'),
                'country': info.get('country', 'Indonesia'),
                'ceo': info.get('companyOfficers', [{}])[0].get('name', 'N/A') if info.get('companyOfficers') else 'N/A',
            }
        except Exception as e:
            print(f"Error getting company info for {symbol}: {e}")
            return None

    def get_financial_statements(self, symbol):
        try:
            ticker = f"{symbol}{IDX_SUFFIX}"
            stock = yf.Ticker(ticker)

            income = stock.income_stmt
            balance = stock.balance_sheet
            cashflow = stock.cashflow

            return {
                'income_statement': income,
                'balance_sheet': balance,
                'cash_flow': cashflow
            }
        except Exception as e:
            print(f"Error getting financials for {symbol}: {e}")
            return None

    def get_key_metrics(self, symbol):
        try:
            ticker = f"{symbol}{IDX_SUFFIX}"
            stock = yf.Ticker(ticker)
            info = stock.info

            metrics = {
                'Market Cap': info.get('marketCap', 'N/A'),
                'Enterprise Value': info.get('enterpriseValue', 'N/A'),
                'Trailing PE': info.get('trailingPE', 'N/A'),
                'Forward PE': info.get('forwardPE', 'N/A'),
                'PEG Ratio': info.get('pegRatio', 'N/A'),
                'Price to Sales': info.get('priceToSalesTrailing12Months', 'N/A'),
                'Price to Book': info.get('priceToBook', 'N/A'),
                'EV to Revenue': info.get('enterpriseToRevenue', 'N/A'),
                'EV to EBITDA': info.get('enterpriseToEbitda', 'N/A'),
                'Dividend Yield': info.get('dividendYield', 'N/A'),
                'Dividend Rate': info.get('dividendRate', 'N/A'),
                'Payout Ratio': info.get('payoutRatio', 'N/A'),
                'ROE': info.get('returnOnEquity', 'N/A'),
                'ROA': info.get('returnOnAssets', 'N/A'),
                'Revenue': info.get('totalRevenue', 'N/A'),
                'Revenue Growth': info.get('revenueGrowth', 'N/A'),
                'Gross Margin': info.get('grossMargins', 'N/A'),
                'EBITDA Margin': info.get('ebitdaMargins', 'N/A'),
                'Operating Margin': info.get('operatingMargins', 'N/A'),
                'Profit Margin': info.get('profitMargins', 'N/A'),
                'Debt to Equity': info.get('debtToEquity', 'N/A'),
                'Current Ratio': info.get('currentRatio', 'N/A'),
                'Quick Ratio': info.get('quickRatio', 'N/A'),
                'Book Value': info.get('bookValue', 'N/A'),
                'Price to Cash Flow': info.get('priceToCashFlow', 'N/A'),
                'Free Cash Flow': info.get('freeCashflow', 'N/A'),
                'Operating Cash Flow': info.get('operatingCashflow', 'N/A'),
                'Beta': info.get('beta', 'N/A'),
                '52 Week High': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52 Week Low': info.get('fiftyTwoWeekLow', 'N/A'),
                '50 Day MA': info.get('fiftyDayAverage', 'N/A'),
                '200 Day MA': info.get('twoHundredDayAverage', 'N/A'),
            }

            for key, value in metrics.items():
                if value == 'N/A':
                    continue
                if isinstance(value, (int, float)):
                    if 'Margin' in key or 'Yield' in key or 'Ratio' in key or 'ROE' in key or 'ROA' in key:
                        metrics[key] = f"{value * 100:.2f}%" if abs(value) < 10 else f"{value:.2f}%"
                    elif 'Market Cap' in key or 'Revenue' in key or 'EBITDA' in key or 'Cash Flow' in key:
                        if abs(value) >= 1e12:
                            metrics[key] = f"Rp {value/1e12:.2f} T"
                        elif abs(value) >= 1e9:
                            metrics[key] = f"Rp {value/1e9:.2f} B"
                        elif abs(value) >= 1e6:
                            metrics[key] = f"Rp {value/1e6:.2f} M"
                        else:
                            metrics[key] = f"Rp {value:,.0f}"
                    else:
                        metrics[key] = f"{value:.2f}"

            return metrics

        except Exception as e:
            print(f"Error getting metrics for {symbol}: {e}")
            return None

    def get_multiple_stocks(self, symbols, period='6mo'):
        all_data = {}
        for symbol in symbols:
            df = self.get_stock_data(symbol, period)
            if not df.empty:
                all_data[symbol] = df
            time.sleep(0.5)
        return all_data

    def search_stock(self, query):
        results = []
        query_upper = query.upper()

        for symbol, name in IDX_STOCKS.items():
            if query_upper in symbol or query_upper in name.upper():
                results.append({'symbol': symbol, 'name': name})

        return results

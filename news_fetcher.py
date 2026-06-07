import requests
import pandas as pd
from datetime import datetime, timedelta
from textblob import TextBlob
import feedparser
import re
from config import IDX_STOCKS

class NewsFetcher:
    def __init__(self):
        self.news_sources = {
            'yahoo_finance': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'google_news': 'https://news.google.com/rss/search',
            'reuters_business': 'https://www.rss-bridge.org/bridge01/?action=display&bridge=Reuters&feed=business&format=Atom',
            'cnbc_indonesia': 'https://www.cnbcindonesia.com/rss',
            'kontan': 'https://rss.kontan.co.id/news',
            'bisnis_com': 'https://www.bisnis.com/rss',
            '.idx': 'https://www.idx.co.id/ruang-info/berita',
        }

        self.indonesia_keywords = [
            'indonesia', 'ihsg', 'idx', 'bei', 'rupiah', 'bi rate',
            'bank indonesia', 'emiten', 'saham', 'obligasi', 'komoditas',
            'nickel', 'coal', 'palm oil', 'cpo', 'timah', 'tembaga'
        ]

        self.global_keywords = [
            'fed', 'federal reserve', 'interest rate', 'inflation',
            'gdp', 'recession', 'trade war', 'tariff', 'geopolitics',
            'oil', 'gold', 'dollar', 'treasury', 'bond yield'
        ]

    def fetch_rss_news(self, source, query=None, max_items=20):
        news_items = []

        try:
            if source == 'yahoo_finance':
                url = f"{self.news_sources[source]}/s?symbol={query}&region=US&lang=en-US"
            elif source == 'google_news':
                search_query = f"{query} saham Indonesia" if query else "saham Indonesia"
                url = f"{self.news_sources[source]}/{search_query}&hl=id&gl=ID&ceid=ID:id"
            else:
                url = self.news_sources.get(source, '')

            if url:
                feed = feedparser.parse(url)

                for entry in feed.entries[:max_items]:
                    news_item = {
                        'title': entry.get('title', ''),
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', ''),
                        'published': entry.get('published', ''),
                        'source': source,
                        'sentiment': self.analyze_sentiment(entry.get('title', '') + ' ' + entry.get('summary', '')),
                        'relevance': self.calculate_relevance(entry.get('title', ''), query)
                    }
                    news_items.append(news_item)

        except Exception as e:
            print(f"Error fetching from {source}: {e}")

        return news_items

    def fetch_stock_news(self, symbol, max_items=30):
        all_news = []

        for source in ['yahoo_finance', 'google_news']:
            try:
                news = self.fetch_rss_news(source, symbol, max_items=max_items // 2)
                all_news.extend(news)
            except Exception as e:
                print(f"Error fetching from {source}: {e}")

        # Fallback: generate sample news if empty
        if not all_news:
            stock_name = IDX_STOCKS.get(symbol, symbol)
            all_news = [
                {
                    'title': f'{stock_name} ({symbol}) - Data berita tidak tersedia dari sumber eksternal',
                    'link': f'https://finance.yahoo.com/quote/{symbol}.JK',
                    'summary': f'Berita untuk {stock_name} belum tersedia. Silakan kunjungi Yahoo Finance untuk berita terbaru.',
                    'published': '',
                    'source': 'system',
                    'sentiment': {'polarity': 0, 'subjectivity': 0, 'label': 'Neutral'},
                    'relevance': 1.0,
                },
                {
                    'title': f'Analisa {stock_name} - kunjungi marketplace saham untuk berita terkini',
                    'link': f'https://www.google.com/search?q={symbol}+saham+berita',
                    'summary': f'Untuk berita terbaru tentang {stock_name}, silakan kunjungi portal berita keuangan.',
                    'published': '',
                    'source': 'system',
                    'sentiment': {'polarity': 0, 'subjectivity': 0, 'label': 'Neutral'},
                    'relevance': 0.5,
                },
            ]

        all_news.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        return all_news[:max_items]

    def fetch_market_news(self, category='general', max_items=30):
        all_news = []

        sources = ['google_news', 'cnbc_indonesia', 'kontan']

        for source in sources:
            try:
                news = self.fetch_rss_news(source, max_items=max_items // len(sources))
                all_news.extend(news)
            except Exception:
                continue

        market_keywords = ['ihsg', 'bej', 'bursa', 'saham', 'index']
        for news in all_news:
            title_lower = news.get('title', '').lower()
            news['market_relevance'] = any(kw in title_lower for kw in market_keywords)

        all_news.sort(key=lambda x: x.get('published', ''), reverse=True)
        return all_news[:max_items]

    def fetch_geopolitical_news(self, max_items=25):
        all_news = []

        geopolitics_queries = [
            'geopolitics economy',
            'trade war tariff',
            'oil price opec',
            'fed interest rate',
            'china economy',
            'global recession'
        ]

        for query in geopolitics_queries:
            try:
                news = self.fetch_rss_news('google_news', query, max_items=5)
                all_news.extend(news)
            except Exception:
                continue

        all_news.sort(key=lambda x: x.get('sentiment', {}).get('polarity', 0), reverse=True)
        return all_news[:max_items]

    def analyze_sentiment(self, text):
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            if polarity > 0.3:
                label = 'Positive'
            elif polarity < -0.3:
                label = 'Negative'
            else:
                label = 'Neutral'

            return {
                'polarity': polarity,
                'subjectivity': subjectivity,
                'label': label
            }
        except Exception:
            return {'polarity': 0, 'subjectivity': 0, 'label': 'Neutral'}

    def calculate_relevance(self, text, query):
        if not query:
            return 0.5

        text_lower = text.lower()
        query_lower = query.lower()

        relevance = 0

        if query_lower in text_lower:
            relevance += 0.5

        stock_name = IDX_STOCKS.get(query.upper(), '').lower()
        if stock_name and stock_name in text_lower:
            relevance += 0.3

        for keyword in self.indonesia_keywords:
            if keyword in text_lower:
                relevance += 0.05

        return min(relevance, 1.0)

    def get_news_sentiment_summary(self, news_list):
        if not news_list:
            return {
                'total_news': 0,
                'avg_sentiment': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'sentiment_score': 'Neutral'
            }

        sentiments = [n.get('sentiment', {}).get('polarity', 0) for n in news_list]
        labels = [n.get('sentiment', {}).get('label', 'Neutral') for n in news_list]

        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        positive_count = labels.count('Positive')
        negative_count = labels.count('Negative')
        neutral_count = labels.count('Neutral')

        if avg_sentiment > 0.2:
            score = 'Bullish'
        elif avg_sentiment < -0.2:
            score = 'Bearish'
        else:
            score = 'Neutral'

        return {
            'total_news': len(news_list),
            'avg_sentiment': avg_sentiment,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'sentiment_score': score,
            'sentiment_distribution': {
                'positive': positive_count / len(news_list) * 100 if news_list else 0,
                'negative': negative_count / len(news_list) * 100 if news_list else 0,
                'neutral': neutral_count / len(news_list) * 100 if news_list else 0
            }
        }

    def get_news_impact(self, news_list):
        impacts = []

        high_impact_keywords = [
            'rate cut', 'rate hike', 'inflation', 'recession',
            'earnings', 'dividend', 'merger', 'acquisition',
            'regulation', 'ban', 'tariff', 'sanction'
        ]

        for news in news_list:
            title = news.get('title', '').lower()
            summary = news.get('summary', '').lower()
            combined = title + ' ' + summary

            impact_score = 0
            impact_factors = []

            for kw in high_impact_keywords:
                if kw in combined:
                    impact_score += 1
                    impact_factors.append(kw)

            sentiment = news.get('sentiment', {}).get('polarity', 0)
            if abs(sentiment) > 0.5:
                impact_score += 1
                impact_factors.append('high_sentiment')

            if news.get('relevance', 0) > 0.7:
                impact_score += 1
                impact_factors.append('high_relevance')

            impacts.append({
                'title': news.get('title', ''),
                'impact_score': impact_score,
                'impact_factors': impact_factors,
                'sentiment': news.get('sentiment', {}),
                'link': news.get('link', '')
            })

        impacts.sort(key=lambda x: x['impact_score'], reverse=True)
        return impacts

    def get_sector_news(self, sector, max_items=15):
        sector_keywords = {
            'banking': ['bank', 'bi rate', 'kredit', 'perbankan'],
            'mining': ['tambang', 'mining', 'nickel', 'coal', 'timah'],
            'consumer': ['consumer', 'ritel', 'konsumeren', 'FMCG'],
            'technology': ['tech', 'digital', 'telko', 'telekomunikasi'],
            'property': ['properti', 'property', 'real estate', 'konstruksi'],
            'energy': ['energi', 'oil', 'gas', ' listrik', 'pln'],
        }

        keywords = sector_keywords.get(sector.lower(), [sector])
        all_news = []

        for keyword in keywords:
            news = self.fetch_rss_news('google_news', keyword, max_items=5)
            all_news.extend(news)

        unique_news = []
        seen_titles = set()
        for news in all_news:
            title = news.get('title', '')
            if title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(news)

        return unique_news[:max_items]

    def format_news_for_display(self, news_list):
        formatted = []

        for news in news_list:
            sentiment = news.get('sentiment', {})
            polarity = sentiment.get('polarity', 0)

            if polarity > 0.2:
                sentiment_icon = '🟢'
            elif polarity < -0.2:
                sentiment_icon = '🔴'
            else:
                sentiment_icon = '⚪'

            formatted.append({
                'icon': sentiment_icon,
                'title': news.get('title', 'No Title'),
                'sentiment': sentiment.get('label', 'Neutral'),
                'sentiment_score': f"{polarity:.2f}",
                'source': news.get('source', 'Unknown'),
                'published': news.get('published', 'N/A'),
                'link': news.get('link', '#'),
                'relevance': f"{news.get('relevance', 0):.0%}"
            })

        return formatted

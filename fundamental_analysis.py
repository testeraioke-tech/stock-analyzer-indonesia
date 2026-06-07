import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class FundamentalAnalyzer:
    def __init__(self, financials, metrics, company_info):
        self.financials = financials
        self.metrics = metrics
        self.company_info = company_info

    def get_valuation_score(self):
        score = 0
        max_score = 0

        pe = self._parse_metric(self.metrics.get('Trailing PE'))
        pb = self._parse_metric(self.metrics.get('Price to Book'))
        ps = self._parse_metric(self.metrics.get('Price to Sales'))
        ev_ebitda = self._parse_metric(self.metrics.get('EV to EBITDA'))

        if pe is not None:
            max_score += 25
            if pe < 10:
                score += 25
            elif pe < 15:
                score += 20
            elif pe < 20:
                score += 15
            elif pe < 25:
                score += 10
            else:
                score += 5

        if pb is not None:
            max_score += 25
            if pb < 1:
                score += 25
            elif pb < 2:
                score += 20
            elif pb < 3:
                score += 15
            elif pb < 5:
                score += 10
            else:
                score += 5

        if ps is not None:
            max_score += 25
            if ps < 1:
                score += 25
            elif ps < 2:
                score += 20
            elif ps < 3:
                score += 15
            elif ps < 5:
                score += 10
            else:
                score += 5

        if ev_ebitda is not None:
            max_score += 25
            if ev_ebitda < 5:
                score += 25
            elif ev_ebitda < 10:
                score += 20
            elif ev_ebitda < 15:
                score += 15
            elif ev_ebitda < 20:
                score += 10
            else:
                score += 5

        if max_score > 0:
            return (score / max_score) * 100
        return None

    def get_profitability_score(self):
        score = 0
        max_score = 0

        roe = self._parse_percent(self.metrics.get('ROE'))
        roa = self._parse_percent(self.metrics.get('ROA'))
        gm = self._parse_percent(self.metrics.get('Gross Margin'))
        om = self._parse_percent(self.metrics.get('Operating Margin'))
        nm = self._parse_percent(self.metrics.get('Profit Margin'))

        if roe is not None:
            max_score += 25
            if roe > 20:
                score += 25
            elif roe > 15:
                score += 20
            elif roe > 10:
                score += 15
            elif roe > 5:
                score += 10
            else:
                score += 5

        if roa is not None:
            max_score += 25
            if roa > 10:
                score += 25
            elif roa > 7:
                score += 20
            elif roa > 5:
                score += 15
            elif roa > 3:
                score += 10
            else:
                score += 5

        if gm is not None:
            max_score += 15
            if gm > 50:
                score += 15
            elif gm > 40:
                score += 12
            elif gm > 30:
                score += 10
            elif gm > 20:
                score += 7
            else:
                score += 3

        if om is not None:
            max_score += 15
            if om > 25:
                score += 15
            elif om > 20:
                score += 12
            elif om > 15:
                score += 10
            elif om > 10:
                score += 7
            else:
                score += 3

        if nm is not None:
            max_score += 20
            if nm > 20:
                score += 20
            elif nm > 15:
                score += 16
            elif nm > 10:
                score += 12
            elif nm > 5:
                score += 8
            else:
                score += 4

        if max_score > 0:
            return (score / max_score) * 100
        return None

    def get_financial_health_score(self):
        score = 0
        max_score = 0

        de = self._parse_metric(self.metrics.get('Debt to Equity'))
        cr = self._parse_metric(self.metrics.get('Current Ratio'))
        qr = self._parse_metric(self.metrics.get('Quick Ratio'))

        if de is not None:
            max_score += 35
            if de < 50:
                score += 35
            elif de < 100:
                score += 28
            elif de < 150:
                score += 21
            elif de < 200:
                score += 14
            else:
                score += 7

        if cr is not None:
            max_score += 35
            if cr > 2:
                score += 35
            elif cr > 1.5:
                score += 28
            elif cr > 1:
                score += 21
            elif cr > 0.8:
                score += 14
            else:
                score += 7

        if qr is not None:
            max_score += 30
            if qr > 1.5:
                score += 30
            elif qr > 1:
                score += 24
            elif qr > 0.7:
                score += 18
            elif qr > 0.5:
                score += 12
            else:
                score += 6

        if max_score > 0:
            return (score / max_score) * 100
        return None

    def get_growth_score(self):
        score = 0
        max_score = 0

        rev_growth = self._parse_percent(self.metrics.get('Revenue Growth'))

        if rev_growth is not None:
            max_score += 50
            if rev_growth > 20:
                score += 50
            elif rev_growth > 15:
                score += 40
            elif rev_growth > 10:
                score += 30
            elif rev_growth > 5:
                score += 20
            else:
                score += 10

        if self.financials.get('income_statement') is not None:
            income = self.financials['income_statement']
            if not income.empty and len(income.columns) >= 2:
                max_score += 50
                latest = income.iloc[:, 0]
                prev = income.iloc[:, 1]

                if 'Total Revenue' in latest.index and 'Total Revenue' in prev.index:
                    rev_growth_actual = (latest['Total Revenue'] - prev['Total Revenue']) / abs(prev['Total Revenue']) * 100
                    if rev_growth_actual > 20:
                        score += 25
                    elif rev_growth_actual > 10:
                        score += 20
                    elif rev_growth_actual > 0:
                        score += 15
                    else:
                        score += 5

                if 'Net Income' in latest.index and 'Net Income' in prev.index:
                    if prev['Net Income'] != 0:
                        ni_growth = (latest['Net Income'] - prev['Net Income']) / abs(prev['Net Income']) * 100
                        if ni_growth > 20:
                            score += 25
                        elif ni_growth > 10:
                            score += 20
                        elif ni_growth > 0:
                            score += 15
                        else:
                            score += 5

        if max_score > 0:
            return (score / max_score) * 100
        return None

    def get_dividend_score(self):
        score = 0
        max_score = 0

        div_yield = self._parse_percent(self.metrics.get('Dividend Yield'))
        payout = self._parse_percent(self.metrics.get('Payout Ratio'))

        if div_yield is not None:
            max_score += 60
            if div_yield > 5:
                score += 60
            elif div_yield > 4:
                score += 50
            elif div_yield > 3:
                score += 40
            elif div_yield > 2:
                score += 30
            elif div_yield > 1:
                score += 20
            else:
                score += 10

        if payout is not None:
            max_score += 40
            if 30 <= payout <= 60:
                score += 40
            elif 20 <= payout < 30 or 60 < payout <= 70:
                score += 32
            elif 10 <= payout < 20 or 70 < payout <= 80:
                score += 24
            else:
                score += 12

        if max_score > 0:
            return (score / max_score) * 100
        return None

    def get_overall_score(self):
        valuation = self.get_valuation_score()
        profitability = self.get_profitability_score()
        health = self.get_financial_health_score()
        growth = self.get_growth_score()
        dividend = self.get_dividend_score()

        scores = {
            'Valuation': valuation,
            'Profitability': profitability,
            'Financial Health': health,
            'Growth': growth,
            'Dividend': dividend
        }

        valid_scores = [s for s in scores.values() if s is not None]
        overall = np.mean(valid_scores) if valid_scores else None

        return {
            'overall': overall,
            'breakdown': scores
        }

    def get_investment_recommendation(self):
        scores = self.get_overall_score()
        overall = scores['overall']

        if overall is None:
            return {'recommendation': 'INSUFFICIENT DATA', 'confidence': 'Low'}

        if overall >= 75:
            rec = 'STRONG BUY'
            confidence = 'High'
        elif overall >= 60:
            rec = 'BUY'
            confidence = 'Medium-High'
        elif overall >= 45:
            rec = 'HOLD'
            confidence = 'Medium'
        elif overall >= 30:
            rec = 'SELL'
            confidence = 'Medium-High'
        else:
            rec = 'STRONG SELL'
            confidence = 'High'

        return {
            'recommendation': rec,
            'confidence': confidence,
            'overall_score': overall,
            'breakdown': scores['breakdown']
        }

    def create_financial_charts(self):
        if not self.financials.get('income_statement') is None:
            income = self.financials['income_statement']
            if not income.empty:
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('Revenue & Net Income', 'Margins', 'Balance Sheet', 'Cash Flow')
                )

                if 'Total Revenue' in income.index and 'Net Income' in income.index:
                    quarters = [str(q.date()) if hasattr(q, 'date') else str(q) for q in income.columns[:4]]
                    fig.add_trace(go.Bar(
                        x=quarters, y=income.loc['Total Revenue'].iloc[:4],
                        name='Revenue', marker_color='blue'
                    ), row=1, col=1)
                    fig.add_trace(go.Bar(
                        x=quarters, y=income.loc['Net Income'].iloc[:4],
                        name='Net Income', marker_color='green'
                    ), row=1, col=1)

                if self.financials.get('balance_sheet') is not None:
                    balance = self.financials['balance_sheet']
                    if not balance.empty:
                        quarters = [str(q.date()) if hasattr(q, 'date') else str(q) for q in balance.columns[:4]]
                        if 'Total Assets' in balance.index:
                            fig.add_trace(go.Bar(
                                x=quarters, y=balance.loc['Total Assets'].iloc[:4],
                                name='Total Assets', marker_color='lightblue'
                            ), row=1, col=2)
                        if 'Total Debt' in balance.index:
                            fig.add_trace(go.Bar(
                                x=quarters, y=balance.loc['Total Debt'].iloc[:4],
                                name='Total Debt', marker_color='red'
                            ), row=1, col=2)

                if self.financials.get('cash_flow') is not None:
                    cashflow = self.financials['cash_flow']
                    if not cashflow.empty:
                        quarters = [str(q.date()) if hasattr(q, 'date') else str(q) for q in cashflow.columns[:4]]
                        if 'Operating Cash Flow' in cashflow.index:
                            fig.add_trace(go.Bar(
                                x=quarters, y=cashflow.loc['Operating Cash Flow'].iloc[:4],
                                name='Operating CF', marker_color='green'
                            ), row=2, col=1)
                        if 'Free Cash Flow' in cashflow.index:
                            fig.add_trace(go.Bar(
                                x=quarters, y=cashflow.loc['Free Cash Flow'].iloc[:4],
                                name='Free CF', marker_color='orange'
                            ), row=2, col=1)

                fig.update_layout(
                    height=600,
                    showlegend=True,
                    template='plotly_dark',
                    title_text="Fundamental Analysis Charts"
                )

                return fig

        return None

    def _parse_metric(self, value):
        if value is None or value == 'N/A':
            return None
        if isinstance(value, (int, float)):
            return float(value)
        try:
            value_str = str(value).replace('%', '').replace(',', '').replace('Rp', '').strip()
            return float(value_str)
        except:
            return None

    def _parse_percent(self, value):
        if value is None or value == 'N/A':
            return None
        if isinstance(value, (int, float)):
            return float(value) * 100 if abs(value) < 10 else float(value)
        try:
            value_str = str(value).replace('%', '').replace(',', '').strip()
            return float(value_str)
        except:
            return None

    def get_full_analysis(self):
        return {
            'company_info': self.company_info,
            'metrics': self.metrics,
            'scores': self.get_overall_score(),
            'recommendation': self.get_investment_recommendation(),
            'financials': {
                'has_income': self.financials.get('income_statement') is not None and not self.financials['income_statement'].empty if self.financials.get('income_statement') is not None else False,
                'has_balance': self.financials.get('balance_sheet') is not None and not self.financials['balance_sheet'].empty if self.financials.get('balance_sheet') is not None else False,
                'has_cashflow': self.financials.get('cash_flow') is not None and not self.financials['cash_flow'].empty if self.financials.get('cash_flow') is not None else False,
            }
        }

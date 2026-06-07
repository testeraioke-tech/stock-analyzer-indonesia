import os
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')

IDX_STOCKS = {
    'BBCA': 'Bank Central Asia',
    'BBRI': 'Bank Rakyat Indonesia',
    'BMRI': 'Bank Mandiri',
    'BBNI': 'Bank Negara Indonesia',
    'TLKM': 'Telkom Indonesia',
    'ASII': 'Astra International',
    'UNVR': 'Unilever Indonesia',
    'HMSP': 'Hm Sampoerna',
    'GGRM': 'Gudang Garam',
    'SMGR': 'Semen Indonesia',
    'ADRO': 'Adaro Energy',
    'PTBA': 'Bukit Asam',
    'ITMG': 'Indo Tambangraya Megah',
    'INDF': 'Indofood Sukses Makmur',
    'ICBP': 'Indofood CBP Sukses Makmur',
    'KLBF': 'Kalbe Farma',
    'SIDO': 'Sido Muncul',
    'CPIN': 'Charoen Pokphand Indonesia',
    'JPFA': 'Japfa Comfeed Indonesia',
    'WIKA': 'Wijaya Karya',
    'WSKT': 'Waskita Karya',
    'BSDE': 'Bumi Serpong Damai',
    'SMRA': 'Summarecon Agung',
    'BSML': 'Bumi Star梅利亚',
    'EXCL': 'XL Axiata',
    'ISAT': 'Indosat Ooredoo',
    'TOWR': 'Sarana Menara Nusantara',
    'TBIG': 'Tower Bersama Infrastructure',
    'MDKA': 'Merdeka Copper Gold',
    'ANTM': 'Aneka Tambang',
    'INCO': 'Vale Indonesia',
    'TINS': 'Timah',
    'MDRN': 'Merdeka Battery Materials',
    'AKRA': 'AKR Corporindo',
    'TPIA': 'Chandra Asri Petrochemical',
    'INKP': 'Indah Kiat Pulp & Paper',
    'BRPT': 'Barito Pacific',
    'LPKR': 'Lippo Cikarang',
    'CTRA': 'Ciputra Development',
    'PWON': 'Pamularsari Putra Land',
    'PANI': 'Pani Indonesia',
}

IDX_SUFFIX = '.JK'

TECHNICAL_INDICATORS = [
    'SMA_20', 'SMA_50', 'SMA_200',
    'EMA_12', 'EMA_26',
    'RSI_14',
    'MACD', 'MACD_Signal', 'MACD_Hist',
    'BB_Upper', 'BB_Middle', 'BB_Lower',
    'ATR_14',
    'ADX_14',
    'OBV',
    'VWAP'
]

FUNDAMENTAL_METRICS = [
    'Market Cap', 'PE Ratio', 'PB Ratio',
    'Dividend Yield', 'EPS', 'ROE', 'ROA',
    'Debt to Equity', 'Current Ratio',
    'Revenue', 'Net Income', 'Gross Margin',
    'Operating Margin', 'Net Margin'
]

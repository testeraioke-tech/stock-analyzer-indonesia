import os
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')

IDX_STOCKS = {
    # === BIG CAP (Blue Chips) ===
    'BBCA': 'Bank Central Asia',
    'BBRI': 'Bank Rakyat Indonesia',
    'BMRI': 'Bank Mandiri',
    'BBNI': 'Bank Negara Indonesia',
    'TLKM': 'Telkom Indonesia',
    'ASII': 'Astra International',
    'UNVR': 'Unilever Indonesia',
    'HMSP': 'Hm Sampoerna',
    'GGRM': 'Gudang Garam',
    'ADRO': 'Adaro Energy',
    'PTBA': 'Bukit Asam',
    'ITMG': 'Indo Tambangraya Megah',
    'INDF': 'Indofood Sukses Makmur',
    'ICBP': 'Indofood CBP Sukses Makmur',
    
    # === BANKING ===
    'BRIS': 'Bank Syariah Indonesia',
    'BTPS': 'Bank BTPN Syariah',
    'MEGA': 'Bank Mega',
    'NISP': 'Bank OCBC NISP',
    'BNGA': 'Bank CIMB Niaga',
    'BTPX': 'Bank BTPN',
    'ARTO': 'Bank Jago',
    'BBYB': 'Bank Neo Commerce',
    'BBBS': 'Bank Bumi Arta',
    'AGRO': 'Bank Jasa Arta',
    'PNBN': 'Bank Pan Indonesia',
    'PNBS': 'Bank Panin Syariah',
    'NCLI': 'Bank Neo Commerce Tbk',
    'BDMN': 'Bank Danamon',
    
    # === TELECOMMUNICATION ===
    'EXCL': 'XL Axiata',
    'ISAT': 'Indosat Ooredoo',
    'FREN': 'Smartfren Telecom',
    'TBIG': 'Tower Bersama Infrastructure',
    'TOWR': 'Sarana Menara Nusantara',
    'MTEL': 'Tower Bersama Infrastructure',
    
    # === MINING & ENERGY ===
    'ANTM': 'Aneka Tambang',
    'INCO': 'Vale Indonesia',
    'TINS': 'Timah',
    'MDKA': 'Merdeka Copper Gold',
    'MDRN': 'Merdeka Battery Materials',
    'HRUM': 'Harum Energy',
    'BSSR': 'Borneo Iron',
    'INDY': 'Indika Energy',
    'BAPI': 'Bakrie & Brothers',
    'AKRA': 'AKR Corporindo',
    'ELSA': 'Elnusa',
    'RAJA': 'Rukun Raharja',
    'PGAS': 'Perusahaan Gas Negara',
    'MEDC': 'Medco Energi Internasional',
    'PWGR': 'Panwani Group',
    'ADMG': 'Adaro Minerals Indonesia',
    'ITMA': 'Itama Majorasari Makmur',
    'BBRM': 'Bakrie & Brothers',
    'INDR': 'Indofood Agri Resources',
    
    # === CONSUMER ===
    'SIDO': 'Sido Muncul',
    'CPIN': 'Charoen Pokphand Indonesia',
    'JPFA': 'Japfa Comfeed Indonesia',
    'MYOR': 'Mayora Indah',
    'KLBF': 'Kalbe Farma',
    'SDMU': 'Sudarmajaya Makmur',
    'GOOD': 'Good Year Indonesia',
    'IMAS': 'Indomobil Sukses Internasional',
    'RALS': 'Ramayana Lestari Sentosa',
    'MAPI': 'Mitra Adiperkasa',
    'LPPF': 'Lippo Retail Properti',
    'ACES': 'Ace Hardware Indonesia',
    'ERAA': 'Erajaya Swasembada',
    'SMSM': 'Selamat Sempurna',
    'ASGR': 'Astra Graphia',
    'TSPC': 'Tempo Scan Pacific',
    'MERK': 'Merck Tbk',
    'SIDO': 'Sido Muncul',
    
    # === PROPERTY & REAL ESTATE ===
    'BSDE': 'Bumi Serpong Damai',
    'SMRA': 'Summarecon Agung',
    'CTRA': 'Ciputra Development',
    'PWON': 'Pamularsari Putra Land',
    'LPKR': 'Lippo Cikarang',
    'PANI': 'Pani Indonesia',
    'DMAS': 'Damai Sejahtera Mandiri',
    'DILD': 'Duta Luas Propertindo',
    'ASRI': 'Alam Sutera Realty',
    'BSML': 'Bumi Star梅利亚',
    'COWL': 'Cowell Development',
    'DILD': 'Duta Luas Propertindo',
    'ELTY': 'Bakrieland Development',
    'INTP': 'Indocement Tunggal Prakarsa',
    'PANI': 'Pani Indonesia',
    'TARA': 'Bali Towerindo Sentra',
    
    # === INDUSTRIAL ===
    'SMGR': 'Semen Indonesia',
    'INTP': 'Indocement Tunggal Prakarsa',
    'WIKA': 'Wijaya Karya',
    'WSKT': 'Waskita Karya',
    'PTPP': 'Pembangunan Perumahan',
    'ADHI': 'Adhi Karya',
    'JSMR': 'Jasa Marga',
    'WTON': 'Waskita Beton Precast',
    'TBIG': 'Tower Bersama Infrastructure',
    'TOWR': 'Sarana Menara Nusantara',
    'SRTG': 'Surya Taruna Gemilang',
    'SMSM': 'Selamat Sempurna',
    'IMAS': 'Indomobil Sukses Internasional',
    
    # === TRADE & RETAIL ===
    'MAPI': 'Mitra Adiperkasa',
    'LPPF': 'Lippo Retail Properti',
    'RALS': 'Ramayana Lestari Sentosa',
    'ACES': 'Ace Hardware Indonesia',
    'ERAA': 'Erajaya Swasembada',
    'LPGI': 'Lebih Global Investindo',
    'TCID': 'MNC Trading Center',
    'TCPI': 'Transcoal Pacific',
    
    # === TRANSPORTATION ===
    'GIAA': 'Garuda Indonesia',
    'BIRD': 'Garudafood Putra Putri Jaya',
    'SMDR': 'Samudera Indonesia',
    'TMAS': 'Timas Lestari',
    'HITS': 'Bakrie & Brothers',
    'SMDM': 'Surya Dumai Industri',
    
    # === HEALTHCARE ===
    'KLBF': 'Kalbe Farma',
    'SIDO': 'Sido Muncul',
    'PRDA': 'Prodia Widyahusada Tbk',
    'SILO': 'Siloam International Hospitals',
    'HEAL': 'Siloam International Hospitals',
    'MIKA': 'Mitra Keluarga Karyasehat',
    'PRDA': 'Prodia Widyahusada Tbk',
    
    # === MEDIA & ENTERTAINMENT ===
    'SCMA': 'Surya Citra Media',
    'EMTK': 'Elang Mahkota Teknologi',
    'VIVA': 'Visi Media Asia',
    'GDST': 'Genta Sukses Mandiri',
    'BFOR': 'Bali Bintang Sejahtera',
    
    # === AGRICULTURE & FOOD ===
    'INDF': 'Indofood Sukses Makmur',
    'ICBP': 'Indofood CBP Sukses Makmur',
    'CPIN': 'Charoen Pokphand Indonesia',
    'JPFA': 'Japfa Comfeed Indonesia',
    'LSIP': 'London Sumatra Indonesia',
    'AALI': 'Astra Agro Lestari',
    'SSMS': 'Sawit Sumbermas Sarana',
    'DSNG': 'Dharma Satya Nusantara',
    'PSGO': 'Palma Serasau Group',
    'ANJT': 'Aneka Tambang',
    'MDKA': 'Merdeka Copper Gold',
    
    # === CHEMICALS ===
    'TPIA': 'Chandra Asri Petrochemical',
    'BRPT': 'Barito Pacific',
    'INKP': 'Indah Kiat Pulp & Paper',
    'INTP': 'Indocement Tunggal Prakarsa',
    'SIDO': 'Sido Muncul',
    'HRUM': 'Harum Energy',
    'PBRX': 'Panberas Raya',
    
    # === INFRASTRUCTURE ===
    'JSMR': 'Jasa Marga',
    'WIKA': 'Wijaya Karya',
    'WSKT': 'Waskita Karya',
    'PTPP': 'Pembangunan Perumahan',
    'ADHI': 'Adhi Karya',
    'WTON': 'Waskita Beton Precast',
    'TPIA': 'Chandra Asri Petrochemical',
    
    # === TECHNOLOGY ===
    'GOTO': 'GoTo Gojek Tokopedia',
    'BUKA': 'Bukalapak.com',
    'EMTK': 'Elang Mahkota Teknologi',
    'DCII': 'DCI Indonesia',
    'BALI': 'Bali Towerindo Sentra',
    'WIFI': 'Link Net',
    'MTEL': 'Telekomunikasi Indonesia',
    
    # === MISC ===
    'BNII': 'Bank Negara Indonesia',
    'CLEO': 'Clean Indonesia',
    'KMDS': 'Kedaung Mulia Group',
    'KMTR': 'Kedaung Mulia Group',
    'BSML': 'Bumi Star梅利亚',
    'BSSR': 'Borneo Iron',
    'PBRX': 'Panberas Raya',
    'DSNG': 'Dharma Satya Nusantara',
    'SMDR': 'Samudera Indonesia',
    'HITS': 'Bakrie & Brothers',
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

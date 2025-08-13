"""
Initial list of target companies for ESG analysis
Sectors: Technology, Finance, Healthcare, Energy, Consumer, Industrial, etc.
Regions: Americas, Europe, Asia, Middle East, Africa
"""

COMPANIES = [
    # Technology
    {"name": "Apple Inc.", "ticker": "AAPL", "sector": "Technology", "region": "Americas"},
    {"name": "Microsoft Corp.", "ticker": "MSFT", "sector": "Technology", "region": "Americas"},
    {"name": "Alphabet Inc.", "ticker": "GOOGL", "sector": "Technology", "region": "Americas"},
    {"name": "Meta Platforms", "ticker": "META", "sector": "Technology", "region": "Americas"},
    {"name": "Amazon.com Inc.", "ticker": "AMZN", "sector": "Technology", "region": "Americas"},
    {"name": "IBM Corp.", "ticker": "IBM", "sector": "Technology", "region": "Americas"},
    {"name": "Tencent Holdings", "ticker": "0700.HK", "sector": "Technology", "region": "Asia"},
    {"name": "Samsung Electronics", "ticker": "005930.KS", "sector": "Technology", "region": "Asia"},
    {"name": "Sony Group", "ticker": "6758.T", "sector": "Technology", "region": "Asia"},
    {"name": "SAP SE", "ticker": "SAP", "sector": "Technology", "region": "Europe"},
    {"name": "ASML Holding", "ticker": "ASML.AS", "sector": "Technology", "region": "Europe"},
    {"name": "Nokia", "ticker": "NOKIA.HE", "sector": "Technology", "region": "Europe"},

    # Finance
    {"name": "JPMorgan Chase", "ticker": "JPM", "sector": "Finance", "region": "Americas"},
    {"name": "Goldman Sachs", "ticker": "GS", "sector": "Finance", "region": "Americas"},
    {"name": "Morgan Stanley", "ticker": "MS", "sector": "Finance", "region": "Americas"},
    {"name": "Bank of America", "ticker": "BAC", "sector": "Finance", "region": "Americas"},
    {"name": "HSBC Holdings", "ticker": "HSBA.L", "sector": "Finance", "region": "Europe"},
    {"name": "Barclays", "ticker": "BARC.L", "sector": "Finance", "region": "Europe"},
    {"name": "Santander", "ticker": "SAN", "sector": "Finance", "region": "Europe"},
    {"name": "UBS Group", "ticker": "UBSG.SW", "sector": "Finance", "region": "Europe"},
    {"name": "Deutsche Bank", "ticker": "DBK.DE", "sector": "Finance", "region": "Europe"},
    {"name": "Bank of China", "ticker": "3988.HK", "sector": "Finance", "region": "Asia"},
    {"name": "Mizuho Financial", "ticker": "8411.T", "sector": "Finance", "region": "Asia"},
    {"name": "First Abu Dhabi Bank", "ticker": "FAB.AD", "sector": "Finance", "region": "Middle East"},

    # Healthcare
    {"name": "Johnson & Johnson", "ticker": "JNJ", "sector": "Healthcare", "region": "Americas"},
    {"name": "Pfizer Inc.", "ticker": "PFE", "sector": "Healthcare", "region": "Americas"},
    {"name": "Moderna Inc.", "ticker": "MRNA", "sector": "Healthcare", "region": "Americas"},
    {"name": "AbbVie Inc.", "ticker": "ABBV", "sector": "Healthcare", "region": "Americas"},
    {"name": "Roche Holding", "ticker": "ROG.SW", "sector": "Healthcare", "region": "Europe"},
    {"name": "Novartis AG", "ticker": "NVS", "sector": "Healthcare", "region": "Europe"},
    {"name": "Sanofi", "ticker": "SAN.PA", "sector": "Healthcare", "region": "Europe"},
    {"name": "AstraZeneca", "ticker": "AZN.L", "sector": "Healthcare", "region": "Europe"},
    {"name": "Takeda Pharmaceutical", "ticker": "4502.T", "sector": "Healthcare", "region": "Asia"},
    {"name": "Shanghai Pharmaceuticals", "ticker": "601607.SS", "sector": "Healthcare", "region": "Asia"},

    # Energy
    {"name": "Exxon Mobil", "ticker": "XOM", "sector": "Energy", "region": "Americas"},
    {"name": "Chevron Corp.", "ticker": "CVX", "sector": "Energy", "region": "Americas"},
    {"name": "Royal Dutch Shell", "ticker": "RDSA.L", "sector": "Energy", "region": "Europe"},
    {"name": "BP PLC", "ticker": "BP.L", "sector": "Energy", "region": "Europe"},
    {"name": "TotalEnergies SE", "ticker": "TTE.PA", "sector": "Energy", "region": "Europe"},
    {"name": "Saudi Aramco", "ticker": "2222.SR", "sector": "Energy", "region": "Middle East"},
    {"name": "QatarEnergy", "ticker": "QE", "sector": "Energy", "region": "Middle East"},
    {"name": "PetroChina", "ticker": "0857.HK", "sector": "Energy", "region": "Asia"},
    {"name": "Reliance Industries", "ticker": "RELIANCE.NS", "sector": "Energy", "region": "Asia"},

    # Consumer
    {"name": "Procter & Gamble", "ticker": "PG", "sector": "Consumer", "region": "Americas"},
    {"name": "Coca-Cola Company", "ticker": "KO", "sector": "Consumer", "region": "Americas"},
    {"name": "PepsiCo", "ticker": "PEP", "sector": "Consumer", "region": "Americas"},
    {"name": "Nestle SA", "ticker": "NESN.SW", "sector": "Consumer", "region": "Europe"},
    {"name": "Unilever PLC", "ticker": "ULVR.L", "sector": "Consumer", "region": "Europe"},
    {"name": "LVMH", "ticker": "MC.PA", "sector": "Consumer", "region": "Europe"},
    {"name": "Alibaba Group", "ticker": "BABA", "sector": "Consumer", "region": "Asia"},
    {"name": "Toyota Motor Corp.", "ticker": "7203.T", "sector": "Consumer", "region": "Asia"},
    {"name": "Jumia Technologies", "ticker": "JMIA", "sector": "Consumer", "region": "Africa"},

    # Industrial
    {"name": "Siemens AG", "ticker": "SIE.DE", "sector": "Industrial", "region": "Europe"},
    {"name": "General Electric", "ticker": "GE", "sector": "Industrial", "region": "Americas"},
    {"name": "Caterpillar Inc.", "ticker": "CAT", "sector": "Industrial", "region": "Americas"},
    {"name": "Mitsubishi Corp.", "ticker": "8058.T", "sector": "Industrial", "region": "Asia"},
    {"name": "Hitachi Ltd.", "ticker": "6501.T", "sector": "Industrial", "region": "Asia"},
    {"name": "ABB Ltd.", "ticker": "ABBN.SW", "sector": "Industrial", "region": "Europe"},
    {"name": "Bharat Heavy Electricals", "ticker": "BHEL.NS", "sector": "Industrial", "region": "Asia"}
]


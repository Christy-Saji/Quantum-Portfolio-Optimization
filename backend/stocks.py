import numpy as np
import pandas as pd
import yfinance as yf

NIFTY_50 = {
    'RELIANCE': {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries', 'sector': 'Energy'},
    'HDFCBANK': {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank', 'sector': 'Banking'},
    'BHARTIARTL': {'symbol': 'BHARTIARTL.NS', 'name': 'Bharti Airtel', 'sector': 'Telecom'},
    'TCS': {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services', 'sector': 'IT'},
    'ICICIBANK': {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank', 'sector': 'Banking'},
    'SBIN': {'symbol': 'SBIN.NS', 'name': 'State Bank of India', 'sector': 'Banking'},
    'INFY': {'symbol': 'INFY.NS', 'name': 'Infosys', 'sector': 'IT'},
    'BAJFINANCE': {'symbol': 'BAJFINANCE.NS', 'name': 'Bajaj Finance', 'sector': 'Finance'},
    'HINDUNILVR': {'symbol': 'HINDUNILVR.NS', 'name': 'Hindustan Unilever', 'sector': 'FMCG'},
    'LT': {'symbol': 'LT.NS', 'name': 'Larsen & Toubro', 'sector': 'Infrastructure'},
    'MARUTI': {'symbol': 'MARUTI.NS', 'name': 'Maruti Suzuki', 'sector': 'Automobile'},
    'HCLTECH': {'symbol': 'HCLTECH.NS', 'name': 'HCL Technologies', 'sector': 'IT'},
    'M&M': {'symbol': 'M&M.NS', 'name': 'Mahindra & Mahindra', 'sector': 'Automobile'},
    'KOTAKBANK': {'symbol': 'KOTAKBANK.NS', 'name': 'Kotak Mahindra Bank', 'sector': 'Banking'},
    'ITC': {'symbol': 'ITC.NS', 'name': 'ITC Limited', 'sector': 'FMCG'},
    'SUNPHARMA': {'symbol': 'SUNPHARMA.NS', 'name': 'Sun Pharma', 'sector': 'Pharma'},
    'AXISBANK': {'symbol': 'AXISBANK.NS', 'name': 'Axis Bank', 'sector': 'Banking'},
    'ULTRACEMCO': {'symbol': 'ULTRACEMCO.NS', 'name': 'UltraTech Cement', 'sector': 'Cement'},
    'TITAN': {'symbol': 'TITAN.NS', 'name': 'Titan Company', 'sector': 'Consumer'},
    'NTPC': {'symbol': 'NTPC.NS', 'name': 'NTPC Limited', 'sector': 'Power'},
    'BAJAJFINSV': {'symbol': 'BAJAJFINSV.NS', 'name': 'Bajaj Finserv', 'sector': 'Finance'},
    'ONGC': {'symbol': 'ONGC.NS', 'name': 'Oil and Natural Gas Corporation', 'sector': 'Energy'},
    'ADANIPORTS': {'symbol': 'ADANIPORTS.NS', 'name': 'Adani Ports', 'sector': 'Infrastructure'},
    'BEL': {'symbol': 'BEL.NS', 'name': 'Bharat Electronics', 'sector': 'Defense'},
    'JSWSTEEL': {'symbol': 'JSWSTEEL.NS', 'name': 'JSW Steel', 'sector': 'Metals'},
    'BAJAJ-AUTO': {'symbol': 'BAJAJ-AUTO.NS', 'name': 'Bajaj Auto', 'sector': 'Automobile'},
    'ASIANPAINT': {'symbol': 'ASIANPAINT.NS', 'name': 'Asian Paints', 'sector': 'Consumer'},
    'COALINDIA': {'symbol': 'COALINDIA.NS', 'name': 'Coal India', 'sector': 'Mining'},
    'WIPRO': {'symbol': 'WIPRO.NS', 'name': 'Wipro', 'sector': 'IT'},
    'ZOMATO': {'symbol': 'ZOMATO.NS', 'name': 'Zomato', 'sector': 'Food Tech'},
    'NESTLEIND': {'symbol': 'NESTLEIND.NS', 'name': 'Nestle India', 'sector': 'FMCG'},
    'ADANIENT': {'symbol': 'ADANIENT.NS', 'name': 'Adani Enterprises', 'sector': 'Infrastructure'},
    'POWERGRID': {'symbol': 'POWERGRID.NS', 'name': 'Power Grid Corporation', 'sector': 'Power'},
    'TATASTEEL': {'symbol': 'TATASTEEL.NS', 'name': 'Tata Steel', 'sector': 'Metals'},
    'HINDALCO': {'symbol': 'HINDALCO.NS', 'name': 'Hindalco Industries', 'sector': 'Metals'},
    'SBILIFE': {'symbol': 'SBILIFE.NS', 'name': 'SBI Life Insurance', 'sector': 'Insurance'},
    'EICHERMOT': {'symbol': 'EICHERMOT.NS', 'name': 'Eicher Motors', 'sector': 'Automobile'},
    'SHRIRAMFIN': {'symbol': 'SHRIRAMFIN.NS', 'name': 'Shriram Finance', 'sector': 'Finance'},
    'GRASIM': {'symbol': 'GRASIM.NS', 'name': 'Grasim Industries', 'sector': 'Cement'},
    'INDIGO': {'symbol': 'INDIGO.NS', 'name': 'Interglobe Aviation', 'sector': 'Aviation'},
    'TECHM': {'symbol': 'TECHM.NS', 'name': 'Tech Mahindra', 'sector': 'IT'},
    'JIOFIN': {'symbol': 'JIOFIN.NS', 'name': 'Jio Financial Services', 'sector': 'Finance'},
    'HDFCLIFE': {'symbol': 'HDFCLIFE.NS', 'name': 'HDFC Life Insurance', 'sector': 'Insurance'},
    'TRENT': {'symbol': 'TRENT.NS', 'name': 'Trent Limited', 'sector': 'Retail'},
    'TATAMOTORS': {'symbol': 'TATAMOTORS.NS', 'name': 'Tata Motors', 'sector': 'Automobile'},
    'TATACONSUM': {'symbol': 'TATACONSUM.NS', 'name': 'Tata Consumer Products', 'sector': 'FMCG'},
    'CIPLA': {'symbol': 'CIPLA.NS', 'name': 'Cipla', 'sector': 'Pharma'},
    'DRREDDY': {'symbol': 'DRREDDY.NS', 'name': "Dr. Reddy's Laboratories", 'sector': 'Pharma'},
    'APOLLOHOSP': {'symbol': 'APOLLOHOSP.NS', 'name': 'Apollo Hospitals', 'sector': 'Healthcare'},
    'MAXHEALTH': {'symbol': 'MAXHEALTH.NS', 'name': 'Max Healthcare Institute', 'sector': 'Healthcare'},
}


def get_stock_list():
    return [{'ticker': t, 'name': info['name'], 'sector': info['sector']} 
            for t, info in sorted(NIFTY_50.items())]


def fetch_stock_data(tickers, period='2y'):
    symbols = [NIFTY_50[t]['symbol'] for t in tickers]
    print(f"Fetching {len(tickers)} stocks from Yahoo Finance...")
    
    raw_data = yf.download(symbols, period=period, progress=False)
    
    if len(tickers) == 1:
        data = raw_data['Adj Close'] if 'Adj Close' in raw_data.columns else raw_data['Close']
        data = pd.DataFrame(data, columns=tickers)
    else:
        if isinstance(raw_data.columns, pd.MultiIndex):
            data = raw_data['Adj Close']
        else:
            data = raw_data['Adj Close'] if 'Adj Close' in raw_data.columns else raw_data['Close']
        data.columns = tickers
    
    prices = data.dropna()
    print(f"Got {len(prices)} days of data")
    return prices


def calculate_returns_and_cov(prices):
    returns = np.log(prices / prices.shift(1)).dropna()
    expected_returns = returns.mean().values * 252
    covariance = returns.cov().values * 252
    return expected_returns, covariance

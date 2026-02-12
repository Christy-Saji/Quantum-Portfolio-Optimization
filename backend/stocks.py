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
    'JUBLFOOD': {'symbol': 'JUBLFOOD.NS', 'name': 'Jubilant FoodWorks', 'sector': 'Food Tech'},
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
    'BRITANNIA': {'symbol': 'BRITANNIA.NS', 'name': 'Britannia Industries', 'sector': 'FMCG'},
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
    """Fetch stock data from Yahoo Finance with fallback to mock data."""
    print(f"Fetching {len(tickers)} stocks from Yahoo Finance...")
    stock_status = {}
    individual_data = {}

    for ticker in tickers:
        try:
            symbol = NIFTY_50[ticker.upper()]['symbol']
            stock_data = yf.download(symbol, period=period, progress=False, auto_adjust=True)
            if not stock_data.empty and len(stock_data) > 50:
                individual_data[ticker] = stock_data['Close'] if 'Close' in stock_data.columns else stock_data.iloc[:, 0]
                stock_status[ticker] = 'available'
                print(f"  + {ticker}: {len(stock_data)} days")
            else:
                stock_status[ticker] = 'data_unavailable'
                print(f"  ! {ticker}: Insufficient data")
        except Exception as e:
            stock_status[ticker] = 'data_unavailable'
            print(f"  x {ticker}: {str(e)[:60]}")

    if individual_data:
        try:
            prices = pd.DataFrame(individual_data)
        except ValueError:
            prices = pd.concat(individual_data, axis=1)
            prices.columns = list(individual_data.keys())
        prices = prices.dropna()
        for ticker in tickers:
            if ticker not in prices.columns and stock_status.get(ticker) == 'available':
                stock_status[ticker] = 'data_unavailable'
        if not prices.empty and len(prices) > 50:
            print(f"\n+ {len(prices.columns)}/{len(tickers)} stocks, {len(prices)} days")
            return prices, stock_status

    print("\n! Using mock data for demonstration.")
    prices = generate_mock_data(tickers, period)
    stock_status = {ticker: 'mock_data' for ticker in tickers}
    return prices, stock_status


def generate_mock_data(tickers, period='2y'):
    """Generate synthetic stock data when API fails."""
    days_map = {'1d': 1, '5d': 5, '1mo': 21, '3mo': 63, '6mo': 126, '1y': 252, '2y': 504, '5y': 1260}
    n_days = days_map.get(period, 504)
    dates = pd.date_range(end=pd.Timestamp.now(), periods=n_days, freq='B')
    mock_data = {}

    sector_params = {
        'IT': (0.15, 0.25), 'Banking': (0.10, 0.30), 'Pharma': (0.12, 0.22),
        'FMCG': (0.08, 0.18), 'Energy': (0.09, 0.28), 'Automobile': (0.11, 0.32),
        'Finance': (0.13, 0.27), 'default': (0.10, 0.25)
    }

    for ticker in tickers:
        np.random.seed(sum(ord(c) for c in ticker))
        sector = NIFTY_50.get(ticker, {}).get('sector', 'default')
        base_ret, base_vol = sector_params.get(sector, sector_params['default'])
        annual_return = base_ret + np.random.uniform(-0.08, 0.12)
        daily_return = annual_return / 252
        daily_vol = base_vol / np.sqrt(252)
        start_price = np.random.uniform(800, 2500)
        mock_data[ticker] = start_price * np.exp(np.cumsum(np.random.normal(daily_return, daily_vol, n_days)))

    return pd.DataFrame(mock_data, index=dates)


def calculate_returns_and_cov(prices):
    returns = np.log(prices / prices.shift(1)).dropna()
    return returns.mean().values * 252, returns.cov().values * 252

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
    """
    Fetch stock data from Yahoo Finance with robust fallback mechanisms.
    Tries: batch download -> individual downloads -> mock data
    """
    symbols = [NIFTY_50[t]['symbol'] for t in tickers]
    print(f"Fetching {len(tickers)} stocks from Yahoo Finance...")
    
    prices = pd.DataFrame()
    
    # Strategy 1: Try batch download (fastest)
    try:
        print("Trying batch download...")
        raw_data = yf.download(
            symbols, 
            period=period, 
            progress=False,
            auto_adjust=True,
            threads=True
        )
        
        if not raw_data.empty:
            # Handle single vs multiple stocks
            if len(tickers) == 1:
                if 'Close' in raw_data.columns:
                    prices = pd.DataFrame(raw_data['Close'], columns=tickers)
                else:
                    prices = pd.DataFrame(raw_data, columns=tickers)
            else:
                # Multiple stocks
                if isinstance(raw_data.columns, pd.MultiIndex):
                    prices = raw_data['Close']
                    prices.columns = tickers
                else:
                    prices = raw_data
                    if len(prices.columns) == len(tickers):
                        prices.columns = tickers
            
            prices = prices.dropna()
            
            if not prices.empty and len(prices) > 50:  # Need at least 50 days
                print(f"✓ Batch download successful")
                print(f"Got {len(prices)} days of data")
                print_sample_data(prices, tickers)
                return prices
    except Exception as e:
        print(f"Batch download failed: {e}")
    
    # Strategy 2: Try downloading stocks one by one
    print("Trying individual downloads...")
    individual_data = {}
    success_count = 0
    
    for ticker in tickers:
        try:
            symbol = NIFTY_50[ticker]['symbol']
            stock_data = yf.download(
                symbol, 
                period=period, 
                progress=False,
                auto_adjust=True
            )
            
            if not stock_data.empty:
                if 'Close' in stock_data.columns:
                    individual_data[ticker] = stock_data['Close']
                else:
                    individual_data[ticker] = stock_data.iloc[:, 0]
                success_count += 1
                print(f"  ✓ {ticker}: {len(stock_data)} days")
        except Exception as e:
            print(f"  ✗ {ticker}: {e}")
    
    if individual_data:
        prices = pd.DataFrame(individual_data).dropna()
        
        if not prices.empty and len(prices) > 50:
            print(f"✓ Individual downloads successful ({success_count}/{len(tickers)} stocks)")
            print(f"Got {len(prices)} days of data")
            print_sample_data(prices, tickers)
            return prices
    
    # Strategy 3: Fallback to mock data
    print("⚠ All downloads failed. Generating mock data for demonstration.")
    prices = generate_mock_data(tickers, period)
    print(f"Got {len(prices)} days of data (synthetic)")
    print_sample_data(prices, tickers)
    return prices


def generate_mock_data(tickers, period='2y'):
    """Generate synthetic stock data for demonstration when API fails"""
    days_map = {'1d': 1, '5d': 5, '1mo': 21, '3mo': 63, '6mo': 126, '1y': 252, '2y': 504, '5y': 1260, '10y': 2520, 'ytd': 252, 'max': 5000}
    n_days = days_map.get(period, 504)
    
    dates = pd.date_range(end=pd.Timestamp.now(), periods=n_days, freq='B')
    mock_data = {}
    
    # Assign realistic sector-based characteristics
    sector_params = {
        'IT': {'base_return': 0.15, 'volatility': 0.25},
        'Banking': {'base_return': 0.10, 'volatility': 0.30},
        'Pharma': {'base_return': 0.12, 'volatility': 0.22},
        'FMCG': {'base_return': 0.08, 'volatility': 0.18},
        'Energy': {'base_return': 0.09, 'volatility': 0.28},
        'Automobile': {'base_return': 0.11, 'volatility': 0.32},
        'Finance': {'base_return': 0.13, 'volatility': 0.27},
        'default': {'base_return': 0.10, 'volatility': 0.25}
    }
    
    for i, ticker in enumerate(tickers):
        # Use ticker name to generate unique but reproducible seed
        ticker_seed = sum(ord(c) for c in ticker)  # Convert ticker to number
        np.random.seed(ticker_seed)
        
        # Get sector-specific params or use default
        sector = NIFTY_50.get(ticker, {}).get('sector', 'default')
        base_params = sector_params.get(sector, sector_params['default'])
        
        # Target annualized return with sector bias and randomness: -10% to +25%
        sector_base = base_params['base_return']
        random_variation = np.random.uniform(-0.08, 0.12)  # ±8-12% variation
        target_annual_return = sector_base + random_variation
        
        # Daily metrics
        daily_return = target_annual_return / 252
        daily_volatility = base_params['volatility'] / np.sqrt(252)
        
        # Generate price series
        start_price = np.random.uniform(800, 2500)
        daily_returns = np.random.normal(daily_return, daily_volatility, n_days)
        price_series = start_price * np.exp(np.cumsum(daily_returns))
        mock_data[ticker] = price_series
        
    return pd.DataFrame(mock_data, index=dates)


def print_sample_data(prices, tickers):
    """Print the latest 5 days of closing prices in a table format"""
    print("\nSample Data - Latest 5 Days of Closing Prices:")
    print("=" * 80)
    
    # Get the last 5 rows
    sample_df = prices.tail(5)
    
    # Format the dataframe for better display
    pd.options.display.float_format = '{:.2f}'.format
    print(sample_df.to_string())
    print("=" * 80)
    print()


def calculate_returns_and_cov(prices):
    returns = np.log(prices / prices.shift(1)).dropna()
    expected_returns = returns.mean().values * 252
    covariance = returns.cov().values * 252
    return expected_returns, covariance

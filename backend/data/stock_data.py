import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("Warning: yfinance not installed. Install with: pip install yfinance")


NSE_STOCKS = {
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


class StockDataManager:
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent
        self.data_dir = Path(data_dir)
        self.stocks = NSE_STOCKS.copy()
        self.price_data = None
        self.returns_data = None
        self._selected_stocks = list(self.stocks.keys())[:10]
    
    def get_stock_list(self) -> List[Dict[str, Any]]:
        return [
            {'ticker': ticker, 'name': info['name'], 'sector': info['sector'], 'symbol': info['symbol']}
            for ticker, info in sorted(self.stocks.items())
        ]
    
    def search_stocks(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        query = query.upper().strip()
        if not query:
            return self.get_stock_list()[:limit]
        
        results = []
        for ticker, info in self.stocks.items():
            if query in ticker or query in info['name'].upper():
                results.append({
                    'ticker': ticker,
                    'name': info['name'],
                    'sector': info['sector'],
                    'symbol': info['symbol']
                })
        return results[:limit]
    
    def fetch_data(self, tickers: Optional[List[str]] = None, period: str = '2y',
                   use_cache: bool = False) -> pd.DataFrame:
        if tickers is None:
            tickers = list(self.stocks.keys())
        
        self._selected_stocks = tickers
        
        if use_cache:
            cache_file = self.data_dir / 'nse_stocks.csv'
            if cache_file.exists():
                try:
                    cached_data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                    available_tickers = [t for t in tickers if t in cached_data.columns]
                    if len(available_tickers) == len(tickers):
                        self.price_data = cached_data[tickers]
                        return self.price_data
                except Exception:
                    pass
        
        if not YFINANCE_AVAILABLE:
            raise RuntimeError("yfinance is required for live data. Install with: pip install yfinance")
        
        try:
            symbols = [self.stocks[t]['symbol'] for t in tickers]
            print(f"Fetching live data for {len(tickers)} stocks (2 years)...")
            
            raw_data = yf.download(symbols, period=period, progress=False)
            
            if len(tickers) == 1:
                if isinstance(raw_data, pd.DataFrame):
                    data = raw_data['Adj Close'] if 'Adj Close' in raw_data.columns else raw_data['Close']
                    data = pd.DataFrame(data)
                    data.columns = tickers
                else:
                    data = pd.DataFrame(raw_data)
                    data.columns = tickers
            else:
                if isinstance(raw_data.columns, pd.MultiIndex):
                    data = raw_data['Adj Close'] if 'Adj Close' in raw_data.columns.get_level_values(0) else raw_data['Close']
                else:
                    data = raw_data['Adj Close'] if 'Adj Close' in raw_data.columns else raw_data['Close']
                data.columns = tickers
            
            self.price_data = data.dropna()
            self._save_cache(self.price_data)
            print(f"Fetched {len(self.price_data)} trading days of data")
            return self.price_data
        except Exception as e:
            raise RuntimeError(f"Failed to fetch live data: {str(e)}")
    
    def _save_cache(self, data: pd.DataFrame) -> None:
        try:
            cache_file = self.data_dir / 'nse_stocks.csv'
            data.to_csv(cache_file)
        except Exception:
            pass
    
    def calculate_returns(self, method: str = 'log') -> pd.DataFrame:
        if self.price_data is None:
            raise RuntimeError("Must fetch data first")
        
        if method == 'log':
            self.returns_data = np.log(self.price_data / self.price_data.shift(1)).dropna()
        else:
            self.returns_data = self.price_data.pct_change().dropna()
        return self.returns_data
    
    def get_expected_returns(self, annualize: bool = True) -> np.ndarray:
        if self.returns_data is None:
            self.calculate_returns()
        mean_returns = self.returns_data.mean().values
        return mean_returns * 252 if annualize else mean_returns
    
    def get_covariance_matrix(self, annualize: bool = True) -> np.ndarray:
        if self.returns_data is None:
            self.calculate_returns()
        cov_matrix = self.returns_data.cov().values
        return cov_matrix * 252 if annualize else cov_matrix
    
    def get_correlation_matrix(self) -> np.ndarray:
        if self.returns_data is None:
            self.calculate_returns()
        return self.returns_data.corr().values
    
    def get_stock_metrics(self) -> pd.DataFrame:
        if self.returns_data is None:
            self.calculate_returns()
        
        metrics = pd.DataFrame({
            'Expected Return': self.returns_data.mean() * 252,
            'Volatility': self.returns_data.std() * np.sqrt(252),
            'Sharpe Ratio': (self.returns_data.mean() * 252) / (self.returns_data.std() * np.sqrt(252))
        })
        return metrics.round(4)
    
    def prepare_optimization_inputs(self, tickers: List[str]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        if self.price_data is None or not all(t in self.price_data.columns for t in tickers):
            self.fetch_data(tickers, use_cache=False)
        
        self.calculate_returns()
        returns_subset = self.returns_data[tickers]
        expected_returns = returns_subset.mean().values * 252
        covariance = returns_subset.cov().values * 252
        
        return expected_returns, covariance, tickers


def get_available_stocks() -> List[Dict[str, Any]]:
    manager = StockDataManager()
    return manager.get_stock_list()


def calculate_portfolio_metrics(selected_indices: List[int], returns: np.ndarray,
                                covariance: np.ndarray, stock_names: Optional[List[str]] = None) -> Dict[str, Any]:
    n, k = len(returns), len(selected_indices)
    
    if k == 0:
        return {'expected_return': 0.0, 'portfolio_risk': 0.0, 'sharpe_ratio': 0.0, 'selected_stocks': []}
    
    weights = np.zeros(n)
    weights[selected_indices] = 1.0 / k
    portfolio_return = np.dot(weights, returns)
    portfolio_variance = weights @ covariance @ weights
    portfolio_risk = np.sqrt(portfolio_variance)
    sharpe_ratio = portfolio_return / portfolio_risk if portfolio_risk > 0 else 0
    
    result = {
        'expected_return': float(portfolio_return),
        'portfolio_risk': float(portfolio_risk),
        'sharpe_ratio': float(sharpe_ratio),
        'portfolio_variance': float(portfolio_variance),
        'num_stocks': k,
        'weights': weights[selected_indices].tolist()
    }
    
    if stock_names:
        result['selected_stocks'] = [stock_names[i] for i in selected_indices]
    else:
        result['selected_indices'] = selected_indices
    
    return result


if __name__ == "__main__":
    print("=== Stock Data Manager Example ===\n")
    manager = StockDataManager()
    
    stocks = manager.get_stock_list()
    print(f"Available Stocks: {len(stocks)}")
    for stock in stocks[:5]:
        print(f"  {stock['ticker']}: {stock['name']} ({stock['sector']})")
    print()
    
    tickers = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']
    print(f"Fetching live data for: {tickers}")
    prices = manager.fetch_data(tickers, use_cache=False)
    print(f"Data shape: {prices.shape}\n")
    
    metrics = manager.get_stock_metrics()
    print("Stock Metrics:")
    print(metrics)

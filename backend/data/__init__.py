"""
Data Processing Module

This module handles stock data management for portfolio optimization.
"""

from .stock_data import StockDataManager, get_available_stocks, calculate_portfolio_metrics

__all__ = ['StockDataManager', 'get_available_stocks', 'calculate_portfolio_metrics']

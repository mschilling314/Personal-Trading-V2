import backtrader as bt
import pandas as pd


def orchestrate(data_specs: dict, model: backtrader.Strategy, results_directory: str = "./backtest/results/"):
    """
    Create a new backtesting flow.  Flow should go:
    1. Load data -> provide flexibitility to user, data is then passed off to specified data loader
    2. Initialize backtest -> something similar to original execute_backtest function's intent
    3. Provide analysis -> store results, trades, and graphs provided by backtesting module

    Inputs:
    ------
    data_specs: has the keys "loader" (function, specify one of the loaders implemented in data_loaders.py) "loader_args" which are then passed into the loader function and should match its signature.
    model: extends the backtesting.Strategy class, this is what's being tested, must have __init__() and next()
    results_directory: where you'd like the results to be stored for a given test.  Recommended to extend path from default if executing multiple backtests in parallel.
    """
    data = bt.feeds.BacktraderCSV()



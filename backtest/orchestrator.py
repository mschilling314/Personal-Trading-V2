import datetime
import backtesting
import pandas as pd
from data_loaders import load_data_from_yfinance
from data_loaders import load_data_from_alpha_vantage
from models.CoinFlip import CoinFlip

SCHEMA = {"Open": float, "High": float, "Low": float, "Close": float, "Volume": float}


def orchestrate(data_specs: dict, model: backtesting.Strategy, results_directory: str="./backtest/results/") -> None:
    """
    Create a new backtesting flow.  Flow should go:
    1. Load data -> provide flexibitility to user, data is then passed off to specified data loader
    2. Initialize backtest -> something similar to original execute_backtest function's intent
    3. Provide analysis -> store results, trades, and graphs provided by backtesting module

    Inputs:
    ------
    data_specs: has the keys "loader" (function, specify one of the loaders implemented in data_loaders.py) "ticker" (str), "interval" (str, refers to desired granularity of data), "start_date" (datetime.date), and "end_date" (datetime.date)
    model: extends the backtesting.Strategy class, this is what's being tested, must have __init__() and next()
    results_directory: where you'd like the results to be stored for a given test.  Recommended to extend path from default if executing multiple backtests in parallel.
    """
    try:
        loader = data_specs["loader"]
        datas = loader(ticker=data_specs["ticker"], interval=data_specs["interval"], start_date=data_specs["start_date"], end_date=data_specs["end_date"])
    except KeyError as ke:
        print(f"Loading from YFinance because we encountered {ke}")
        datas = load_data_from_yfinance()
    finally:
        datas = datas.astype(dtype=SCHEMA)
        datas.index = pd.to_datetime(datas.index)
        bt = backtesting.Backtest(data=datas, strategy=model, exclusive_orders=True)
        stats = bt.run()
        stats.to_csv(f"{results_directory}{model.__name__}_results.csv")
        stats.to_csv(f"{results_directory}{model.__name__}_trades.csv")
        # bt.plot(filename=f"{results_directory}{model.__name__}_graphs.html", open_browser=False)
        print("Backtesting has concluded.")



if __name__=="__main__":
    data_specs = {"loader": load_data_from_alpha_vantage, "ticker": "TQQQ", "interval": "1min", "start_date": datetime.date(2024,1,1), "end_date": datetime.date(2024,10,1)}
    orchestrate(data_specs=data_specs, model=CoinFlip)
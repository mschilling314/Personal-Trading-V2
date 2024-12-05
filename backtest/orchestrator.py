import datetime
import backtesting
import pandas as pd
from data_loaders import load_data_from_yfinance
from data_loaders import load_stock_data_from_alpha_vantage
from data_loaders import get_daily_crypto_data
from data_loaders import load_day_data_yfinance
from models.CoinFlip import CoinFlip
from models.DollarCostAverage import DollarCostAverage

SCHEMA = {"Open": float, "High": float, "Low": float, "Close": float, "Volume": float}


def orchestrate(data_specs: dict, model: backtesting.Strategy, results_directory: str="./backtest/results/"):
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
        datas = loader(**data_specs["loader_args"])
    except KeyError as ke:
        print(f"Loading from YFinance because we encountered {ke}")
        datas = load_data_from_yfinance()
    finally:
        datas = datas.astype(dtype=SCHEMA)
        datas.index = pd.to_datetime(datas.index)
        if data_specs["loader_args"]["ticker"] in ["BTC-USD", "ETH-USD"]:
            datas = datas * 10**-6
        bt = backtesting.Backtest(data=datas, strategy=model, exclusive_orders=True, cash=100000000000000)
        stats = bt.run()
        stats.to_csv(f"{results_directory}{model.__name__}_results.csv")
        trades = stats["_trades"]
        trades.to_csv(f"{results_directory}{model.__name__}_trades.csv")
        # bt.plot(filename=f"{results_directory}{model.__name__}_graphs.html", open_browser=False)
        print("\nBacktesting has concluded.")
        return stats, trades


def dca_analysis(trades):
    total_investment = len(trades) * 1000 # slightly off
    current_equity = trades["Size"].iloc[-1] * trades["ExitPrice"].iloc[-1]
    total_return = round(current_equity/total_investment, 2)
    annualized_return = 100 * round((1+total_return) ** (365/(len(trades) * 14)) - 1, 4) # slightly off because of last period only being 2 days
    start = trades["EntryTime"].iloc[0].strftime('%Y-%m-%d')
    finish = trades["ExitTime"].iloc[-1].strftime('%Y-%m-%d')
    print(f"Analysis ran from approximately {start} to {finish}")
    print(f"The total invested was ${total_investment}.\nThe final value of these investments was ${current_equity}\nThe total return was {total_return}x.\nThe annualized return was {annualized_return}%.\n")


if __name__=="__main__":
    starting_date = datetime.date(2023, 1, 1)
    # data_specs = {"loader": load_stock_data_from_alpha_vantage, "ticker": "TQQQ", "interval": "1min", "start_date": datetime.date(2024,1,1), "end_date": datetime.date(2024,10,1)}
    print("Analysis for Bitcoin.")
    data_specs = {"loader": load_day_data_yfinance, "loader_args": {"ticker": "BTC-USD", "start_date": starting_date}}
    _, trades = orchestrate(data_specs=data_specs, model=DollarCostAverage)
    dca_analysis(trades=trades)

    print("Analysis for ETH.")
    data_specs = {"loader": load_day_data_yfinance, "loader_args": {"ticker": "ETH-USD", "start_date": starting_date}}
    _, trades = orchestrate(data_specs=data_specs, model=DollarCostAverage)
    dca_analysis(trades=trades)

    print("Analysis for SPY.")
    data_specs = {"loader": load_day_data_yfinance, "loader_args": {"ticker": "SPY", "start_date": starting_date}}
    _, trades = orchestrate(data_specs=data_specs, model=DollarCostAverage)
    dca_analysis(trades=trades)

    print("Analysis for QQQ.")
    data_specs = {"loader": load_day_data_yfinance, "loader_args": {"ticker": "QQQ", "start_date": starting_date}}
    _, trades = orchestrate(data_specs=data_specs, model=DollarCostAverage)
    dca_analysis(trades=trades)

    print("Analysis for TQQQ.")
    data_specs = {"loader": load_day_data_yfinance, "loader_args": {"ticker": "TQQQ", "start_date": starting_date}}
    _, trades = orchestrate(data_specs=data_specs, model=DollarCostAverage)
    dca_analysis(trades=trades)

    
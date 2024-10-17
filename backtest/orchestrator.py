import datetime
import backtesting
from data_loaders import load_data_from_yfinance
from data_loaders import load_data_from_alpha_vantage
import models as modelz


def execute_backtest(data, strat, ticker: str="TQQQ"):
    bt = backtesting.Backtest(data=data, strategy=strat, exclusive_orders=True, cash=10000)
    stats = bt.run()
    results_file_name = "results/" + ticker + f"{strat.__name__}_results.csv"
    trades_file_name = "trades/" + ticker + f"{strat.__name__}_trades.csv"
    stats.to_csv(results_file_name)
    stats["_trades"].to_csv(trades_file_name)
    print("\Test finished.\n")
    graph_file_name = "graphs/" + ticker + f"{strat.__name__}_Vol.html"
    # bt.plot(filename=graph_file_name)

def execute_backtest_v2(data, strat, start, end, ticker: str="TQQQ", money=10000):
    bt = backtesting.Backtest(data=data, strategy=strat, exclusive_orders=True, cash=money)
    stats = bt.run()
    return stats["Equity Final [$]"]


def orchestrate(data_specs: dict, model: backtesting.Strategy, results_directory: str="./backtesting/results/") -> None:
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
        data = loader(ticker=data_specs["ticker"], interval=data_specs["interval"], start_date=data_specs["start_date"], end_date=data_specs["end_date"])
    except:
        data = load_data_from_yfinance()
    finally:
        bt = backtesting.Backtest(data=data, strategy=model, exclusive_orders=True, cash=10000)
        stats = bt.run()
        stats.to_csv(f"{results_directory}{model.__name__}_results.csv")
        stats.to_csv(f"{results_directory}{model.__name__}_trades.csv")
        bt.plot(filename=f"{results_directory}{model.__name__}_graphs.html", open_browser=False)



if __name__=="__main__":
    data_specs = {"loader": load_data_from_alpha_vantage, "ticker": "TQQQ", "interval": "1m", "start_date": datetime.date(2024,1,1), "end_date": datetime.date(2024,2,1)}
    orchestrate(data_specs=data_specs, model=modelz.VolatilityLongStrategy.VolatilityLongStrategy)
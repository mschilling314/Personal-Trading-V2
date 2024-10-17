import backtesting


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


if __name__=="__main__":
    pass
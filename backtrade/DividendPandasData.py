import backtrader as bt
import pandas as pd


class DividendPandasData(bt.feeds.PandasData):
    lines = ("dividends",)
    params = (
        ('dividends', -1),  # Map the dividends column from the DataFrame to the new 'dividends' line
    )
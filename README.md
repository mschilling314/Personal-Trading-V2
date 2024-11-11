# Personal-Trading-V2

## What Is This?
The goal of this repository was to implement a simple trading strategy designed to fix what I saw as the core inadequacy of stop-limit orders: slippage.  Before we get into that however, let's discuss what's in the repository.

### Repository Contents
- Backtesting
    - Contains backtesting.py, which is at the time of writing, an absolute mess because I was essentially trying to go as fast as possible in my implementation, plus I was actually learning how to backtest as I went.
    - There are two data fetching functions, one uses YFinance (free, but with the limitation that you can only get minutely granularity for the previous 30 days) and one that uses AlphaVantage (free for 25 such months per day).  Needs refactoring and clean-up.
- Logs
    - Contains app run logs, updated by the workflows using standard Git Commit and push as that's cheaper than using an actual logging service, and somewhat easier to set up.
- Source (src)
    - Contains modules I defined for the purpose of reuse in trading flows.
    - Logger: enables me to easily initialize a reusable standard logger across workflows with consistent settings.
     - Schwab: provides an interface between my workflows and Schwab itself, so that I can use simple Python functions for everything from authorizing the workflow to placing orders to getting account details.  In the event I wanted to change brokers, I'd use this as a template to implement a similar module for that broker.  While there are solutions out there for this already (such as [SchwabDev](https://github.com/tylerebowers/Schwab-API-Python/blob/main/README.md) by Tyler Bowers), I wanted to implement this for myself for a few reasons:
        1. Learning experience: I was able to get more experience reading documentation, referencing existing solutions, etc.
        2. Lightweight: I can only implement what I need, ideally cutting down on amount of code in the product, which can save time spinning up instances as well as memory.
        3. Pythonic:  My last goal here is to make it a bit more Pythonic, as for example other people implement the order placement it still involves creating an order JSON object.  The idea here is that instead, I want to move towards being able to call a function, feed it variables, and have that order object reliably constructed for me.
    - Stock Data (stock_data):  Uses Yahoo Finance to get data on a given stock.  This is because the strategy I was going to implement would've compared the closing and opening price to make a buy decision.

- Testing (under construction)
- Trading Scripts (trading_scripts)
    - Holds the scripts called by workflows to enable actual trading.  Might refactor to use class-based models instead, for easier interfacing with backtesting in the future (since under that paradigm you could "promote" a model by moving it from the backtesting directory to a models directory with potentially few changes).
- Miscellaneous in Root
    - trading_data.sqlite:  To save on cost (money and effort), I had the idea of storing records of trades in a SQLite database that's updated by GitHub Actions much the same way logs are.  In the future I might move this to a separate private repository once I start actually trading.
    - requirements.txt: Pretty standard, but ideally I want to keep the requirements as simple as possible.

## Strategy

Initially, I conceived of a strategy aiming to capture volatility.  The idea was that most trading operates as extremely educated betting, where you bet on whether an asset's price will go up (going long) or down (going short).  

But, that's very difficult to predict, so what if you instead tried to bet on the stock moving each day (which is nigh guaranteed, I don't think I've ever seen a stock stay the same price through the entire day)?  To do this, I was initially going to create long-short pairs (this was before I learned about the options trading strategy of straddling), with stop-loss and limit conditions to capture that volatility.  Unfortunately, the PDT rule ruined my fun, and so I turned my attention solely to the long side of the equation, thinking it could still be a winning strategy by fixing another financial instrument:  the stop-loss order.

In particular, my thinking was that the reason a stop-limit order eats assets alive is overnight price fluctuation (a particular form of slippage), since that change can't be acted upon due to the closed market.  I also held that small daily gains are better than none, hence a second sell condition essentially in the form of a limit order.

To fix the perceived hole though, I thought a simple strategy might work, the strategy goes like so:
1. At 9:30 ET, buy as much of a leveraged ETF (more on why later) as you'd like.
2. In the event you lose some percent value, sell (stop-loss).  In the event you gain some percent value, sell (limit to capture some small percentage profit, ideally consistently).
3. If neither sell event comes to pass by 15:55 ET (five minutes prior to market close), sell to prevent overnight slippage.

The reasoning behind using a leveraged ETF was that since the leveraging multiplies the movement of the underlying asset, it'd be easier to hit limits (my inital goal was to try and hit something like 0.1% daily gain) and profit from the sale.
 
## How this differs from my (private) Version 1 (i.e., why this is Version 2)
In V1, the idea was to use an AWS lambda called every minute during trading hours to continuously check and see if it was time to sell or not.
The problem with that strategy is two-fold:  AWS is complex and expensive (comparatively, especially just to live-test a prototyped strategy), and using that many invocations is wasteful.

The new strategy is to use a OCO order (one cancels the other) wherein once we buy the leveraged ETF, we place a limit order to capture profit and a stop-loss order to mitigate loss.  This occurs when the 9:30 ET action fires.  Then, at 15:55 ET, we have another action take place to see if either order executed, and if not the orders are cancelled and an immediate sale happens, with outcome logged in a SQLite database.

Initial backtesting was promising (because I was only able to access 1 month of market data from Yahoo Finance, this was before I found AlphaVantage), in fact a bit <i>too</i> promising (2500% annualized returns with a Sharpe ratio of 1.67 and max drawdown of -6.28%).  Once I stopped daydreaming about a 25x multiplier to my wealth, I went searching for better data and found AlphaVantage, which I then used to backtest across several years, where I got the much more realistic result of a -99% gain, so I need a new strategy.  For now though, I plan to finish implementing the trading mechanisms themselves and perform refactors so that when the next idea hits I can more quickly backtest and deploy it.

## To Do List:
- Create DST Workflow to update the execution times of GitHub Actions on specific dates (maybe make a separate repo with a global PAT???)
- Unit testing?
- Live Testing
    - Tests needed to perform:
        - Ensure refresh token is acquireable
        - Trading flow (end-to-end)
            - Ensure that orders can be placed
            - Ensure account lookup works properly
    - Once confirmed to work, disable
- Create adapter class to enable model classes to be directly deployed to live trading environments following backtesting without code modification
    - issue:  new adapter class needed for each brokerage supported
- Come up with a better strategy
- Rewrite YFinance loader to handle:
    - Broader use cases (differing intervals)
    - Handling of short intervals in background (i.e., for 1m interval, make sure it fits the 30-day constraint, fetch fully the last 30 days of data)
        - probably overthinking this, try just timedelta of 30 days...
- Decide on Object-oriented refactor (store things like auth token, base_url, etc in fields initialized once instead of referencing from environ vars every time)
    - Possible option:
        - Class SchwabTrader
            - Responsible for actually interacting with Schwab's API endpoints
            - encapsulates important re-used data such as auth tokens, base_url, account_id, etc enabling you to not constantly use os.environ
            - Still provides Pythonic order access
            - likely to be a very long class once fully implemented though, may sacrifice readability :/
        - Class Positions
            - Responsible for holding data on positions
            - Could be a field of SchwabTrader
        - Class Order/Transaction
            - Really just a transaction data record, may not be useful though

- Eventual C++ refactor (V3)?
    - Pros: 
        - possible performance boost, step into HFT space
        - learning experience
    - Cons: 
        - difficult, may not fit use case
        - lack of support in the form of libraries/documentation
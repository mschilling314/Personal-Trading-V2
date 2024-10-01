# Personal-Trading-V2
 
## How this differs from V1
In V1, the idea was to use an AWS lambda called every minute during trading hours to continuously check and see if it was time to sell or not.
The problem with that strategy is two-fold:  AWS is complex and expensive (comparatively), and using that many invocations is wasteful.

The new strategy is to use a OCO order (one cancels the other) wherein once we buy the leveraged ETF, we place a limit order to capture profit and a stop-loss order to mitigate loss.  This occurs when the 9:30 ET action fires.  Then, at 15:55 ET, we have another action take place to see if either order executed, and if not the orders are cancelled and an immediate sale happens, with outcome logged in a CSV (functioning as a shitty database).

## To Do List:
- Create Morning and Afternoon GitHub Actions
- Create DST Workflow to update the execution times of GitHub Actions on specific dates (maybe make a separate repo with a global PAT???)
- Implement Schwab Trading
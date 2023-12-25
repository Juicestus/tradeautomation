# Trading Algorithms

Monorepo of trading algorithms, plotting libraries, research, and execution infrastructure.

## Model to Strategy Pipeline
1. Proofs and notes in Jupyter
2. Model backtesting in Python
3. Tune parameters
4. Implement in Go, paper-trade on Alpaca
5. Production and Deployment 😉

## priceanalytics
Python library for creating and backtesting models
- [backtest](./priceanalytics/backtest.py): Backtesting utility class
- [data](./priceanalytics/data.py): Retrieves data using Alpaca SDK 
- [indicators](./priceanalytics/indicators.py): Package for commmonly used math/stat/analytic functions
- [keys](./priceanalytics/keys.py): Holds keys as string literals - to be replaced

## strategies
Strategy research
- [squarebounds](./strategies/squarebounds/): Proprietary trading algorithm in production
- [stochastics](./strategies/stochastics/): Research and testing of stochastic algorithms

## tradeautomation
Infrastructure for executing strategies in production written in Go. 
# Trading Algorithms

Monorepo of trading algorithms, plotting libraries, research, and an order entry system.

## Model to Strategy Pipeline
1. Proofs and notes in Jupyter
2. Model backtesting in Python
3. Tune parameters
4. Implement in Go, paper-trade on Alpaca
5. Production and Deployment 😉

## Directories
- [priceanalytics](#priceanalytics): Python library for creating and backtesting models

- [strategies](#strategies): Directory for strategy research

- [tradeautomation](#tradeautomation): Infrastructure for executing strategies in production

## priceanalytics
- backtest    Backtesting utility class
- data        Gathers data from Alpaca SDK 
- indicators  Package for commmonly used math/stat/analytic functions
- keys        Holds keys as string literals, will replaced with a config file reader like tradeautomation
- plot        Custom plotting library

## strategies
- squarebounds: Proprietary trading algorithm in production
- stochastics: Research and testing of stochastic algorithms

## tradeautomation
Order entry system written in Go. Deployed to AWS EC2 instance.
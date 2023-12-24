Monorepo of trading algorithms

Important Directories
====================

- priceanalytics: Python library for creating/testing models
  (see additional priceanalytics information later)

- tradeautomation: Infrastructure for executing models in
  production, written in Go
  (see additional tradeautomation information later)

# The following are model directories and contain notebooks
# and scirpts for testing their respective models

- squarebounds: For the "squarebounds"/"sbosc" model

- stochastics: For the testing of stochastic models

priceanalytics
==============
Has a few packages:
- backtest
- data        (deprecated)
- indicators  package for commmonly used math/stat/analytic functions
- keys        (deprecated) holds keys as string literals, will
              replaced with a config file reader like tradeautomation
- plot        package with plotting utilities

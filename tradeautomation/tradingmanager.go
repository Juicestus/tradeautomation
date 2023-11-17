package main

import (
	//"context"
	"fmt"
	//"log"
	//"os"
	//"time"

	//"github.com/shopspring/decimal"
	"github.com/alpacahq/alpaca-trade-api-go/v3/alpaca"
	"github.com/alpacahq/alpaca-trade-api-go/v3/marketdata"
	"github.com/alpacahq/alpaca-trade-api-go/v3/marketdata/stream"
)

type TradingManager struct {
	tradeClient   *alpaca.Client
	dataClient    *marketdata.Client
	streamClient  *stream.StocksClient
	feed          marketdata.Feed
	lastOrder     string
	ticker        string
}

func InitTradingManager(config *APIConfig, ticker string) *TradingManager {
	baseURL := "https://paper-api.alpaca.markets" //default
	feed := "iex" //default
	manager := &TradingManager{
		tradeClient: alpaca.NewClient(alpaca.ClientOpts{
			APIKey:    config.ApiKey,
			APISecret: config.SecretKey,
			BaseURL:   baseURL,
		}),
		dataClient: marketdata.NewClient(marketdata.ClientOpts{
			APIKey:    config.ApiKey,
			APISecret: config.SecretKey,
		}),
		streamClient: stream.NewStocksClient(feed,
			stream.WithCredentials(config.ApiKey, config.SecretKey),
		),
		feed:          feed,
		ticker:         ticker,
	}
	return manager;
}

func (man *TradingManager) String() string {
	return fmt.Sprintf("TradingManager ticker=%s", man.ticker)
}
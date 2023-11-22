package main

import (
	//"context"
	"fmt"
	"log"

	//"log"
	//"os"
	"errors"
	"time"

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

func (man *TradingManager) CancelAllOrders() error {
	orders, err := man.tradeClient.GetOrders(alpaca.GetOrdersRequest{
		Status: "open",
		Until: time.Now(),
		Limit: 100,
	})
	if err != nil {
		return errors.New("Failed to get open orders")
	}
	for _, order := range orders {
		if err := man.tradeClient.CancelOrder(order.ID); err != nil {
			return errors.New("Failed to cancel an order")

		}
	}
	//fmt.Printf("%d order(s) canceled", len(orders))
	return nil
}

func LogBar(bar stream.Bar) {

}

func (man *TradingManager) OnBar(currentBar stream.Bar) {
	if !man.GetClockFatal().IsOpen {
		return
	}

	if man.lastOrder != "" {
		man.tradeClient.CancelOrder(man.lastOrder)
	}

	bars, err := man.dataClient.GetBars(man.ticker, marketdata.GetBarsRequest{
		TimeFrame: marketdata.OneMin,
		Start: time.Now().Add(-15 * time.Minute),
		End: time.Now(),
		Feed: man.feed,
	})
	if err != nil {
		log.Fatalf("Failed to get historical data %v.", err)
	}
	//for _, pastBar := range bars {
		//log.Printf("PastBar time=%d:%d close=%f", pastBar.Timestamp.UTC().Hour(), pastBar.Timestamp.UTC().Minute(), pastBar.Close)
	//}

}

func (man* TradingManager) GetClockFatal() *alpaca.Clock {
	clock, err := man.tradeClient.GetClock()
	if err != nil {
		//return false, errors.New("Failed to get clock")
		log.Fatalf("Failed to get clock")
	}
	return clock
}

func (man* TradingManager) CheckMarketOpen() bool {
	clock := man.GetClockFatal()	
	if clock.IsOpen {
		return true
	}
	timeToOpen := int(clock.NextOpen.Sub(clock.Timestamp).Minutes())
	fmt.Printf("%d minutes until market open\n", timeToOpen);
	time.Sleep(1 * time.Minute)
	return false
}

func (man* TradingManager) CheckMarketClosed(buffer time.Duration) {
	clock := man.GetClockFatal()	
	untilClose := clock.NextClose.Sub(clock.Timestamp.Add(buffer))
	time.Sleep(untilClose)
	fmt.Println("Market closing soon. Closing position")
	if _, err := man.tradeClient.ClosePosition(man.ticker, alpaca.ClosePositionRequest{}); err != nil {
		log.Fatalf("Failed to close position: %v", man.ticker)
	}
	fmt.Println("Position closed")
}


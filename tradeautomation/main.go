// package tradeautomation
package main

import (
	//"context"
	"context"
	"fmt"
	"log"
	"time"

	"github.com/alpacahq/alpaca-trade-api-go/v3/marketdata"
	//"log"
	//"os"
	//"time"
	//"github.com/shopspring/decimal"
	//"github.com/alpacahq/alpaca-trade-api-go/v3/alpaca"
	//"github.com/alpacahq/alpaca-trade-api-go/v3/marketdata"
	//"github.com/alpacahq/alpaca-trade-api-go/v3/marketdata/stream"
)

func Mins(mins int) time.Duration {
	return time.Duration(mins) * time.Minute
}

func main() {

	cfg := LoadAPIConfig("secret.json")
	fmt.Println(cfg.String())

	man := InitTradingManager(cfg, "AAPL")
	fmt.Println(man.String())

	if err := man.CancelAllOrders(); err != nil {
		log.Fatalf(err.Error())
	}

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	if err := man.streamClient.Connect(ctx); err != nil {
		log.Fatalf("Failed to connect to marketdata stream")
	}
	if err := man.streamClient.SubscribeToBars(man.OnBar, man.ticker); err != nil {
		log.Fatalf("Failed to subscribe to the marketdata stream")
	}
	go func() {
		if err := <-man.streamClient.Terminated(); err != nil {
			log.Fatalf("The marketdata stream was terminated")
		}
	}()


	for {

	}
	//ProductionIterative(man)
	//TestHistorical(man)
}

func TestHistorical(man *TradingManager) {
	// Test for squarebounds (change file name)
}

func ProductionIterative(man *TradingManager) {
 
	for {
		if !man.CheckMarketOpen() {
			continue
		}

		bars, err := man.dataClient.GetBars(man.ticker, marketdata.GetBarsRequest{
			TimeFrame: marketdata.OneMin,
			Start: time.Now().Add(time.Minute * -(Mins(40) + 1)),
			End: time.Now(),
			//Start: time.Now().Add(-1 * Mins(600)),
			//End: time.Now().Add(-1 * Mins(400)),
			Feed: man.feed,
		})
		fmt.Println("gotbars")
		if err != nil {
			log.Fatalf("Failed to get historical data %v.", err)
		}
		fmt.Println("Got some bars:")
		for _, bar := range bars {
			fmt.Println(bar.Close)
		}

		man.CheckMarketClosed(Mins(15))


	}

}


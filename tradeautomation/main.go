// package tradeautomation
package main
import (
	//"context"
	"context"
	"log"
	//"log"
	//"os"
	//"time"
	//"github.com/shopspring/decimal"
	//"github.com/alpacahq/alpaca-trade-api-go/v3/alpaca"
	//"github.com/alpacahq/alpaca-trade-api-go/v3/marketdata"
	//"github.com/alpacahq/alpaca-trade-api-go/v3/marketdata/stream"
)

func main() {

	cfg := LoadAPIConfig("secret.json")
	log.Println(cfg.String())

	man := InitTradingManager(cfg, "AAPL")
	log.Println(man.String())

	if err := man.CancelAllOrders(); err != nil {
		log.Fatalf(err.Error())
	}

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	if err := man.streamClient.Connect(ctx); err != nil {
		log.Fatalf("Failed to connect to marketdata stream")
	}
	//if err := man.streamClient.SubscribeToBars(man.OnBar, man.ticker); err != nil {
	//	log.Fatalf("Failed to subscribe to the marketdata stream")
	//}
	go func() {
		if err := <-man.streamClient.Terminated(); err != nil {
			log.Fatalf("The marketdata stream was terminated")
		}
	}()

  man.TestAlgorithm()

	for {

	}
}

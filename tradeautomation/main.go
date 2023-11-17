//package tradeautomation
package main

import (
	//"context"
	"fmt"
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
	fmt.Println(cfg.String())

	man := InitTradingManager(cfg, "AAPL")
	fmt.Println(man.String())

}


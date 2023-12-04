package main

import (
	"fmt"

	"github.com/shopspring/decimal"
	"github.com/alpacahq/alpaca-trade-api-go/v3/alpaca"
)

type Order interface {
  OrderRequest() alpaca.PlaceOrderRequest
  String() string
  OrderQty() int
}

type LimitOrder struct {
  Qty int
  Ticker string
  Price float64
  Side string
}

func (o LimitOrder) OrderQty() int {
  return o.Qty
}

func (o LimitOrder) String() string {
  return fmt.Sprintf("limit %s %d * %s @ $%.2f Σ $%.2f", o.Side, o.Qty, o.Ticker, o.Price, o.Price * float64(o.Qty))
}

// This could be made a lot better (ie stop loss)
// https://pkg.go.dev/github.com/alpacahq/alpaca-trade-api-go/alpaca#PlaceOrderRequest
func (o LimitOrder) OrderRequest() alpaca.PlaceOrderRequest {
  alpside := alpaca.Side(o.Side)
	decimalQty := decimal.NewFromInt(int64(o.Qty))
  return alpaca.PlaceOrderRequest{
		Symbol:      o.Ticker,
		Qty:         &decimalQty,
		Side:        alpside,
		Type:        "limit",
		LimitPrice:  alpaca.RoundLimitPrice(decimal.NewFromFloat(o.Price), alpside),
		TimeInForce: "gtc", // needs some type of cancel logic
	}
}



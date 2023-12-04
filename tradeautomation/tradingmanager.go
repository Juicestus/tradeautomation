package main

import (
	"fmt"
	"log"

	"errors"
	"time"

	"github.com/alpacahq/alpaca-trade-api-go/v3/alpaca"
	"github.com/alpacahq/alpaca-trade-api-go/v3/marketdata"
	"github.com/alpacahq/alpaca-trade-api-go/v3/marketdata/stream"
)

const (
	stdlen = 14
	siglen = 28
  apportionment = 1
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
  return fmt.Sprintf("TradingManager: ticker=%s", man.ticker)
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
	log.Printf("Successfully canceled %d order(s)", len(orders))
	return nil
}

func (man *TradingManager) OnBar(currentBar stream.Bar) {
  log.Println("TradingManager recived new bar")
	if !man.GetClockFatal().IsOpen {
    log.Println("Market is not open yet")
		return
	}

  // TODO: make sure len(data) >= siglen
  // TODO: make sure the bot ends a little bit before closing

	if man.lastOrder != "" {
		man.tradeClient.CancelOrder(man.lastOrder)
	}

	bars, err := man.dataClient.GetBars(man.ticker, marketdata.GetBarsRequest{
		TimeFrame: marketdata.OneMin,
		Start: time.Now().Add(-stdlen * time.Minute),
		End: time.Now(),
		Feed: man.feed,
	})
	if err != nil {
		log.Fatalf("Failed to get historical data %v", err)
	}

	_open := StripBar(bars, func(bar marketdata.Bar) float64 { return bar.Open })
	_close := StripBar(bars, func(bar marketdata.Bar) float64 { return bar.Close })

	bull, bear, sig := SquareBoundsOscilator(_open, _close, stdlen, siglen)
	for i := 0; i < len(bull); i++ {
		//fmt.Printf("bull=%.4f  bear=%.4f  sig=%.4f\n", bull[i], bear[i], sig[i])
	}

  currentPrice := _close[len(_close) - 1]

  account, err := man.tradeClient.GetAccount()
  if err != nil {
    fmt.Printf("Could not get account data")
    return
  }

  buyingPower, _ := account.BuyingPower.Float64()

  posQty, _, err := man.GetPositionInfo()
  if err != nil {
    log.Printf("Get position failed, skipping bar")
    return
  }

  log.Printf("Current trading price of %s is $%.2f", man.ticker, currentPrice)
  log.Printf("Account buying power is $%.2f", buyingPower)
  if posQty > 0 {
    log.Printf("Account holds %d shares of %s totaling $%.2f", posQty, man.ticker, float64(posQty) * currentPrice)
  } else {
    log.Printf("Account holds no position in %s", man.ticker)
  }

  buyCondition := CrossOver(bull, bear) || true
  sellCondition := CrossOver(sig, bull)

  log.Printf("Buy condition: (algorithm)=%t && (qty==0)=%t", buyCondition, posQty == 0)
  log.Printf("Sell condition: (algorithm)=%t && (qty>0)=%t", sellCondition, posQty > 0)

  if buyCondition && posQty == 0 {
    log.Printf("Algorithm entering %s @ $%.2f", man.ticker, currentPrice)
    purchaseQty := int((apportionment * buyingPower) / currentPrice)
    order := LimitOrder{
      Qty: purchaseQty,
      Side: "buy",
      Ticker: man.ticker,
      Price: currentPrice,
    }
    err := man.PlaceOrder(order)
    if err != nil {
      fmt.Printf("Place order failed")
    }
  }

  if sellCondition && posQty > 0 {
    log.Printf("Algorithm exiting  %s @ $%.2f", man.ticker, currentPrice)
    order := LimitOrder{
      Qty: posQty,
      Side: "sell",
      Ticker: man.ticker,
      Price: currentPrice,
    }
    err := man.PlaceOrder(order)
    if err != nil {
      fmt.Printf("Place order failed")
    }
  }
}

func (man* TradingManager) PlaceOrder(order Order) error {
  if order.OrderQty() <= 0 {
		log.Printf("Order %s not sent because qty <= 0", order.String())
	}
  orderRes, err := man.tradeClient.PlaceOrder(order.OrderRequest())
  if err != nil {
    log.Printf("Order %s failed to place", order)
    return err
  }
  log.Printf("Order %s placed successfully", order)
  man.lastOrder = orderRes.ID
  return nil
}

func (man* TradingManager) GetPositionInfo() (int, float64, error) {
	position, err := man.tradeClient.GetPosition(man.ticker)
	if err != nil {
		if apiErr, ok := err.(*alpaca.APIError); !ok || apiErr.Message != "position does not exist" {
			return 0, 0.0, fmt.Errorf("Get position failed")
		}
    return 0, 0.0, nil
	} else {
    qty := int(position.Qty.IntPart())
    //qty = position.Qty.Float64()
    val, _ := position.MarketValue.Float64()
    return qty, val, nil
	}
}
// first crosses above second
func CrossOver(a, b []float64) bool {
  return a[len(a) - 1] > b[len(b) - 1] && a[len(a) - 2] < b[len(b) - 2]
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


func (man* TradingManager) TestAlgorithm() {
  tstart := time.Date(2023, 11, 27, 9+6, 0, 0, 0, time.UTC)
  tend := time.Date(2023, 11, 27, 14+6, 0, 0, 0, time.UTC)

	bars, err := man.dataClient.GetBars(man.ticker, marketdata.GetBarsRequest{
		TimeFrame: marketdata.OneMin,
		Start: tstart,
		End: tend,
		Feed: man.feed,
	})
	if err != nil {
		log.Fatalf("Failed to get historical data %v", err)
	}

	_open := StripBar(bars, func(bar marketdata.Bar) float64 { return bar.Open })
	_close := StripBar(bars, func(bar marketdata.Bar) float64 { return bar.Close })

	bull, bear, sig := SquareBoundsOscilator(_open, _close, stdlen, siglen)

	//for i := 0; i < len(bull); i++ {
		//fmt.Printf("open=%.4f  close=%.4f  bull=%.4f  bear=%.4f  sig=%.4f\n", _open[i], _close[i], bull[i], bear[i], sig[i])
	//}

  for l := siglen; l <= len(bull); l++ {

    cbull := bull[:l]
    cbear := bear[:l]
    csig := sig[:l]

    if CrossOver(cbull, cbear) {
      fmt.Printf("%d Buy @ $%f\n", l, _close[l - 1])
    }
    if CrossOver(csig, cbull) {
      fmt.Printf("%d Sell @ $%f\n", l, _close[l - 1])
    }
  }

}

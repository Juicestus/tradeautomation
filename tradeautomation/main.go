// package tradeautomation
package main

import (
	"context"
	"log"
  "net/http"
  "os"
  "fmt"
  "io"
)

const (
  prod = true
  logf = "tradeautomation.log"
)

func main() {

  f, err := os.OpenFile(logf, os.O_RDWR | os.O_CREATE | os.O_APPEND, 0666)
  if err != nil {
    log.Printf("Error opening log file: %v", err)
  }
  defer f.Close()

  wrt := io.MultiWriter(os.Stdout, f)
  log.SetOutput(wrt)

	cfg := LoadAPIConfig("secret.json")
	//log.Println(cfg.String())

	man := InitTradingManager(cfg, "AAPL")
	log.Println(man.String())

  if err := man.CancelAllOrders(); err != nil {
    log.Print(err)
  }

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	if err := man.streamClient.Connect(ctx); err != nil {
		log.Fatalf("Failed to connect to marketdata stream")
	}
  if prod {
	  if err := man.streamClient.SubscribeToBars(man.OnBar, man.ticker); err != nil {
		  log.Fatalf("Failed to subscribe to the marketdata stream")
	  }
  }
	go func() {
		if err := <-man.streamClient.Terminated(); err != nil {
			log.Fatalf("The marketdata stream was terminated")
		}
	}()

  if !prod {
    man.TestAlgorithm()
  }

  http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "no content")
  })

  http.HandleFunc("/log", func(w http.ResponseWriter, r *http.Request) {
  	f, err := os.Open(logf)
    if err != nil {
      fmt.Fprintf(w, "Failed to retrive log file")
      return
    }
    defer f.Close()
    data, err := io.ReadAll(f)
    if err != nil {
      fmt.Fprintf(w, "Failed to retrive log file")
      return
    }
    fmt.Fprintf(w, string(data))
  })

  log.Print(http.ListenAndServe(":8080", nil))
}

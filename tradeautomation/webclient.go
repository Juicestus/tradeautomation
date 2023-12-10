package main

import (
	"fmt"
	"os"
  "log"
  "net/http"
  "io"
  "strings"
)

type HTMLTemplate struct {
  Path string
  content string
}

func LoadHTML(path string) (*HTMLTemplate, error) {
  f, err := os.Open(path)
  if err != nil {
    return nil, fmt.Errorf("Failed to load template %s", path)
  }
  defer f.Close()
  content, err := io.ReadAll(f)
  if err != nil {
    return nil, fmt.Errorf("Failed to load template %s", path)
  }
  return &HTMLTemplate{
    Path: path,
    content: string(content),
  }, nil
}

func (t* HTMLTemplate) Fill(id, value string) {
  t.content = strings.Replace(t.content, "{{" + id + "}}", value, -1)
}

func (t* HTMLTemplate) Write(w http.ResponseWriter) {
  fmt.Fprintf(w, t.content)
}


type ClientData struct {
  Ticker string
  PosQty int
  PosVal float64
  BuyingPower float64
  OrderHistory []Order

  // Should abstract these -- worry abt that later
  Close []float64
  Bull []float64
  Bear []float64
  Sig []float64
}

func RunWebClient(logf string, prod bool, sup func()ClientData) {

  cd := sup()

  d, err := LoadHTML("templates/dashboard.html")
  if err != nil {
    log.Fatal(err)
  }

  http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
    d.Fill("tkr", cd.Ticker)
    d.Fill("qty", fmt.Sprintf("%d", cd.PosQty))
    d.Fill("val", fmt.Sprintf("%.2f", cd.PosVal))
    d.Fill("buypwr", fmt.Sprintf("%.2f", cd.BuyingPower))

    d.Write(w)
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

  if prod {
    log.Print(http.ListenAndServe("0.0.0.0:80", nil))
  } else {
    log.Print(http.ListenAndServe("127.0.0.1:8080", nil))
  }

}

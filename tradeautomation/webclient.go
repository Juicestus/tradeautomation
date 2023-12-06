package main

import (
	"fmt"
	"os"
  "log"
  "net/http"
  "io"
)

func RunWebClient(logf string, prod bool) {
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

  if prod {
    log.Print(http.ListenAndServe("0.0.0.0:80", nil))
  } else {
    log.Print(http.ListenAndServe("127.0.0.1:8080", nil))
  }

}

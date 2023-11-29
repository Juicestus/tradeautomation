package main

//"context"
// "fmt"
// "log"

//"log"
//"os"
// "errors"
// "time"

import (
	"fmt"
	"math"
  "log"
  "os"

	"github.com/alpacahq/alpaca-trade-api-go/v3/marketdata"
)

// func Strip_open_close[T](bars []marketdata.Bar, supplier func(marketdata.Bar)(float64)) ([]float64, []float64) {
// 	_open := []float64{}
// 	_close := []float64{}
// 	for i, bar := range bars {
// 		_open[i] = bar._open
// 		_close[i] = bar._close
// 	}
// 	return _open, _close
// }

func StripBar[T any](bars []marketdata.Bar, supplier func(marketdata.Bar)(T)) []T {
	result := make([]T, len(bars))
	for i, bar := range bars {
		result[i] = supplier(bar)
	}
	return result
}

func SquareBoundsOscilator(_open []float64, _close []float64, stdlen int, siglen int) ([]float64, []float64, []float64) {
	N := len(_close)
  //alphastd := float64(2 / (stdlen + 1))
  alphastd := 2.0 / float64(stdlen + 1)
  //alphasig := float64(2 / (siglen + 1))
  alphasig := 2.0 / float64(siglen + 1)

  up1 := make([]float64, N)
	up2 := make([]float64, N)
	dn1 := make([]float64, N)
	dn2 := make([]float64, N)
	bull := make([]float64, N)
	bear := make([]float64, N)
	sig := make([]float64, N)

  up1[0] =  _close[0]
  dn1[0] = _close[0]
  sig[0] = _close[0]

  up2[0] = math.Pow(_close[0], 2)
  dn2[0] = math.Pow(_close[0], 2)

  fmt.Println(alphastd)
  fmt.Println(alphasig)
  fmt.Println(up1[0])


	for i := 1; i < N; i++ {
        up1[i] = max(_close[i], _open[i], up1[i - 1] - alphastd * (up1[i - 1] - _close[i]))
        dn1[i] = min(_close[i], _open[i], dn1[i - 1] + alphastd * (_close[i] - dn1[i - 1]))

        up2[i] = max(math.Pow(_close[i] , 2), math.Pow(_open[i] , 2), up2[i - 1] - alphastd * (up2[i - 1] - math.Pow(_close[i] , 2)))
        dn2[i] = min(math.Pow(_close[i] , 2), math.Pow(_open[i] , 2), dn2[i - 1] + alphastd * (math.Pow(_close[i] , 2) - dn2[i - 1]))

        bull[i] = math.Sqrt(dn2[i] - math.Pow(dn1[i] , 2))
        bear[i] = math.Sqrt(up2[i] - math.Pow(up1[i] , 2))

        //sig[i] = sig[i - 1] + alphastd_sig * (np.maximum(bull[i], bear[i]) - sig[i - 1])
		sig[i] = sig[i - 1] + alphasig * (max(bull[i], bear[i]) - sig[i - 1])

    //fmt.Printf("up1=%.4f dn1=%.4f up2=%.4f dn2=%.4f bull=%.4f bear=%.4f\n", up1[i], dn1[i], up2[i], dn2[i], bull[i], bear[i])
	}

    return bull, bear, sig
}

func WriteArray(fn string, arr []float64) {
  f, err := os.OpenFile(fn, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
  if err != nil {
    log.Println(err)
  }
  defer f.Close()
  for _, e := range arr {
    s := fmt.Sprintf("%.8f\n", e)
    if _, err := f.WriteString(s); err != nil {
      log.Println(err)
    }
  }
}

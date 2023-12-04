package main

import (
	"fmt"
	"os"
	"encoding/json"
  "log"
)

type APIConfig struct {
	ApiKey string `json:"ApiKey"`
	SecretKey string `json:"SecretKey"`
}

func LoadAPIConfig(filename string) *APIConfig {
	var cfg APIConfig
	file, err := os.Open(filename)
	if err != nil {
		log.Fatalf("Failed to open config file%s\n", filename)
	}
	defer file.Close()
	parser := json.NewDecoder(file)
	if err := parser.Decode(&cfg); err != nil {
		log.Fatalf("Failed to parse config file\n")
	}
	return &cfg
}

func (cfg *APIConfig) String() string {
	return fmt.Sprintf("ApiKey=%s SecretKey=%s", cfg.ApiKey, cfg.SecretKey)
}




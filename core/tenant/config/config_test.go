package config

import (
	"fmt"
	"os"
	"testing"
)

func TestLoadConfig(t *testing.T) {
	// Set environment variables for testing
	os.Setenv("APP_SERVER_PORT", "8080")
	os.Setenv("APP_SERVER_LOCATION", "localhost")
	os.Setenv("APP_DATABASE_DB_TYPE", "mysql")
	os.Setenv("APP_DATABASE_USERNAME", "root")
	os.Setenv("APP_DATABASE_PASSWORD", "password")
	os.Setenv("APP_DATABASE_URL", "localhost:3306")
	os.Setenv("APP_DATABASE_MAX_OPEN_CONNS", "100")
	os.Setenv("APP_DATABASE_MAX_IDLE_CONNS", "10")
	os.Setenv("APP_LOG_FILE", "log.txt")
	// Assume config.toml exists with some default values
	cfg, err := LoadConfig("./config.toml")
	if err != nil {
		t.Errorf("LoadConfig() error = %v", err)
	}
	fmt.Println(cfg.String())
}

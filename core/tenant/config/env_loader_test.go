package config

import (
	"fmt"
	"os"
	"testing"
)

func TestEnvLoader_Load(t *testing.T) {
	// Set environment variables for testing
	os.Setenv("SERVICE_PORT", "8080")
	os.Setenv("SERVICE_LOCATION", "localhost")
	os.Setenv("DATABASE_DB_TYPE", "mysql")
	os.Setenv("DATABASE_USERNAME", "root")
	os.Setenv("DATABASE_PASSWORD", "password")
	os.Setenv("DATABASE_URL", "(localhost:3306)/tenant")
	os.Setenv("DATABASE_MAX_OPEN_CONNS", "100")
	os.Setenv("DATABASE_MAX_IDLE_CONNS", "10")
	os.Setenv("LOG_PATH", "log.txt")

	cfg := &Config{}
	l := NewEnvLoader()
	if err := l.Load(cfg); err != nil {
		t.Errorf("Load() error = %v", err)
	}
	fmt.Println(cfg.String())
}

package config

import (
	"fmt"
	"os"
)

type EnvLoader struct {
}

func NewEnvLoader() *EnvLoader {
	return &EnvLoader{}
}

func (l *EnvLoader) Load(cfg *Config) error {
	// No operation, as environment variables are accessed directly in the application.
	if v := os.Getenv("APP_SERVER_PORT"); v != "" {
		fmt.Sscanf(v, "%d", &cfg.Server.Port)
	}
	if v := os.Getenv("APP_SERVER_LOCATION"); v != "" {
		cfg.Server.Location = v
	}
	if v := os.Getenv("APP_DATABASE_DB_TYPE"); v != "" {
		cfg.DataBase.DBType = v
	}
	if v := os.Getenv("APP_DATABASE_USERNAME"); v != "" {
		cfg.DataBase.UserName = v
	}
	if v := os.Getenv("APP_DATABASE_PASSWORD"); v != "" {
		cfg.DataBase.Password = v
	}
	if v := os.Getenv("APP_DATABASE_URL"); v != "" {
		cfg.DataBase.Url = v
	}
	if v := os.Getenv("APP_DATABASE_MAX_OPEN_CONNS"); v != "" {
		fmt.Sscanf(v, "%d", &cfg.DataBase.MaxOpenConns)
	}
	if v := os.Getenv("APP_DATABASE_MAX_IDLE_CONNS"); v != "" {
		fmt.Sscanf(v, "%d", &cfg.DataBase.MaxIdleConns)
	}
	if v := os.Getenv("APP_LOG_FILE"); v != "" {
		cfg.Log.LogFile = v
	}
	return nil
}

func (l *EnvLoader) Watch(cfg *Config, onChange func()) {
}

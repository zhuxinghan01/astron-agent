package config

import (
	"os"
	"testing"
)

func TestNewEnvLoader(t *testing.T) {
	loader := NewEnvLoader()

	if loader == nil {
		t.Errorf("NewEnvLoader() returned nil")
	}

	// Test that it creates an empty struct (no fields to validate)
	if loader == nil {
		t.Errorf("NewEnvLoader() should return non-nil EnvLoader")
	}
}

func TestEnvLoader_Load(t *testing.T) {
	tests := []struct {
		name     string
		envVars  map[string]string
		wantErr  bool
		validate func(*Config) error
	}{
		{
			name: "all environment variables set",
			envVars: map[string]string{
				"SERVICE_PORT":            "8080",
				"SERVICE_LOCATION":        "us-west",
				"DATABASE_DB_TYPE":        "mysql",
				"DATABASE_USERNAME":       "envuser",
				"DATABASE_PASSWORD":       "envpass",
				"DATABASE_URL":            "localhost:3306/envdb",
				"DATABASE_MAX_OPEN_CONNS": "15",
				"DATABASE_MAX_IDLE_CONNS": "8",
				"LOG_PATH":                "/var/log/env.log",
			},
			wantErr: false,
			validate: func(cfg *Config) error {
				if cfg.Server.Port != 8080 {
					t.Errorf("Expected port 8080, got %d", cfg.Server.Port)
				}
				if cfg.Server.Location != "us-west" {
					t.Errorf("Expected location 'us-west', got %s", cfg.Server.Location)
				}
				if cfg.DataBase.DBType != "mysql" {
					t.Errorf("Expected dbType 'mysql', got %s", cfg.DataBase.DBType)
				}
				if cfg.DataBase.UserName != "envuser" {
					t.Errorf("Expected username 'envuser', got %s", cfg.DataBase.UserName)
				}
				if cfg.DataBase.Password != "envpass" {
					t.Errorf("Expected password 'envpass', got %s", cfg.DataBase.Password)
				}
				if cfg.DataBase.Url != "localhost:3306/envdb" {
					t.Errorf("Expected url 'localhost:3306/envdb', got %s", cfg.DataBase.Url)
				}
				if cfg.DataBase.MaxOpenConns != 15 {
					t.Errorf("Expected MaxOpenConns 15, got %d", cfg.DataBase.MaxOpenConns)
				}
				if cfg.DataBase.MaxIdleConns != 8 {
					t.Errorf("Expected MaxIdleConns 8, got %d", cfg.DataBase.MaxIdleConns)
				}
				if cfg.Log.LogFile != "/var/log/env.log" {
					t.Errorf("Expected log file '/var/log/env.log', got %s", cfg.Log.LogFile)
				}
				return nil
			},
		},
		{
			name:    "no environment variables set",
			envVars: map[string]string{},
			wantErr: false,
			validate: func(cfg *Config) error {
				// All fields should remain at zero values
				if cfg.Server.Port != 0 {
					t.Errorf("Expected port 0, got %d", cfg.Server.Port)
				}
				if cfg.Server.Location != "" {
					t.Errorf("Expected empty location, got %s", cfg.Server.Location)
				}
				if cfg.DataBase.DBType != "" {
					t.Errorf("Expected empty dbType, got %s", cfg.DataBase.DBType)
				}
				return nil
			},
		},
		{
			name: "partial environment variables set",
			envVars: map[string]string{
				"SERVICE_PORT":     "9090",
				"DATABASE_DB_TYPE": "postgresql",
				"LOG_PATH":         "/tmp/partial.log",
			},
			wantErr: false,
			validate: func(cfg *Config) error {
				if cfg.Server.Port != 9090 {
					t.Errorf("Expected port 9090, got %d", cfg.Server.Port)
				}
				if cfg.DataBase.DBType != "postgresql" {
					t.Errorf("Expected dbType 'postgresql', got %s", cfg.DataBase.DBType)
				}
				if cfg.Log.LogFile != "/tmp/partial.log" {
					t.Errorf("Expected log file '/tmp/partial.log', got %s", cfg.Log.LogFile)
				}
				// Unset variables should remain empty/zero
				if cfg.Server.Location != "" {
					t.Errorf("Expected empty location, got %s", cfg.Server.Location)
				}
				if cfg.DataBase.UserName != "" {
					t.Errorf("Expected empty username, got %s", cfg.DataBase.UserName)
				}
				return nil
			},
		},
		{
			name: "invalid SERVICE_PORT",
			envVars: map[string]string{
				"SERVICE_PORT": "invalid_port",
			},
			wantErr: true,
		},
		{
			name: "invalid DATABASE_MAX_OPEN_CONNS",
			envVars: map[string]string{
				"DATABASE_MAX_OPEN_CONNS": "not_a_number",
			},
			wantErr: true,
		},
		{
			name: "invalid DATABASE_MAX_IDLE_CONNS",
			envVars: map[string]string{
				"DATABASE_MAX_IDLE_CONNS": "also_not_a_number",
			},
			wantErr: true,
		},
		{
			name: "empty string environment variables",
			envVars: map[string]string{
				"SERVICE_PORT":     "",
				"SERVICE_LOCATION": "",
				"DATABASE_DB_TYPE": "",
			},
			wantErr: false,
			validate: func(cfg *Config) error {
				// Empty strings should not override zero values
				if cfg.Server.Port != 0 {
					t.Errorf("Expected port 0 (empty env var), got %d", cfg.Server.Port)
				}
				if cfg.Server.Location != "" {
					t.Errorf("Expected empty location (empty env var), got %s", cfg.Server.Location)
				}
				if cfg.DataBase.DBType != "" {
					t.Errorf("Expected empty dbType (empty env var), got %s", cfg.DataBase.DBType)
				}
				return nil
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Store original environment values
			originalEnv := make(map[string]string)
			envKeys := []string{
				"SERVICE_PORT", "SERVICE_LOCATION",
				"DATABASE_DB_TYPE", "DATABASE_USERNAME", "DATABASE_PASSWORD",
				"DATABASE_URL", "DATABASE_MAX_OPEN_CONNS", "DATABASE_MAX_IDLE_CONNS",
				"LOG_PATH",
			}

			for _, key := range envKeys {
				originalEnv[key] = os.Getenv(key)
				os.Unsetenv(key) // Clear environment first
			}

			// Set test environment variables
			for key, value := range tt.envVars {
				os.Setenv(key, value)
			}

			// Cleanup environment after test
			defer func() {
				for _, key := range envKeys {
					if originalVal, exists := originalEnv[key]; exists {
						os.Setenv(key, originalVal)
					} else {
						os.Unsetenv(key)
					}
				}
			}()

			// Test EnvLoader.Load
			loader := NewEnvLoader()
			cfg := &Config{}
			err := loader.Load(cfg)

			if (err != nil) != tt.wantErr {
				t.Errorf("EnvLoader.Load() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			if !tt.wantErr && tt.validate != nil {
				if err := tt.validate(cfg); err != nil {
					t.Errorf("Config validation failed: %v", err)
				}
			}
		})
	}
}

func TestEnvLoader_Load_IntegerParsing(t *testing.T) {
	tests := []struct {
		name    string
		envVar  string
		value   string
		wantErr bool
	}{
		{
			name:    "valid integer SERVICE_PORT",
			envVar:  "SERVICE_PORT",
			value:   "8080",
			wantErr: false,
		},
		{
			name:    "zero SERVICE_PORT",
			envVar:  "SERVICE_PORT",
			value:   "0",
			wantErr: false,
		},
		{
			name:    "negative SERVICE_PORT",
			envVar:  "SERVICE_PORT",
			value:   "-1",
			wantErr: false,
		},
		{
			name:    "invalid SERVICE_PORT",
			envVar:  "SERVICE_PORT",
			value:   "abc",
			wantErr: true,
		},
		{
			name:    "float SERVICE_PORT",
			envVar:  "SERVICE_PORT",
			value:   "8080.5",
			wantErr: false, // fmt.Sscanf with %d will parse "8080.5" as 8080 (truncates)
		},
		{
			name:    "valid DATABASE_MAX_OPEN_CONNS",
			envVar:  "DATABASE_MAX_OPEN_CONNS",
			value:   "10",
			wantErr: false,
		},
		{
			name:    "invalid DATABASE_MAX_OPEN_CONNS",
			envVar:  "DATABASE_MAX_OPEN_CONNS",
			value:   "invalid",
			wantErr: true,
		},
		{
			name:    "valid DATABASE_MAX_IDLE_CONNS",
			envVar:  "DATABASE_MAX_IDLE_CONNS",
			value:   "5",
			wantErr: false,
		},
		{
			name:    "invalid DATABASE_MAX_IDLE_CONNS",
			envVar:  "DATABASE_MAX_IDLE_CONNS",
			value:   "not_number",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Clear all environment variables first
			envKeys := []string{
				"SERVICE_PORT", "DATABASE_MAX_OPEN_CONNS", "DATABASE_MAX_IDLE_CONNS",
			}
			originalEnv := make(map[string]string)
			for _, key := range envKeys {
				originalEnv[key] = os.Getenv(key)
				os.Unsetenv(key)
			}

			// Set the specific test environment variable
			os.Setenv(tt.envVar, tt.value)

			// Cleanup
			defer func() {
				for _, key := range envKeys {
					if originalVal, exists := originalEnv[key]; exists {
						os.Setenv(key, originalVal)
					} else {
						os.Unsetenv(key)
					}
				}
			}()

			loader := NewEnvLoader()
			cfg := &Config{}
			err := loader.Load(cfg)

			if (err != nil) != tt.wantErr {
				t.Errorf("EnvLoader.Load() with %s=%s, error = %v, wantErr %v", tt.envVar, tt.value, err, tt.wantErr)
			}
		})
	}
}

func TestEnvLoader_Watch(t *testing.T) {
	// Test the Watch method (currently empty implementation)
	loader := NewEnvLoader()
	cfg := &Config{}

	callbackCalled := false
	onChange := func() {
		callbackCalled = true
	}

	// This should not panic or error, even though it's a no-op
	defer func() {
		if r := recover(); r != nil {
			t.Errorf("EnvLoader.Watch() should not panic: %v", r)
		}
	}()

	loader.Watch(cfg, onChange)

	// Since it's a no-op, callback should not be called
	if callbackCalled {
		t.Errorf("EnvLoader.Watch() callback should not be called in current implementation")
	}
}

func TestEnvLoader_Interface(t *testing.T) {
	// Test that EnvLoader implements ConfLoader interface
	var _ ConfLoader = &EnvLoader{}

	loader := NewEnvLoader()

	// Test that we can call interface methods
	cfg := &Config{}

	// Load method
	err := loader.Load(cfg)
	if err != nil {
		t.Errorf("EnvLoader.Load() should not error with clean environment: %v", err)
	}

	// Watch method
	loader.Watch(cfg, func() {})
	// No error expected since it's a no-op
}

func TestEnvLoader_LoadPreservesExistingConfig(t *testing.T) {
	// Test that Load only overrides values that have corresponding env vars

	// Pre-populate config with values
	cfg := &Config{}
	cfg.Server.Port = 3000
	cfg.Server.Location = "original-location"
	cfg.DataBase.DBType = "original-db"
	cfg.Log.LogFile = "original.log"

	// Set only one environment variable
	originalPort := os.Getenv("SERVICE_PORT")
	os.Setenv("SERVICE_PORT", "8080")
	defer func() {
		if originalPort != "" {
			os.Setenv("SERVICE_PORT", originalPort)
		} else {
			os.Unsetenv("SERVICE_PORT")
		}
	}()

	loader := NewEnvLoader()
	err := loader.Load(cfg)

	if err != nil {
		t.Errorf("EnvLoader.Load() should not error: %v", err)
	}

	// Port should be overridden by env var
	if cfg.Server.Port != 8080 {
		t.Errorf("Expected port to be overridden to 8080, got %d", cfg.Server.Port)
	}

	// Other values should remain unchanged (since no env vars set for them)
	if cfg.Server.Location != "original-location" {
		t.Errorf("Expected location to remain 'original-location', got %s", cfg.Server.Location)
	}
	if cfg.DataBase.DBType != "original-db" {
		t.Errorf("Expected dbType to remain 'original-db', got %s", cfg.DataBase.DBType)
	}
	if cfg.Log.LogFile != "original.log" {
		t.Errorf("Expected log file to remain 'original.log', got %s", cfg.Log.LogFile)
	}
}

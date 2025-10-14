package config

import (
	"os"
	"path/filepath"
	"testing"
)

func TestNewLocalLoader(t *testing.T) {
	tests := []struct {
		name         string
		path         string
		expectedPath string
	}{
		{
			name:         "with custom path",
			path:         "/custom/path/config.toml",
			expectedPath: "/custom/path/config.toml",
		},
		{
			name:         "with empty path",
			path:         "",
			expectedPath: "./config.toml",
		},
		{
			name:         "with relative path",
			path:         "configs/app.toml",
			expectedPath: "configs/app.toml",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			loader := NewLocalLoader(tt.path)

			if loader == nil {
				t.Errorf("NewLocalLoader() returned nil")
				return
			}

			if loader.Path != tt.expectedPath {
				t.Errorf("NewLocalLoader() path = %s, want %s", loader.Path, tt.expectedPath)
			}
		})
	}
}

func TestLocalLoader_Load(t *testing.T) {
	// Create temporary directory for test files
	tempDir := t.TempDir()

	tests := []struct {
		name       string
		configFile string
		wantErr    bool
		validate   func(*Config) error
	}{
		{
			name: "valid TOML config",
			configFile: `
[service]
port = 8080
location = "us-east"

[database]
dbType = "mysql"
username = "testuser"
password = "testpass"
url = "localhost:3306/testdb"
maxOpenConns = 10
maxIdleConns = 5

[log]
path = "/tmp/test.log"
`,
			wantErr: false,
			validate: func(cfg *Config) error {
				if cfg.Server.Port != 8080 {
					t.Errorf("Expected port 8080, got %d", cfg.Server.Port)
				}
				if cfg.Server.Location != "us-east" {
					t.Errorf("Expected location 'us-east', got %s", cfg.Server.Location)
				}
				if cfg.DataBase.DBType != "mysql" {
					t.Errorf("Expected dbType 'mysql', got %s", cfg.DataBase.DBType)
				}
				if cfg.DataBase.UserName != "testuser" {
					t.Errorf("Expected username 'testuser', got %s", cfg.DataBase.UserName)
				}
				if cfg.DataBase.Password != "testpass" {
					t.Errorf("Expected password 'testpass', got %s", cfg.DataBase.Password)
				}
				if cfg.DataBase.Url != "localhost:3306/testdb" {
					t.Errorf("Expected url 'localhost:3306/testdb', got %s", cfg.DataBase.Url)
				}
				if cfg.DataBase.MaxOpenConns != 10 {
					t.Errorf("Expected MaxOpenConns 10, got %d", cfg.DataBase.MaxOpenConns)
				}
				if cfg.DataBase.MaxIdleConns != 5 {
					t.Errorf("Expected MaxIdleConns 5, got %d", cfg.DataBase.MaxIdleConns)
				}
				if cfg.Log.LogFile != "/tmp/test.log" {
					t.Errorf("Expected log file '/tmp/test.log', got %s", cfg.Log.LogFile)
				}
				return nil
			},
		},
		{
			name: "partial TOML config",
			configFile: `
[service]
port = 9090

[database]
dbType = "postgresql"
username = "partialuser"
`,
			wantErr: false,
			validate: func(cfg *Config) error {
				if cfg.Server.Port != 9090 {
					t.Errorf("Expected port 9090, got %d", cfg.Server.Port)
				}
				if cfg.Server.Location != "" {
					t.Errorf("Expected empty location, got %s", cfg.Server.Location)
				}
				if cfg.DataBase.DBType != "postgresql" {
					t.Errorf("Expected dbType 'postgresql', got %s", cfg.DataBase.DBType)
				}
				if cfg.DataBase.UserName != "partialuser" {
					t.Errorf("Expected username 'partialuser', got %s", cfg.DataBase.UserName)
				}
				// Other fields should be zero values
				if cfg.DataBase.Password != "" {
					t.Errorf("Expected empty password, got %s", cfg.DataBase.Password)
				}
				if cfg.DataBase.MaxOpenConns != 0 {
					t.Errorf("Expected MaxOpenConns 0, got %d", cfg.DataBase.MaxOpenConns)
				}
				return nil
			},
		},
		{
			name: "empty TOML config",
			configFile: `# Empty config file
`,
			wantErr: false,
			validate: func(cfg *Config) error {
				// All fields should be zero values
				if cfg.Server.Port != 0 {
					t.Errorf("Expected port 0, got %d", cfg.Server.Port)
				}
				if cfg.DataBase.DBType != "" {
					t.Errorf("Expected empty dbType, got %s", cfg.DataBase.DBType)
				}
				return nil
			},
		},
		{
			name: "invalid TOML syntax",
			configFile: `
[service
port = 8080  # Missing closing bracket
location = "invalid
`,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Create config file
			configPath := filepath.Join(tempDir, "test_config.toml")
			err := os.WriteFile(configPath, []byte(tt.configFile), 0644)
			if err != nil {
				t.Fatalf("Failed to write test config file: %v", err)
			}

			// Create loader and load config
			loader := NewLocalLoader(configPath)
			cfg := &Config{}
			err = loader.Load(cfg)

			if (err != nil) != tt.wantErr {
				t.Errorf("LocalLoader.Load() error = %v, wantErr %v", err, tt.wantErr)
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

func TestLocalLoader_Load_FileNotFound(t *testing.T) {
	loader := NewLocalLoader("/path/that/does/not/exist.toml")
	cfg := &Config{}

	err := loader.Load(cfg)

	if err == nil {
		t.Errorf("LocalLoader.Load() with non-existent file should return error")
	}
}

func TestLocalLoader_Load_PermissionDenied(t *testing.T) {
	// Create a temporary file with restricted permissions
	tempDir := t.TempDir()
	configPath := filepath.Join(tempDir, "restricted_config.toml")

	// Write config file
	err := os.WriteFile(configPath, []byte(`[service]\nport = 8080`), 0644)
	if err != nil {
		t.Fatalf("Failed to write test config file: %v", err)
	}

	// Remove read permissions (this may not work on all systems)
	err = os.Chmod(configPath, 0000)
	if err != nil {
		t.Skipf("Cannot change file permissions on this system: %v", err)
	}

	// Restore permissions for cleanup
	defer os.Chmod(configPath, 0644)

	loader := NewLocalLoader(configPath)
	cfg := &Config{}

	err = loader.Load(cfg)

	if err == nil {
		t.Errorf("LocalLoader.Load() with permission denied file should return error")
	}
}

func TestLocalLoader_Watch(t *testing.T) {
	// Test the Watch method (currently empty implementation)
	loader := NewLocalLoader("test.toml")
	cfg := &Config{}

	callbackCalled := false
	onChange := func() {
		callbackCalled = true
	}

	// This should not panic or error, even though it's a no-op
	defer func() {
		if r := recover(); r != nil {
			t.Errorf("LocalLoader.Watch() should not panic: %v", r)
		}
	}()

	loader.Watch(cfg, onChange)

	// Since it's a no-op, callback should not be called
	if callbackCalled {
		t.Errorf("LocalLoader.Watch() callback should not be called in current implementation")
	}
}

func TestLocalLoader_Interface(t *testing.T) {
	// Test that LocalLoader implements ConfLoader interface
	var _ ConfLoader = &LocalLoader{}

	loader := NewLocalLoader("test.toml")

	// Test that we can call interface methods
	cfg := &Config{}

	// Load method
	err := loader.Load(cfg)
	// Error is expected since file doesn't exist, but method should be callable
	if err == nil {
		t.Log("Load method succeeded unexpectedly (file might exist)")
	}

	// Watch method
	loader.Watch(cfg, func() {})
	// No error expected since it's a no-op
}

func TestLocalLoader_DefaultPath(t *testing.T) {
	// Test that default path is used when empty string is provided
	loader := NewLocalLoader("")

	expectedDefaultPath := "./config.toml"
	if loader.Path != expectedDefaultPath {
		t.Errorf("NewLocalLoader(\"\") should use default path %s, got %s", expectedDefaultPath, loader.Path)
	}
}

func TestLocalLoader_StructFields(t *testing.T) {
	// Test LocalLoader struct fields
	testPath := "/test/path/config.toml"
	loader := &LocalLoader{Path: testPath}

	if loader.Path != testPath {
		t.Errorf("LocalLoader.Path = %s, want %s", loader.Path, testPath)
	}

	// Test that Path field is accessible and modifiable
	newPath := "/new/path/config.toml"
	loader.Path = newPath

	if loader.Path != newPath {
		t.Errorf("After modification, LocalLoader.Path = %s, want %s", loader.Path, newPath)
	}
}

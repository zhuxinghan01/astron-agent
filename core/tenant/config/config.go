package config

type Config struct {
	Server struct {
		Port     int    `toml:"port"`
		Location string `toml:"location"`
	} `toml:"server"`

	DataBase struct {
		DBType       string `toml:"dbType"`
		UserName     string `toml:"username"`
		Password     string `toml:"password"`
		Url          string `toml:"url"`
		MaxOpenConns int    `toml:"maxOpenConns"`
		MaxIdleConns int    `toml:"maxIdleConns"`
	} `toml:"database"`

	Log struct {
		LogFile string `toml:"logFile"`
	} `toml:"log"`
}

func LoadConfig(path string) (*Config, error) {
	cfg := &Config{}
	loader := NewLocalLoader(path)
	if err := loader.Load(cfg); err != nil {
		return nil, err
	}
	return cfg, nil
}

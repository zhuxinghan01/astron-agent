package database

import (
	"fmt"
	"tenant/config"
	"testing"
)

func TestNewDatabase(*testing.T) {
	conf := &config.Config{
		DataBase: struct {
			DBType       string `toml:"dbType"`
			UserName     string `toml:"username"`
			Password     string `toml:"password"`
			Url          string `toml:"url"`
			MaxOpenConns int    `toml:"maxOpenConns"`
			MaxIdleConns int    `toml:"maxIdleConns"`
		}(struct {
			DBType       string
			UserName     string
			Password     string
			Url          string
			MaxOpenConns int
			MaxIdleConns int
		}{
			DBType:       "mysql",
			UserName:     "dev_admin",
			Password:     "Ug7sU%Kx^i^PtskG",
			Url:          "(km8avzyout43.mysql.hf04.dbaas.private:23350)/app_service",
			MaxOpenConns: 10,
			MaxIdleConns: 5,
		}),
	}
	_, err := NewDatabase(conf)
	fmt.Println(err)
}

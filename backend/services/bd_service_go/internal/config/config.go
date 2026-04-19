package config

import (
    "os"
    "strconv"
    "time"
)

type Config struct {
    DB     DBConfig
    Server ServerConfig
}

type DBConfig struct {
    Host     string
    Port     int
    User     string
    Password string
    Name     string
    PoolSize int32
}

type ServerConfig struct {
    Port         string
    ReadTimeout  time.Duration
    WriteTimeout time.Duration
}

func Load() *Config {
    return &Config{
        DB: DBConfig{
            Host:     getEnv("DB_HOST", "localhost"),
            Port:     getEnvAsInt("DB_PORT", 5432),
            User:     getEnv("DB_USER", "postgres"),
            Password: getEnv("DB_PASSWORD", "postgres"),
            Name:     getEnv("DB_NAME", "trackdb"),
            PoolSize: int32(getEnvAsInt("DB_POOL_SIZE", 10)),
        },
        Server: ServerConfig{
            Port:         getEnv("SERVER_PORT", "8004"),
            ReadTimeout:  time.Duration(getEnvAsInt("SERVER_READ_TIMEOUT", 5)) * time.Second,
            WriteTimeout: time.Duration(getEnvAsInt("SERVER_WRITE_TIMEOUT", 10)) * time.Second,
        },
    }
}

func getEnv(key, defaultValue string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return defaultValue
}

func getEnvAsInt(key string, defaultValue int) int {
    if value := os.Getenv(key); value != "" {
        if intVal, err := strconv.Atoi(value); err == nil {
            return intVal
        }
    }
    return defaultValue
}
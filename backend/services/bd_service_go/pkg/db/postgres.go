package db

import (
    "context"
    "fmt"
    "time"

    "github.com/jackc/pgx/v5/pgxpool"
    "trackservice/internal/config"
)

func NewPostgresPool(cfg config.DBConfig) (*pgxpool.Pool, error) {
    connString := fmt.Sprintf(
        "postgres://%s:%s@%s:%d/%s?sslmode=disable",
        cfg.User, cfg.Password, cfg.Host, cfg.Port, cfg.Name,
    )

    poolConfig, err := pgxpool.ParseConfig(connString)
    if err != nil {
        return nil, fmt.Errorf("unable to parse connection string: %w", err)
    }

    poolConfig.MaxConns = cfg.PoolSize
    poolConfig.MinConns = 2
    poolConfig.MaxConnLifetime = time.Hour
    poolConfig.MaxConnIdleTime = 30 * time.Minute

    pool, err := pgxpool.NewWithConfig(context.Background(), poolConfig)
    if err != nil {
        return nil, fmt.Errorf("unable to create connection pool: %w", err)
    }

    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    if err := pool.Ping(ctx); err != nil {
        return nil, fmt.Errorf("unable to ping database: %w", err)
    }

    return pool, nil
}
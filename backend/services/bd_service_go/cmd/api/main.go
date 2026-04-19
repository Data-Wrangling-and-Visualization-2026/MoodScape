package main

import (
    "log"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/gofiber/fiber/v2"
    "github.com/gofiber/fiber/v2/middleware/cors"
    "github.com/gofiber/fiber/v2/middleware/logger"
    "github.com/gofiber/fiber/v2/middleware/recover"
    "github.com/joho/godotenv"
    "trackservice/internal/config"
    "trackservice/internal/handler"
    "trackservice/internal/repository/postgres"
    "trackservice/internal/service"
    "trackservice/pkg/db"
)

func main() {
    // Загрузка .env
    _ = godotenv.Load()

    cfg := config.Load()

    pool, err := db.NewPostgresPool(cfg.DB)
    if err != nil {
        log.Fatalf("Failed to connect to database: %v", err)
    }
    defer pool.Close()

    trackRepo := postgres.NewTrackRepository(pool)

    trackService := service.NewTrackService(trackRepo)

    trackHandler := handler.NewTrackHandler(trackService)

    // Настройка Fiber
    app := fiber.New(fiber.Config{
        ReadTimeout:  cfg.Server.ReadTimeout,
        WriteTimeout: cfg.Server.WriteTimeout,
        IdleTimeout:  120 * time.Second,
        ErrorHandler: func(c *fiber.Ctx, err error) error {
            code := fiber.StatusInternalServerError
            if e, ok := err.(*fiber.Error); ok {
                code = e.Code
            }
            return c.Status(code).JSON(fiber.Map{"error": err.Error()})
        },
    })

    // Middleware
    app.Use(logger.New())
    app.Use(recover.New())
    app.Use(cors.New(cors.Config{
        AllowOrigins: "*",
        AllowMethods: "GET,POST,PUT,DELETE",
    }))

    // Health check
    app.Get("/health", func(c *fiber.Ctx) error {
        return c.JSON(fiber.Map{"status": "healthy"})
    })

    trackHandler.RegisterRoutes(app)

    go func() {
        if err := app.Listen(":" + cfg.Server.Port); err != nil {
            log.Fatalf("Failed to start server: %v", err)
        }
    }()

    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    log.Println("Shutting down server...")
    if err := app.Shutdown(); err != nil {
        log.Printf("Server forced to shutdown: %v", err)
    }
}
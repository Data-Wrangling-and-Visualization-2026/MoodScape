package repository

import (
    "context"
    "trackservice/internal/domain"
)

type EventRepository interface {
    Save(ctx context.Context, event *domain.Event) (*domain.Event, error)
    FindByID(ctx context.Context, id int) (*domain.Event, error)
    FindByYear(ctx context.Context, year int) ([]*domain.Event, error)
    FindByYearRange(ctx context.Context, yearFrom, yearTo int) ([]*domain.Event, error)
    GetAllYears(ctx context.Context) ([]int, error)
    SearchByName(ctx context.Context, query string, limit int) ([]*domain.Event, error)
    FindAll(ctx context.Context, limit, offset int) ([]*domain.Event, error)
    Delete(ctx context.Context, id int) (bool, error)
    GetStatistics(ctx context.Context) (map[string]interface{}, error)
}
package repository

import (
    "context"

    "trackservice/internal/domain"
)

type TrackRepository interface {
    Save(ctx context.Context, track *domain.Track) (*domain.Track, error)
    FindByID(ctx context.Context, id int) (*domain.Track, error)
    Filter(ctx context.Context, filter FilterParams) ([]*domain.Track, error)
}

type FilterParams struct {
    Genre         *string
    YearFrom      *int
    YearTo        *int
    Emotion       *string
    MinIntensity  float64
    MaxIntensity  float64
    Search        *string
    Limit         *int
    Offset        *int
    SortBy        string
    SortOrder     string // "asc" or "desc"
}
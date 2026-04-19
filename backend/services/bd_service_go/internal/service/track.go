package service

import (
    "context"
    "errors"
    "strings"

    "trackservice/internal/domain"
    "trackservice/internal/repository"
)

type TrackService struct {
    repo repository.TrackRepository
}

func NewTrackService(repo repository.TrackRepository) *TrackService {
    return &TrackService{repo: repo}
}

func (s *TrackService) FilterTracks(ctx context.Context, filter repository.FilterParams) ([]*domain.Track, error) {
    if filter.Emotion != nil {
        if !domain.ValidEmotions[*filter.Emotion] {
            return nil, errors.New("invalid emotion")
        }
    }
    if filter.YearFrom != nil && filter.YearTo != nil && *filter.YearFrom > *filter.YearTo {
        return nil, errors.New("year_from must be <= year_to")
    }
    if filter.Search != nil && len(strings.TrimSpace(*filter.Search)) < 3 {
        return nil, errors.New("search query must be at least 3 characters")
    }
    return s.repo.Filter(ctx, filter)
}
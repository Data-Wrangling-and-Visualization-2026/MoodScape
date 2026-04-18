package handler

import (
    "strconv"

    "github.com/gofiber/fiber/v2"
    "trackservice/internal/repository"
    "trackservice/internal/service"
    "trackservice/internal/domain"
)

type TrackHandler struct {
    service *service.TrackService
}

func NewTrackHandler(service *service.TrackService) *TrackHandler {
    return &TrackHandler{service: service}
}

func (h *TrackHandler) Filter(c *fiber.Ctx) error {
    var filter repository.FilterParams

    genre := c.Query("genre")
    if genre != "" {
        filter.Genre = &genre
    }

    yearFromStr := c.Query("year_from")
    if yearFromStr != "" {
        yf, err := strconv.Atoi(yearFromStr)
        if err == nil {
            filter.YearFrom = &yf
        }
    }

    yearToStr := c.Query("year_to")
    if yearToStr != "" {
        yt, err := strconv.Atoi(yearToStr)
        if err == nil {
            filter.YearTo = &yt
        }
    }

    emotion := c.Query("emotion")
    if emotion != "" {
        filter.Emotion = &emotion
    }

    minIntensity := c.QueryFloat("min_intensity", 0.0)
    maxIntensity := c.QueryFloat("max_intensity", 10.0)
    filter.MinIntensity = minIntensity
    filter.MaxIntensity = maxIntensity

    search := c.Query("search")
    if search != "" {
        filter.Search = &search
    }

    limitStr := c.Query("limit")
    if limitStr != "" {
        l, err := strconv.Atoi(limitStr)
        if err == nil {
            filter.Limit = &l
        }
    }

    offsetStr := c.Query("offset")
    if offsetStr != "" {
        o, err := strconv.Atoi(offsetStr)
        if err == nil {
            filter.Offset = &o
        }
    }

    sortBy := c.Query("sort_by", "release_date")
    filter.SortBy = sortBy
    sortOrder := c.Query("sort_order", "desc")
    filter.SortOrder = sortOrder

    tracks, err := h.service.FilterTracks(c.Context(), filter)
    if err != nil {
        return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": err.Error()})
    }

    type TrackResponse struct {
        *domain.Track
        AverageScore float64 `json:"average_score"`
        Year         int     `json:"year"`
    }

    response := make([]TrackResponse, len(tracks))
    for i, t := range tracks {
        response[i] = TrackResponse{
            Track:        t,
            AverageScore: t.CalculateAverageScore(),
            Year:         t.ReleaseDate.Year(),
        }
    }

    return c.JSON(response)
}

func (h *TrackHandler) RegisterRoutes(app *fiber.App) {
    tracks := app.Group("/tracks")
    tracks.Get("/filter/", h.Filter)
}
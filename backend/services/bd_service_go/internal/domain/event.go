package domain

import (
    "strings"
    "time"
)

const (
    MinYear = 1900
    MaxYear = 2030
)

type Event struct {
    ID          int        `json:"id"`
    Year        int        `json:"year"`
    EventName   string     `json:"event_name"`
    Description *string    `json:"description,omitempty"`
    CreatedAt   *time.Time `json:"created_at,omitempty"`
    UpdatedAt   *time.Time `json:"updated_at,omitempty"`
}

func (e *Event) Validate() bool {
    if e.Year < MinYear || e.Year > MaxYear {
        return false
    }
    trimmedName := strings.TrimSpace(e.EventName)
    if len(trimmedName) < 2 || len(trimmedName) > 500 {
        return false
    }
    return true
}

func (e *Event) GetDecade() int {
    return (e.Year / 10) * 10
}

func (e *Event) GetEra() string {
    switch {
    case e.Year < 1960:
        return "post_war"
    case e.Year < 1980:
        return "cold_war"
    case e.Year < 1991:
        return "late_soviet"
    case e.Year < 2000:
        return "nineties"
    case e.Year < 2010:
        return "two_thousands"
    case e.Year < 2020:
        return "twenty_tens"
    default:
        return "twenty_twenties"
    }
}
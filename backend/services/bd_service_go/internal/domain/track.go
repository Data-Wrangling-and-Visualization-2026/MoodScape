package domain

import (
    "strings"
    "time"
)

var ValidEmotions = map[string]bool{
    "happiness": true, "sadness": true, "fear": true,
    "anger": true, "disgust": true, "anticipation": true,
}

type EmotionComponent struct {
    Emotion string  `json:"emotion"`
    Weight  float64 `json:"weight"`
}

type AudioFeatures struct {
    Tempo            float64 `json:"tempo"`
    Energy           float64 `json:"energy"`
    Danceability     float64 `json:"danceability"`
    Acousticness     float64 `json:"acousticness"`
    Instrumentalness float64 `json:"instrumentalness"`
    Valence          float64 `json:"valence"`
    Key              int     `json:"key"`
    Mode             int     `json:"mode"`
    Loudness         float64 `json:"loudness"`
    Speechiness      float64 `json:"speechiness"`
    Duration         float64 `json:"duration"`
}

type Track struct {
    ID                int                `json:"id"`
    Title             string             `json:"title"`
    Author            string             `json:"author"`
    Genre             string             `json:"genre"`
    Text              string             `json:"text"`
    Emotion           string             `json:"emotion"`
    EmotionIntensity  float64            `json:"emotion_intensity"`
    EmotionComponents []EmotionComponent `json:"emotion_components"`
    AudioFeatures     AudioFeatures      `json:"audio_features"`
    ReleaseDate       time.Time          `json:"release_date"`
    CreatedAt         *time.Time         `json:"created_at,omitempty"`
    UpdatedAt         *time.Time         `json:"updated_at,omitempty"`
}

func (t *Track) Validate() bool {
    if strings.TrimSpace(t.Title) == "" || len(t.Title) > 255 {
        return false
    }
    if strings.TrimSpace(t.Author) == "" || len(t.Author) > 255 {
        return false
    }
    if strings.TrimSpace(t.Genre) == "" || len(t.Genre) > 100 {
        return false
    }
    if !ValidEmotions[t.Emotion] {
        return false
    }
    if t.EmotionIntensity < 0 || t.EmotionIntensity > 10 {
        return false
    }
    return true
}

func (t *Track) CalculateAverageScore() float64 {
    sum := t.AudioFeatures.Energy + t.AudioFeatures.Danceability + t.AudioFeatures.Valence
    return sum / 3.0
}

func (t *Track) GetEmotionCategory() string {
    switch {
    case t.EmotionIntensity < 3.0:
        return "low"
    case t.EmotionIntensity < 7.0:
        return "medium"
    default:
        return "high"
    }
}

// Custom JSON marshalling для emotion_components и audio_features будет обрабатываться на уровне БД.
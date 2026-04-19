package postgres

import (
    "context"
    "encoding/json"
    "time"

    sq "github.com/Masterminds/squirrel"
    "github.com/jackc/pgx/v5/pgxpool"
    "trackservice/internal/domain"
    "trackservice/internal/repository"
)

type TrackRepo struct {
    db *pgxpool.Pool
}

func NewTrackRepository(db *pgxpool.Pool) repository.TrackRepository {
    return &TrackRepo{db: db}
}

func (r *TrackRepo) Save(ctx context.Context, track *domain.Track) (*domain.Track, error) {
    emotionComponentsJSON, _ := json.Marshal(track.EmotionComponents)
    audioFeaturesJSON, _ := json.Marshal(track.AudioFeatures)

    if track.ID != 0 {
        query := sq.Update("tracks").
            Set("title", track.Title).
            Set("author", track.Author).
            Set("genre", track.Genre).
            Set("text", track.Text).
            Set("emotion", track.Emotion).
            Set("emotion_intensity", track.EmotionIntensity).
            Set("emotion_components", emotionComponentsJSON).
            Set("audio_features", audioFeaturesJSON).
            Set("release_date", track.ReleaseDate).
            Set("updated_at", time.Now().UTC()).
            Where(sq.Eq{"id": track.ID}).
            Suffix("RETURNING id, title, author, genre, text, emotion, emotion_intensity, emotion_components, audio_features, release_date, created_at, updated_at").
            PlaceholderFormat(sq.Dollar)

        sql, args, err := query.ToSql()
        if err != nil {
            return nil, err
        }
        return r.scanTrack(ctx, sql, args)
    }

    query := sq.Insert("tracks").
        Columns("title", "author", "genre", "text", "emotion", "emotion_intensity", "emotion_components", "audio_features", "release_date", "created_at", "updated_at").
        Values(track.Title, track.Author, track.Genre, track.Text, track.Emotion, track.EmotionIntensity, emotionComponentsJSON, audioFeaturesJSON, track.ReleaseDate, time.Now().UTC(), time.Now().UTC()).
        Suffix("RETURNING id, title, author, genre, text, emotion, emotion_intensity, emotion_components, audio_features, release_date, created_at, updated_at").
        PlaceholderFormat(sq.Dollar)

    sql, args, err := query.ToSql()
    if err != nil {
        return nil, err
    }
    return r.scanTrack(ctx, sql, args)
}

func (r *TrackRepo) scanTrack(ctx context.Context, sql string, args []interface{}) (*domain.Track, error) {
    row := r.db.QueryRow(ctx, sql, args...)
    var t domain.Track
    var emotionCompJSON, audioFeatJSON []byte

    err := row.Scan(
        &t.ID, &t.Title, &t.Author, &t.Genre, &t.Text,
        &t.Emotion, &t.EmotionIntensity, &emotionCompJSON, &audioFeatJSON,
        &t.ReleaseDate, &t.CreatedAt, &t.UpdatedAt,
    )
    if err != nil {
        return nil, err
    }
    json.Unmarshal(emotionCompJSON, &t.EmotionComponents)
    json.Unmarshal(audioFeatJSON, &t.AudioFeatures)
    return &t, nil
}

func (r *TrackRepo) FindByID(ctx context.Context, id int) (*domain.Track, error) {
    query := sq.Select("id", "title", "author", "genre", "text", "emotion", "emotion_intensity", "emotion_components", "audio_features", "release_date", "created_at", "updated_at").
        From("tracks").
        Where(sq.Eq{"id": id}).
        PlaceholderFormat(sq.Dollar)

    sql, args, err := query.ToSql()
    if err != nil {
        return nil, err
    }
    return r.scanTrack(ctx, sql, args)
}

func (r *TrackRepo) Filter(ctx context.Context, filter repository.FilterParams) ([]*domain.Track, error) {
    builder := sq.Select("id", "title", "author", "genre", "text", "emotion", "emotion_intensity", "emotion_components", "audio_features", "release_date", "created_at", "updated_at").
        From("tracks").
        PlaceholderFormat(sq.Dollar)

    if filter.Genre != nil && *filter.Genre != "" {
        builder = builder.Where(sq.ILike{"genre": "%" + *filter.Genre + "%"})
    }

    if filter.YearFrom != nil || filter.YearTo != nil {
        startDate := time.Date(1900, 1, 1, 0, 0, 0, 0, time.UTC)
        if filter.YearFrom != nil {
            startDate = time.Date(*filter.YearFrom, 1, 1, 0, 0, 0, 0, time.UTC)
        }
        endDate := time.Now()
        if filter.YearTo != nil {
            endDate = time.Date(*filter.YearTo, 12, 31, 23, 59, 59, 999999999, time.UTC)
        }
        builder = builder.Where(sq.Expr("release_date BETWEEN ? AND ?", startDate, endDate))
    }

    if filter.Emotion != nil && *filter.Emotion != "" {
        builder = builder.Where(sq.Eq{"emotion": *filter.Emotion})
    }

    builder = builder.Where(sq.And{
        sq.GtOrEq{"emotion_intensity": filter.MinIntensity},
        sq.LtOrEq{"emotion_intensity": filter.MaxIntensity},
    })

    if filter.Search != nil && *filter.Search != "" {
        builder = builder.Where(sq.Or{
            sq.ILike{"title": "%" + *filter.Search + "%"},
            sq.ILike{"text": "%" + *filter.Search + "%"},
        })
    }

    sortColumn := "release_date"
    if filter.SortBy != "" {
        // Проверка допустимых полей (можно вынести)
        allowedSortColumns := map[string]bool{
            "release_date": true, "created_at": true, "title": true, "author": true, "emotion_intensity": true,
        }
        if allowedSortColumns[filter.SortBy] {
            sortColumn = filter.SortBy
        }
    }

    if filter.SortOrder == "asc" {
        builder = builder.OrderBy(sortColumn + " ASC")
    } else {
        builder = builder.OrderBy(sortColumn + " DESC")
    }

    if filter.Limit != nil {
        builder = builder.Limit(uint64(*filter.Limit))
    }
    if filter.Offset != nil {
        builder = builder.Offset(uint64(*filter.Offset))
    }

    sql, args, err := builder.ToSql()
    if err != nil {
        return nil, err
    }

    rows, err := r.db.Query(ctx, sql, args...)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var tracks []*domain.Track
    for rows.Next() {
        var t domain.Track
        var emotionCompJSON, audioFeatJSON []byte
        if err := rows.Scan(
            &t.ID, &t.Title, &t.Author, &t.Genre, &t.Text,
            &t.Emotion, &t.EmotionIntensity, &emotionCompJSON, &audioFeatJSON,
            &t.ReleaseDate, &t.CreatedAt, &t.UpdatedAt,
        ); err != nil {
            return nil, err
        }
        json.Unmarshal(emotionCompJSON, &t.EmotionComponents)
        json.Unmarshal(audioFeatJSON, &t.AudioFeatures)
        tracks = append(tracks, &t)
    }
    return tracks, nil
}

// Остальные методы (FindByAuthor, FindByGenre, ...) реализуются аналогично с использованием Squirrel.
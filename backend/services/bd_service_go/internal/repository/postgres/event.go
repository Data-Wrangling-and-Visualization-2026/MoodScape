package postgres

import (
    "context"
    "time"

    sq "github.com/Masterminds/squirrel"
    "github.com/jackc/pgx/v5"
    "github.com/jackc/pgx/v5/pgxpool"
    "trackservice/internal/domain"
    "trackservice/internal/repository"
)

type EventRepo struct {
    db *pgxpool.Pool
}

func NewEventRepository(db *pgxpool.Pool) repository.EventRepository {
    return &EventRepo{db: db}
}

func (r *EventRepo) Save(ctx context.Context, event *domain.Event) (*domain.Event, error) {
    if event.ID != 0 {
        // Update
        query := sq.Update("events").
            Set("year", event.Year).
            Set("event_name", event.EventName).
            Set("description", event.Description).
            Set("updated_at", time.Now().UTC()).
            Where(sq.Eq{"id": event.ID}).
            Suffix("RETURNING id, year, event_name, description, created_at, updated_at").
            PlaceholderFormat(sq.Dollar)

        sql, args, err := query.ToSql()
        if err != nil {
            return nil, err
        }

        row := r.db.QueryRow(ctx, sql, args...)
        var saved domain.Event
        err = row.Scan(&saved.ID, &saved.Year, &saved.EventName, &saved.Description, &saved.CreatedAt, &saved.UpdatedAt)
        if err != nil {
            return nil, err
        }
        return &saved, nil
    }

    // Insert
    query := sq.Insert("events").
        Columns("year", "event_name", "description", "created_at", "updated_at").
        Values(event.Year, event.EventName, event.Description, time.Now().UTC(), time.Now().UTC()).
        Suffix("RETURNING id, year, event_name, description, created_at, updated_at").
        PlaceholderFormat(sq.Dollar)

    sql, args, err := query.ToSql()
    if err != nil {
        return nil, err
    }

    row := r.db.QueryRow(ctx, sql, args...)
    var saved domain.Event
    err = row.Scan(&saved.ID, &saved.Year, &saved.EventName, &saved.Description, &saved.CreatedAt, &saved.UpdatedAt)
    if err != nil {
        return nil, err
    }
    return &saved, nil
}

func (r *EventRepo) FindByID(ctx context.Context, id int) (*domain.Event, error) {
    query := sq.Select("id", "year", "event_name", "description", "created_at", "updated_at").
        From("events").
        Where(sq.Eq{"id": id}).
        PlaceholderFormat(sq.Dollar)

    sql, args, err := query.ToSql()
    if err != nil {
        return nil, err
    }

    row := r.db.QueryRow(ctx, sql, args...)
    var event domain.Event
    err = row.Scan(&event.ID, &event.Year, &event.EventName, &event.Description, &event.CreatedAt, &event.UpdatedAt)
    if err != nil {
        if err == pgx.ErrNoRows {
            return nil, nil
        }
        return nil, err
    }
    return &event, nil
}

func (r *EventRepo) FindByYear(ctx context.Context, year int) ([]*domain.Event, error) {
    query := sq.Select("id", "year", "event_name", "description", "created_at", "updated_at").
        From("events").
        Where(sq.Eq{"year": year}).
        OrderBy("event_name").
        PlaceholderFormat(sq.Dollar)

    sql, args, err := query.ToSql()
    if err != nil {
        return nil, err
    }

    rows, err := r.db.Query(ctx, sql, args...)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var events []*domain.Event
    for rows.Next() {
        var e domain.Event
        if err := rows.Scan(&e.ID, &e.Year, &e.EventName, &e.Description, &e.CreatedAt, &e.UpdatedAt); err != nil {
            return nil, err
        }
        events = append(events, &e)
    }
    return events, nil
}

func (r *EventRepo) FindByYearRange(ctx context.Context, yearFrom, yearTo int) ([]*domain.Event, error) {
    query := sq.Select("id", "year", "event_name", "description", "created_at", "updated_at").
        From("events").
        Where(sq.And{
            sq.GtOrEq{"year": yearFrom},
            sq.LtOrEq{"year": yearTo},
        }).
        OrderBy("year", "event_name").
        PlaceholderFormat(sq.Dollar)

    sql, args, err := query.ToSql()
    if err != nil {
        return nil, err
    }

    rows, err := r.db.Query(ctx, sql, args...)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var events []*domain.Event
    for rows.Next() {
        var e domain.Event
        if err := rows.Scan(&e.ID, &e.Year, &e.EventName, &e.Description, &e.CreatedAt, &e.UpdatedAt); err != nil {
            return nil, err
        }
        events = append(events, &e)
    }
    return events, nil
}

func (r *EventRepo) GetAllYears(ctx context.Context) ([]int, error) {
    query := sq.Select("DISTINCT year").
        From("events").
        OrderBy("year DESC").
        PlaceholderFormat(sq.Dollar)

    sql, args, err := query.ToSql()
    if err != nil {
        return nil, err
    }

    rows, err := r.db.Query(ctx, sql, args...)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var years []int
    for rows.Next() {
        var y int
        if err := rows.Scan(&y); err != nil {
            return nil, err
        }
        years = append(years, y)
    }
    return years, nil
}

func (r *EventRepo) SearchByName(ctx context.Context, query string, limit int) ([]*domain.Event, error) {
    sqlBuilder := sq.Select("id", "year", "event_name", "description", "created_at", "updated_at").
        From("events").
        Where(sq.ILike{"event_name": "%" + query + "%"}).
        OrderBy("year DESC").
        Limit(uint64(limit)).
        PlaceholderFormat(sq.Dollar)

    sql, args, err := sqlBuilder.ToSql()
    if err != nil {
        return nil, err
    }

    rows, err := r.db.Query(ctx, sql, args...)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var events []*domain.Event
    for rows.Next() {
        var e domain.Event
        if err := rows.Scan(&e.ID, &e.Year, &e.EventName, &e.Description, &e.CreatedAt, &e.UpdatedAt); err != nil {
            return nil, err
        }
        events = append(events, &e)
    }
    return events, nil
}

func (r *EventRepo) FindAll(ctx context.Context, limit, offset int) ([]*domain.Event, error) {
    query := sq.Select("id", "year", "event_name", "description", "created_at", "updated_at").
        From("events").
        OrderBy("year DESC", "event_name").
        Limit(uint64(limit)).
        Offset(uint64(offset)).
        PlaceholderFormat(sq.Dollar)

    sql, args, err := query.ToSql()
    if err != nil {
        return nil, err
    }

    rows, err := r.db.Query(ctx, sql, args...)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var events []*domain.Event
    for rows.Next() {
        var e domain.Event
        if err := rows.Scan(&e.ID, &e.Year, &e.EventName, &e.Description, &e.CreatedAt, &e.UpdatedAt); err != nil {
            return nil, err
        }
        events = append(events, &e)
    }
    return events, nil
}

func (r *EventRepo) Delete(ctx context.Context, id int) (bool, error) {
    query := sq.Delete("events").
        Where(sq.Eq{"id": id}).
        PlaceholderFormat(sq.Dollar)

    sql, args, err := query.ToSql()
    if err != nil {
        return false, err
    }

    tag, err := r.db.Exec(ctx, sql, args...)
    if err != nil {
        return false, err
    }
    return tag.RowsAffected() > 0, nil
}

func (r *EventRepo) GetStatistics(ctx context.Context) (map[string]interface{}, error) {
    return map[string]interface{}{}, nil
}
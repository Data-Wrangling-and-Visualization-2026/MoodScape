-- init-db.sql for bd_service
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    event_name VARCHAR(500) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_events_year ON events(year);
CREATE INDEX IF NOT EXISTS idx_events_name_trgm ON events USING GIN (event_name gin_trgm_ops);

CREATE TABLE IF NOT EXISTS tracks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    text TEXT NOT NULL,
    emotion VARCHAR(50) NOT NULL,                    -- доминантная эмоция
    emotion_intensity FLOAT NOT NULL,                -- общая интенсивность (0-10)
    emotion_components JSONB NOT NULL,               -- список компонентов: [{"emotion": "...", "weight": ...}]
    audio_features JSONB NOT NULL,
    release_date DATE NOT NULL, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_emotion CHECK (emotion IN ('happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation')),
    CONSTRAINT valid_intensity CHECK (emotion_intensity >= 0 AND emotion_intensity <= 10)
);

CREATE INDEX IF NOT EXISTS idx_tracks_author ON tracks(author);
CREATE INDEX IF NOT EXISTS idx_tracks_genre ON tracks(genre);
CREATE INDEX IF NOT EXISTS idx_tracks_emotion ON tracks(emotion);
CREATE INDEX IF NOT EXISTS idx_tracks_emotion_intensity ON tracks(emotion_intensity);
CREATE INDEX IF NOT EXISTS idx_tracks_created_at ON tracks(created_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_tracks_author_title ON tracks(author, title);
CREATE INDEX IF NOT EXISTS idx_tracks_text_trgm ON tracks USING GIN (text gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_tracks_title_trgm ON tracks USING GIN (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_tracks_emotion_components ON tracks USING GIN (emotion_components);

-- GIN индекс для JSONB (поиск внутри emotion_components)
CREATE INDEX IF NOT EXISTS idx_tracks_emotion_components ON tracks USING GIN (emotion_components);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_events_updated_at ON events;
CREATE TRIGGER update_events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_tracks_updated_at ON tracks;
CREATE TRIGGER update_tracks_updated_at
    BEFORE UPDATE ON tracks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
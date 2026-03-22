-- init-db.sql for bd_service
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS tracks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    text TEXT NOT NULL,
    emotion VARCHAR(50) NOT NULL,
    emotion_intensity FLOAT NOT NULL,
    audio_features JSONB NOT NULL,
    release_date DATE NOT NULL, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_emotion CHECK (emotion IN ('joy', 'sadness', 'anger', 'fear', 'surprise', 'love', 'calm', 'energy')),
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

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_tracks_updated_at ON tracks;
CREATE TRIGGER update_tracks_updated_at
    BEFORE UPDATE ON tracks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
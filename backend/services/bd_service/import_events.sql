-- import_events.sql
\echo 'Starting events data import...'

CREATE TEMP TABLE temp_events (
    year INTEGER,
    event_name VARCHAR(500),
    description TEXT
);

\copy temp_events (year, event_name, description) FROM '/docker-entrypoint-initdb.d/events_v1.csv' DELIMITER ',' CSV HEADER;

INSERT INTO events (year, event_name, description)
SELECT year, event_name, description 
FROM temp_events 
WHERE NOT EXISTS (
    SELECT 1 FROM events 
    WHERE events.year = temp_events.year 
    AND events.event_name = temp_events.event_name
);

DROP TABLE temp_events;

\echo 'Events import completed. Total rows in events table:'
SELECT COUNT(*) FROM events;
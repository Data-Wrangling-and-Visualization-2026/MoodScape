# MoodScape - LLM Service

A service for analyzing emotions in music tracks using an LLM (Ollama). It analyzes song lyrics and audio features to determine the primary emotion and its intensity.

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git, Git LFS
- 8+ GB RAM (16 GB recommended)
- Yandex Music Plus (required for full audio extraction in the parse service)

---

## Installation & Run

```bash
# 1. Clone the repository
git clone git@github.com:Data-Wrangling-and-Visualization-2026/MoodScape.git
cd MoodScape
cd backend

# 2. Create environment variables file
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Check status
docker-compose ps
````

---

## Parse Service

Swagger documentation (when running locally):

```
http://localhost:8001
```

To enable this service:

```
PARSE_SCHEDULER_ENABLED: true  # Enable scheduler
PARSE_INTERVAL_SECONDS: 90     # Retry interval in seconds if parser fails
```

Requirements:

* bd_service_postgres container
* parser_service_app container

The service parses Yandex Music playlists:

* First: charts
* Then: playlists from the user's liked playlists

To configure playlists for parsing, add them to your Yandex Music account.

We also use epoch-based playlists such as "Best of 00s", "Best of 2010s", etc.

---

## Preprocessing

The parser service saves results into the following tables:

* track_metadata
* track_analysis_results

To extract data via pgAdmin, run:

```sql
SELECT * 
FROM track_analysis_results ta 
JOIN track_metadata tm 
ON ta.track_id = tm.track_id;
```

Then:

1. Export the result as a .csv file
2. Copy it into the preprocessing directory
3. Run preprocess.ipynb

---

## LLM Service

Swagger documentation (when running locally):

```
http://localhost:8002
```

Requirements:

* bd_service_postgres container
* bd_service_app container
* llm_service_app container
* ollama container

To start analysis:

1. Run support_script.py from the preprocessing directory
2. This fills the queue in the LLM service
3. Processing will start automatically

---

## Backend

Swagger documentation (when running locally):

```
http://localhost:8002
```

### Important

Before testing, you must populate the database, since docker-compose uses a default empty PostgreSQL container.

From the preprocessing directory (when the PostgreSQL container is running):

```bash
docker cp processed_ai_tracks.csv bd_service_postgres:/tmp/processed_ai_tracks.csv

docker exec -it bd_service_postgres \
psql -U bd_user -d bd_trackdb \
-c "\copy tracks FROM '/tmp/processed_ai_tracks.csv' DELIMITER ',' CSV HEADER;"
```

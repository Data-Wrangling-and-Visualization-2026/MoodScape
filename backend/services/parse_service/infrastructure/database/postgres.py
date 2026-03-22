import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from backend.services.parse_service.infrastructure.database.models import Base


class PostgresDatabase:
    def __init__(self, database_url: str | None = None):
        """Create SQLAlchemy engine/session factory for Postgres."""
        resolved_url = database_url or os.getenv("PARSE_DB_URL")
        if not resolved_url:
            raise RuntimeError("PARSE_DB_URL is not set")

        self.database_url = resolved_url
        self.engine = create_engine(self.database_url, pool_pre_ping=True, future=True)
        self.session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def initialize(self) -> None:
        """Create missing database tables for parse service."""
        Base.metadata.create_all(bind=self.engine)

        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    ALTER TABLE track_metadata
                    ADD COLUMN IF NOT EXISTS source VARCHAR(64) DEFAULT 'yandex_music'
                    """
                )
            )
            connection.execute(
                text(
                    """
                    ALTER TABLE track_metadata
                    ADD COLUMN IF NOT EXISTS genre VARCHAR(128)
                    """
                )
            )
            connection.execute(
                text(
                    """
                    ALTER TABLE track_metadata
                    ADD COLUMN IF NOT EXISTS year INTEGER
                    """
                )
            )
            connection.execute(
                text(
                    """
                    ALTER TABLE track_metadata
                    ADD COLUMN IF NOT EXISTS storage_uri VARCHAR(1024)
                    """
                )
            )
            connection.execute(
                text(
                    """
                    ALTER TABLE track_metadata
                    ADD COLUMN IF NOT EXISTS main_artist VARCHAR(255)
                    """
                )
            )
            connection.execute(
                text(
                    """
                    DO $$
                    BEGIN
                        IF EXISTS (
                            SELECT 1
                            FROM information_schema.columns
                            WHERE table_schema = 'public'
                              AND table_name = 'track_metadata'
                              AND column_name = 'artists'
                        ) THEN
                            EXECUTE '
                                UPDATE track_metadata
                                SET main_artist = COALESCE(
                                    NULLIF(main_artist, ''''),
                                    NULLIF(split_part(artists, '','', 1), ''''),
                                    ''unknown''
                                )
                                WHERE main_artist IS NULL OR main_artist = ''''
                            ';
                        ELSE
                            EXECUTE '
                                UPDATE track_metadata
                                SET main_artist = COALESCE(NULLIF(main_artist, ''''), ''unknown'')
                                WHERE main_artist IS NULL OR main_artist = ''''
                            ';
                        END IF;
                    END
                    $$;
                    """
                )
            )
            connection.execute(
                text(
                    """
                    ALTER TABLE track_metadata
                    ALTER COLUMN main_artist SET NOT NULL
                    """
                )
            )
            connection.execute(
                text(
                    """
                    ALTER TABLE track_processing_status
                    ADD COLUMN IF NOT EXISTS lyrics_available BOOLEAN DEFAULT FALSE NOT NULL
                    """
                )
            )
            connection.execute(
                text(
                    """
                    ALTER TABLE track_processing_status
                    ADD COLUMN IF NOT EXISTS text_available BOOLEAN DEFAULT FALSE NOT NULL
                    """
                )
            )
            connection.execute(
                text(
                    """
                    UPDATE track_processing_status
                    SET lyrics_available = COALESCE(text_available, FALSE)
                    WHERE lyrics_available IS DISTINCT FROM COALESCE(text_available, FALSE)
                    """
                )
            )

    def get_session(self) -> Session:
        """Open a new database session."""
        return self.session_factory()

    def check_connection(self) -> tuple[bool, str | None]:
        """Run lightweight connectivity query and return health tuple."""
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True, None
        except Exception as exc:
            return False, str(exc)

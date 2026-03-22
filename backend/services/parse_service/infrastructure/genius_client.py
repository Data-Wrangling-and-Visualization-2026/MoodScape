import lyricsgenius
import os


class GeniusClient:

    def __init__(self):
        """Create Genius API client using configured token."""
        token = os.getenv("GENIUS_TOKEN")
        if not token:
            raise RuntimeError("GENIUS_TOKEN is not set. Add it to .env or exported env.")

        self.client = lyricsgenius.Genius(token)

    def get_lyrics(self, title: str, artist: str):
        """Fetch lyrics text for title/artist pair if found."""
        song = self.client.search_song(title, artist)
        if song:
            return song.lyrics
        return None

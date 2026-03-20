import os
import requests
from yandex_music import Client


class YandexMusicClient:

    def __init__(self):
        """Create authenticated Yandex Music client."""
        token = os.getenv("YANDEX_TOKEN")
        if not token:
            raise RuntimeError("YANDEX_TOKEN is not set. Add it to .env or exported env.")

        self.client = Client(token)
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Initialize Yandex client lazily before first API call."""
        if self._initialized:
            return
        self.client = self.client.init()
        self._initialized = True

    def get_chart_tracks(self):
        """Load current chart tracks + playlists from Yandex Music."""
        self._ensure_initialized()
        chart = self.client.chart()
        playlist = chart.chart

        if not playlist or not playlist.tracks:
            return []

        all_tracks = [item.track for item in playlist.tracks]
        liked_playlists = self.client.users_likes_playlists()

        for item in liked_playlists:
            playlist = item.playlist
            full_playlist = self.client.users_playlists(playlist.kind, playlist.owner.uid)
            
            for track_item in full_playlist.tracks:
                all_tracks.append(track_item.track)

        return all_tracks

    def get_discovery_tracks(self):
        """
        Return tracks considered by the periodic parser.

        Fix: use a dedicated source-aggregation method so chart/playlist/subscription
        providers can be expanded without changing use-case logic.
        """
        return self.get_chart_tracks()

    def download_track(self, track_id: str, path: str):
        """Download track audio by ID to a local file path."""
        self._ensure_initialized()
        track = self.client.tracks(track_id)[0]
        download_info = track.get_download_info()[0]
        url = download_info.get_direct_link()

        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(path, "wb") as file_obj:
            file_obj.write(response.content)

        return track
    
    
    def get_lyrics(self, track_id) -> str:
        self._ensure_initialized()
        return self.client.tracks_lyrics(track_id).fetch_lyrics()

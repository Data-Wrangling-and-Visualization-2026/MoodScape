import requests
from app.models.schemas import TrackPost
from app.config import settings


class BdClient:
    def __init__(self):
        self.base_url = settings.BD_URL

    # returns True if service is running
    def check_health(self) -> bool:
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
                )
            status = response.json.__get__("status")
            return status == "healthy"
        except Exception as e:
            print(f"An error ocurred while checking bd health: {e}")
        return False
    
    # retuns True if the song was loaded to db successfully 
    def load_track(self, song_analysis : TrackPost):
        try:
            response = requests.post(
                f"{self.base_url}/track",
                song_analysis.model_dump(),
                timeout = 10
                )
            return response.status_code == 201
        except Exception as e:
            print(f"An error occured while loading the song: {e}")
        return False
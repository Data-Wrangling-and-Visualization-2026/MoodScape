import requests
from app.config import settings


class ParserClient():
    def __init__(self):
        self.base_url = settings.PARSER_URL
        self.timeout = settings.PARSER_TIMEOUT

    # returns True if service is running
    def check_health(self) -> bool:
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
                )
            status = response.json.__get__("status")
            return status == "healthy"
        except Exception as e:
            print(f"An error ocurred while checking parser health: {e}")
        return False

    #  returns the list with tracks ready for llm analysis
    def get_song(self):
        try:
            response = requests.get(
                f"{self.base_url}/tracks/ready_for_llm",
                timeout=self.timeout
                )
            response.raise_for_status()
            tracks = response.json().get("tracks")
            if tracks:
                return tracks
        except Exception as e:
            print(f"Error occured while fetching the tracks: {e}")
    
        return []
    

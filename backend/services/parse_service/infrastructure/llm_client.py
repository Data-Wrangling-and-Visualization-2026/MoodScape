import os
import logging
import requests

class LLMClient:
    def __init__(self):
        """Resolve base URL for `llm_service` callback endpoint."""
        self.base_url = os.getenv("LLM_SERVICE_URL", "http://llm_service:8002")

    def start_analysis(self, track_id: str) -> bool:
        """Send async trigger to llm_service. Returns True only on accepted/success."""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/analyze",
                json={"track_id": track_id},
                timeout=5,
            )
            return response.status_code in (200, 202)
        except Exception as exc:
            logging.getLogger(__name__).warning(
                "LLM request failed for track_id=%s: %s",
                track_id,
                exc,
            )
            return False

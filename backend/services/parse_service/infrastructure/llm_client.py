import os
import logging
import requests
from typing import Dict, Any

class LLMClient:
    def __init__(self):
        """Resolve base URL for `llm_service` callback endpoint."""
        self.base_url = os.getenv("LLM_SERVICE_URL", "http://llm_service:8002")
        self.logger = logging.getLogger(__name__)

    def send_for_analysis(self, track_data: Dict[str, Any]) -> bool:
        """Send track data to llm_service in the required format."""
        try:
            response = requests.post(
                f"{self.base_url}/analyze",
                json=track_data,
                timeout=30,
            )
            success = response.status_code in (200, 201, 202)
            if not success:
                self.logger.warning(
                    "LLM request failed for track_id=%s: status=%s",
                    track_data.get("track_id"),
                    response.status_code
                )
            return success
        except Exception as exc:
            self.logger.exception(
                "LLM request failed for track_id=%s: %s",
                track_data.get("track_id"),
                exc
            )
            return False
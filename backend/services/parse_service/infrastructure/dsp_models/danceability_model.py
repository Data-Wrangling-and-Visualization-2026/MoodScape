from pathlib import Path

from .base_model import EssentiaTFModel


class DanceabilityModel:

    def __init__(self):
        """Load danceability classifier artifacts."""
        models_dir = Path(__file__).resolve().parents[2] / "models"
        self.model = EssentiaTFModel(
            graph_path=str(models_dir / "danceability-vggish-audioset-1.pb"),
            metadata_path=str(models_dir / "danceability-vggish-audioset-1.json"),
            model_type="vggish"
        )

    def predict(self, audio_path: str) -> float:
        """Return normalized danceability score for audio file."""
        result = self.model.predict(audio_path, sample_rate=16000)
        return float(result.get("danceable", 0.0))

from pathlib import Path

from .base_model import EssentiaTFModel


class SpeechinessModel:

    def __init__(self):
        """Load speechiness classifier artifacts."""
        models_dir = Path(__file__).resolve().parents[2] / "models"
        self.model = EssentiaTFModel(
            graph_path=str(models_dir / "voice_instrumental-musicnn-msd-1.pb"),
            metadata_path=str(models_dir / "voice_instrumental-musicnn-msd-1.json"),
            model_type="musicnn"
        )

    def predict(self, audio_path: str) -> float:
        """Return speechiness proxy score (voice presence)."""
        result = self.model.predict(audio_path, sample_rate=16000)
        return float(result.get("voice", 0.0))

from pathlib import Path

from .base_model import EssentiaTFModel


class ValenceModel:

    def __init__(self):
        """Load valence classifier artifacts."""
        models_dir = Path(__file__).resolve().parents[2] / "models"
        self.model = EssentiaTFModel(
            graph_path=str(models_dir / "mood_happy-musicnn-msd-1.pb"),
            metadata_path=str(models_dir / "mood_happy-musicnn-msd-1.json"),
            model_type="musicnn"
        )

    def predict(self, audio_path: str) -> float:
        """Return normalized valence score for audio file."""
        result = self.model.predict(audio_path, sample_rate=22050)
        return float(result.get("happy", 0.0))

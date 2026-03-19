from pathlib import Path

from .base_model import EssentiaTFModel


class AcousticnessModel:

    def __init__(self):
        """Load acousticness classifier artifacts."""
        models_dir = Path(__file__).resolve().parents[2] / "models"
        self.model = EssentiaTFModel(
            graph_path=str(models_dir / "mood_acoustic-musicnn-msd-1.pb"),
            metadata_path=str(models_dir / "mood_acoustic-musicnn-msd-1.json"),
            model_type="musicnn"
        )

    def predict(self, audio_path: str) -> float:
        """Return normalized acousticness score for audio file."""
        result = self.model.predict(audio_path, sample_rate=22050)
        return float(result.get("acoustic", 0.0))

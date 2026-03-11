from pathlib import Path

from .base_model import EssentiaTFModel


class InstrumentalnessModel:

    def __init__(self):
        """Load instrumentalness classifier artifacts."""
        models_dir = Path(__file__).resolve().parents[2] / "models"
        self.model = EssentiaTFModel(
            graph_path=str(models_dir / "voice_instrumental-musicnn-msd-1.pb"),
            metadata_path=str(models_dir / "voice_instrumental-musicnn-msd-1.json"),
            model_type="musicnn"
        )

    def predict(self, audio_path: str) -> float:
        """Return instrumentalness score inferred from voice/instrumental classes."""
        result = self.model.predict(audio_path, sample_rate=22050)

        # предполагаем классы: ['voice', 'instrumental']
        return float(result.get("instrumental", 0.0))

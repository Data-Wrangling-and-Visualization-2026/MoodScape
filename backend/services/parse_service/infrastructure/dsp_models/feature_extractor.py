from .danceability_model import DanceabilityModel
from .acousticness_model import AcousticnessModel
from .valence_model import ValenceModel
from .instrumentalness_model import InstrumentalnessModel
from .speechiness_model import SpeechinessModel

class HighLevelFeatureExtractor:

    def __init__(self):
        """Initialize all high-level DSP submodels."""
        self.danceability = DanceabilityModel()
        self.acousticness = AcousticnessModel()
        self.valence = ValenceModel()
        self.instrumentalness = InstrumentalnessModel()
        self.speechiness = SpeechinessModel()

    def extract(self, audio_path: str) -> dict:
        """Run all submodels and return a compact DSP feature dictionary."""
        return {
            "danceability": self.danceability.predict(audio_path),
            "acousticness": self.acousticness.predict(audio_path),
            "valence": self.valence.predict(audio_path),
            "instrumentalness": self.instrumentalness.predict(audio_path),
            "speechiness": self.speechiness.predict(audio_path),
        }

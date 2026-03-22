import json
import numpy as np
import essentia.standard as es


class EssentiaTFModel:

    def __init__(self, graph_path: str, metadata_path: str, model_type: str):
        """Load graph/metadata configuration for one TensorFlow audio model."""
        self.graph_path = graph_path
        self.metadata_path = metadata_path
        self.model_type = model_type

        with open(metadata_path, "r") as f:
            self.metadata = json.load(f)

    def predict(self, audio_path: str, sample_rate: int):
        """Run model inference and return class->score mapping."""
        loader = es.MonoLoader(
            filename=audio_path,
            sampleRate=sample_rate,
            resampleQuality=4
        )
        audio = loader()

        if self.model_type == "vggish":
            activations = es.TensorflowPredictVGGish(
                graphFilename=self.graph_path
            )(audio)
        else:
            activations = es.TensorflowPredictMusiCNN(
                graphFilename=self.graph_path
            )(audio)

        mean_activations = activations.mean(axis=0)

        return dict(zip(self.metadata["classes"], mean_activations))

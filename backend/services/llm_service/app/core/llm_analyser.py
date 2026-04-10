from openai import OpenAI
from app.config import settings
from typing import List, cast, Optional, Tuple
from app.core import prompt_templates
from app.models.schemas import LlmResponse, EmotionVector, TrackGet, AudioFeatures, MixedEmotion
from pydantic import ValidationError
from openai.types.chat import ChatCompletionMessageParam
import json
import re

class LlmAnalyser():
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.OLLAMA_URL.rstrip('/') + '/v1',
            api_key="ollama",
        )
        self.MODEL = settings.OLLAMA_MODEL
        self.temperature = settings.TEMPERATURE

    def validate_track(self, track: dict) -> Optional[TrackGet]:
        try:
            return TrackGet(**track)
        except ValidationError as e:
            print(f"Track info is not valid: {e}")
            return None

    def __chat(self, lyrics: str, audio_features: AudioFeatures, temperature: float = 0.3) -> str:
        messages = prompt_templates.get_prompt(lyrics, audio_features)
        response = self.client.chat.completions.create(
            model=self.MODEL,
            messages=cast(List[ChatCompletionMessageParam], messages),
            temperature=temperature
        )
        return response.choices[0].message.content or ""

    def __validate_emotion_vector(self, response: str) -> Optional[EmotionVector]:
        """Парсит JSON с полями components и intensity"""
        # Ищем JSON объект
        try:
            # Пытаемся найти первый { и последний }
            start = response.find('{')
            end = response.rfind('}') + 1
            if start == -1 or end == 0:
                return None
            json_str = response[start:end]
            data = json.loads(json_str)
            # Проверяем наличие необходимых полей
            if "components" not in data or "intensity" not in data:
                return None
            # Валидация через Pydantic
            return EmotionVector.model_validate(data)
        except (json.JSONDecodeError, ValidationError, KeyError) as e:
            print(f"Failed to parse EmotionVector: {e}")
            return None

    def analyse(self, lyrics: str, audio_features: AudioFeatures, max_attempts: int = 5) -> EmotionVector:
        """Возвращает EmotionVector (смешанные эмоции + интенсивность)"""
        for attempt in range(max_attempts):
            print(f"Getting response from Ollama, attempt {attempt+1}")
            response = self.__chat(lyrics, audio_features, self.temperature)
            vector = self.__validate_emotion_vector(response)
            if vector:
                return vector
        # Fallback
        print("Failed to get valid emotion vector, using fallback")
        return EmotionVector(
            components=[MixedEmotion(emotion='sadness', weight=1.0)],
            intensity=5.0
        )

llm_analyser = LlmAnalyser()
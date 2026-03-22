from openai import OpenAI
from app.config import settings
from typing import List, cast
from app.core import prompt_templates
from app.models.schemas import LlmResponse
from pydantic import ValidationError
from openai.types.chat import ChatCompletionMessageParam
from app.models.schemas import TrackGet, AudioFeatures
import json
import re

class LlmAnalyser():
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.OLLAMA_URL.rstrip('/') + '/v1',
            api_key="ollama", 
        )
        self.MODEL = settings.OLLAMA_MODEL
        self.allowed_emotions = ['happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation']
        self.temperature = settings.TEMPERATURE

    def validate_track(self, track : dict):
        try:
            track_pydantic = TrackGet(**track)
            return track_pydantic
        except ValidationError as e:
            print(f"Track info is not valid: {e}")
        return None

    def __chat(self, lyrics : str, audio_features : AudioFeatures, temperature : float = 0.3) -> str:
        message = prompt_templates.get_prompt(lyrics, audio_features)
        messages = cast(List[ChatCompletionMessageParam], message)
        response = self.client.chat.completions.create(model=self.MODEL, messages=messages)
        return response.choices[0].message.content or ""
    
    def __validate(self, response : str):
        pattern = r'\{[^{}]*"emotion"[^{}]*"emotion_intensity"[^{}]*\}'
        match = re.search(pattern, response, re.DOTALL)
        
        if match:
            json_str = match.group()
            try:
                data = json.loads(json_str)
                
                if "emotion" not in data or "emotion_intensity" not in data:
                    return None
                
                if data["emotion"] not in self.allowed_emotions:
                    return None
                
                if not (0 <= data["emotion_intensity"] <= 10):
                    return None
                
                validated = LlmResponse.model_validate(data)
                
                return validated.emotion, validated.emotion_intensity
                
            except (json.JSONDecodeError, ValidationError):
                return None
        return None

    def analyse(self, lyrics : str, audio_features : AudioFeatures, max_attempts: int = 5):
        values = None
        cnt = 0
        while not values and cnt < max_attempts:
            print(f"Getting the response from ollama, attempt {cnt}")
            cnt += 1
            response = self.__chat(lyrics=lyrics, audio_features=audio_features)
            values = self.__validate(response)
        
        if not values:
            return "sadness", 0.5
        
        return values

llm_analyser = LlmAnalyser()
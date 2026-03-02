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
            base_url=settings.OLLAMA_URL,
            api_key="ollama", 
        )
        self.MODEL = settings.OLLAMA_MODEL
        self.allowed_emotions = ['happiness', 'sadness', 'fear', 'anger', 'disgust', 'anticipation']
        self.temperature = settings.TEMPERATURE

    # check if the track corresponds to a pydantic model
    def validate_track(self, track : dict):
        try:
            track_pydantic = TrackGet(**track)
            return track_pydantic
        except ValidationError as e:
            print(f"Track info is not valid: {e}")
        return None

    # returns model response
    def __chat(self, lyrics : str, audio_features : AudioFeatures, temperature : float = 0.3) -> str:
        message = prompt_templates.get_prompt(lyrics, audio_features)
        messages = cast(List[ChatCompletionMessageParam], message)
        response = self.client.chat.completions.create(model=self.MODEL, messages=messages)
        return response.choices[0].message.content or ""
    
    # validates that the response gave the json in a format:
    # {
    #   "emotion" : "happiness" <- an emotion from the list of allowed emotions
    #   "emotion_intensity" : 3.5 <- intensity in a range from 0 to 10
    # }
    def __validate(self, response : str):
        pattern = r'\{\s*"emotion":\s*"[^"]+",\s*"emotion_intensity":\s*\d+\.?\d*\s*\}'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            json_match = match.group()
            data = json.loads(json_match)
            try:
                LlmResponse.model_validate_json(data)
                emotion = data["emotion"]
                emotion_intensity = data["emotion_intensity"]
                return emotion, emotion_intensity
            except ValidationError as e:
                print(e)
                return None
        print("No match found")
        return None

    # goes through the response -> validation cycle
    # until the response is valid
    def analyse(self, lyrics : str, audio_features : AudioFeatures):
        values = None
        cnt = 0
        while not values:
            print(f"Getting the response from ollama, attempt {cnt}")
            cnt += 1
            response = self.__chat(lyrics=lyrics, audio_features=audio_features)
            values = self.__validate(response)
        return values
        

llm_analyser = LlmAnalyser()

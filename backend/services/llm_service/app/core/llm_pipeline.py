from app.clients.parser_client import ParserClient
from app.clients.bd_client import BdClient
from app.core.llm_analyser import LlmAnalyser
from app.models.schemas import TrackGet, TrackPost
import asyncio

class LlmPipeline:
    def __init__(self):
        self.parser = ParserClient()
        self.bd = BdClient()
        self.llm_analyser = LlmAnalyser()
        self.is_running = False
        self.iterate_break = 30
        
    async def start(self):
        self.is_running = True
        print(f"Llm server is running. Polling each {self.iterate_break} seconds")
        while self.is_running:
            await self.__iterate()

        await asyncio.sleep(self.iterate_break)

    async def stop(self):
        self.is_running = False
    
    async def __iterate(self):

        if not (self.parser.check_health() and self.bd.check_health()):
            return
        
        tracks = self.parser.get_song()
        print(f"{len(tracks)} tracks obtained for analysis")

        for track in tracks:
            valid_track = self.llm_analyser.validate_track(track)

            if valid_track:

                lyrics = valid_track.text
                audio_features = valid_track.audio_features
                
                emotion, emotion_intensity = self.llm_analyser.analyse(
                    lyrics, audio_features
                    )
                track_post = TrackPost(
                    **valid_track.model_dump(),
                    emotion=emotion,
                    emotion_intensity=emotion_intensity
                )
                if self.bd.load_track(track_post):
                    print(f"Successfully saved track {track_post.id}")
            else:
                print("The track format is invalid")
                continue
        return

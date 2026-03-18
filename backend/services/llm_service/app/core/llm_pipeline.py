from app.clients.parser_client import ParserClient
from app.clients.bd_client import BdClient
from app.core.llm_analyser import LlmAnalyser
from app.models.schemas import TrackPost
import asyncio

class LlmPipeline:
    def __init__(self):
        self.parser = ParserClient()
        self.bd = BdClient()
        self.llm_analyser = LlmAnalyser()
        self.is_running = False
        self.iterate_break = 30
        self.message_queue = asyncio.Queue()
        
    async def start(self):
        self.is_running = True
        print(f"Llm server is running. Polling each {self.iterate_break} seconds")
        
        producer = asyncio.create_task(self._add_tracks_to_queue())
        consumer = asyncio.create_task(self._process_queue())
        try:
            await asyncio.gather(producer, consumer)
        except Exception as e:
            self.is_running = False
            producer.cancel()
            consumer.cancel()
            print(f"An error occured while gathering and processing the tracks: {e}")
            

    def stop(self):
        self.is_running = False
    

    async def _add_tracks_to_queue(self):
        while self.is_running:
            if not (self.parser.check_health()):
                await asyncio.sleep(self.iterate_break)
                print("Parser service is not healthy")
                continue
            
            track = await asyncio.to_thread(self.parser.get_song)
            if track:
                await self.message_queue.put(track)
            await asyncio.sleep(self.iterate_break)



    async def _process_queue(self):
        
        while self.is_running:
            
            if not (self.bd.check_health()):
                await asyncio.sleep(self.iterate_break)
                print("Db service is not healthy")
                continue

            track = await self.message_queue.get()
            
            try:    
                valid_track = self.llm_analyser.validate_track(track)
                if valid_track:

                    lyrics = valid_track.text
                    audio_features = valid_track.audio_features
                    
                    emotion, emotion_intensity = await asyncio.to_thread(self.llm_analyser.analyse,
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
            finally:
                self.message_queue.task_done()

        return

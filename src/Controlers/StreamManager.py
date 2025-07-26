import os
from typing import List
import re

class StreamManager:
    def __init__(self , stream_name:str,ROI:List[List[int]]=list , type:str = "video"):
        """
        This class responsible for return create stream Object
        :param stream_name: stream name may be a video directory or stream name
        :param type: is this a video or realtime stream
        """
        self.stream_name = stream_name
        self.normalized_stream_name = StreamManager.normalize_stream_name(stream_name)
        self.queue_name = self.normalized_stream_name+"frame"
        self.status = "pending"
        parent_dir = os.path.dirname(os.path.dirname(__file__))
        self.save_dir = os.path.join(parent_dir, "assets", self.normalized_stream_name)
        os.makedirs(self.save_dir , exist_ok=True)
        self.ROI = ROI
    def Stream_schema(self):
        return {"stream_name":self.stream_name,
                "queue_name":self.queue_name,
                "status":self.status,
                "save_dir":self.save_dir,
                "num_violation":0,
                "ROI":self.ROI}

    @staticmethod
    def normalize_stream_name(name: str) -> str:
        """
        Normalize a stream name:
        - Lowercase
        - Replace spaces with underscores
        - Remove most special characters except underscores and letters/numbers
        """
        # Lowercase
        name = name.lower()
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        # Remove everything except letters (Arabic & English), numbers, and underscores
        name = re.sub(r'[^\w\u0600-\u06FF]', '', name)
        return name


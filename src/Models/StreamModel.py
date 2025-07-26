from .Base import Base
from .DB_schema import Stream
from  Controlers.StreamManager import StreamManager
from  Helper import get_setting
from typing import List

class StreamModel(Base):
    def __init__(self , db_client:object):
        super().__init__( db_client)

        self.collection = self.db_client[get_setting().STREAM_COLLECTION]  ## add to env

    async def create_stream(self, stream:Stream):
        result = await self.collection.insert_one(
            stream.model_dump(by_alias=True, exclude_unset=True)
        )
        return result

    async def search_for_stream(self, stream_name):
        result = await self.collection.find_one({
            "stream_name": stream_name})
        return  result

    async def search_and_insert_if_not_exists(self,stream_name , ROI:List[List[int]]=list):
        search_result = await  self.search_for_stream(stream_name=stream_name)
        if search_result is not None :
            return True ,  search_result
        stream_manger = StreamManager(stream_name=stream_name,ROI = ROI)
        stream = stream_manger.Stream_schema()
        stream = Stream(**stream)
        await self.create_stream(stream)
        return False , stream.model_dump(by_alias=True, exclude_unset=True)
    async def update(self , queue_name , value_dict):
        result = await self.collection.update_one({'queue_name': queue_name},
                                         {'$set': value_dict})
        return  result
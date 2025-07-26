from pydantic import BaseModel , Field
from typing import Optional,Literal , List
from  bson.objectid import  ObjectId
class Stream(BaseModel):
    id :Optional[ObjectId] =Field(None,alias = "_id")
    stream_name:str
    queue_name:str
    TCP_socket:Optional[int] = Field(None)
    num_violation:Optional[int] = Field(None)
    status:Literal["pending", "processing" , "finished"]
    ROI:List[List[int]]
    save_dir:str
    class Config:
        arbitrary_types_allowed = True

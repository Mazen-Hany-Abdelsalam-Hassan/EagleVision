from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    Name:str
    Version :str
    ## Message Broker
    HOST :str
    RABBITMQ_PORT:int #= 5672
    BROKER_USERNAME:str #= "guest"
    BROKER_PASSWORD:str #= "guest"
    ## Workers
    BACKEND:str #= "rpc://"
    BROKER:str   #= 'pyamqp://guest@localhost//'
    ## variables
    #END_OF_STREAM : bytes

    ## DB Parameters
    CLIENT :str # "mongodb://localhost:27007"
    DB_NAME :str #"VideoStream"
    STREAM_COLLECTION :str #"Stream"
    END_OF_STREAM:bytes  ## b"End Of Stream"
    SERVER_PORTS:List[int]
    IMAGE_SHAPE:List[int]
    MODEL_IOU:float
    MODEL_CONF:float



    class Config:
        env_file = '.env'
def get_setting():
    return Settings()
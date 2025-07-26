from celery import Celery
from Helper import Settings , get_setting
from Controlers import FrameReader
from motor.motor_asyncio import  AsyncIOMotorClient
from pymongo import MongoClient



frame_reader_worker = Celery("Tasks",
                                broker="pyamqp://guest@localhost//",
                                backend="rpc://")



@frame_reader_worker.task
def frame_reader(frame_queue,regoin_of_interst):

    """
    Celery task to convert video to frames and send to queue
    """
    client = MongoClient('mongodb://127.0.0.1:27007/')

    # Access your database
    db = client["VideoStream"]

    # Access your collection
    collection = db['Stream']

    video_queue =  FrameReader(frame_queue=frame_queue,
                               collection = collection,
                               regoin_of_interst = regoin_of_interst)

    video_queue.main()
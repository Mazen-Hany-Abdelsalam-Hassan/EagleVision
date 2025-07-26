from celery import Celery

from Controlers import VideoToFrames
from Helper import Settings , get_setting
env = get_setting()
video_to_frames_worker = Celery("Tasks",
                                broker=env.BROKER,
                                backend=env.BACKEND )



@video_to_frames_worker.task
def process_video_to_frames(stream: str, queue_name:str):
    """
    Celery task to convert video to frames and send to queue
    """
    video_queue =  VideoToFrames(stream_name=stream , queue_name = queue_name)
    video_queue.enqueue_video_frames()
    video_queue.close()


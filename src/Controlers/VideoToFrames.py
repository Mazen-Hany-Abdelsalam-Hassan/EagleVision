import cv2
import pika
from turbojpeg import TurboJPEG
from Helper import Settings , get_setting

class VideoToFrames:
    def __init__(self,stream_name,  queue_name):
        # Initialize TurboJPEG encoder

        self.jpeg_encoder = TurboJPEG()
        self.stream_name = stream_name
        env = get_setting()
        self.end_of_stream = env.END_OF_STREAM
        # RabbitMQ connection setup
        connection_params = pika.ConnectionParameters(
            host=env.HOST,
            port=env.RABBITMQ_PORT,
            virtual_host='/',
            credentials=pika.PlainCredentials(username= env.BROKER_USERNAME,
                                              password= env.BROKER_PASSWORD)
        )
        self.connection = pika.BlockingConnection(connection_params)
        self.channel = self.connection.channel()
        self.queue_name = queue_name


        self.channel.queue_declare(queue=self.queue_name, durable=False)

    def enqueue_video_frames(self):
        """
        Reads video frames, encodes them using TurboJPEG, and publishes each frame to RabbitMQ.
        """
        video = cv2.VideoCapture(self.stream_name)
        if not video.isOpened():
            print(f"Error: Cannot open video file {self.stream_name}")
            return False, "video_not_opened"

        while True:
            ret, frame = video.read()
            if not ret:
                self._publish_frame(self.end_of_stream)
                break

            frame = cv2.resize(frame , (960, 608))

            jpeg_bytes = self.jpeg_encoder.encode(frame)

            self._publish_frame(jpeg_bytes)
        video.release()
        return True, "video_sent"

    def _publish_frame(self, jpeg_bytes):
        """
        Publish a single JPEG-encoded frame to RabbitMQ.
        """
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=jpeg_bytes,
            properties=pika.BasicProperties(
                delivery_mode=1,
            )
        )

    def close(self):
        """
        Close the RabbitMQ connection.
        """
        self.connection.close()
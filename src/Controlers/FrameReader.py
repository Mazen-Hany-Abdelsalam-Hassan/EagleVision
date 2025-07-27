import  cv2
import time
from turbojpeg import  TurboJPEG
import pika
import socket
from Helper import Settings , get_setting
import struct
from Models.StreamModel import StreamModel
from AI_Service import AI_Service
import threading

class FrameReader:
    def __init__(self, frame_queue:str, collection , regoin_of_interst):
        self.jpeg_encoder = TurboJPEG()
        self.frame_queue = frame_queue
        env = get_setting()
        self.end_of_stream = env.END_OF_STREAM
        self.clients = []
        self.num_violation = 0

        self.server = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
        for port in env.SERVER_PORTS:
            try:
                self.server.bind(("localhost", port))
                #print(f"The Server is Hosted at this PORT {port}")
                break
            except:
                pass
        # Enums
        connection_params = pika.ConnectionParameters(
            host=env.HOST,
            port=env.RABBITMQ_PORT,
            virtual_host='/',
            credentials=pika.PlainCredentials(username=env.BROKER_USERNAME,
                                              password=env.BROKER_PASSWORD)
        )
        self.connection = pika.BlockingConnection(connection_params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.frame_queue, durable=False)


        self.server.listen()
        accept_new_thread = threading.Thread(target=self.accept_new, daemon=True)
        accept_new_thread.start()

        self.collection = collection
        self.detection_service = AI_Service.AI_Service(region_of_interest = regoin_of_interst)




        value_dict = {"status":"processing" ,
                      "Tcp_socket":port}
        new_values = {"$set": value_dict}
        filter = {"queue_name": frame_queue}
        self.collection.update_one(filter ,new_values)



    def accept_new(self):
        while True:
            try:
                client, address = self.server.accept()
                #print("HIIIIIIIIIIIIII")
                #print(address)
                self.clients.append((client , address))

            except:
                #print("Server disconnect")
                break

    def broadcasting(self, message):
        for client,address in self.clients:
            try:
                #print(address)
                client.sendall(message)
            except:
                #print(address)
                self.clients.remove((client,address))
                client.close()


    def main(self):
        try:
            while True:
                method_frame, header_frame, encoded_frame = self.channel.basic_get(queue=self.frame_queue,
                                                                          auto_ack=True)
                if encoded_frame != self.end_of_stream:
                    if encoded_frame is None :
                        continue
                    p1 = time.time()
                    image = self.jpeg_encoder.decode(encoded_frame)
                    violation = self.detection_service.main(image)
                    if violation:
                        self.num_violation+=1
                    encoded_frame = self.jpeg_encoder.encode(image)
                    length = struct.pack(">L", len(encoded_frame))
                    msg = length + encoded_frame
                    self.broadcasting(msg)
                    p2 = time.time()
                    waited = (p2-p1)*1000
                    if waited < 33:
                        cv2.waitKey(int(33-waited))
                else:
                    break

        finally:
            for (client ,address) in self.clients:
                client.close()
            value_dict = {"status": "finished",
                          "num_violation":self.num_violation}
            new_values = {"$set": value_dict}
            filter = {"queue_name": self.frame_queue}
            self.collection.update_one(filter ,new_values)
            self.server.close()
            self.connection.close()

import socket
import struct
class StreamShow:
    def __init__(self, PORT):
        self.host = "localhost"
        try :
            self.client = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
            self.client.connect((self.host , PORT))
        except:
            print("Server Not available ")

    def receive_all(self, length):
        """Helper function to receive exactly n bytes"""
        data = b''
        while len(data) < length:
            packet = self.client.recv(length - len(data))
            if not packet:
                return None
            data += packet
        return data
    def main(self):
        try:
            while True:
                length_data = self.receive_all(4)
                if not length_data:
                    print("Server disconnected.")
                    break
                frame_length = struct.unpack(">L", length_data)[0]
                frame_data = self.receive_all(frame_length)

                if not frame_data:
                    print("Server disconnected.")
                    break
                yield frame_data

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.client.close()



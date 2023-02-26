import socketserver
import struct
import json
from collections import OrderedDict


MAX_PACKET_SIZE = 512
packet_format = "8s2I"
TIMEOUT = 60


class UDPHandler(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def unpack_packet(self, packet):
        packet_header = packet[:16]
        packet_payload = packet[16:]
        packet_id, packet_index, packet_count = struct.unpack(packet_format, packet_header)
        return packet_id, packet_index, packet_count, packet_payload

    def combine_packets(self, packets):
        data = b''.join(v for _, v in packets['packets'].items())
        return json.loads(data)

    def handle(self):
        data = self.request[0]
        packet_id, packet_index, packet_count, packet_payload = self.unpack_packet(data)

        print(f"Recived data: [{packet_id}], segment: [{packet_index}]")

        if packet_id not in self.server.chunks:
            self.server.chunks[packet_id] = {
                'packet_count': packet_count,
                'packets': OrderedDict()
            }

        if packet_index not in self.server.chunks[packet_id]['packets']:
            self.server.chunks[packet_id]['packets'][packet_index] = packet_payload

        if len(self.server.chunks[packet_id]['packets']) == int(self.server.chunks[packet_id]['packet_count']):
            data = self.combine_packets(self.server.chunks.pop(packet_id))
            return


class UDPServer(socketserver.UDPServer):

    def __init__(self, address, handler_class):
        super().__init__(address, handler_class)
        self.chunks = {

        }
        """
        e.g:
            {
                "package_id": {
                    "packet_count": 3
                    "packets": {
                        "idx": data
                    }
                }
            }
        """


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999
    server = UDPServer((HOST, PORT), UDPHandler)
    server.serve_forever()

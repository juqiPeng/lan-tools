import socket
import json
import struct
from typing import Optional, Tuple
import uuid
import math

packet_format = "8s2I"
MAX_PACKET_SIZE = 512


class UDPClient:

    def __init__(self, address: Optional[Tuple[str, int]] = ("192.168.1.3", 9999)) -> None:
        self.address = address

    def pack_packet(self, packet_id, packet_index, packet_count, data):
        packet_header = struct.pack(packet_format, packet_id, packet_index, packet_count)
        return packet_header + data

    def send_chunk(self, sock, packet):
        sock.sendto(packet, self.address)
        sock.settimeout(0.1)

    def send_data(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(('192.168.1.2', 12345))
            total_len = len(data)
            uid = str(uuid.uuid4())[:8]
            uid_byte = bytes(uid, encoding='UTF-8')
            packet_count = math.ceil(total_len / MAX_PACKET_SIZE)
            print(f"send data: [{uid}], the length is: [{total_len}], number of packets to split: [{packet_count}]")
            for seq, i in enumerate(range(0, total_len, MAX_PACKET_SIZE)):
                packet_data = data[i:i+MAX_PACKET_SIZE]
                packet = self.pack_packet(uid_byte, seq, packet_count, packet_data)
                self.send_chunk(sock, packet)
                print(f"[{uid}] segment {seq} has been sent.")



if __name__ == "__main__":
    data = {}
    for i in range(20):
        key = f'key_{i}'
        data[key] = {"index": i, "data": list(range(i))}

    byte_data = bytes(json.dumps(data), encoding='utf-8')
    UDPClient().send_data(byte_data)

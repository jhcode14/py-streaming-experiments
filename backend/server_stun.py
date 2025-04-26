from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
import struct

MAGIC_COOKIE = 0x2112A442
class STUN(DatagramProtocol):
    """
    STUN server implementation
    """
    def datagramReceived(self, data, addr):
        # validate first 2 bits are 0s
        first_byte = data[0]
        if first_byte & 0b11000000 != 0b00000000:
            raise Exception("Invalid STUN message")
        
        # get message type (14 bits)
        msg_type = int.from_bytes(data[:2], "big", signed=False) & 0b0011111111111111

        # check if we are binding request
        if msg_type != 0x0001:
            raise Exception("Invalid STUN message")

        # get message length (16 bits)
        msg_len = int.from_bytes(data[2:4], "big", signed=False)

        # get magic cookie (32 bits) & validate
        magic_cookie = int.from_bytes(data[4:8], "big", signed=False)
        if magic_cookie != MAGIC_COOKIE:
            raise Exception("Invalid STUN message")

        # get transaction ID (96 bits)
        transaction_id = int.from_bytes(data[8:20], "big", signed=False)

        # construct STUN message response header
        response_header = bytearray(20)
        
        # set 0b00 + message type (2+14 bits)
        struct.pack_into(">H", response_header, 0, 0x0101)

        # set message length (16 bits)
        struct.pack_into(">H", response_header, 2, 12)

        # set magic cookie (32 bits)
        struct.pack_into(">I", response_header, 4, MAGIC_COOKIE)

        # set transaction ID (96 bits)
        response_header[8:20] = transaction_id.to_bytes(12, "big")

        # construct STUN message attributes header
        response_attributes_header = bytearray(4)
        struct.pack_into(">H", response_attributes_header, 0, 0x0020) # XOR-MAPPED-ADDRESS
        struct.pack_into(">H", response_attributes_header, 2, 8) # length

        response_attribute_value = bytearray(8)
        
        # TODO: Make assumption that we are using IPv4
        struct.pack_into(">B", response_attribute_value, 1, 0x01)

        # set X-port 
        x_port = addr[1] ^ (MAGIC_COOKIE >> 16)
        struct.pack_into(">H", response_attribute_value, 2, x_port)

        # set X-ip
        ip_arr_str = addr[0].split(".")
        magic_cookie_arr = MAGIC_COOKIE.to_bytes(4, "big")
        for i in range(4):
            response_attribute_value[i + 4] = (int(ip_arr_str[i]) ^ magic_cookie_arr[i])

        # construct STUN message response
        response = response_header + response_attributes_header + response_attribute_value

        # send response
        self.transport.write(response, addr)
        print("Sent STUN response to", addr)

reactor.listenUDP(9999, STUN())
reactor.run()
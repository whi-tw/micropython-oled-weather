import logging

import socket
import uasyncio as asyncio

def mtStr(s):
    return bytes([len(s) >> 8, len(s) & 255]) + s.encode('utf-8')


def mtPacket(cmd, variable, payload):
    return bytes([cmd, len(variable) + len(payload)]) + variable + payload


def mtpConnect(name):
    return mtPacket(
        0b00010000,
        mtStr("MQTT") +  # protocol name
        b'\x04' +  # protocol level
        b'\x00' +  # connect flag
        b'\xFF\xFF',  # keepalive
        mtStr(name)
    )


def mtpDisconnect():
    return bytes([0b11100000, 0b00000000])


def mtpPub(topic, data):
    return mtPacket(0b00110001, mtStr(topic), data)


class MQTTClient:
    def __init__(self, server, port, client_id, base_topic):
        self.server = server
        self.port = port
        self.client_id = client_id
        self.base_topic = base_topic

    async def publish(self, topic: str, value: bytes):
        s = socket.socket()
        s.connect(socket.getaddrinfo(self.server, self.port)[0][-1])
        s.send(mtpConnect(self.client_id))
        await asyncio.sleep(2)
        logging.info("publishing {} to {}/{}".format(value, self.base_topic, topic))
        s.send(mtpPub("{}/{}".format(self.base_topic, topic), value))
        s.send(mtpDisconnect())
        s.close()

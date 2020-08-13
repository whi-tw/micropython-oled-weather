import sys
import logging

from machine import Pin, I2C
import uasyncio as asyncio

from mqtt_as import MQTTClient

from .config import config
from . import guicontroller, sensorcontroller

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

device_name = "OFFICE"
mqtt_topic = "home/climate/{}".format(device_name)

mc = MQTTClient(config)

async def connect_mqtt(client):
    await client.connect()
    while True:
        await asyncio.sleep(1)

async def pub_mqtt(topic, value):
    await mc.publish(
        "{}/{}".format(mqtt_topic, topic).encode("utf-8"),
        str(value).encode("utf-8"),
        retain=True
    )


def on_sensor_change(sensor: sensorcontroller.Sensor):
    if sensor.serial == internal_temp_sensor.serial:
        gui.set_value(sensor.current_value, "TEMP_IN")
        gui.set_value(sensor.min_value, "TEMP_MIN")
        gui.set_value(sensor.max_value, "TEMP_MAX")
        loop = asyncio.get_event_loop()
        loop.create_task(pub_mqtt(
            "TEMP/IN/CURRENT",
            sensor.current_value
        ))
    elif sensor.serial == external_temp_sensor.serial:
        gui.set_value(sensor.current_value, "TEMP_OUT")
        loop = asyncio.get_event_loop()
        loop.create_task(pub_mqtt(
            "TEMP/OUT/CURRENT",
            sensor.current_value
        ))
    elif sensor.serial == internal_humidity_sensor.serial:
        gui.set_value(sensor.current_value, "HUMID_IN")
        gui.set_value(sensor.min_value, "HUMID_MIN")
        gui.set_value(sensor.max_value, "HUMID_MAX")
        loop = asyncio.get_event_loop()
        loop.create_task(pub_mqtt(
            "HUMIDITY/IN/CURRENT",
            sensor.current_value
        ))


gui = guicontroller.GUI(128, 64, I2C(-1, scl=Pin(25), sda=Pin(33)))
s = sensorcontroller.SensorController(on_sensor_change)
internal_temp_sensor = s.add_sensor(sensorcontroller.DallasTempSensor, Pin(14), serial=b'(yd\x84\x07\x00\x00\xb3')
external_temp_sensor = s.add_sensor(sensorcontroller.DallasTempSensor, Pin(14), serial=b'(\x84tV\xb5\x01<\xdb')
internal_humidity_sensor = s.add_sensor(sensorcontroller.DHT22Sensor, Pin(27), serial=b'INTERNAL_HUMIDITY')

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(connect_mqtt(mc))
finally:
    mc.close()  # Prevent LmacRxBlk:1 errors
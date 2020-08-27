import sys
import logging

import gc

from machine import Pin, I2C
import uasyncio as asyncio

from mqtt_as import MQTTClient

from .config import config
from . import sensorcontroller, displaymanager

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

device_name = "OFFICE"
mqtt_topic = "home/climate/{}".format(device_name)


async def wifi_handler(connected):
    wifi_image = displaymanager.PBM("wifi")
    if connected:
        displaymanager.blit(wifi_image, 117, 1)
    else:
        displaymanager.fill_rect(117, 1, wifi_image.width, wifi_image.height, 0)
    del wifi_image
    gc.collect()


config["wifi_coro"] = wifi_handler


class DataManager:
    def __init__(self):
        self.storage = {}

    def get(self):
        return self.storage


async def connect_mqtt(client):
    await client.connect()
    while True:
        await pub_mqtt("status", "status", retain=False)
        await asyncio.sleep(10)


async def pub_mqtt(topic, value, retain=True):
    activity_led.value(1)
    await mc.publish(
        "{}/{}".format(mqtt_topic, topic).encode("utf-8"),
        str(value).encode("utf-8"),
        retain=retain
    )
    activity_led.value(0)


def on_sensor_change(sensor: sensorcontroller.Sensor):
    if sensor.serial == internal_temp_sensor.serial:
        datamanager.storage["TEMP_IN"] = sensor.current_value
        datamanager.storage["TEMP_IN_SIMPLE"] = "{:2.0f}C".format(sensor.current_value)
        datamanager.storage["TEMP_MIN"] = sensor.min_value
        datamanager.storage["TEMP_MAX"] = sensor.max_value
        loop = asyncio.get_event_loop()
        loop.create_task(pub_mqtt(
            "TEMP/IN/CURRENT",
            sensor.current_value
        ))
    elif sensor.serial == external_temp_sensor.serial:
        datamanager.storage["TEMP_OUT"] = sensor.current_value
        loop = asyncio.get_event_loop()
        loop.create_task(pub_mqtt(
            "TEMP/OUT/CURRENT",
            sensor.current_value
        ))
    elif sensor.serial == internal_humidity_sensor.serial:
        datamanager.storage["HUMIDITY_IN"] = sensor.current_value
        datamanager.storage["HUMIDITY_IN_SIMPLE"] = "{:2.0f}%".format(sensor.current_value)
        datamanager.storage["HUMIDITY_MIN"] = sensor.min_value
        datamanager.storage["HUMIDITY_MAX"] = sensor.max_value
        loop = asyncio.get_event_loop()
        loop.create_task(pub_mqtt(
            "HUMIDITY/IN/CURRENT",
            sensor.current_value
        ))


mc = MQTTClient(config)
datamanager = DataManager()
dm = displaymanager.DisplayManager(128, 64, I2C(-1, scl=Pin(25), sda=Pin(33)), Pin(32, Pin.IN), datamanager)
dm.add_screen(
    dm.screen_factory(
        displaymanager.ScreenConfig("overview", {"TEMP_IN_SIMPLE": (19, 38), "HUMIDITY_IN_SIMPLE": (84, 38)})
    ))
dm.add_screen(dm.screen_factory(displaymanager.ScreenConfig("detail", {})))
dm.start()

s = sensorcontroller.SensorController(on_sensor_change)
internal_temp_sensor = s.add_sensor(sensorcontroller.DallasTempSensor, Pin(14), serial=b'(yd\x84\x07\x00\x00\xb3')
external_temp_sensor = s.add_sensor(sensorcontroller.DallasTempSensor, Pin(14), serial=b'(\x84tV\xb5\x01<\xdb')
internal_humidity_sensor = s.add_sensor(sensorcontroller.DHT22Sensor, Pin(27), serial=b'INTERNAL_HUMIDITY')

activity_led = Pin(2, Pin.OUT)
activity_led.value(0)

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(connect_mqtt(mc))
finally:
    mc.close()  # Prevent LmacRxBlk:1 errors

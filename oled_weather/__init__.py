import sys
import logging

import gc

from machine import Pin, I2C
import uasyncio as asyncio

from mqtt_as import MQTTClient

from .config import config
from . import sensorcontroller, displaymanager
from .font import dogica16_values, dogica8_values

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

device_name = "OFFICE"
mqtt_topic = "home/climate/{}".format(device_name)


async def wifi_handler(connected):
    dm.header.set_icon_visible("wifi", connected)


async def connect_handler(connected):
    dm.header.set_icon_visible("cloud", connected)

config["wifi_coro"] = wifi_handler
config["connect_coro"] = connect_handler


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


def format_sensor_val(f, kind=None):
    if f == 100:
        s = "100"
    elif f == -100:
        s = "-100"
    elif f == 0:
        s = "0"
    else:
        s = "{:4.1f}".format(f)
    if kind == "temp":
        return "{}°C".format(s)
    elif kind == "humidity":
        return "{}%".format(s)
    return s

def on_sensor_change(sensor: sensorcontroller.Sensor):
    if sensor.serial == internal_temp_sensor.serial:
        datamanager.storage["TEMP_IN"] = format_sensor_val(sensor.current_value, "temp")
        datamanager.storage["TEMP_IN_SIMPLE"] = "{:2.0f}°C".format(sensor.current_value)
        datamanager.storage["TEMP_MIN"] = format_sensor_val(sensor.min_value, "temp")
        datamanager.storage["TEMP_MAX"] = format_sensor_val(sensor.max_value, "temp")
        loop = asyncio.get_event_loop()
        loop.create_task(pub_mqtt(
            "TEMP/IN/CURRENT",
            sensor.current_value
        ))
    elif sensor.serial == external_temp_sensor.serial:
        datamanager.storage["TEMP_OUT"] = format_sensor_val(sensor.current_value, "temp")
        loop = asyncio.get_event_loop()
        loop.create_task(pub_mqtt(
            "TEMP/OUT/CURRENT",
            sensor.current_value
        ))
    elif sensor.serial == internal_humidity_sensor.serial:
        datamanager.storage["HUMIDITY_IN"] = format_sensor_val(sensor.current_value, "humidity")
        datamanager.storage["HUMIDITY_IN_SIMPLE"] = "{:2.0f}%".format(sensor.current_value)
        datamanager.storage["HUMIDITY_MIN"] = format_sensor_val(sensor.min_value, "humidity")
        datamanager.storage["HUMIDITY_MAX"] = format_sensor_val(sensor.max_value, "humidity")
        loop = asyncio.get_event_loop()
        loop.create_task(pub_mqtt(
            "HUMIDITY/IN/CURRENT",
            sensor.current_value
        ))


mc = MQTTClient(config)
datamanager = displaymanager.DataManager()
dm = displaymanager.DisplayManager(128, 64, I2C(-1, scl=Pin(25), sda=Pin(33)), Pin(32, Pin.IN), datamanager, header_height=8)
dm.set_header("header")
dm.header.add_icon("wifi", False)
dm.header.add_icon("cloud", False)

dm.add_screen(
    dm.screen_factory(
        displaymanager.ScreenConfig(
            "overview", {
                "TEMP_IN_SIMPLE": displaymanager.screen.VarLocation(6, 31, "l", dogica16_values),
                "HUMIDITY_IN_SIMPLE": displaymanager.screen.VarLocation(77, 31, "l", dogica16_values)
            }
        )
    ))
dm.add_screen(
    dm.screen_factory(
        displaymanager.ScreenConfig(
            "detail", {
                "TEMP_IN": displaymanager.screen.VarLocation(61, 23, "r", dogica8_values),
                "TEMP_OUT": displaymanager.screen.VarLocation(61, 31, "r", dogica8_values),
                "TEMP_MIN": displaymanager.screen.VarLocation(61, 39, "r", dogica8_values),
                "TEMP_MAX": displaymanager.screen.VarLocation(61, 47, "r", dogica8_values),
                "HUMIDITY_IN": displaymanager.screen.VarLocation(128, 23, "r", dogica8_values),
                "HUMIDITY_MIN": displaymanager.screen.VarLocation(128, 39, "r", dogica8_values),
                "HUMIDITY_MAX": displaymanager.screen.VarLocation(128, 47, "r", dogica8_values)
            }
        )
    )
)
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

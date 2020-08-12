import sys
import logging

from machine import Pin, I2C
import uasyncio as asyncio

from simple_mqtt import MQTTClient

from . import guicontroller, sensorcontroller

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

mqtt_broker = "test.mosquitto.org"
mqtt_port = 1883
client_id = "6a1b2d81-45e0-4519-b05d-f521a4db8459"
device_name = "OFFICE"
mqtt_topic = "f5ebd52c-543c-4c57-974b-cabdac021a82/" + device_name


mc = MQTTClient(client_id, mqtt_broker, mqtt_port)


async def pub_mqtt(topic, value):
    mc.connect()
    mc.publish(
        (mqtt_topic + "/" + topic).encode("utf-8"),
        str(value).encode("utf-8"),
        retain=True
    )


def on_sensor_change(sensor: sensorcontroller.Sensor):
    if sensor.serial == internal_sensor.serial:
        gui.set_value(sensor.current_value, "TEMP_IN")
        gui.set_value(sensor.min_value, "TEMP_MIN")
        gui.set_value(sensor.max_value, "TEMP_MAX")
        loop = asyncio.get_event_loop()
        loop.create_task(pub_mqtt(
            "TEMP/IN/CURRENT",
            sensor.current_value
        ))


gui = guicontroller.GUI(128, 64, I2C(-1, scl=Pin(5), sda=Pin(4)))
s = sensorcontroller.SensorController(on_sensor_change)
internal_sensor = s.add_sensor(sensorcontroller.DallasTempSensor, Pin(14), serial=b'(yd\x84\x07\x00\x00\xb3')
# external_sensor = s.add_sensor(sensorcontroller.DallasTempSensor, Pin(14), serial=b'(\xa3\x7f\x82\x07\x00\x00\xbd')

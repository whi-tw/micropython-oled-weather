import dht
import ds18x20
import machine
import onewire
import uasyncio as asyncio


class Sensor:
    def __init__(self, serial, on_change):
        self.serial = serial
        self.on_change = on_change
        self.current_value = None
        self.min_value = None
        self.max_value = None

    def update(self, data):
        changed = False
        if self.current_value is None:
            self.current_value = data
            self.min_value = data
            self.max_value = data
            changed = True
        if data > self.max_value:
            self.max_value = data
            changed = True
        elif data < self.min_value:
            self.min_value = data
            changed = True
        if self.current_value != data:
            self.current_value = data
            changed = True
        if changed:
            self.on_change(self)


class DallasTempSensor(Sensor):
    def __init__(self, serial, pin: machine.Pin, on_change):
        self.pin = pin
        self.ds_sensor = ds18x20.DS18X20(onewire.OneWire(self.pin))
        super(DallasTempSensor, self).__init__(serial=serial, on_change=on_change)
        loop = asyncio.get_event_loop()
        loop.create_task(self.read())

    async def read(self):
        iterations = 10
        while True:
            total = 0
            for i in range(0, iterations):
                self.ds_sensor.convert_temp()
                await asyncio.sleep_ms(750)
                total += self.ds_sensor.read_temp(self.serial)
                await asyncio.sleep_ms(250)
            total /= iterations
            super(DallasTempSensor, self).update(total)


class DHT22Sensor(Sensor):
    def __init__(self, serial, pin: machine.Pin, on_change):
        self.pin = pin
        self.sensor = dht.DHT22(pin)
        super(DHT22Sensor, self).__init__(serial=serial, on_change=on_change)
        loop = asyncio.get_event_loop()
        loop.create_task(self.read())

    async def read(self):
        delay_millis = 2000
        iterations = int(10000/delay_millis)
        while True:
            total = 0
            for i in range(0, iterations):
                self.sensor.measure()
                total += self.sensor.humidity()
                await asyncio.sleep_ms(delay_millis)
            total /= iterations
            super(DHT22Sensor, self).update(total)


class SensorController:
    sensors = []

    def __init__(self, change_callback):
        self.change_callback = change_callback

    def on_update(self, sensor: Sensor):
        self.change_callback(sensor)

    def add_sensor(self, sensor_class, pin: machine.Pin, serial: bytes = None) -> Sensor:
        if serial:
            ident = serial
        else:
            ident = str(len(self.sensors)).encode("utf-8")
        sensor = sensor_class(ident, pin, self.on_update)
        self.sensors.append(sensor)
        return sensor

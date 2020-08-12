import network
import uasyncio as asyncio

import oled_weather

sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.active(True)
    sta_if.connect("***REMOVED***", "***REMOVED***")
    while not sta_if.isconnected():
        pass
print('network config:', sta_if.ifconfig())

loop = asyncio.get_event_loop()
loop.run_forever()
#######################################
#               IMPORTS               #
#######################################
import wilson
import random

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_bluefruit_connect.packet import Packet
# Only the packet classes that are imported will be known to Packet.
from adafruit_bluefruit_connect.button_packet import ButtonPacket

#######################################
#                 INIT                #
#######################################
## Bluetooth low energy
ble = BLERadio()
uart_service = UARTService()
advertisement = ProvideServicesAdvertisement(uart_service)

## Wilson's behaviors
behaviour = [wilson.hello, wilson.grumpy, wilson.love, wilson.wtf, wilson.dead]

#######################################
#              MAIN LOOP              #
#######################################
while True:
    ble.start_advertising(advertisement)

    while not ble.connected:
        wilson.idle()
        # print(crickit.touch_1.raw_value)
        if not wilson.ss.digital_read(wilson.BUTTON_1):
            random.choice(behaviour)()
        if not wilson.ss.digital_read(wilson.BUTTON_2):
            wilson.hide()

    while ble.connected:
        wilson.idle()
        if uart_service.in_waiting:
            # Packet is arriving.
            packet = Packet.from_stream(uart_service)
            if isinstance(packet, ButtonPacket) and packet.pressed:
                if packet.button == ButtonPacket.UP :
                    wilson.forward()

                elif packet.button == ButtonPacket.DOWN :
                    wilson.backward()

                elif packet.button == ButtonPacket.BUTTON_1:
                    random.choice(behaviour)()

                elif packet.button == ButtonPacket.BUTTON_2:
                    wilson.hide()
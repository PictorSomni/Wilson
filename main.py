#######################################
#               IMPORTS               #
#######################################
import wilson
import random
from time import monotonic

from adafruit_ble import BLERadio
from adafruit_ble.advertising.adafruit import AdafruitColor

#######################################
#                 INIT                #
#######################################
## Bluetooth low energy
ble = BLERadio()
advertisement = AdafruitColor()

## Wilson's behaviors
behaviour = [wilson.hello, wilson.grumpy, wilson.love, wilson.wtf, wilson.dead]

#######################################
#              MAIN LOOP              #
#######################################
while True:
    wilson.attitude("blink")
    t = monotonic()
    while monotonic() - t < random.randint(2, 10):
        wilson.attitude("open")
        if not wilson.ss.digital_read(wilson.BUTTON_1):
            random.choice(behaviour)()
        if not wilson.ss.digital_read(wilson.BUTTON_2):
            wilson.hide()  

        for entry in ble.start_scan(AdafruitColor, timeout=5):
            print(f"#{entry.color:06x}\n")

            if entry.color == 0x110000 :
                wilson.hide()
                break
            
            elif entry.color == 0x000011 :
                random.choice(behaviour)()
                break
            
            elif entry.color == 0x001100 :
                wilson.wait(1)
                wilson.wtf()
                wilson.wait(3)
                break

    ble.stop_scan()
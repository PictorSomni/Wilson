#######################################
#               IMPORTS               #
#######################################
import os
import random
from time import monotonic
import gc

# import adafruit_imageload
import analogio
import audiocore
import audiopwmio
import board
import displayio
import storage
import sdcardio

from adafruit_crickit import crickit
from adafruit_ssd1351 import SSD1351


#######################################
#                 INIT                #
#######################################
## Seesaw
ss = crickit.seesaw

## Servos
crickit.servo_1.set_pulse_width_range(min_pulse=500, max_pulse=2200)
crickit.servo_2.set_pulse_width_range(min_pulse=500, max_pulse=2200)
DELAY = 0.006
crickit.servo_1.angle = 70 # UP - DOWN
crickit.servo_2.angle = 90 # LEFT - RIGHT

## Release any resources currently in use for the displays
displayio.release_displays()

## SPI connection
spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D5
rst = board.D6
# sd_cs = DigitalInOut(board.D10)

## Random
seed = analogio.AnalogIn(board.A1)
random.seed(seed.value)
seed.deinit()

## Display
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs,
                                 reset=rst, baudrate=16000000)
display = SSD1351(display_bus, width=128, height=128, rotation=180)

## SD card
sdcard = sdcardio.SDCard(spi, board.D10)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, '/sd')

## Audio output
gc_audio = audiopwmio.PWMAudioOut(board.A0)
audio_file = None

## Motor
motor1 = crickit.dc_motor_1
motor2 = crickit.dc_motor_2

## Buttons
BUTTON_1 = crickit.SIGNAL1
BUTTON_2 = crickit.SIGNAL2
ss.pin_mode(BUTTON_1, ss.INPUT_PULLUP)
ss.pin_mode(BUTTON_2, ss.INPUT_PULLUP)


#######################################
#              FUNCTIONS              #
#######################################
def wait(wait):
    now = monotonic()
    while (monotonic() - now) < wait :
        pass


def attitude(image) :
    # bitmap, palette = adafruit_imageload.load(f"/sd/images/{image}.bmp",
    #                                       bitmap=displayio.Bitmap,
    #                                       palette=displayio.Palette)
    # tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    bitmap = displayio.OnDiskBitmap(f"/sd/images/{image}.bmp")
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
    group = displayio.Group()
    group.append(tile_grid)
    display.show(group)
    gc.collect()

def color(color = 0x000000) :
    color_bitmap = displayio.Bitmap(128, 128, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = color

    tile_grid = displayio.TileGrid(color_bitmap,
                               pixel_shader=color_palette,
                               x=0, y=0)
    group = displayio.Group()
    group.append(tile_grid)
    display.show(group)

def play_file(filename):
    audio_path = "/sd/sounds/{}".format(filename)
    files = [file for file in os.listdir(audio_path)]
    global audio_file  # pylint: disable=global-statement

    if gc_audio.playing:
        gc_audio.stop()
    if audio_file:
        audio_file.close()

    audio_file = open("{}/{}".format(audio_path, random.choice(files)), "rb")
    wav = audiocore.WaveFile(audio_file)
    gc_audio.play(wav)
    while gc_audio.playing:
        pass
    gc_audio.stop()
    audio_file.close()
    gc.collect()

def control(servo, start, end, delay=DELAY, increment=1):
    if int(end) < int(start) :
        increment = -increment
    for angle in range(int(start), int(end), increment):  # min to max degrees
        servo.angle = angle
        wait(delay)

#######################################
#               BEHAVIOR              #
#######################################
def hello():    
    attitude("nice")
    control(crickit.servo_1, crickit.servo_1.angle, 40, DELAY)
    attitude("nice")
    play_file("hello")
    attitude("happy")
    wait(1)
    control(crickit.servo_1, crickit.servo_1.angle, 70, DELAY)

def grumpy():
    attitude("what")
    control(crickit.servo_1, crickit.servo_1.angle, 40, DELAY)

    play_file("hey")
    attitude("doubt")
    control(crickit.servo_1, crickit.servo_1.angle, 40, DELAY)
    wait(1)
    control(crickit.servo_2, crickit.servo_2.angle, 50, DELAY)
    play_file("ah")
    control(crickit.servo_1, crickit.servo_1.angle, 70, DELAY)
    wait(1)
    control(crickit.servo_2, crickit.servo_2.angle, 90, DELAY)

def love():
    attitude("happy")
    control(crickit.servo_1, crickit.servo_1.angle, 40, DELAY)
    play_file("heyho")
    wait(0.5)
    attitude("love")
    play_file("hooo")
    wait(1)
    attitude("happy")
    play_file("haha")
    control(crickit.servo_1, crickit.servo_1.angle, 70, DELAY)

def dead():    
    attitude("dead")
    control(crickit.servo_1, crickit.servo_1.angle, 40, DELAY)
    play_file("ok")
    wait(1)
    control(crickit.servo_1, crickit.servo_1.angle, 70, DELAY)

def wtf():    
    attitude("small")
    control(crickit.servo_1, crickit.servo_1.angle, 40, DELAY)
    play_file("wow")
    wait(1)
    control(crickit.servo_1, crickit.servo_1.angle, 70, DELAY)

def hide():
    wait(2)
    attitude("small")
    wait(1)
    attitude("ninja")
    play_file("hum")
    wait(1)
    motor1.throttle = -1
    motor2.throttle = 1
    wait(0.5)
    motor1.throttle = 0
    motor2.throttle = 0
    wait(0.5)
    play_file("hum")
    motor1.throttle = 1
    motor2.throttle = -1
    wait(0.5)
    motor1.throttle = 0
    motor2.throttle = 0

def forward():
   motor1.throttle = -1
   motor2.throttle = 1
   wait(0.5)
   stop()

def backward():
   motor1.throttle = 1
   motor2.throttle = -1
   wait(0.5)
   stop()

def stop():
    motor1.throttle = 0
    motor2.throttle = 0

def idle():
    attitude("open")
    
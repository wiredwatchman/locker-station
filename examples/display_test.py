# Display test for the 2.42 inch SSD1309 OLED (128x64) on a Raspberry Pi Pico W.
# Requires ssd1309.py in the same folder as this file, or on the board's root.
from machine import Pin, SPI
from ssd1309 import Display
import time

# Initialize SPI
spi = SPI(0,
          baudrate=10000000,
          polarity=0,
          phase=0,
          sck=Pin(2),
          mosi=Pin(3))

# Initialize display control pins
dc = Pin(20, Pin.OUT)
cs = Pin(17, Pin.OUT)
rst = Pin(21, Pin.OUT)

# Create display instance
display = Display(spi=spi, dc=dc, cs=cs, rst=rst)

def test_pattern():
    # Clear the display
    print("Clearing display...")
    display.clear()
    display.present()
    time.sleep(2)

    # Draw frame
    print("Drawing frame...")
    display.draw_rectangle(0, 0, 127, 63, False)
    display.present()
    time.sleep(2)

    # Draw crosshairs
    print("Drawing crosshairs...")
    display.draw_line(0, 32, 127, 32, False)  # Horizontal line
    display.draw_line(64, 0, 64, 63, False)   # Vertical line
    display.present()
    time.sleep(2)

    # Draw some circles
    print("Drawing circles...")
    for r in [10, 20, 30]:
        display.draw_circle(64, 32, r, False)
        display.present()
        time.sleep(1)

# Run the test
while True:
    test_pattern()
    print("Pattern complete - restarting...")
    time.sleep(2)

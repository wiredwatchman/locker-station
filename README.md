# Locker Station

A Raspberry Pi Pico W project that runs a Wi-Fi access point and a web-based keypad for unlocking tool lockers. Each locker is driven by its own GPIO output (through a relay), and an unlock stays active for a set time before turning off automatically.

## Video

[https://youtu.be/bO4WF4EHszQ?si=DD2BQw904iKUgMGK)

## Story

The short version: the maintenance department wanted a vending machine, the budget said no, so a crew of apprentices and techs built a locker system in their free time instead. See the video above for the full story.

## Files

| File | Purpose |
| --- | --- |
| `main.py` | Main program: access point, keypad web page, locker control, cooldown, logging |
| `ssd1309.py` | MicroPython driver for the 2.42 inch SSD1309 128x64 OLED display |
| `examples/display_test.py` | Working test pattern for the 2.42 inch OLED (SPI wiring below) |
| `.gitignore` | Keeps runtime logs and editor files out of the repo |

## Parts list

Fill in quantities and part numbers for your build.

| Part | Qty | Notes |
| --- | --- | --- |
| Raspberry Pi Pico W | 1 | Runs MicroPython |
| Relay module, opto-isolated | 1 per locker | One channel per locker (up to 26) |
| 2.42 inch SSD1309 OLED, 128x64, SPI | 1 | Optional |
| 5V power supply for lock circuits | 1 | Size for total lock current |
| Jumper wire, terminal blocks | as needed | |
| Lockers / lock hardware | per locker | |

## Hardware

- Raspberry Pi Pico W
- Up to 26 relay channels (one per locker), wired to the GPIO pins in the table below
- Optional: 2.42 inch SSD1309 OLED on SPI0

### Wiring safety

- The Pico's GPIO pins are 3.3V logic and cannot power a lock directly. Drive each lock through a relay module with an optoisolator.
- Keep lock power separate from the Pico's power, and fuse the lock supply.
- Check your relay module's current rating against the lock's current draw before connecting it.
- Disconnect power before rewiring.

### Locker to GPIO map

| Locker | GPIO | Locker | GPIO |
| --- | --- | --- | --- |
| 1 | 0 | 14 | 13 |
| 2 | 1 | 15 | 14 |
| 3 | 2 | 16 | 15 |
| 4 | 3 | 17 | 16 |
| 5 | 4 | 18 | 17 |
| 6 | 5 | 19 | 18 |
| 7 | 6 | 20 | 19 |
| 8 | 7 | 21 | 20 |
| 9 | 8 | 22 | 21 |
| 10 | 9 | 23 | 22 |
| 11 | 10 | 24 | 26 |
| 12 | 11 | 25 | 27 |
| 13 | 12 | 26 | 28 |

### OLED wiring (SPI0, as used in `display_test.py`)

| Signal | Pico pin |
| --- | --- |
| SCK | GP2 |
| MOSI | GP3 |
| CS | GP17 |
| DC | GP20 |
| RST | GP21 |

## Setup

1. Flash MicroPython onto the Pico W.
2. Copy `main.py` and `ssd1309.py` to the board's root (`main.py` runs automatically on boot).
3. Connect to the `JosephLockerStation` Wi-Fi network and open `http://192.168.4.1` in a browser.
4. Enter a valid code on the keypad, then press a locker button.

## Before you publish or deploy

- **Change the access codes.** The `valid_codes` dictionary in `main.py` holds the PIN codes and their user names. Replace them with your own.
- **Change the access point password.** `ap_password` in `main.py` is a placeholder. Use something stronger.
- Do not commit real codes or passwords to a public repository.

## Notes

- Each locker has a 15 second cooldown between authorized activations, and it resets 12 seconds after it is opened.
- Every attempt is logged to `code_entries.txt` on the Pico's flash storage with a timestamp, the code used, the locker, and whether it succeeded.
- The OLED driver is included and tested with `examples/display_test.py`. It is not yet wired into `main.py`.

## License

Add a license file before making the repository public (for example, MIT).

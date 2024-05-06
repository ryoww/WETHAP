import mip
import network
from utime import sleep_ms

import env


def install_requirements():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)

    count = 1
    while not wifi.isconnected() and count <= env.ATTEMPTS:
        print(f"WiFi connecting. Attempt {count}.")
        if wifi.status() != network.STAT_CONNECTING:
            wifi.connect(env.SSID, env.PASSWORD)
        sleep_ms(env.WIFI_DELAY)
        count += 1
    print("wifi connected")
    mip.install("ssd1306")
    print("requirements packages installed")

    wifi.disconnect()

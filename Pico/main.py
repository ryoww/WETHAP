from bme680 import *
from machine import I2C, Pin
import time
import urequests
import network
import json
import machine
import ntptime
import ssd1306


led = machine.Pin("LED", machine.Pin.OUT)
led.off()

# ssd1306初期化
try:
    display_i2c = I2C(1, sda=Pin(18), scl=Pin(19))
    time.sleep_ms(100)
    display = ssd1306.SSD1306_I2C(128, 64, display_i2c)
except:
    is_display = False
else:
    # ssd1306接続フラグ
    is_display = True
if is_display:
    display.fill(0)
    display.text("WETHAP", 40, 0)
    display.hline(0, 10, 128, 1)
    display.text("Hello World!", 17, 33)
    display.rect(5, 20, 118, 35, 1)
    display.show()

    time.sleep(1)
    display.fill(0)
    display.text("booting...", 24, 0)
    display.hline(0, 9, 128, 1)
    display.show()

# bme680初期化
try:
    bme_i2c = I2C(0, sda=Pin(0), scl=Pin(1))
    time.sleep_ms(100)
    bme = BME680_I2C(bme_i2c)
except Exception as error:
    if is_display:
        display.text("bme680 error", 16, 11)
        display.show()
    raise error
else:
    if is_display:
        display.text("bme680 connect", 8, 11)
        display.show()


# 定数定義
lab_id = "テストT"
url = "https://adelppi.duckdns.org/addInfo"
finish_time = ("09:25","10:10", "11:10", "11:55", "13:30", "14:15", "15:15", "16:00", "17:00", "17:45", "18:45", "19:30")

ssid = "************"
password = "********"

# wifi初期化
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
if is_display:
    display.text("wifi activate", 12, 22)
    display.text("connecting...", 12, 33)
    display.show()
# wifi接続待機
max_wait = 30
for i in range(max_wait):
    time.sleep(1)
    if wlan.isconnected():
        print("online")
        if is_display:
            display.text("wifi connect", 16, 44)
            display.show()
        break
else:
    print("offline")
    if is_display:
        display.text("connect failed", 8, 44)
        display.show()
    raise Exception("WiFi connect failed")

rtc = machine.RTC()
timZone = 9
ntptime.host = "ntp.nict.jp"
# 起動時初期化フラグ
is_init = False

# ポストフラグ
is_post = False
# 時間更新フラグ
is_time = False

while True:
    t0 = machine.RTC().datetime()

    # 内部時計更新
    if not is_init or (t0[5] == 0 and not is_time):
        try:
            ntptime.settime()
        except:
            print("failed to update real-time clock")
            if is_display:
                display.fill(0)
                display.text("time update", 20, 24)
                display.text("failed", 44, 32)
                display.show()
        else:
            t0 = machine.RTC().datetime()
            is_time = True
            if not is_init:
                is_init = True
                print("initialize complete")
            print("real-time clock updated")
            if is_display:
                display.fill(0)
                display.text("time update", 20, 24)
                display.text("success", 36, 32)
                display.show()
    if t0[5] != 0 and is_time:
        is_time = False

    # 起動時初期化完了で点灯
    if is_init:
        led.on()

    hour = t0[4] + timZone
    day = t0[2]

    if hour >= 24:
        hour -= 24
        day += 1

    print(t0)
    print(f"Temp:{bme.temperature:.3g}C, Humidity:{bme.humidity:.3g}%, Pressure:{bme.pressure:.5g}hPa, Gas:{bme.gas}")
    print(f"{t0[0]}-{t0[1]}-{day} {hour}:{t0[5]}:{t0[6]}")

    # 取得データ表示
    # NOTE: 此処の処理でループ時間約2秒増加
    if is_display:
        display.fill(0)
        display.show()
        display.text(f"{t0[0]}-{t0[1]:02d}-{day:02d}", 24, 0)
        display.text(f"{hour:02d}:{t0[5]:02d}:{t0[6]:02d}", 32, 10)
        display.hline(0, 20, 128, 1)
        display.text(f"Temp:{bme.temperature:.3g}C", 24, 22)
        display.text(f"Hmd.:{bme.humidity:.3g}%", 24, 33)
        display.text(f"Pres.:{bme.pressure:.5g}hPa", 4, 44)
        display.text(f"Gas:{bme.gas}", 20, 55)
        display.show()

    nowtime = f"{hour:02d}:{t0[5]:02d}"

    sec = t0[6]
    # print(sec)

    if is_init and nowtime in finish_time and not is_post:
        is_post = True
        data = {
            "labID": lab_id,
            "date": f"{t0[0]}-{t0[1]:02d}-{day:02d}",
            "numGen": int(finish_time.index(nowtime)) + 1,
            "temperature": f"{bme.temperature:.2f}",
            "humidity": f"{bme.humidity:.3f}",
            "pressure": f"{bme.pressure:.2f}",
        }

        led.off()
        response = urequests.post(url, data=json.dumps(data).encode("unicode_escape"), headers={"Content-Type": "application/json"})

        print(data["labID"])
        print(response.status_code)
        print(response.content)

        if is_display:
            if response.status_code == 200:
                display.fill(0)
                display.text("post:success", 16, 0)
                display.hline(0, 9, 128, 1)
                display.text(f'date:{data["date"]}', 4, 11)
                display.text(f'numGen:{data["numGen"]}', (72-len(str(data["numGen"]))*8)//2, 22)
                display.text(f'Temp:{data["temperature"]}C', (80-len(data["temperature"])*8)//2, 33)
                display.text(f'Hmd.:{data["humidity"]}%', (80-len(data["humidity"])*8)//2, 44)
                display.text(f'Pres.:{data["pressure"]}hPa', (56-len(data["pressure"])*8)//2, 55)
                display.show()
            else:
                display.fill(0)
                display.text("post failed", 20, 24)
                display.text(f"with {response.status_code}", (88-len(str(response.status_code))*8)//2, 32)
                display.show()

        time.sleep(1)
        led.on()

    if is_post and nowtime not in finish_time:
        is_post = False

    time.sleep(1)

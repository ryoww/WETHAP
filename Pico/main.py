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
    display = ssd1306.SSD1306_I2C(128, 64, I2C(1, sda=Pin(18), scl=Pin(19)))
except:
    is_display = False
    loop_time = 3
else:
    # ssd1306接続判定用
    is_display = True
    loop_time = 5
if is_display:
    display.fill(0)
    display.text("WETHAP", 40, 0)
    display.text("Hello World!", 17, 33)
    display.hline(0, 10, 128, 1)
    display.rect(5, 20, 118, 35, 1)
    display.show()

    time.sleep(1)
    display.fill(0)
    display.text("booting...", 24, 0)
    display.hline(0, 9, 128, 1)
    display.show()

# bme680初期化
try:
    bme = BME680_I2C(I2C(0, scl=Pin(1), sda=Pin(0)))
except Exception as err:
    if is_display:
        display.text("bme680 error", 16, 11)
        display.show()
    raise err
else:
    if is_display:
        display.text("bme680 connect", 8, 11)
        display.show()


# 定数定義
labID = "テストT"
url = "https://adelppi.duckdns.org/addInfo"
finish_time = ["09:25","10:10", "11:10", "11:55", "13:30", "14:15", "15:15", "16:00", "17:00", "17:45", "18:45", "19:30", "20:48"]

ssid = '************'
password = '********'

# wifi初期化
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
if wlan.active():
    if is_display:
        display.text("wifi activate", 8, 22)
        display.text("connecting...", 12, 33)
        display.show()
else:
    if is_display:
        display.text("wifi error", 24, 22)
        display.show()
    raise Exception
# wifi接続待機
max_wait = 60
for i in range(max_wait):
    time.sleep(1)
    if wlan.isconnected():
        break
if i < max_wait - 1:
    if is_display:
        display.text("wifi connect", 14, 44)
        display.show()
else:
    if is_display:
        display.text("offline", 36, 44)
        display.show()
    raise Exception


rtc = machine.RTC()
timZone = 9
ntptime.host = "ntp.nict.jp"
# 時計初回更新フラグ
is_init = False


while True:
    # 時計更新
    # 起動後更新成功するまでと1時間に1回更新実行
    t0 = machine.RTC().datetime()
    if (not is_init) or (t0[5] == 0 and t0[6] == 0):
        try:
            ntptime.settime()
        except:
            if is_display:
                display.fill(0)
                display.text("time update", 20, 24)
                display.text("faild", 44, 32)
                display.show()
        else:
            t0 = machine.RTC().datetime()
            is_init = True
            if is_display:
                display.fill(0)
                display.text("time update", 20, 24)
                display.text("succeed", 36, 32)
                display.show()

    # セットアップ完了で点灯
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
    # NOTE: 此処の処理でループ時間約1秒増加してる
    if is_display:
        display.fill(0)
        display.show()
        display.text(f"{t0[0]}-{t0[1]:02d}-{day:02d}", 24, 0)
        time_disp = f"{hour:02d}:{t0[5]:02d}:{t0[6]:02d}"
        display.text(time_disp, (128-len(time_disp)*8)//2, 10)
        display.hline(0, 20, 128, 1)
        display.text(f"Temp:{bme.temperature:.3g}C", 24, 22)
        display.text(f"Hmd.:{bme.humidity:.3g}%", 24, 33)
        display.text(f"Pres.:{bme.pressure:.5g}hPa", 4, 44)
        display.text(f"Gas:{bme.gas}", 20, 55)
        display.show()

    nowtime = f"{hour:02d}:{t0[5]:02d}"

    sec = t0[6]
    # print(sec)

    if is_init and nowtime in finish_time and sec in range(loop_time):
        data = {
            "labID": labID,
            "date": f"{t0[0]}-{t0[1]:02d}-{day:02d}",
            "numGen": int(finish_time.index(nowtime)) + 1,
            "temperature": f"{bme.temperature:.2f}",
            "humidity": f"{bme.humidity:.3f}",
            "pressure": f"{bme.pressure:.2f}",
        }

        print(data["labID"])

        response = urequests.post(url, data=json.dumps(data).encode("unicode_escape"), headers={"Content-Type": "application/json"})

        print(f"{response.status_code}")
        print(f"{response.content}")

        if is_display:
            if response.status_code == 200:
                display.fill(0)
                display.text('post:succeed', 8, 0)
                display.hline(0, 9, 128, 1)
                display.text(f'date:{data["date"]}', 4, 11)
                display.text(f'numGen:{data["numGen"]}', (128-len(str(data["numGen"]))*8-56)//2, 22)
                display.text(f'Temp:{data["temperature"]}C', (128-len(data["temperature"])*8-48)//2, 33)
                display.text(f'Hmd.:{data["humidity"]}%', (128-len(data["humidity"])*8-48)//2, 44)
                display.text(f'Pres.:{data["pressure"]}hPa', (128-len(data["pressure"])*8-72)//2, 55)
                display.show()
            else:
                display.fill(0)
                display.text("post failed", 20, 24)
                display.text(f"with {response.status_code}", 32, 32)
                display.show()

        led.off()
        time.sleep(1)
        led.on()

    time.sleep(1)

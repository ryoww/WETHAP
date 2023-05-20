import json
import time

import network
import ntptime
import urequests
from bme680 import BME680_I2C
from display_manager import DisplayManager
from env_collector import EnvCollector
from machine import I2C, RTC, Pin


def update_time(rtc, url):
    """内部時計を更新
    Args:
        rtc (RTC): RTCオブジェクト
        url (str): 現在時間取得用APIのURL
    """
    try:
        response = urequests.get(url)
    except:
        return False

    if response.status_code == 200:
        data = response.json()
        ymd, time = data["utc_datetime"].split("T")
        year, month, day = list(map(int, ymd.split("-")))
        hour, minute, seconds = time.split("+")[0].split(":")
        second, second_sub = list(map(int, seconds.split(".")))
        week = data["day_of_week"]

        rtc.datetime((year, month, day, week, int(hour), int(minute), second, second_sub))
        return True
    else:
        return False


# 定数定義
LAB_ID = "T4教室"
URL = "https://adelppi.duckdns.org/addInfo"
TIME_URL = "https://worldtimeapi.org/api/ip"
NTP_URL = "ntp.nict.jp"
FINISH_TIME = ("09:25", "10:10", "11:10", "11:55", "13:30", "14:15", "15:15", "16:00", "17:00", "17:45", "18:45", "19:30")
DEBUG_TIME = ("21:00", "00:00", "08:00")

SSID = "************"
PASSWORD = "********"

i2c = I2C(1, sda=Pin(14), scl=Pin(15))
dht = Pin(13, Pin.IN, Pin.PULL_UP)

led = Pin("LED", Pin.OUT)
led.off()

# ssd1306初期化
display = DisplayManager(i2c)
display.add_text("WETHAP", new=True).line()
if display.display:
    display.display.rect(5, 20, 118, 35, 1)
display.add_text("Hello World!", 3).show()

time.sleep(1)
display.add_text("booting...", new=True).line().show(False)

# センサー初期化
try:
    collector = EnvCollector(i2c)
except:
    print("bme680 error")
    try:
        collector = EnvCollector(dht)
    except:
        print("dht11 error")
        display.multi_text("no sensor detect")
        raise Exception("No sensor detect")
    else:
        print("dht11 connect")
        display.add_text("dht11 connect").show(False)
else:
    print("bme680 connect")
    display.add_text("bme680 connect").show(False)

# 起動時初期化フラグ
is_init = False
# WiFi接続フラグ
is_online = False
# ポストフラグ
is_post = False
# 時間更新フラグ
is_time = False

# wifi初期化
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
display.add_text("wifi activate")
display.add_text("connecting...").show(False)
# wifi接続待機
max_wait = 30
for i in range(max_wait):
    time.sleep(1)
    if wlan.isconnected():
        is_online = True
        print("online")
        display.add_text("wifi connect").show(False)
        break
else:
    print("offline")
    display.multi_text("wifi connect", "failed")
    raise Exception("WiFi connect failed")

rtc = RTC()
timeZone = 9
ntptime.host = NTP_URL

try:
    while True:
        # WiFi再接続
        if not wlan.isconnected():
            led.off()
            is_online = False
            print("offline detect")
            display.multi_text("offline detect")
            wlan.connect(SSID, PASSWORD)
            for i in range(max_wait):
                time.sleep(1)
                if wlan.isconnected():
                    led.on()
                    is_online = True
                    print("reconnect")
                    display.multi_text("reconnect")
                    break
            else:
                print("offline")
                display.multi_text("wifi reconnect", "failed")

        t0 = rtc.datetime()

        # 内部時計更新
        if (not is_init or (t0[5] == 0 and not is_time)) and is_online:
            try:
                ntptime.settime()
            except:
                print("clock update by NTP failed")
                if update_time(rtc, TIME_URL):
                    t0 = rtc.datetime()
                    is_time = True
                    if not is_init:
                        is_init = True
                        print("initialize complete")
                    print("clock update by API success")
                    display.multi_text("time update", "success")
                else:
                    print("clock update by API failed")
                    display.multi_text("time update", "failed")
            else:
                t0 = rtc.datetime()
                is_time = True
                if not is_init:
                    is_init = True
                    print("initialize complete")
                print("clock update by NTP success")
                print(t0)
                display.multi_text("time update", "success")
        if t0[5] != 0 and is_time:
            is_time = False

        # 正常稼働通知
        if is_init and is_online:
            led.on()

        hour = t0[4] + timeZone
        day = t0[2]

        if hour >= 24:
            hour -= 24
            day += 1

        envs = collector.get_env()
        print(t0)
        print(f'Temp:{envs["temperature"]:.3f}C, Humidity:{envs["humidity"]:.3f}%, Pressure:{envs["pressure"]:.5g}hPa, Gas:{envs["gas"]}')
        print(f"{t0[0]}-{t0[1]}-{day} {hour}:{t0[5]}:{t0[6]}")

        # 取得データ表示
        # NOTE: ループ時間増加
        display.clear()
        time.sleep_ms(100)
        display.add_text(f"{t0[0]}-{t0[1]:02d}-{day:02d}", new=True)
        display.add_text(f"{hour:02d}:{t0[5]:02d}:{t0[6]:02d}").line()
        display.add_text(f'Temp:{envs["temperature"]:.3f}C')
        display.add_text(f'Hmd.:{envs["humidity"]:.3f}%')
        display.add_text(f'Pres.:{envs["pressure"]:.5g}hPa')
        display.add_text(f'Gas:{envs["gas"]}').show()

        nowtime = f"{hour:02d}:{t0[5]:02d}"

        sec = t0[6]

        if is_init and is_online and nowtime in FINISH_TIME and not is_post:
            data = {
                "labID": LAB_ID,
                "date": f"{t0[0]}-{t0[1]:02d}-{day:02d}",
                "numGen": int(FINISH_TIME.index(nowtime)) + 1,
                "temperature": f'{envs["temperature"]:.2f}',
                "humidity": f'{envs["humidity"]:.3f}',
                "pressure": f'{envs["pressure"]:.2f}',
            }

            led.off()
            display.multi_text("posting...")
            try:
                response = urequests.post(URL, data=json.dumps(data).encode("unicode_escape"), headers={"Content-Type": "application/json"})
            except:
                print("post failed")
                display.multi_text("post failed")
            else:
                is_post = True
                print(data["labID"])
                print(response.status_code)
                print(response.content)

                if response.status_code == 200:
                    display.add_text("post:success", new=True).line()
                    display.add_text(f'date:{data["date"]}')
                    display.add_text(f'numGen:{data["numGen"]}')
                    display.add_text(f'Temp:{data["temperature"]}C')
                    display.add_text(f'Hmd.:{data["humidity"]}%')
                    display.add_text(f'Pres.:{data["pressure"]}hPa').show()
                else:
                    display.multi_text("post failed", f"with {response.status_code}")

            time.sleep(1)
            led.on()

    #     if is_post and nowtime not in FINISH_TIME:
    #         is_post = False

        if is_init and is_online and nowtime in DEBUG_TIME and not is_post:
            data = {
                "labID": LAB_ID,
                "date": f"{t0[0]}-{t0[1]:02d}-{day:02d}",
                "numGen": int(DEBUG_TIME.index(nowtime)) + 20,
                "temperature": f'{envs["temperature"]:.2f}',
                "humidity": f'{envs["humidity"]:.3f}',
                "pressure": f'{envs["pressure"]:.2f}',
            }

            led.off()
            display.multi_text("posting...")
            try:
                response = urequests.post(URL, data=json.dumps(data).encode("unicode_escape"), headers={"Content-Type": "application/json"})
            except:
                print("post failed")
                display.multi_text("post failed")
            else:
                is_post = True
                print(data["labID"])
                print(response.status_code)
                print(response.content)

                if response.status_code == 200:
                    display.add_text("test:success", new=True).line()
                    display.add_text(f'date:{data["date"]}')
                    display.add_text(f'numGen:{data["numGen"]}')
                    display.add_text(f'Temp:{data["temperature"]}C')
                    display.add_text(f'Hmd.:{data["humidity"]}%')
                    display.add_text(f'Pres.:{data["pressure"]}hPa').show()
                else:
                    display.multi_text("post failed", f"with {response.status_code}")
            time.sleep(1)
            led.on()
        if is_post and nowtime not in DEBUG_TIME and nowtime not in FINISH_TIME:
            is_post = False
        time.sleep(1)
except Exception as err:
    print(err)
    display.split_text(err)

import json

import network
import ntptime
import urequests
import utime
from machine import ADC, I2C, RTC, Pin, reset

from display_manager import DisplayManager
from env_collector import EnvCollector


def update_time(rtc: RTC, url: str) -> bool:
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
        data: dict[str, str] = response.json()
        ymd, time = data["utc_datetime"].split("T")
        year, month, day = list(map(int, ymd.split("-")))
        hour, minute, seconds = time.split("+")[0].split(":")
        second, second_sub = list(map(int, seconds.split(".")))
        week = data["day_of_week"]

        rtc.datetime(
            (year, month, day, week, int(hour), int(minute), second, second_sub)
        )
        return True
    else:
        return False


# 定数定義
LAB_ID: str = "T4教室"
URL: str = "https://adelppi.duckdns.org/addInfo"
TIME_URL: str = "https://worldtimeapi.org/api/ip"
NTP_URL: str = "ntp.nict.jp"
FINISH_TIME: tuple[str] = (
    "09:25",
    "10:10",
    "11:10",
    "11:55",
    "13:30",
    "14:15",
    "15:15",
    "16:00",
    "17:00",
    "17:45",
    "18:45",
    "19:30",
)
TIMEZONE: int = 9
TEMP_ADJ_RANGE: int = 15
HUMID_ADJ_RANGE: int = 30

SSID: str = "************"
PASSWORD: str = "********"

i2c = I2C(1, sda=Pin(14, pull=Pin.PULL_UP), scl=Pin(15, pull=Pin.PULL_UP))
dht = Pin(13, Pin.IN, Pin.PULL_UP)
temp_adj = ADC(0)
humid_adj = ADC(1)

led = Pin("LED", Pin.OUT, value=True)

# ssd1306初期化
display = DisplayManager(i2c)
display.add_text("WETHAP", new=True).line()
if display.display:
    display.display.rect(5, 20, 118, 35, 1)
display.add_text("Hello World!", 3).show()

utime.sleep(1)
led.off()
display.add_text("booting...", new=True).line().show(False)

# センサー初期化
try:
    collector = EnvCollector(i2c)
except:
    display.multi_text("no sensor detect")
    raise RuntimeError("No sensor detect")
else:
    if "DHT20" in collector.sensors:
        print("DHT20 connect")
        display.add_text("DHT20 connect").show(False)
        try:
            collector.add_sub_sensor(i2c)
        except:
            print("LPS25HB not connect")
            display.add_text("no sub sensor").show(False)
        else:
            print("LS25HB connect")
            display.add_text("LPS25HB connect").show(False)
    else:
        print("BME680 connect")
        display.add_text("BME680 connect").show(False)

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
max_wait = 60
for i in range(max_wait):
    utime.sleep(1)
    if wlan.isconnected():
        is_online = True
        print("online")
        display.add_text("wifi connect").show(False)
        break
else:
    print("offline")
    display.multi_text("wifi connect", "failed")
    raise RuntimeError("WiFi connect failed")

rtc = RTC()
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
                utime.sleep(1)
                if wlan.isconnected():
                    led.on()
                    is_online = True
                    print("reconnect")
                    display.multi_text("reconnect")
                    break
            else:
                print("offline")
                display.multi_text("wifi reconnect", "failed")

        now = rtc.datetime()

        # 内部時計更新
        if (not is_init or (now[5] == 0 and not is_time)) and is_online:
            try:
                ntptime.settime()
            except:
                print("clock update by NTP failed")
                if update_time(rtc, TIME_URL):
                    now = rtc.datetime()
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
                now = rtc.datetime()
                is_time = True
                if not is_init:
                    is_init = True
                    print("initialize complete")
                print("clock update by NTP success")
                print(now)
                display.multi_text("time update", "success")
        if now[5] != 0 and is_time:
            is_time = False

        # 正常稼働通知
        if is_init and is_online:
            led.on()

        hour = now[4] + TIMEZONE
        day = now[2]

        if hour >= 24:
            hour -= 24
            day += 1

        led.off()
        envs = collector.get_env()
        temp_offset = (temp_adj.read_u16() / 65535 - 0.5) * 2 * TEMP_ADJ_RANGE
        humid_offset = (humid_adj.read_u16() / 65535 - 0.5) * 2 * HUMID_ADJ_RANGE
        print(temp_offset)
        print(humid_offset)
        envs["temperature"] += temp_offset
        envs["humidity"] += humid_offset
        led.on()
        print(now)
        print(
            f'Temp:{envs["temperature"]:.3f}C, Humidity:{envs["humidity"]:.3f}%, Pressure:{envs["pressure"]:.5g}hPa, Gas:{envs["gas"]}'
        )
        print(f"{now[0]}-{now[1]}-{day} {hour}:{now[5]}:{now[6]}")

        # 取得データ表示
        # NOTE: ループ時間増加
        display.clear()
        utime.sleep_ms(100)

        display.multi_text(
            f"{now[0]}-{now[1]:02d}-{day:02d}",
            f"{hour:02d}:{now[5]:02d}:{now[6]:02d}",
            f'Temp:{envs["temperature"]:.3f}C',
            f'Hmd.:{envs["humidity"]:.3f}%',
            f'Pres.:{envs["pressure"]:.5g}hPa',
            lines=[2],
        )

        now_time = f"{hour:02d}:{now[5]:02d}"

        if is_init and is_online and now_time in FINISH_TIME and not is_post:
            data: dict[str, str | int] = {
                "labID": LAB_ID,
                "date": f"{now[0]}-{now[1]:02d}-{day:02d}",
                "numGen": int(FINISH_index(now_time)) + 1,
                "temperature": f'{envs["temperature"]:.2f}',
                "humidity": f'{envs["humidity"]:.3f}',
                "pressure": f'{envs["pressure"]:.2f}',
            }

            led.off()
            display.multi_text("posting...")
            try:
                response = urequests.post(
                    URL,
                    data=json.dumps(data).encode("unicode_escape"),
                    headers={"Content-Type": "application/json"},
                )
            except:
                print("post failed")
                display.multi_text("post failed")
            else:
                print(data["labID"])
                print(response.status_code)
                print(response.content)

                if response.status_code == 200:
                    is_post = True
                    display.add_text("post:success", new=True).line()
                    display.add_text(f'date:{data["date"]}')
                    display.add_text(f'numGen:{data["numGen"]}')
                    display.add_text(f'Temp:{data["temperature"]}C')
                    display.add_text(f'Hmd.:{data["humidity"]}%')
                    display.add_text(f'Pres.:{data["pressure"]}hPa').show()
                else:
                    display.multi_text("post failed", f"with {response.status_code}")
            led.on()

        if is_post and now_time not in FINISH_TIME:
            is_post = False

        utime.sleep(1)

except Exception:
    reset()

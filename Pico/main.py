from bme680 import *
from machine import I2C, Pin
import time
import urequests
import network
import json
import machine
import ntptime
import ssd1306


class DisplayManager:
    """ssd1306表示処理をまとめたクラス
    Args:
        i2c (I2C): I2Cオブジェクト
        margin (int, optional): 文字間のマージン量
    """
    def __init__(self, i2c, margin=3):
        self.grid = 8
        self.margin = margin
        self.current = 0
        try:
            self.display = ssd1306.SSD1306_I2C(128, 64, i2c)
        except:
            self.display = None
            print("ssd1306 not connect")
        else:
            print("ssd1306 connected")

    def clear(self):
        """無表示化
        """
        if self.display:
            self.current = 0
            self.display.fill(0)
            self.display.show()
        return self

    def add_text(self, text, row=None, new=False):
        """表示行追加
        Args:
            text (str): 表示させるテキスト
            row (int, optional): 表示行を指定 未指定で次の行に追加
            new (bool, optional): Trueで新規 Falseで追加モード
        """
        if self.display:
            if new:
                self.display.fill(0)
                self.current = 0
            write = row if row else self.current
            self.display.text(text, (128-len(text)*self.grid)//2, write*(self.grid+self.margin))
            self.current = write + 1
        return self

    def multi_text(self, *texts):
        """複数行を中央揃えで表示
        Args:
            (str): 表示するテキストを入力 複数入力可
        """
        if self.display:
            self.display.fill(0)
            if len(texts) % 2 == 0:
                self.current = (6 - len(texts)) // 2
                print(self.current)
                [self.add_text(text) for text in texts]
            else:
                char = self.grid+self.margin
                pos = ((64+char)-char*len(texts))//2
                [self.display.text(text, (128-len(text)*self.grid)//2, pos+char*i) for i, text in enumerate(texts)]
            self.display.show()
            self.current = 0
        return self

    def line(self, row=None):
        """現在の表示行の下に線を追加
        Args:
            row (int, optional): 表示行を指定 未指定で次の行に追加
        """
        if self.display:
            write = row if row else self.current - 1
            self.display.hline(0, (write+1)*(self.grid+self.margin//2), 128, 1)
        return self

    def show(self, new=True):
        """描画更新
        Args:
            new (bool, optional): Trueで描画後現在行を初期化 Falseで描画後現在行を初期化しない
        """
        if self.display:
            if new:
                self.current = 0
            self.display.show()
        return self


def update_time(rtc, url):
    """内部時計を更新
    Args:
        rtc (RTC): RTCオブジェクト
        url (str): 現在時間取得用APIのURL
    """
    response = urequests.get(url)

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


led = machine.Pin("LED", machine.Pin.OUT)
led.off()

# ssd1306初期化
display_i2c = I2C(1, sda=Pin(18), scl=Pin(19))
display = DisplayManager(display_i2c)
display.add_text("WETHAP", new=True).line()
if display.display:
    display.display.rect(5, 20, 118, 35, 1)
display.add_text("Hello World!", 3).show()

time.sleep(1)
display.add_text("booting...", new=True).line().show(False)

# bme680初期化
try:
    bme_i2c = I2C(0, sda=Pin(0), scl=Pin(1))
    bme = BME680_I2C(bme_i2c)
except Exception as error:
    display.multi_text("bme680 error")
    raise error
else:
    display.add_text("bme680 connect").show(False)

# 定数定義
lab_id = "T4教室"
url = "https://adelppi.duckdns.org/addInfo"
time_url = "https://worldtimeapi.org/api/ip"
finish_time = ("09:25", "10:10", "10:22", "11:10", "11:55", "13:30", "14:15", "15:15", "16:00", "17:00", "17:45", "18:45", "19:30")

ssid = "************"
password = "********"

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
wlan.connect(ssid, password)
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
    display.multi_text("connect failed")
    raise Exception("WiFi connect failed")

rtc = machine.RTC()
timeZone = 9
ntptime.host = "ntp.nict.jp"

while True:
    # WiFi再接続
    if not wlan.isconnected():
        led.off()
        is_online = False
        print("offline detect")
        display.multi_text("offline detect")
        wlan.connect(ssid, password)
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
            display.multi_text("reconnect failed")

    t0 = rtc.datetime()

    # 内部時計更新
    if (not is_init or (t0[5] == 0 and not is_time)) and is_online:
        try:
            ntptime.settime()
        except:
            print("clock update by NTP failed")
            if update_time(rtc, time_url):
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

    print(t0)
    print(f"Temp:{bme.temperature:.3g}C, Humidity:{bme.humidity:.3g}%, Pressure:{bme.pressure:.5g}hPa, Gas:{bme.gas}")
    print(f"{t0[0]}-{t0[1]}-{day} {hour}:{t0[5]}:{t0[6]}")

    # 取得データ表示
    # NOTE: ループ時間増加
    display.clear()
    display.add_text(f"{t0[0]}-{t0[1]:02d}-{day:02d}", new=True)
    display.add_text(f"{hour:02d}:{t0[5]:02d}:{t0[6]:02d}").line()
    display.add_text(f"Temp:{bme.temperature:.3g}C")
    display.add_text(f"Hmd.:{bme.humidity:.3g}%")
    display.add_text(f"Pres.:{bme.pressure:.5g}hPa")
    display.add_text(f"Gas:{bme.gas}").show()

    nowtime = f"{hour:02d}:{t0[5]:02d}"

    sec = t0[6]
    # print(sec)

    if is_init and is_online and nowtime in finish_time and not is_post:
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

    if is_post and nowtime not in finish_time:
        is_post = False

    time.sleep(1)

from bme680 import *
from machine import I2C, Pin
import time
import urequests
import network
import socket
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
    loop_time = 4
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
if is_display:
    if wlan.active():
        display.text("wifi activate", 8, 22)
        display.text("connecting...", 12, 33)
        display.show()
    else:
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
    display.text("wifi connect", 14, 44)
    display.show()
else:
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
                display.text("successed", 28, 32)
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
    # print("{}".format(rtc.datetime()))
    print("Temp:{:.3g}C, Humidity:{:.3g}%, Pressure:{:.5g}hPa, Gas:{}".format(bme.temperature, bme.humidity, bme.pressure, bme.gas))
    print("{}-{}-{} {}:{}:{}".format(t0[0], t0[1], day, hour, t0[5], t0[6]))

    # 取得データ表示
    # NOTE: 此処の処理でループ時間約1秒増加してる
    if is_display:
        display.fill(0)
        display.text(f"{t0[0]}-{t0[1]:02d}-{day:02d}", 24, 0)
        time_disp = f"{hour:02d}:{t0[5]:02d}:{t0[6]:02d}"
        display.text(time_disp, (128-len(time_disp)*8)//2, 10)
        display.hline(0, 20, 128, 1)
        display.text(f"Temp:{bme.temperature:.3g}C", 24, 22)
        display.text(f"Hmd.:{bme.humidity:.3g}%", 24, 33)
        display.text(f"Pres.:{bme.pressure:.5g}hPa", 4, 44)
        display.text(f"Gas:{bme.gas}", 20, 55)
        display.show()

    # data = {}

    #    year = now[0]
    #    month = now[1]
    #    day = now[2]
    # sec = now[5]

    # nowtime = ("{:02d}:{:02d}".format(rtc.datetime()[4],rtc.datetime()[5]))
    nowtime = "{:02d}:{:02d}".format(hour, t0[5])
    # print(now)

    sec = t0[6]
    print(sec)

    # if sec % 5 == 0:
    # if nowtime in finish_time and sec in [0, 1]:
    if is_init and nowtime in finish_time and sec in range(loop_time):
        #    print("success")
        # if nowtime in finish_time and rtc.datetime()[6] in [0,1]:
        # wesult = requests.get("https://weathernews.jp/onebox/35.731350/139.798464/q=%E5%8D%97%E5%8D%83%E4%BD%8F%EF%BC%88%E6%9D%B1%E4%BA%AC%E9%83%BD%EF%BC%89&v=e8be546f5505407d1788791e7e7b3b0c15fbfd38af41f3dab5a6d2b88cb74d84&temp=c&lang=ja")

        # soup = BeautifulSoup(result.text,"html.parser")

        # tags = soup.find("ul",class_="weather-now__ul")
        # p_tit_tags = tags.li.text

        # weather = p_tit_tags

        data = {
            "labID": labID,
            # "time"        : "{}-{}-{} {}:{}:{}".format(t0[0], t0[1], day, hour, t0[5], t0[6]),
            # "date"        : "{}-{}-{} {}:{}:{}".format(t0[0], t0[1], day, hour, t0[5], t0[6]),
            # "date"        : "{}-{:02d}-{:02d}".format(year,month,day),
            # "date"        : "{}-{}-{}".format(t0[0],t0[1],day),
            "date": f"{t0[0]}-{t0[1]:02d}-{day:02d}",
            "numGen"      : int(finish_time.index(nowtime)) + 1,
            # "numGen": 1,
            "temperature": f"{bme.temperature:.2f}",
            "humidity": f"{bme.humidity:.3f}",
            "pressure": f"{bme.pressure:.2f}",
        }

        # URL = (url,data=ujson.dumps(data))
        # print(URL)

        print(data["labID"])

        response = urequests.post(url, data=json.dumps(data).encode("unicode_escape"), headers={"Content-Type": "application/json"})

        print("{}".format(response.status_code))
        print("{}".format(response.content))

        if is_display:
            if response.status_code == 200:
                display.fill(0)
                display.text('post:successed', 8, 0)
                display.hline(0, 9, 128, 1)
                display.text(f'date:{data["date"]}', 4, 11)
                display.text(f'numGen:{data["numGen"]}', (128-len(str(data["numGen"]))*8-56)//2, 22)
                display.text(f'Temp:{data["temperature"]}C', (128-len(data["temperature"])*8-48)//2, 33)
                display.text(f'Hmd.:{data["humidity"]}%', (128-len(data["humidity"])*8-48)//2, 44)
                display.text(f'Pres.:{data["pressure"]}hPa', (128-len(data["pressure"])*8-72)//2, 55)
                display.show()
            else:
                display.fill(0)
                display.text("post faild", 20, 24)
                display.text("with {response.status_code}", 32, 32)
                display.show()

        led.off()
        time.sleep(1)
        led.on()

    time.sleep(1)

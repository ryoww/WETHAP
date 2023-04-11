#!/usr/bin/env python

import bme680
import time
import requests
from datetime import datetime
import pprint
from bs4 import BeautifulSoup

print("""read-all.py - Displays temperature, pressure, humidity, and gas.

Press Ctrl+C to exit!

""")

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
except (RuntimeError, IOError):
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)

# These calibration data can safely be commented
# out, if desired.

print('Calibration data:')
for name in dir(sensor.calibration_data):

    if not name.startswith('_'):
        value = getattr(sensor.calibration_data, name)

        if isinstance(value, int):
            print('{}: {}'.format(name, value))

# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the data.

sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

print('\n\nInitial reading:')
for name in dir(sensor.data):
    value = getattr(sensor.data, name)

    if not name.startswith('_'):
        print('{}: {}'.format(name, value))

sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

# Up to 10 heater profiles can be configured, each
# with their own temperature and duration.
# sensor.set_gas_heater_profile(200, 150, nb_profile=1)
# sensor.select_gas_heater_profile(1)

url = "https://adelppi.duckdns.org/addInfo"

finish_time = ["9:25","10:10","11:10","11:55","13:30","14:15","15:15","16:00","17:00","17:45","18:45","19:30"]

print('\n\nPolling:')
try:
    while True:

        now = datetime.now()

        if sensor.get_sensor_data():
            output = '{0:.2f} C,{1:.2f} hPa,{2:.2f} %RH'.format(
                sensor.data.temperature,
                sensor.data.pressure,
                sensor.data.humidity)

            if sensor.data.heat_stable:
                print(output)

                # data[now.strftime("%Y/%m/%d %H:%M")] = {"T":sensor.data.temperature,"H":sensor.data.humidity,"AP":sensor.data.pressure}
                # pprint.pprint(data)

            # else:
            #     print(output)

            data = {}

            nowtime = now.strftime("%H:%M")

            #1時間毎にリクエストを送信(テスト中は5秒毎)
            # if now.second %5 == 0:
            if nowtime in finish_time and now.second == 0:
                try:

                    result = requests.get("https://weathernews.jp/onebox/35.731350/139.798464/q=%E5%8D%97%E5%8D%83%E4%BD%8F%EF%BC%88%E6%9D%B1%E4%BA%AC%E9%83%BD%EF%BC%89&v=e8be546f5505407d1788791e7e7b3b0c15fbfd38af41f3dab5a6d2b88cb74d84&temp=c&lang=ja")

                    soup = BeautifulSoup(result.text,"html.parser")

                    tags = soup.find("ul",class_="weather-now__ul")
                    p_tit_tags = tags.li.text

                    weather = p_tit_tags

                    data[now.strftime("%Y/%m/%d/%H:%M")] = {
                            "weather"      : weather.replace("天気",""),
                            "temperature" : sensor.data.temperature,
                            "humidity"    : sensor.data.humidity,
                            "pressure"    : sensor.data.pressure
                            }

                    response = requests.post(url, json=data)

                    pprint.pprint(data)



                    print(f'Status code: {response.status_code}')
                    print(f'Response content: {response.content}')

                except requests.exceptions.RequestException as e:
                    # エラーが発生した場合はログに出力
                    print(f'Request error: {e}')

        time.sleep(1)

except KeyboardInterrupt:
    pass
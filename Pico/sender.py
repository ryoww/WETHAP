import asyncio

import network
import ntptime
import urequests
from machine import ADC, I2C, RTC, Pin, unique_id

from display_manager import DisplayManager
from env_collector import EnvCollector
from ws import AsyncWebsocketClient


class Config:
    def __init__(
        self,
        adjust_temp_range: int = 15,
        adjust_humid_range: int = 30,
        timezone: int = 9,
    ) -> None:
        self.timezone = timezone
        self.adjust_temp_range = adjust_temp_range
        self.adjust_humid_range = adjust_humid_range

    def load_env(self, env):
        self.labID = env.LAB_ID

        self.wifi_ssid = env.SSID
        self.wifi_password = env.PASSWORD
        self.wifi_attempts = env.ATTEMPTS
        self.wifi_delay = env.WIFI_DELAY

        self.api_server = env.WS_URL
        self.time_api_server = env.TIME_URL
        self.ntp_server = env.NTP_URL

        self.socket_delay = env.SOCKET_DELAY


class Sender:
    def __init__(
        self, config: Config, led: Pin, i2c: I2C, temp_adj: ADC, humid_adj: ADC
    ) -> None:
        self.config = config
        self.labID = self.config.labID
        self.machine_id = str(unique_id().hex())
        self.led = led
        self.i2c = i2c
        self.temp_adj = temp_adj
        self.humid_adj = humid_adj

        self.rtc = RTC()
        ntptime.host = self.config.ntp_server
        self.wifi = network.WLAN(network.STA_IF)
        self.ws = AsyncWebsocketClient(self.config.socket_delay)
        self.display = DisplayManager(self.i2c)
        self.lock = asyncio.Lock()

    def init_sensor(self):
        """センサ初期化"""
        try:
            self.collector = EnvCollector(self.i2c)
        except Exception:
            self.display.multi_text("no sensor detect")
            raise RuntimeError("No sensor detect")
        else:
            if "DHT20" in self.collector.sensors:
                print("DHT20 connect")
                self.display.add_text("DHT20 connect").show(False)
                try:
                    self.collector.add_sub_sensor(self.i2c)
                except Exception:
                    print("LPS25HB not connect")
                    self.display.add_text("no sub sensor").show(False)
                else:
                    print("LS25HB connect")
                    self.display.add_text("LPS25HB connect").show(False)
            else:
                print("BME680 connect")
                self.display.add_text("BME680 connect").show(False)

    async def wifi_connect(self) -> None:
        self.wifi.active(1)
        count = 1

        while not self.wifi.isconnected() and count <= self.config.wifi_attempts:
            print(f"WiFi connecting. Attempt {count}.")
            if self.wifi.status() != network.STAT_CONNECTING:
                self.wifi.connect(self.config.wifi_ssid, self.config.wifi_password)
            await asyncio.sleep_ms(self.config.wifi_delay)
            count += 1

        if self.wifi.isconnected():
            print(f"ifconfig: {self.wifi.ifconfig()}")
        else:
            print("Wifi not connected.")

    def _update_rtc(self) -> bool:
        """内部時計を更新
        Args:
            url (str): 現在時間取得用APIのURL
        """
        response = urequests.get(self.config.time_api_server)

        if response.status_code == 200:
            data: dict[str, str] = response.json()
            ymd, time = data["utc_datetime"].split("T")
            year, month, day = list(map(int, ymd.split("-")))
            hour, minute, seconds = time.split("+")[0].split(":")
            second, second_sub = list(map(int, seconds.split(".")))
            week = data["day_of_week"]

            self.rtc.datetime(
                (year, month, day, week, int(hour), int(minute), second, second_sub)
            )
            print("rtc time update success")
            return True
        else:
            print("rtc time update failed")
            return False

    def update_time(self):
        try:
            ntptime.settime()
        except Exception:
            print("clock update by NTP failed")
            if self._update_rtc():
                print("clock update by API success")
                self.display.multi_text("time update", "success")
            else:
                print("clock update by API failed")
                self.display.multi_text("time update", "failed")
                raise RuntimeError("time update failed")
        else:
            print("clock update by NTP success")
            print(self.now())
            self.display.multi_text("time update", "success")

    def get_info(self):
        envs = self.collector.collect_envs()
        envs["temperature"] += (
            (self.temp_adj.read_u16() / 65535 - 0.5) * 2 * self.config.adjust_temp_range
        )
        envs["humidity"] += (
            (self.humid_adj.read_u16() / 65535 - 0.5)
            * 2
            * self.config.adjust_humid_range
        )
        return envs

    def now(self):
        now = list(self.rtc.datetime())
        now[4] += self.config.timezone
        if now[4] >= 24:
            now[4] -= 24
            now[2] += 1
        now = tuple(now)
        return now

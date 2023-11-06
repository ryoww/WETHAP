from machine import I2C, Pin

from bme680 import BME680_I2C
from dht20 import DHT20
from lps25hb import LPS25HB


class EnvCollector:
    def __init__(self, interface: I2C) -> None:
        self.using_sensors = []
        if isinstance(interface, I2C):
            try:
                self.sensor = DHT20(0x38, interface)
                self.using_sensors.append("DHT20")
            except:
                try:
                    self.sensor = BME680_I2C(interface)
                    self.using_sensors.append("BME680")
                except:
                    print("I2C device not found")
                    raise RuntimeError("I2C device not found")
        else:
            print("Unknown input interface")
            raise RuntimeError("Unknown input interface")
        self.sub_sensor = None

    def add_sub_sensor(self, interface: I2C):
        try:
            self.sub_sensor = LPS25HB(0x5C, interface)
            self.using_sensors.append("LPS25HB")
        except:
            print("sub sensor is not found")
            raise RuntimeError("sub sensor is not found")

    @property
    def sensors(self):
        return self.using_sensors

    def get_env(self) -> dict[str, float]:
        if isinstance(self.sensor, BME680_I2C):
            self.envs: dict[str, float] = {
                "temperature": self.sensor.temperature,
                "humidity": self.sensor.humidity,
                "pressure": self.sensor.pressure,
                "gas": self.sensor.gas,
            }
        elif isinstance(self.sensor, DHT20):
            envs = self.sensor.measurements
            self.envs = {
                "temperature": envs["t"],
                "humidity": envs["rh"],
                "pressure": -1,
                "gas": -1,
            }
            if self.sub_sensor:
                self.envs["pressure"] = self.sub_sensor.measurement()
        return self.envs

from machine import I2C

from dht20 import DHT20
from lps25hb import LPS25HB


class EnvCollector:
    def __init__(self, interface: I2C) -> None:
        self.using_sensors = []
        if isinstance(interface, I2C):
            try:
                self.sensor = DHT20(0x38, interface)
                self.using_sensors.append("DHT20")
            except Exception:
                raise RuntimeError("I2C device not found")
        else:
            print("Unknown input interface")
            raise RuntimeError("Unknown input interface")
        self.sub_sensor = None

    def add_sub_sensor(self, interface: I2C):
        try:
            self.sub_sensor = LPS25HB(0x5C, interface)
            self.using_sensors.append("LPS25HB")
        except Exception:
            print("sub sensor is not found")
            raise RuntimeError("sub sensor is not found")

    @property
    def sensors(self):
        return self.using_sensors

    def collect_envs(self) -> dict[str, float]:
        envs = self.sensor.measurements
        envs = {
            "temperature": envs["t"],
            "humidity": envs["rh"],
            "pressure": -1,
            "gas": -1,
        }
        if self.sub_sensor:
            envs["pressure"] = self.sub_sensor.measurement()
        return envs

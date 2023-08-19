import time

from bme680 import BME680_I2C
from dht import DHT11
from dht20 import DHT20
from machine import I2C, Pin


class EnvCollector:
    def __init__(self, interface: I2C | Pin) -> None:
        if isinstance(interface, I2C):
            try:
                self.sensor = BME680_I2C(interface)
            except:
                try:
                    self.sensor = DHT20(0x38, interface)
                except:
                    raise RuntimeError("I2C device not found")
        elif isinstance(interface, Pin):
            self.sensor = DHT11(interface)
            self.sensor.measure()
            time.sleep(1)
        else:
            raise RuntimeError("Unknown input interface")

    def get_env(self) -> dict[str, float]:
        if isinstance(self.sensor, BME680_I2C):
            self.envs: dict[str, float] = {
                "temperature": self.sensor.temperature,
                "humidity": self.sensor.humidity,
                "pressure": self.sensor.pressure,
                "gas": self.sensor.gas,
            }
        elif isinstance(self.sensor, DHT20):
            envs = self.sensor.measurements()
            self.envs = {
                "temperature": envs["t"],
                "humidity": envs["rh"],
                "pressure": -1,
                "gas": -1,
            }
        elif (self.sensor, DHT11):
            self.sensor.measure()
            self.envs = {
                "temperature": self.sensor.temperature(),
                "humidity": self.sensor.humidity(),
                "pressure": -1,
                "gas": -1,
            }
        return self.envs

import time

from bme680 import BME680_I2C
from dht import DHT11
from machine import I2C, Pin


class EnvCollector:
    def __init__(self, interface: I2C | Pin) -> None:
        if isinstance(interface, I2C):
            try:
                self.sensor = BME680_I2C(interface)
            except:
                raise Exception("I2C device not found")
        elif isinstance(interface, Pin):
            self.sensor = DHT11(interface)
            self.sensor.measure()
            time.sleep(1)
        else:
            raise Exception("Unknown input interface")

    def get_env(self) -> dict[str, float]:
        if isinstance(self.sensor, BME680_I2C):
            self.envs: dict[str, float] = {
                "temperature": self.sensor.temperature,
                "humidity": self.sensor.humidity,
                "pressure": self.sensor.pressure,
                "gas": self.sensor.gas,
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

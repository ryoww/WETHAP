import time

from bme680 import BME680_I2C
from dht import DHT11
from machine import I2C, Pin


class EnvCollector:
    def __init__(self, interface):
        if isinstance(interface, I2C):
            self.sensor = BME680_I2C(interface)
        elif isinstance(interface, Pin):
            self.sensor = DHT11(interface)
            self.sensor.measure()
            time.sleep(1)
        else:
            raise Exception("Unknown device")

    def get_env(self):
        if isinstance(self.sensor, BME680_I2C):
            self.envs = {
                "temperature": self.sensor.temperature,
                "humidity": self.sensor.humidity,
                "pressure": self.sensor.pressure,
                "gas": self.sensor.gas,
            }
        else:
            self.sensor.measure()
            self.envs = {
                "temperature": self.sensor.temperature(),
                "humidity": self.sensor.humidity(),
                "pressure": -1,
                "gas": -1,
            }
        return self.envs

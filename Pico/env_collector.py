from bme680 import BME680_I2C
from machine import I2C


class EnvCollector:
    def __init__(self, interface):
        if isinstance(interface, I2C):
            try:
                self.bme = BME680_I2C(interface)
            except:
                self.bme = None
                return None

    def get_env(self):
        if self.bme:
            self.envs = (self.bme.temperature, self.bme.humidity, self.bme.pressure, self.bme.gas)
            return self.envs

from time import sleep_ms

from machine import I2C


class DHT20:
    def __init__(self, address: int, i2c: I2C, max_wait: int = 100, max_retry: int = 3):
        """DHT20温湿度センサ

        Args:
            address (int): センサのアドレス
            i2c (I2C): I2Cオブジェクト
            max_wait (int, optional): センサ読み取りの最大待ち時間(ms). Defaults to 100.
            max_retry (int, optional): 読み取り結果のCRC不整合時の最大再試行回数. Defaults to 3.
        """
        self.address = address
        self.i2c = i2c
        self.max_wait = max_wait
        self.max_retry = max_retry
        self.polynomial = 0x131
        sleep_ms(100)

        if not self.is_ready():
            self.initialize()
            sleep_ms(100)
            if not self.is_ready():
                raise RuntimeError("DHT20 initialize failed.")

    def get_status(self):
        data = self.i2c.readfrom(self.address, 1)
        return data[0]

    def is_ready(self):
        self.i2c.writeto(self.address, bytes([0x71]))
        return (self.get_status() & 0x18) == 0x18

    def initialize(self):
        buffer = bytes([0x00, 0x00])
        self.i2c.writeto_mem(self.address, 0x1B, buffer)
        self.i2c.writeto_mem(self.address, 0x1C, buffer)
        self.i2c.writeto_mem(self.address, 0x1E, buffer)

    def read(self):
        self.i2c.writeto_mem(self.address, 0xAC, bytes([0x33, 0x00]))
        sleep_ms(80)

        for _ in range(self.max_wait):
            if (self.get_status() & 0x80) != 0x80:
                break
            sleep_ms(1)

        data = self.i2c.readfrom(self.address, 7)
        return data

    def check_crc8(self, data):
        crc = 0xFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ self.polynomial
                else:
                    crc <<= 1
        return crc == 0

    def measurements(self):
        for _ in range(self.max_retry + 1):
            data = self.read()
            if self.check_crc8(data):
                break
        else:
            raise RuntimeError("CRC check error.")

        raw_temperature = (data[3] << 16 | data[4] << 8 | data[5]) & 0xFFFFF
        raw_humidity = data[1] << 12 | data[2] << 4 | data[3] >> 4
        humidity = (raw_humidity / 1048576) * 100
        temperature = ((raw_temperature / 1048576) * 200) - 50
        measurement = {"temperature": temperature, "humidity": humidity}
        return measurement

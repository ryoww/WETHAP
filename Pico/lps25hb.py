import utime
from machine import I2C


class LPS25HB:
    WHO_AM_I_ADDRESS = 0x0F
    LPS25HB_CTRL_REG1 = 0x20
    LPS25HB_PRESS_OUT_XL = 0x28
    LPS25HB_PRESS_OUT_L = 0x29
    LPS25HB_PRESS_OUT_H = 0x2A

    def __init__(self, address: int, i2c: I2C):
        self.address = address
        self.i2c = i2c
        utime.sleep_ms(100)
        self.check()

    def check(self):
        data = self.i2c.readfrom_mem(self.address, self.WHO_AM_I_ADDRESS, 1)
        if data != bytes([0xBD]):
            raise RuntimeError("Could not access LPS25HB.")
        return True

    def measurement(self):
        self.i2c.writeto_mem(self.address, self.LPS25HB_CTRL_REG1, bytes([0x90]))
        utime.sleep_ms(100)

        xl = self.i2c.readfrom_mem(self.address, self.LPS25HB_PRESS_OUT_XL, 1)
        l = self.i2c.readfrom_mem(self.address, self.LPS25HB_PRESS_OUT_L, 1)
        h = self.i2c.readfrom_mem(self.address, self.LPS25HB_PRESS_OUT_H, 1)

        pressure = int.from_bytes(h + l + xl, "big") / 4096
        return pressure

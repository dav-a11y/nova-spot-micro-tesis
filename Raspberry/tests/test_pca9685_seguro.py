import unittest

from Raspberry.codigo.pca9685_seguro import (
    ALL_LED_OFF_H,
    FULL_OFF,
    LED0_ON_L,
    PCA9685Seguro,
)


class FakeBus:
    def __init__(self):
        self.registers = {}
        self.writes = []

    def read_byte_data(self, address, register):
        return self.registers.get((address, register), 0)

    def write_byte_data(self, address, register, value):
        self.registers[(address, register)] = value
        self.writes.append((register, value))

    def close(self):
        pass


class FakeGPIO:
    BCM = 1
    HIGH = 1
    LOW = 0

    def __init__(self):
        self.outputs = []
        self.cleanup_called = False

    def output(self, pin, value):
        self.outputs.append((pin, value))

    def cleanup(self, pin):
        self.cleanup_called = True


def make_driver():
    driver = PCA9685Seguro.__new__(PCA9685Seguro)
    driver._bus = FakeBus()
    driver._gpio = FakeGPIO()
    driver._oe_pin = 17
    driver.address = 0x40
    driver.frequency_hz = 50.0
    driver.armed = True
    return driver


class PCA9685SafeOffTests(unittest.TestCase):
    def test_all_off_sets_every_channel_full_off_and_raises_oe_first(self):
        driver = make_driver()
        driver._bus.registers[(0x40, ALL_LED_OFF_H)] = 0
        driver.all_off()

        self.assertEqual(driver._gpio.outputs[0], (17, FakeGPIO.HIGH))
        for channel in range(16):
            off_h = LED0_ON_L + 4 * channel + 3
            self.assertTrue(driver._bus.registers[(0x40, off_h)] & FULL_OFF)
        self.assertFalse(driver.armed)

    def test_arm_restarts_with_every_channel_off(self):
        driver = make_driver()
        driver.arm()

        for channel in range(16):
            off_h = LED0_ON_L + 4 * channel + 3
            self.assertTrue(driver._bus.registers[(0x40, off_h)] & FULL_OFF)
        self.assertEqual(driver._gpio.outputs[-1], (17, FakeGPIO.LOW))
        self.assertTrue(driver.armed)

    def test_close_leaves_oe_high_without_releasing_pin(self):
        driver = make_driver()
        driver.close()

        self.assertEqual(driver._gpio.outputs[-1], (17, FakeGPIO.HIGH))
        self.assertFalse(driver._gpio.cleanup_called)
        self.assertFalse(driver.armed)

    def test_channel_helpers_validate_and_set_single_channel(self):
        driver = make_driver()
        driver.prepare_channel_off(8)
        off_h = LED0_ON_L + 4 * 8 + 3
        self.assertTrue(driver._bus.registers[(0x40, off_h)] & FULL_OFF)
        with self.assertRaises(ValueError):
            driver.set_channel_off(16)


if __name__ == "__main__":
    unittest.main()

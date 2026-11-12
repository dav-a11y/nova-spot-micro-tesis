"""Control mínimo del PCA9685 con apagado predeterminado y OE físico.

Este módulo no mueve servos por sí solo. Requiere Raspberry Pi, I2C habilitado,
python3-smbus y RPi.GPIO. OE usa numeración BCM y es activo en bajo.
"""

from math import pi
from time import sleep


MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06
ALL_LED_OFF_H = 0xFD
FULL_OFF = 0x10


class PCA9685Seguro:
    def __init__(self, bus_number=1, address=0x40, frequency_hz=50,
                 oe_bcm_gpio=17):
        try:
            from smbus import SMBus
            import RPi.GPIO as GPIO
        except ImportError as error:
            raise RuntimeError(
                "Faltan python3-smbus o RPi.GPIO; ejecutar en la Raspberry") from error

        self._gpio = GPIO
        self._oe_pin = int(oe_bcm_gpio)
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._oe_pin, GPIO.OUT, initial=GPIO.HIGH)
        self._bus = SMBus(int(bus_number))
        self.address = int(address)
        self.frequency_hz = float(frequency_hz)
        self.armed = False
        self.all_off()
        self._set_frequency(self.frequency_hz)

    def _write(self, register, value):
        self._bus.write_byte_data(self.address, register, value & 0xFF)

    def _set_frequency(self, frequency_hz):
        prescale = round(25_000_000 / (4096 * frequency_hz)) - 1
        old_mode = self._bus.read_byte_data(self.address, MODE1)
        self._write(MODE1, (old_mode & 0x7F) | 0x10)
        self._write(PRESCALE, prescale)
        self._write(MODE1, old_mode)
        sleep(0.005)
        self._write(MODE1, old_mode | 0xA1)

    def all_off(self):
        if hasattr(self, "_gpio"):
            self._gpio.output(self._oe_pin, self._gpio.HIGH)
        self.armed = False
        # Latch FULL_OFF on every channel, not only ALL_LED_OFF. Individual
        # channel state survives GPIO cleanup/restart and prevents a stale
        # pulse from reappearing if the global register is not retained.
        self._set_all_channels_off()
        self._write(ALL_LED_OFF_H, FULL_OFF)

    def _set_channel_off(self, channel):
        if not 0 <= int(channel) <= 15:
            raise ValueError("Canal PCA9685 fuera de 0..15")
        off_h = LED0_ON_L + 4 * int(channel) + 3
        value = self._bus.read_byte_data(self.address, off_h)
        self._write(off_h, value | FULL_OFF)

    def _set_all_channels_off(self):
        for channel in range(16):
            self._set_channel_off(channel)

    def prepare_channel_off(self, channel):
        """Deja un canal individual en FULL_OFF antes de armar el PWM."""
        self._set_channel_off(channel)

    def set_channel_off(self, channel):
        """Apaga un canal sin alterar los pulsos de los demás canales."""
        self._set_channel_off(channel)

    def arm(self):
        # Mantén OE alto mientras se apagan todos los canales. Solo los canales
        # que reciban una referencia posterior podrán emitir un pulso.
        self._gpio.output(self._oe_pin, self._gpio.HIGH)
        self._set_all_channels_off()
        self._write(ALL_LED_OFF_H, 0x00)
        self._gpio.output(self._oe_pin, self._gpio.LOW)
        self.armed = True

    def set_pulse_us(self, channel, pulse_us):
        if not self.armed:
            raise RuntimeError("PWM deshabilitado: primero debe armarse el controlador")
        if not 0 <= int(channel) <= 15:
            raise ValueError("Canal PCA9685 fuera de 0..15")
        ticks = round(float(pulse_us) * self.frequency_hz * 4096 / 1_000_000)
        ticks = max(0, min(4095, ticks))
        register = LED0_ON_L + 4 * int(channel)
        self._write(register, 0)
        self._write(register + 1, 0)
        self._write(register + 2, ticks & 0xFF)
        self._write(register + 3, (ticks >> 8) & 0x0F)

    @staticmethod
    def angle_to_pulse(angle_rad, calibration):
        if not calibration.get("calibrated", False):
            raise RuntimeError("Servo sin calibrar")
        direction = int(calibration["direction"])
        center = float(calibration["center_us"])
        # La escala se define respecto de 90 grados desde el centro y siempre
        # queda saturada dentro de los pulsos medidos para esta articulación.
        half_range = min(center - float(calibration["min_us"]),
                         float(calibration["max_us"]) - center)
        pulse = center + direction * float(angle_rad) * half_range / (pi / 2)
        return max(float(calibration["min_us"]),
                   min(float(calibration["max_us"]), pulse))

    def close(self):
        self.all_off()
        self._bus.close()
        # No liberar OE al cerrar: es activo-bajo y debe permanecer en HIGH.

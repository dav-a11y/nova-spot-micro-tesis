/* Prueba simultánea de seis MG996R en CH5-CH10 del PCA9685.

   Arduino Mega 2560 -> PCA9685 (según el tutorial de Naylamp):
     5V  -> VCC       pin 20/SDA -> SDA
     GND -> GND       pin 21/SCL -> SCL
     GND -> OE

   Alimentación del servo (separada):
     fuente 5-6 V (+) -> V+ del PCA9685
     fuente (-)       -> GND del PCA9685 y GND del Arduino

   No alimente el MG996R desde el pin 5V del Arduino.
*/

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

const uint8_t DIRECCION_PCA9685 = 0x40;
const uint8_t CANAL_SERVO_1 = 5;
const uint8_t CANAL_SERVO_2 = 6;
const uint8_t CANAL_SERVO_3 = 7;
const uint8_t CANAL_SERVO_4 = 8;
const uint8_t CANAL_SERVO_5 = 9;
const uint8_t CANAL_SERVO_6 = 10;
const uint16_t FRECUENCIA_HZ = 60;

// Intervalo prudente inicial para un servo todavía no calibrado.
const uint16_t PULSO_MIN_US = 1300;
const uint16_t PULSO_MAX_US = 1700;
const uint16_t PASO_US = 5;
const uint16_t ESPERA_MS = 20;

Adafruit_PWMServoDriver pca9685(DIRECCION_PCA9685);

uint16_t microsegundosACuentas(uint16_t pulso_us) {
  // El PCA9685 divide cada periodo PWM en 4096 cuentas.
  return (uint32_t)pulso_us * FRECUENCIA_HZ * 4096UL / 1000000UL;
}

void escribirPulso(uint8_t canal, uint16_t pulso_us) {
  pca9685.setPWM(canal, 0, microsegundosACuentas(pulso_us));
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  pca9685.begin();
  pca9685.setPWMFreq(FRECUENCIA_HZ);
  delay(10);

  // Mantiene apagados los 16 canales antes de activar únicamente CH5-CH10.
  for (uint8_t canal = 0; canal < 16; canal++) {
    pca9685.setPWM(canal, 0, 4096);
  }
  escribirPulso(CANAL_SERVO_1, 1500);
  escribirPulso(CANAL_SERVO_2, 1500);
  escribirPulso(CANAL_SERVO_3, 1500);
  escribirPulso(CANAL_SERVO_4, 1500);
  escribirPulso(CANAL_SERVO_5, 1500);
  escribirPulso(CANAL_SERVO_6, 1500);

  Serial.println("PCA9685 iniciado: prueba simultanea en CH5-CH10; CH11 apagado");
  Serial.println("Desconecte la alimentacion para detener la prueba.");
}

void loop() {
  for (uint16_t pulso = PULSO_MIN_US; pulso <= PULSO_MAX_US; pulso += PASO_US) {
    escribirPulso(CANAL_SERVO_1, pulso);
    escribirPulso(CANAL_SERVO_2, pulso);
    escribirPulso(CANAL_SERVO_3, pulso);
    escribirPulso(CANAL_SERVO_4, pulso);
    escribirPulso(CANAL_SERVO_5, pulso);
    escribirPulso(CANAL_SERVO_6, pulso);
    delay(ESPERA_MS);
  }

  for (int pulso = PULSO_MAX_US; pulso >= PULSO_MIN_US; pulso -= PASO_US) {
    escribirPulso(CANAL_SERVO_1, (uint16_t)pulso);
    escribirPulso(CANAL_SERVO_2, (uint16_t)pulso);
    escribirPulso(CANAL_SERVO_3, (uint16_t)pulso);
    escribirPulso(CANAL_SERVO_4, (uint16_t)pulso);
    escribirPulso(CANAL_SERVO_5, (uint16_t)pulso);
    escribirPulso(CANAL_SERVO_6, (uint16_t)pulso);
    delay(ESPERA_MS);
  }
}

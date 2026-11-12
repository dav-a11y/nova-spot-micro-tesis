#include <Wire.h>

#define TCA0 0x70
#define TCA1 0x71

#define DIRECCION_ENCODER 0x36

void seleccionarCanal(uint8_t direccionMux, uint8_t canal) {
  Wire.beginTransmission(direccionMux);
  Wire.write(1 << canal);
  Wire.endTransmission();
}

bool leerEncoder(uint16_t &valor) {
  Wire.beginTransmission(DIRECCION_ENCODER);
  Wire.write(0x0E);  // Registro ANGLE del AS5600

  if (Wire.endTransmission(false) != 0) {
    return false;
  }

  if (Wire.requestFrom(DIRECCION_ENCODER, (uint8_t)2) != 2) {
    return false;
  }

  valor = ((uint16_t)Wire.read() << 8) | Wire.read();
  valor &= 0x0FFF;  // 12 bits de resolución

  return true;
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
}

void loop() {
  uint8_t multiplexores[] = {TCA0, TCA1};

  for (uint8_t mux = 0; mux < 2; mux++) {
    for (uint8_t canal = 0; canal < 8; canal++) {

      seleccionarCanal(multiplexores[mux], canal);

      uint16_t lectura;

      Serial.print("TCA");
      Serial.print(mux);
      Serial.print(" | Canal ");
      Serial.print(canal);
      Serial.print(" | ");

      if (leerEncoder(lectura)) {
        float angulo = lectura * 360.0 / 4096.0;

        Serial.print("ADC I2C: ");
        Serial.print(lectura);
        Serial.print(" | Angulo: ");
        Serial.print(angulo, 2);
        Serial.println(" grados");
      } else {
        Serial.println("Encoder no detectado");
      }

      delay(5);
    }
  }

  Serial.println("-----------------------------");
  delay(250);
}
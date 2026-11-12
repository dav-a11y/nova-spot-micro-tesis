#include <Wire.h>

const byte AS5600 = 0x36;

bool responde(byte direccion) {
  Wire.clearWireTimeoutFlag();
  Wire.beginTransmission(direccion);
  return Wire.endTransmission() == 0 && !Wire.getWireTimeoutFlag();
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setWireTimeout(10000, true);
  delay(500);

  Serial.println("\nPRUEBA DIRECTA AS5600");
  Serial.println("Uno A4=SDA, A5=SCL");
}

void loop() {
  if (!responde(AS5600)) {
    Serial.println("No responde 0x36: revise SDA, SCL, VCC y GND.");
    delay(1000);
    return;
  }

  Wire.beginTransmission(AS5600);
  Wire.write(0x0C); // RAW_ANGLE
  if (Wire.endTransmission(false) != 0) {
    Serial.println("AS5600 detectado, pero no acepta RAW_ANGLE.");
    delay(1000);
    return;
  }

  byte cantidad = Wire.requestFrom((uint8_t)AS5600, (uint8_t)2);
  if (cantidad != 2) {
    Serial.println("AS5600 detectado, pero no entrega 2 bytes.");
    delay(1000);
    return;
  }

  uint16_t raw = ((uint16_t)Wire.read() << 8) | Wire.read();
  raw &= 0x0FFF;

  Serial.print("AS5600 OK | Angulo: ");
  Serial.print(raw * 360.0 / 4096.0, 2);
  Serial.println(" grados");
  delay(250);
}

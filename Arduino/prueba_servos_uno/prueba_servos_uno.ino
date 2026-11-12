#include <Wire.h>

void setup() {
  Serial.begin(115200);
  Wire.begin();

  Serial.println("Escaneo I2C...");

  for (byte address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    byte error = Wire.endTransmission();

    if (error == 0) {
      Serial.print("Encontrado dispositivo en 0x");
      if (address < 16) Serial.print("0");
      Serial.println(address, HEX);
    }
  }

  Serial.println("Fin.");
}

void loop() {}

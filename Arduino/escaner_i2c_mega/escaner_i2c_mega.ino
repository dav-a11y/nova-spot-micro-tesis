#include <Wire.h>

void setup() {
  Serial.begin(115200);
  Wire.begin();
  delay(1000);
  Serial.println("Escaner I2C Arduino Mega 2560");
}

void loop() {
  byte encontrados = 0;
  for (byte direccion = 1; direccion < 127; direccion++) {
    Wire.beginTransmission(direccion);
    byte error = Wire.endTransmission();
    if (error == 0) {
      Serial.print("Dispositivo encontrado en 0x");
      if (direccion < 16) Serial.print("0");
      Serial.println(direccion, HEX);
      encontrados++;
    }
  }
  if (encontrados == 0) Serial.println("No se encontraron dispositivos I2C");
  Serial.println("---");
  delay(2000);
}

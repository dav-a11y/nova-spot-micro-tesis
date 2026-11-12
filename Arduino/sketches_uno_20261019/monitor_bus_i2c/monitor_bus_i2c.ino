// Monitor del bus I2C del Uno (A4=SDA, A5=SCL) para conectar dispositivos de uno en uno.
// Cada 1,5 s: nivel de las líneas; si SDA está pegada en 0 intenta liberarla con 9 pulsos
// de SCL; luego escanea direcciones con Wire (timeout) y desactiva la llamada general del
// PCA9685 (0x70) para no confundirla con un TCA9548A. No mueve servos.
#include <Wire.h>
void liberarBus() {
  pinMode(A4, INPUT); pinMode(A5, OUTPUT);
  for (byte i = 0; i < 9 && digitalRead(A4) == LOW; i++) {
    digitalWrite(A5, LOW); delayMicroseconds(10); digitalWrite(A5, HIGH); delayMicroseconds(10);
  }
  pinMode(A5, INPUT);
}
void setup() { Serial.begin(115200); }
void loop() {
  TWCR = 0;  // apaga el TWI para leer las líneas como GPIO
  pinMode(A4, INPUT); pinMode(A5, INPUT); delay(2);
  int sda = digitalRead(A4), scl = digitalRead(A5);
  Serial.print(F("LINEAS SDA=")); Serial.print(sda); Serial.print(F(" SCL=")); Serial.print(scl);
  if (sda == 0 && scl == 1) {
    liberarBus(); delay(2);
    Serial.print(F(" | SDA PEGADA -> tras 9 pulsos SDA=")); Serial.print(digitalRead(A4));
  }
  if (scl == 0) Serial.print(F(" | SCL PEGADA EN 0"));
  Wire.begin(); Wire.setWireTimeout(5000, true);
  // Desactivar ALLCALL del PCA9685 si está.
  Wire.beginTransmission(0x40); Wire.write(0x00);
  if (Wire.endTransmission(false) == 0 && Wire.requestFrom((uint8_t)0x40, (uint8_t)1) == 1) {
    byte m = Wire.read(); Wire.beginTransmission(0x40); Wire.write(0x00); Wire.write(m & ~0x01); Wire.endTransmission();
  }
  Serial.print(F(" | DISPOSITIVOS:"));
  byte n = 0;
  for (byte d = 1; d < 127; d++) {
    Wire.beginTransmission(d);
    byte e = Wire.endTransmission();
    if (e == 0) { Serial.print(F(" 0x")); if (d < 16) Serial.print('0'); Serial.print(d, HEX); n++; }
    if (Wire.getWireTimeoutFlag()) { Serial.print(F(" [TIMEOUT]")); Wire.clearWireTimeoutFlag(); break; }
  }
  if (n == 0) Serial.print(F(" ninguno"));
  if (n > 20) Serial.print(F(" (demasiados: bus pegado)"));
  Serial.println();
  Wire.end();
  delay(1500);
}

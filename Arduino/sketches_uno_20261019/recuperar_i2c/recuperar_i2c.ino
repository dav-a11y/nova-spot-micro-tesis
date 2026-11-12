// 20-oct: recuperación del bus I2C bloqueado (SDA sostenida en 0 por un esclavo).
// Envía hasta 16 pulsos por SCL (A5) hasta que SDA (A4) vuelva a 1 y genera una condición
// STOP. Después escanea el bus con Wire (con tiempo límite) y lo informa por serie.
#include <Wire.h>

void pulsosRecuperacion() {
  pinMode(A4, INPUT);            // SDA liberada (pull-up externo)
  pinMode(A5, OUTPUT);
  for (byte i = 0; i < 16 && digitalRead(A4) == LOW; ++i) {
    digitalWrite(A5, LOW);  delayMicroseconds(10);
    digitalWrite(A5, HIGH); delayMicroseconds(10);
    Serial.print("pulso "); Serial.print(i + 1); Serial.print(": SDA="); Serial.println(digitalRead(A4));
  }
  // STOP: SDA de 0 a 1 con SCL en 1.
  pinMode(A4, OUTPUT); digitalWrite(A4, LOW); delayMicroseconds(10);
  digitalWrite(A5, HIGH); delayMicroseconds(10);
  pinMode(A4, INPUT); delayMicroseconds(10);
  pinMode(A5, INPUT);
}

void setup() {
  Serial.begin(115200);
  delay(300);
  Serial.print("Antes: SDA="); Serial.print(digitalRead(A4)); Serial.print(" SCL="); Serial.println(digitalRead(A5));
  pulsosRecuperacion();
  Serial.print("Después: SDA="); Serial.print(digitalRead(A4)); Serial.print(" SCL="); Serial.println(digitalRead(A5));
  Wire.begin();
  Wire.setWireTimeout(3000, true);
  Serial.print("Dispositivos:");
  for (byte d = 1; d < 127; ++d) {
    Wire.beginTransmission(d);
    if (Wire.endTransmission() == 0) { Serial.print(" 0x"); Serial.print(d, HEX); }
  }
  Serial.println(Wire.getWireTimeoutFlag() ? "  (hubo tiempo límite)" : "");
}

void loop() {}

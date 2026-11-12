#include <Wire.h>

const byte TCA1 = 0x70;
const byte TCA2 = 0x71;
const byte CANAL_FEMUR2 = 6;
const byte AS5600 = 0x36;

byte escribir(byte direccion, byte dato, bool stop = true) {
  for (byte intento = 0; intento < 3; intento++) {
    Wire.clearWireTimeoutFlag();
    Wire.beginTransmission(direccion);
    Wire.write(dato);
    byte error = Wire.endTransmission(stop);
    if (error == 0 && !Wire.getWireTimeoutFlag()) {
      delay(30);
      return 0;
    }
    Wire.begin();
    delay(30);
  }
  return 5;
}

bool ping(byte direccion) {
  for (byte intento = 0; intento < 3; intento++) {
    Wire.clearWireTimeoutFlag();
    Wire.beginTransmission(direccion);
    byte error = Wire.endTransmission();
    if (error == 0 && !Wire.getWireTimeoutFlag()) return true;
    Wire.begin();
    delay(30);
  }
  return false;
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setWireTimeout(10000, true);
  delay(500);
}

void loop() {
  Serial.println("\n--- PRUEBA FEMUR 2: TCA 0x71, SD6/SC6 ---");

  Serial.print("TCA 0x70: ");
  Serial.println(ping(TCA1) ? "responde" : "no responde");
  Serial.print("TCA 0x71: ");
  Serial.println(ping(TCA2) ? "responde" : "no responde");

  escribir(TCA1, 0);
  escribir(TCA2, 0);

  byte error = escribir(TCA2, 1 << CANAL_FEMUR2);
  if (error != 0) {
    Serial.println("FALLO: no se puede seleccionar el canal 6 del TCA 0x71.");
    delay(1500);
    return;
  }

  Serial.println("Escaneo de direcciones en canal 6:");
  bool hayDispositivo = false;
  for (byte direccion = 1; direccion < 127; direccion++) {
    if (ping(direccion)) {
      Serial.print("  responde 0x");
      if (direccion < 16) Serial.print('0');
      Serial.println(direccion, HEX);
      hayDispositivo = true;
    }
  }

  if (!hayDispositivo) {
    Serial.println("No responde ningun dispositivo en SD6/SC6.");
    delay(1500);
    return;
  }

  if (!ping(AS5600)) {
    Serial.println("El canal responde, pero el AS5600 esperado en 0x36 no aparece.");
    delay(1500);
    return;
  }

  if (escribir(AS5600, 0x0C, false) != 0) {
    Serial.println("FALLO: AS5600 detectado, pero no acepta RAW_ANGLE.");
    delay(1500);
    return;
  }

  byte cantidad = Wire.requestFrom((uint8_t)AS5600, (uint8_t)2);
  if (cantidad != 2) {
    Serial.println("FALLO: AS5600 detectado, pero no entrega los 2 bytes.");
    delay(1500);
    return;
  }

  uint16_t raw = ((uint16_t)Wire.read() << 8) | Wire.read();
  raw &= 0x0FFF;
  Serial.print("OK: FEMUR 2 responde. Angulo = ");
  Serial.print(raw * 360.0 / 4096.0, 2);
  Serial.println(" grados");
  delay(1500);
}

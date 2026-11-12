// Diagnostico I2C canal por canal. Solo lectura: no envia PWM al PCA9685.
#include <Wire.h>

bool baseBus[128];

bool responde(byte dir) {
  Wire.beginTransmission(dir);
  return Wire.endTransmission() == 0;
}

void cerrarTCAs() {
  for (byte t = 0x70; t <= 0x77; t++) {
    if (responde(t)) { Wire.beginTransmission(t); Wire.write(0); Wire.endTransmission(); }
  }
}

int leerControl(byte tca) {
  if (Wire.requestFrom(tca, (uint8_t)1) != 1) return -1;
  return Wire.read();
}

void imprimirHex(byte v) { Serial.print("0x"); if (v < 16) Serial.print('0'); Serial.print(v, HEX); }

void diagnostico() {
  cerrarTCAs();
  Serial.println(F("\n===== BUS PRINCIPAL (todos los canales cerrados) ====="));
  for (byte d = 1; d < 127; d++) {
    baseBus[d] = responde(d);
    if (baseBus[d]) { Serial.print(F("  ")); imprimirHex(d); Serial.println(); }
  }

  for (byte tca = 0x70; tca <= 0x77; tca++) {
    if (!baseBus[tca]) continue;
    Serial.print(F("\n===== TCA ")); imprimirHex(tca); Serial.println(F(" ====="));
    for (byte canal = 0; canal < 8; canal++) {
      cerrarTCAs();
      Wire.beginTransmission(tca); Wire.write(1 << canal); byte err = Wire.endTransmission();
      delay(3);
      int ctrl = leerControl(tca);
      Serial.print(F("Canal ")); Serial.print(canal);
      Serial.print(F(" | escritura=")); Serial.print(err == 0 ? "OK" : "FALLO");
      Serial.print(F(" | control leido=")); if (ctrl < 0) Serial.print(F("sin lectura")); else imprimirHex(ctrl);
      Serial.print(F(" | nuevos:"));
      bool alguno = false;
      for (byte d = 1; d < 127; d++) {
        if (baseBus[d]) continue;
        if (responde(d)) { Serial.print(' '); imprimirHex(d); alguno = true; }
      }
      if (!alguno) Serial.print(F(" ninguno"));
      if (responde(0x36)) {
        Wire.beginTransmission(0x36); Wire.write(0x0B); Wire.endTransmission(false);
        Wire.requestFrom((uint8_t)0x36, (uint8_t)1);
        byte st = Wire.read();
        Serial.print(F(" | AS5600 status=")); imprimirHex(st);
        Serial.print(F(" MD=")); Serial.print((st >> 5) & 1);
        Serial.print(F(" ML=")); Serial.print((st >> 4) & 1);
        Serial.print(F(" MH=")); Serial.print((st >> 3) & 1);
        // Ángulo crudo del AS5600 (registro 0x0C, 12 bits).
        Wire.beginTransmission(0x36); Wire.write(0x0C); Wire.endTransmission(false);
        if (Wire.requestFrom((uint8_t)0x36, (uint8_t)2) == 2) {
          unsigned int raw = ((Wire.read() << 8) | Wire.read()) & 0x0FFF;
          Serial.print(F(" | angulo=")); Serial.print(raw * 360.0 / 4096.0, 2); Serial.print(F(" grados"));
        }
      }
      Serial.println();
    }
  }
  cerrarTCAs();
  Serial.println(F("\nFIN"));
}

void setup() {
  // Nivel de reposo de SDA/SCL antes de iniciar Wire (deben estar en 1 por los pull-up).
  pinMode(A4, INPUT); pinMode(A5, INPUT);
  delay(10);
  Serial.begin(115200);
  Serial.print(F("\nReposo: SDA(A4)=")); Serial.print(digitalRead(A4));
  Serial.print(F(" SCL(A5)=")); Serial.println(digitalRead(A5));
  Wire.begin();
  Wire.setWireTimeout(10000, true);
  // Desactiva solo la direccion LED All Call (0x70) del PCA9685 para que no
  // se confunda con un TCA9548A en 0x70. No cambia ninguna salida PWM.
  Wire.beginTransmission(0x40); Wire.write(0x00); Wire.endTransmission(false);
  Wire.requestFrom((uint8_t)0x40, (uint8_t)1);
  byte mode1 = Wire.read();
  Wire.beginTransmission(0x40); Wire.write(0x00); Wire.write(mode1 & ~0x01); Wire.endTransmission();
  Wire.beginTransmission(0x40); Wire.write(0x00); Wire.endTransmission(false);
  Wire.requestFrom((uint8_t)0x40, (uint8_t)1);
  Serial.print(F("PCA MODE1 antes=")); imprimirHex(mode1);
  Serial.print(F(" despues=")); imprimirHex(Wire.read()); Serial.println(F(" (ALLCALL desactivado)"));
  diagnostico();
}

void loop() {
  delay(6000);
  diagnostico();
}

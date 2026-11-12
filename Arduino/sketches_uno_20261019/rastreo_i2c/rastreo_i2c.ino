#include <Wire.h>

const byte TCA1 = 0x70;
const byte TCA2 = 0x71;
const byte AS5600 = 0x36;

struct Sensor {
  const char *nombre;
  byte tca;
  byte canal;
};

const Sensor sensores[] = {
  {"COXA 1",  TCA2, 3}, {"COXA 2",  TCA2, 5},
  {"COXA 3",  TCA1, 5}, {"COXA 4",  TCA1, 2},
  {"FEMUR 1", TCA2, 1}, {"FEMUR 3", TCA1, 4},
  {"FEMUR 4", TCA1, 1}, {"TIBIA 1", TCA2, 0},
  {"TIBIA 2", TCA2, 4}, {"TIBIA 3", TCA1, 3},
  {"TIBIA 4", TCA1, 0}
};

byte transmitir(byte direccion, byte dato, bool enviarDato, bool stop = true) {
  Wire.clearWireTimeoutFlag();
  unsigned long inicio = micros();
  Wire.beginTransmission(direccion);
  if (enviarDato) Wire.write(dato);
  byte resultado = Wire.endTransmission(stop);

  Serial.print("  I2C 0x");
  if (direccion < 16) Serial.print('0');
  Serial.print(direccion, HEX);
  if (enviarDato) {
    Serial.print(" <- 0x");
    if (dato < 16) Serial.print('0');
    Serial.print(dato, HEX);
  }
  Serial.print(" : codigo ");
  Serial.print(resultado);
  Serial.print(" en ");
  Serial.print(micros() - inicio);
  Serial.print(" us");
  if (Wire.getWireTimeoutFlag()) Serial.print(" [TIMEOUT]");
  Serial.println();
  return resultado;
}

bool leerSensor(const Sensor &sensor) {
  Serial.print("\n[");
  Serial.print(sensor.nombre);
  Serial.print("] TCA 0x");
  Serial.print(sensor.tca, HEX);
  Serial.print(" canal ");
  Serial.println(sensor.canal);

  Serial.println(" Apagar TCA1:");
  transmitir(TCA1, 0, true);
  Serial.println(" Apagar TCA2:");
  transmitir(TCA2, 0, true);
  Serial.println(" Seleccionar canal:");
  if (transmitir(sensor.tca, 1 << sensor.canal, true) != 0) return false;

  Serial.println(" Comprobar AS5600:");
  if (transmitir(AS5600, 0, false) != 0) return false;

  Serial.println(" Pedir RAW_ANGLE:");
  if (transmitir(AS5600, 0x0C, true, false) != 0) return false;

  Wire.clearWireTimeoutFlag();
  unsigned long inicio = micros();
  byte cantidad = Wire.requestFrom(AS5600, (byte)2);
  Serial.print(" Leer 2 bytes: recibidos ");
  Serial.print(cantidad);
  Serial.print(" en ");
  Serial.print(micros() - inicio);
  Serial.print(" us");
  if (Wire.getWireTimeoutFlag()) Serial.print(" [TIMEOUT]");
  Serial.println();

  if (cantidad == 2) {
    uint16_t raw = ((uint16_t)Wire.read() << 8) | Wire.read();
    raw &= 0x0FFF;
    Serial.print(" Angulo: ");
    Serial.println(raw * 360.0 / 4096.0, 2);
  }
  return cantidad == 2;
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setWireTimeout(10000, true);
  delay(500);
  Serial.println("\nRASTREO I2C: 11 AS5600");
}

void loop() {
  for (byte i = 0; i < sizeof(sensores) / sizeof(sensores[0]); i++) {
    if (!leerSensor(sensores[i])) {
      Serial.println(" >>> FALLO: se detiene aqui para conservar evidencia.");
      while (true) delay(1000);
    }
    delay(50);
  }
  Serial.println("\nRonda completa correcta; se reinicia en 3 s.");
  delay(3000);
}

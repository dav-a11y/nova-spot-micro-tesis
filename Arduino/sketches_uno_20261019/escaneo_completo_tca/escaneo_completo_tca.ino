#include <Wire.h>

const byte MUXES[] = {0x70, 0x71};
const byte DIRECCION_MIN = 0x08;
const byte DIRECCION_MAX = 0x77;

bool ping(byte direccion) {
  Wire.clearWireTimeoutFlag();
  Wire.beginTransmission(direccion);
  byte error = Wire.endTransmission();
  return error == 0 && !Wire.getWireTimeoutFlag();
}

bool seleccionar(byte mux, byte canal) {
  for (byte intento = 0; intento < 3; intento++) {
    Wire.clearWireTimeoutFlag();
    Wire.beginTransmission(mux);
    Wire.write(1 << canal);
    byte error = Wire.endTransmission();
    if (error == 0 && !Wire.getWireTimeoutFlag()) {
      delay(20);
      return true;
    }
    Wire.begin();
    Wire.setWireTimeout(10000, true);
    delay(30);
  }
  return false;
}

void apagarTodo() {
  Wire.clearWireTimeoutFlag();
  Wire.beginTransmission(MUXES[0]);
  Wire.write(0);
  Wire.endTransmission();
  delay(10);
  Wire.clearWireTimeoutFlag();
  Wire.beginTransmission(MUXES[1]);
  Wire.write(0);
  Wire.endTransmission();
  delay(20);
}

void escanearCanal(byte mux, byte canal) {
  apagarTodo();

  Serial.print("Mux 0x");
  Serial.print(mux, HEX);
  Serial.print(" canal ");
  Serial.print(canal);
  Serial.print(": ");

  if (!seleccionar(mux, canal)) {
    Serial.println("no se pudo seleccionar");
    return;
  }

  byte encontrados = 0;
  for (byte direccion = DIRECCION_MIN; direccion <= DIRECCION_MAX; direccion++) {
    if (ping(direccion) && direccion != MUXES[0] && direccion != MUXES[1]) {
      if (encontrados > 0) Serial.print(", ");
      Serial.print("0x");
      if (direccion < 16) Serial.print('0');
      Serial.print(direccion, HEX);
      if (direccion == 0x36) Serial.print(" AS5600");
      encontrados++;
    }
  }

  if (encontrados == 0) Serial.print("sin dispositivos en canales secundarios");
  Serial.println();
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setClock(50000);
  Wire.setWireTimeout(10000, true);
  delay(700);

  Serial.println("\nBARRIDO I2C COMPLETO: 2 TCA x 8 CANALES x DIRECCIONES 0x08-0x77");
  Serial.println("Se omiten 0x70/0x71 porque son los multiplexores.");

  for (byte indice = 0; indice < 2; indice++) {
    byte mux = MUXES[indice];
    Serial.print("\nComprobando TCA 0x");
    Serial.print(mux, HEX);
    Serial.print(": ");
    if (!ping(mux)) {
      Serial.println("no responde en bus principal");
      continue;
    }
    Serial.println("responde");

    for (byte canal = 0; canal < 8; canal++) {
      escanearCanal(mux, canal);
    }
  }

  apagarTodo();
  Serial.println("\nFIN DEL BARRIDO");
}

void loop() {
  delay(1000);
}

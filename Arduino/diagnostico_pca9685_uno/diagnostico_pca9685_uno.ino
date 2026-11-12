// Uno: A4->SDA, A5->SCL, 5V->VCC, GND->GND, D7->OE.
// Diagnostico sin movimiento: mantener apagada la fuente de servos.
// Monitor serie 115200. I = escanear; R = leer registros en 0x40.
#include <Wire.h>

const byte OE_PIN = 7;
const byte DIRECCION = 0x40;

void hexadecimal(byte valor) {
  Serial.print(F("0x"));
  if (valor < 16) Serial.print('0');
  Serial.print(valor, HEX);
}

void escanear() {
  byte encontrados = 0;
  Serial.println(F("Escaneo I2C (OE alto, sin movimiento):"));
  for (byte direccion = 1; direccion < 127; ++direccion) {
    Wire.beginTransmission(direccion);
    byte error = Wire.endTransmission();
    if (error == 0) {
      ++encontrados;
      Serial.print(F("Responde "));
      hexadecimal(direccion);
      Serial.println();
    } else if (error == 4 || error == 5) {
      Serial.print(F("Error de bus en "));
      hexadecimal(direccion);
      Serial.println(F("; revise cableado y alimentacion."));
      break;
    }
  }
  if (!encontrados) Serial.println(F("Ningun dispositivo responde."));
  Serial.println(F("Esperado: 0x40; tambien puede responder All Call 0x70."));
}

bool leerRegistro(byte registro, byte &valor) {
  Wire.beginTransmission(DIRECCION);
  Wire.write(registro);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom(DIRECCION, (byte)1) != 1) return false;
  valor = Wire.read();
  return true;
}

void registros() {
  const byte direcciones[] = {0x00, 0x01, 0xFE};
  Serial.println(F("Lectura 0x40: MODE1, MODE2, PRE_SCALE"));
  for (byte i = 0; i < 3; ++i) {
    byte valor;
    if (!leerRegistro(direcciones[i], valor)) {
      Serial.println(F("Fallo de lectura. Revise VCC, GND, SDA y SCL."));
      return;
    }
    hexadecimal(direcciones[i]);
    Serial.print(F(" = "));
    hexadecimal(valor);
    Serial.println();
  }
  Serial.println(F("Lectura completada. No confirma servos ni posicion real."));
}

void setup() {
  digitalWrite(OE_PIN, HIGH);
  pinMode(OE_PIN, OUTPUT);
  Serial.begin(115200);
  Wire.begin();
  Wire.setWireTimeout(25000, true);
  Serial.println(F("NOVA: diagnostico PCA9685 sin movimiento."));
  Serial.println(F("Enviar I para escanear, R para leer registros."));
}

void loop() {
  if (!Serial.available()) return;
  char orden = Serial.read();
  if (orden == 'I' || orden == 'i') escanear();
  else if (orden == 'R' || orden == 'r') registros();
}

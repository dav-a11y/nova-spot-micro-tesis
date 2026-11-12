#include <Wire.h>

const byte TCA_DIRECCIONES[] = {0x70, 0x71};
const byte AS5600 = 0x36;

bool responde(byte direccion) {
  Wire.beginTransmission(direccion);
  return Wire.endTransmission() == 0;
}

void seleccionarCanal(byte tca, byte canal) {
  Wire.beginTransmission(tca);
  Wire.write(1 << canal);
  Wire.endTransmission();
  delay(5);
}

void escanearBusPrincipal() {
  Serial.println("\n--- BUS I2C PRINCIPAL ---");
  bool hayDispositivo = false;

  for (byte direccion = 1; direccion < 127; direccion++) {
    if (responde(direccion)) {
      Serial.print("Detectado: 0x");
      if (direccion < 16) Serial.print('0');
      Serial.println(direccion, HEX);
      hayDispositivo = true;
    }
  }

  if (!hayDispositivo) {
    Serial.println("No responde ningun dispositivo I2C.");
  }
}

void probarTCA(byte tca) {
  Serial.print("\n--- TCA 0x");
  Serial.print(tca, HEX);
  Serial.println(" ---");

  if (!responde(tca)) {
    Serial.println("NO RESPONDE: revise SDA, SCL, GND, VCC y pines A0-A2.");
    return;
  }

  Serial.println("TCA detectado.");

  for (byte canal = 0; canal < 8; canal++) {
    seleccionarCanal(tca, canal);

    Serial.print("Canal ");
    Serial.print(canal);
    Serial.print(": ");

    if (responde(AS5600)) {
      Serial.println("AS5600 detectado (0x36)");
    } else {
      Serial.println("sin AS5600 en 0x36");
    }
  }

  Wire.beginTransmission(tca);
  Wire.write(0);
  Wire.endTransmission();
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setWireTimeout(10000, true);
  delay(500);

  Serial.println("\nDIAGNOSTICO I2C: UNO + TCA9548A + AS5600");
  Serial.println("SDA=A4, SCL=A5, GND comun.");

  escanearBusPrincipal();
  probarTCA(TCA_DIRECCIONES[0]);
  probarTCA(TCA_DIRECCIONES[1]);
  Serial.println("\nDiagnostico terminado. Se repetira en 5 segundos.");
}

void loop() {
  delay(5000);
  escanearBusPrincipal();
  probarTCA(TCA_DIRECCIONES[0]);
  probarTCA(TCA_DIRECCIONES[1]);
}

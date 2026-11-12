// 20-oct: diagnóstico detallado del bus I2C (A4=SDA, A5=SCL) sin mover servos.
// - Vcc real del Uno (referencia interna de 1,1 V).
// - Tensión de SDA y SCL como entradas analógicas: sueltas (solo pull-up externo) y con el
//   pull-up interno (~35 kOhm): 0 V = cortocircuito a GND; 0,4-1,5 V = chip sin VCC que
//   tira por sus diodos; cerca de Vcc = línea sana.
// - Si SDA y SCL están altas: escaneo con Wire (tiempo límite) y lectura de los TCA.
// Se repite cada 2 s para ver si cambia al tocar o reconectar cables.
#include <Wire.h>

long leerVccmV() {
  ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  delay(3); ADCSRA |= _BV(ADSC); while (bit_is_set(ADCSRA, ADSC));
  long r = ADCL; r |= ADCH << 8;
  return 1125300L / r;
}

float voltios(byte pin, long vcc) {
  long s = 0;
  for (byte i = 0; i < 16; ++i) s += analogRead(pin);
  return (s / 16.0) * vcc / 1023.0 / 1000.0;
}

void medir(const char *nombre, byte pin, long vcc) {
  pinMode(pin, INPUT);        delay(5); float suelta = voltios(pin, vcc);
  pinMode(pin, INPUT_PULLUP); delay(5); float conPull = voltios(pin, vcc);
  pinMode(pin, INPUT);
  Serial.print(nombre); Serial.print(": suelta "); Serial.print(suelta, 2);
  Serial.print(" V | con pull-up interno "); Serial.print(conPull, 2); Serial.print(" V -> ");
  if (suelta > 0.8 * vcc / 1000.0) Serial.println("SANA (alta)");
  else if (conPull < 0.15) Serial.println("CORTOCIRCUITO a GND (ni el pull-up interno la sube)");
  else if (suelta < 0.15 && conPull < 1.6) Serial.println("tirada fuerte a GND: chip sin VCC o esclavo bloqueado");
  else Serial.println("intermedia: pull-up débil o chip sin VCC");
}

void setup() { Serial.begin(115200); }

void loop() {
  long vcc = leerVccmV();
  Serial.print("Vcc Uno = "); Serial.print(vcc); Serial.println(" mV");
  medir("SDA (A4)", A4, vcc);
  medir("SCL (A5)", A5, vcc);
  if (digitalRead(A4) && digitalRead(A5)) {
    Wire.begin(); Wire.setWireTimeout(3000, true);
    Serial.print("Escaneo:");
    for (byte d = 1; d < 127; ++d) {
      Wire.beginTransmission(d);
      if (Wire.endTransmission() == 0) { Serial.print(" 0x"); Serial.print(d, HEX); }
    }
    Serial.println(Wire.getWireTimeoutFlag() ? " (tiempo límite)" : "");
    Wire.end();
  } else {
    Serial.println("Escaneo omitido: bus bloqueado");
  }
  Serial.println("--");
  delay(2000);
}

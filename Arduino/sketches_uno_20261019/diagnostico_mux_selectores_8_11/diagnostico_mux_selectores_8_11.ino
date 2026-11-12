// Lectura temporal del CD74HC4067 con selectores conectados a D8-D11.
// No controla el PCA9685 ni mueve servos. SIG del multiplexor va a A0.

const byte PIN_SIG = A0;
const byte PIN_S0 = 8;
const byte PIN_S1 = 9;
const byte PIN_S2 = 10;
const byte PIN_S3 = 11;

void seleccionarCanal(byte canal) {
  digitalWrite(PIN_S0, bitRead(canal, 0));
  digitalWrite(PIN_S1, bitRead(canal, 1));
  digitalWrite(PIN_S2, bitRead(canal, 2));
  digitalWrite(PIN_S3, bitRead(canal, 3));
}

int leerCanal(byte canal) {
  seleccionarCanal(canal);
  delayMicroseconds(100);
  analogRead(PIN_SIG);  // descarta primera conversión tras cambiar canal
  return analogRead(PIN_SIG);
}

void setup() {
  pinMode(PIN_S0, OUTPUT);
  pinMode(PIN_S1, OUTPUT);
  pinMode(PIN_S2, OUTPUT);
  pinMode(PIN_S3, OUTPUT);
  Serial.begin(115200);
}

void loop() {
  Serial.print(F("MUX"));
  for (byte canal = 0; canal < 16; ++canal) {
    Serial.print(',');
    Serial.print(leerCanal(canal));
  }
  Serial.println();
  delay(250);
}

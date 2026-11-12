// Solo lectura de los 16 canales del MUX (S0=D4 ... S3=D7, SIG=A0). No usa I2C ni PWM.
const byte S[4] = {4, 5, 6, 7};
int leer(byte c) {
  for (byte b = 0; b < 4; b++) digitalWrite(S[b], bitRead(c, b));
  delayMicroseconds(500);
  for (byte k = 0; k < 3; k++) analogRead(A0);
  long s = 0; for (byte k = 0; k < 8; k++) s += analogRead(A0);
  return s / 8;
}
void setup() { Serial.begin(115200); for (byte b = 0; b < 4; b++) pinMode(S[b], OUTPUT); }
void loop() {
  Serial.print("ADC");
  for (byte c = 0; c < 16; c++) { Serial.print(','); Serial.print(leer(c)); }
  Serial.println(); delay(100);
}

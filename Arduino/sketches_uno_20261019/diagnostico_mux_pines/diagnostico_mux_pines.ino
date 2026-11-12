// Solo lectura: prueba que pines manejan los selectores del MUX 16CH. Sin PWM.
const byte juegos[3][4] = {{8,9,10,11},{7,6,5,4},{4,5,6,7}};
const char* nombres[3] = {"S0-S3=D8,D9,D10,D11","S0-S3=D7,D6,D5,D4","S0-S3=D4,D5,D6,D7"};
int leer(const byte *p, byte canal) {
  for (byte b = 0; b < 4; b++) digitalWrite(p[b], bitRead(canal, b));
  delayMicroseconds(500);
  for (byte k = 0; k < 3; k++) analogRead(A0);
  long s = 0; for (byte k = 0; k < 8; k++) s += analogRead(A0);
  return s / 8;
}
void setup() {
  Serial.begin(115200);
  for (byte j = 0; j < 3; j++) for (byte b = 0; b < 4; b++) pinMode(juegos[j][b], OUTPUT);
}
void loop() {
  for (byte j = 0; j < 3; j++) {
    for (byte o = 0; o < 3; o++) for (byte b = 0; b < 4; b++) digitalWrite(juegos[o][b], LOW);
    Serial.print(nombres[j]); Serial.print(" |");
    for (byte c = 0; c < 16; c++) { Serial.print(' '); Serial.print(leer(juegos[j], c)); }
    Serial.println();
  }
  Serial.println("--");
  delay(1000);
}

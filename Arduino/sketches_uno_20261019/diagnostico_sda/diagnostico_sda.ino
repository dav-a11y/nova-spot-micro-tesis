// Diagnóstico de qué pone SDA (A4) en 0. Solo libera líneas (INPUT) o las baja (OUTPUT LOW);
// nunca las fuerza en alto, para no hacer cortocircuito con un dispositivo que tire a 0.
#define SDA_P A4
#define SCL_P A5
void suelta(byte p) { pinMode(p, INPUT); }
void baja(byte p) { digitalWrite(p, LOW); pinMode(p, OUTPUT); }
void estado(const char *t) { Serial.print(t); Serial.print(F(": SDA=")); Serial.print(digitalRead(SDA_P)); Serial.print(F(" SCL=")); Serial.println(digitalRead(SCL_P)); }
long tiempoSubida(byte p, unsigned long limite_us) {
  unsigned long t0 = micros();
  while (micros() - t0 < limite_us) if (digitalRead(p)) return micros() - t0;
  return -1;
}
bool recuperar(byte maxPulsos) {
  for (byte i = 1; i <= maxPulsos; i++) {
    baja(SCL_P); delayMicroseconds(20); suelta(SCL_P); delayMicroseconds(20);
    if (digitalRead(SDA_P)) {
      Serial.print(F("   SDA se soltó tras ")); Serial.print(i); Serial.println(F(" pulsos de SCL -> DISPOSITIVO COLGADO"));
      baja(SDA_P); delayMicroseconds(20); suelta(SDA_P);  // STOP: SDA sube con SCL alto
      return true;
    }
  }
  Serial.print(F("   SDA sigue en 0 tras ")); Serial.print(maxPulsos); Serial.println(F(" pulsos -> algo la tira a tierra de forma fija"));
  return false;
}
void setup() {
  Serial.begin(115200); delay(200);
  suelta(SDA_P); suelta(SCL_P); delay(5);
  estado("1) Tras reinicio");
  // 2) Solo actividad en SCL.
  for (byte i = 0; i < 20; i++) { baja(SCL_P); delayMicroseconds(20); suelta(SCL_P); delayMicroseconds(20); }
  delay(1); estado("2) Tras 20 pulsos solo en SCL");
  if (!digitalRead(SDA_P)) recuperar(16);
  // 3) Pulso corto en SDA.
  baja(SDA_P); delayMicroseconds(5); suelta(SDA_P);
  long t = tiempoSubida(SDA_P, 50000);
  Serial.print(F("3) Pulso de 5 us en SDA: vuelve a 1 en "));
  if (t < 0) Serial.println(F("NUNCA (>50 ms)")); else { Serial.print(t); Serial.println(F(" us")); }
  if (t < 0) {
    // 4) Recuperación con pulsos de reloj.
    Serial.println(F("4) Intento de liberar con pulsos de SCL:"));
    bool ok = recuperar(16);
    if (!ok) {
      // 5) Pull-up interno.
      pinMode(SDA_P, INPUT_PULLUP); delay(2);
      Serial.print(F("5) Con pull-up interno del Uno: SDA=")); Serial.println(digitalRead(SDA_P));
      pinMode(SDA_P, INPUT);
      // 6) Espera de 1 s.
      delay(1000); Serial.print(F("6) Tras esperar 1 s: SDA=")); Serial.println(digitalRead(SDA_P));
    }
  }
  // 7) Repetición del pulso corto tras la recuperación.
  delay(5); baja(SDA_P); delayMicroseconds(5); suelta(SDA_P);
  t = tiempoSubida(SDA_P, 50000);
  Serial.print(F("7) Segundo pulso en SDA: vuelve a 1 en "));
  if (t < 0) Serial.println(F("NUNCA")); else { Serial.print(t); Serial.println(F(" us")); }
  estado("8) Estado final");
  Serial.println(F("FIN"));
}
void loop() {}

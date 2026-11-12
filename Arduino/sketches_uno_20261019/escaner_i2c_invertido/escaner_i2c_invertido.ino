// Escaneo I2C por software (bit-bang, ~10 kHz) en los dos sentidos de cableado.
// Solo envía dirección + bit de escritura y libera el bus: no escribe registros.
byte SDA_P, SCL_P;
void alto(byte p) { pinMode(p, INPUT); }            // línea liberada (pull-up externo)
void bajo(byte p) { digitalWrite(p, LOW); pinMode(p, OUTPUT); }
void pausa() { delayMicroseconds(50); }
void inicio() { alto(SDA_P); alto(SCL_P); pausa(); bajo(SDA_P); pausa(); bajo(SCL_P); pausa(); }
void fin() { bajo(SDA_P); pausa(); alto(SCL_P); pausa(); alto(SDA_P); pausa(); }
bool enviar(byte b) {
  for (int i = 7; i >= 0; i--) { if (b & (1 << i)) alto(SDA_P); else bajo(SDA_P); pausa(); alto(SCL_P); pausa(); bajo(SCL_P); pausa(); }
  alto(SDA_P); pausa(); alto(SCL_P); pausa(); bool ack = digitalRead(SDA_P) == LOW; bajo(SCL_P); pausa();
  return ack;
}
void escanear(byte sda, byte scl, const char *nombre) {
  SDA_P = sda; SCL_P = scl;
  Serial.print(nombre); Serial.print(": ");
  bool alguno = false;
  for (byte d = 1; d < 127; d++) {
    inicio(); bool ack = enviar(d << 1); fin();
    if (ack) { Serial.print("0x"); if (d < 16) Serial.print('0'); Serial.print(d, HEX); Serial.print(' '); alguno = true; }
  }
  if (!alguno) Serial.print("ningún dispositivo");
  Serial.println();
  alto(SDA_P); alto(SCL_P);
}
void setup() {
  Serial.begin(115200); delay(300);
  escanear(A4, A5, "Normal    (SDA=A4, SCL=A5)");
  escanear(A5, A4, "Invertido (SDA=A5, SCL=A4)");
}
void loop() {}

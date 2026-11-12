// Barrido combinado: para cada articulación (±10° alrededor de su reposo) mide qué
// potenciómetro (MUX analógico, S0-S3 = D4-D7, SIG = A0) y qué AS5600 (TCA 0x70/0x71)
// siguen el movimiento. Al final apaga todas las salidas.
#include <Wire.h>
const byte PCA = 0x40, SEL[4] = {4, 5, 6, 7};
const char* NOM[12] = {"coxa1","coxa2","coxa3","coxa4","femur1","femur2","femur3","femur4","tibia1","tibia2","tibia3","tibia4"};
const byte CANAL[12] = {0,1,2,3, 4,5,6,7, 8,9,10,14};
const int  BASE[12]  = {159,45,54,74, 110,100,100,100, 100,80,100,70};
void reg(byte r, byte v) { Wire.beginTransmission(PCA); Wire.write(r); Wire.write(v); Wire.endTransmission(); }
void pwm(byte c, int on, int off) { Wire.beginTransmission(PCA); Wire.write(0x06 + 4*c); Wire.write(on & 0xFF); Wire.write(on >> 8); Wire.write(off & 0xFF); Wire.write(off >> 8); Wire.endTransmission(); }
void servo(byte c, int ang) { pwm(c, 0, map(constrain(ang, 0, 180), 0, 180, 102, 512)); }
void todoOff() { for (byte c = 0; c < 16; c++) pwm(c, 0, 4096); }
int adc(byte c) { for (byte b = 0; b < 4; b++) digitalWrite(SEL[b], bitRead(c, b)); delayMicroseconds(500); for (byte k = 0; k < 3; k++) analogRead(A0); long s = 0; for (byte k = 0; k < 8; k++) s += analogRead(A0); return s / 8; }
void cerrarTCA() { for (byte t = 0x70; t <= 0x71; t++) { Wire.beginTransmission(t); Wire.write(0); Wire.endTransmission(); } }
float ang(byte tca, byte ch) {
  cerrarTCA(); Wire.beginTransmission(tca); Wire.write(1 << ch); Wire.endTransmission();
  Wire.beginTransmission(0x36); Wire.write(0x0C); if (Wire.endTransmission(false) != 0) return -1;
  if (Wire.requestFrom((uint8_t)0x36, (uint8_t)2) != 2) return -1;
  return (((Wire.read() << 8) | Wire.read()) & 0x0FFF) * 360.0 / 4096.0;
}
void leer(float *pot, float *enc) {
  for (byte c = 0; c < 16; c++) { long s = 0; for (byte r = 0; r < 4; r++) s += adc(c); pot[c] = s / 4.0; }
  for (byte k = 0; k < 16; k++) { float s = 0; int n = 0; for (byte r = 0; r < 4; r++) { float a = ang(0x70 + k / 8, k % 8); if (a >= 0) { s += a; n++; } } enc[k] = n ? s / n : -1; }
  cerrarTCA();
}
float dif(float a, float b) { float d = a - b; while (d > 180) d -= 360; while (d < -180) d += 360; return d; }
void setup() {
  Serial.begin(115200); Wire.begin(); Wire.setWireTimeout(10000, true);
  for (byte b = 0; b < 4; b++) pinMode(SEL[b], OUTPUT);
  reg(0x00, 0x10); reg(0xFE, 121); reg(0x00, 0x20); delay(5); reg(0x00, 0xA0);
  todoOff();
  Serial.println(F("INICIO"));
  float pa[16], pb[16], ea[16], eb[16];
  for (byte i = 0; i < 12; i++) {
    servo(CANAL[i], BASE[i] - 10); delay(900); leer(pa, ea);
    servo(CANAL[i], BASE[i] + 10); delay(900); leer(pb, eb);
    servo(CANAL[i], BASE[i]); delay(300);
    if (i >= 4) pwm(CANAL[i], 0, 4096);
    int mp = -1; float dp = 0; for (byte c = 0; c < 16; c++) if (fabs(pb[c] - pa[c]) > dp) { dp = fabs(pb[c] - pa[c]); mp = c; }
    int me = -1; float de = 0; for (byte k = 0; k < 16; k++) if (ea[k] >= 0 && eb[k] >= 0 && fabs(dif(eb[k], ea[k])) > de) { de = fabs(dif(eb[k], ea[k])); me = k; }
    Serial.print(F("R,")); Serial.print(NOM[i]); Serial.print(','); Serial.print(CANAL[i]);
    Serial.print(','); Serial.print(mp); Serial.print(','); Serial.print(dp, 1);
    Serial.print(','); Serial.print(me); Serial.print(','); Serial.print(de, 1);
    // Cambio de cada uno de los 16 encoders (-999 si no responde).
    for (byte k = 0; k < 16; k++) { Serial.print(','); if (ea[k] >= 0 && eb[k] >= 0) Serial.print(dif(eb[k], ea[k]), 1); else Serial.print(-999); }
    Serial.println();
  }
  todoOff(); Serial.println(F("FIN"));
}
void loop() {}

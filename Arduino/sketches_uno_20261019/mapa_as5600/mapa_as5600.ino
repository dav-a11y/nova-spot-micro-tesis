// Mapa servo -> AS5600: mueve cada articulación a base-10 y base+10 (dentro de topes)
// y muestra qué canal de los TCA 0x70/0x71 cambia su ángulo. Al final apaga todas las salidas.
#include <Wire.h>
const byte PCA = 0x40;
const char* NOM[12] = {"coxa1","coxa2","coxa3","coxa4","femur1","femur2","femur3","femur4","tibia1","tibia2","tibia3","tibia4"};
const byte CANAL[12] = {0,1,2,3, 4,5,6,7, 8,9,10,14};
const int  BASE[12]  = {159,45,54,74, 110,100,100,100, 100,80,100,70};
void reg(byte r, byte v) { Wire.beginTransmission(PCA); Wire.write(r); Wire.write(v); Wire.endTransmission(); }
void pwm(byte c, int on, int off) {
  Wire.beginTransmission(PCA); Wire.write(0x06 + 4*c);
  Wire.write(on & 0xFF); Wire.write(on >> 8); Wire.write(off & 0xFF); Wire.write(off >> 8); Wire.endTransmission();
}
void servo(byte c, int ang) { pwm(c, 0, map(constrain(ang, 0, 180), 0, 180, 102, 512)); }
void todoOff() { for (byte c = 0; c < 16; c++) pwm(c, 0, 4096); }
void cerrarTCA() { for (byte t = 0x70; t <= 0x71; t++) { Wire.beginTransmission(t); Wire.write(0); Wire.endTransmission(); } }
float angulo(byte tca, byte ch) {
  cerrarTCA(); Wire.beginTransmission(tca); Wire.write(1 << ch); Wire.endTransmission();
  Wire.beginTransmission(0x36); Wire.write(0x0C);
  if (Wire.endTransmission(false) != 0) return -1;
  if (Wire.requestFrom((uint8_t)0x36, (uint8_t)2) != 2) return -1;
  unsigned int raw = ((Wire.read() << 8) | Wire.read()) & 0x0FFF;
  return raw * 360.0 / 4096.0;
}
void leerTodos(float *v) { for (byte k = 0; k < 16; k++) { float s = 0; int n = 0; for (byte r = 0; r < 4; r++) { float a = angulo(0x70 + k / 8, k % 8); if (a >= 0) { s += a; n++; } } v[k] = n ? s / n : -1; } cerrarTCA(); }
float dif(float a, float b) { float d = a - b; while (d > 180) d -= 360; while (d < -180) d += 360; return d; }
void setup() {
  Serial.begin(115200); Wire.begin(); Wire.setWireTimeout(10000, true);
  // PCA9685 a 50 Hz, sin llamada general.
  reg(0x00, 0x10); reg(0xFE, 121); reg(0x00, 0x20); delay(5); reg(0x00, 0xA0);
  todoOff();
  Serial.println(F("INICIO MAPA AS5600"));
  float a[16], b[16];
  for (byte i = 0; i < 12; i++) {
    servo(CANAL[i], BASE[i] - 10); delay(900); leerTodos(a);
    servo(CANAL[i], BASE[i] + 10); delay(900); leerTodos(b);
    servo(CANAL[i], BASE[i]); delay(400);
    if (i >= 4) pwm(CANAL[i], 0, 4096);  // suelta fémures y tibias tras probarlos
    int mejor = -1; float dmax = 0;
    for (byte k = 0; k < 16; k++) if (a[k] >= 0 && b[k] >= 0 && fabs(dif(b[k], a[k])) > dmax) { dmax = fabs(dif(b[k], a[k])); mejor = k; }
    Serial.print(NOM[i]); Serial.print(F(" (CH")); Serial.print(CANAL[i]); Serial.print(F(") -> "));
    if (mejor >= 0 && dmax > 5) { Serial.print(F("TCA 0x7")); Serial.print(mejor / 8); Serial.print(F(" canal ")); Serial.print(mejor % 8); Serial.print(F(" cambio ")); Serial.print(dif(b[mejor], a[mejor]), 1); Serial.print(F(" grados")); }
    else { Serial.print(F("ningun encoder cambia (max ")); Serial.print(dmax, 1); Serial.print(F(")")); }
    Serial.println();
  }
  todoOff(); Serial.println(F("FIN MAPA (todas las salidas OFF)"));
}
void loop() {}

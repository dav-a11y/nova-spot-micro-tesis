// Prueba eléctrica de las líneas I2C del Uno (A4=SDA, A5=SCL). No usa Wire ni mueve servos.
// Para cada línea: la baja 1 ms, la suelta (INPUT sin pull-up interno) y mide cuándo vuelve a 1.
// También comprueba si bajar una arrastra a la otra (cruce o cortocircuito).
void probar(byte pin, byte otra, const char *nombre) {
  pinMode(otra, INPUT);
  pinMode(pin, OUTPUT); digitalWrite(pin, LOW); delay(1);
  int otraBaja = digitalRead(otra);
  pinMode(pin, INPUT);
  unsigned long t0 = micros(); long subida = -1;
  while (micros() - t0 < 20000) { if (digitalRead(pin)) { subida = micros() - t0; break; } }
  Serial.print(nombre); Serial.print(": vuelve a 1 en ");
  if (subida < 0) Serial.print("NUNCA (>20 ms): sin pull-up -> línea suelta o PCA sin VCC");
  else { Serial.print(subida); Serial.print(" us"); if (subida < 50) Serial.print(" (pull-up externo presente)"); else Serial.print(" (lenta: pull-up débil o línea flotante)"); }
  Serial.print(" | la otra línea al bajar esta = "); Serial.println(otraBaja ? "1 (sin cruce)" : "0 (CRUCE o cortocircuito)");
}
void setup() {
  Serial.begin(115200); delay(300);
  for (byte k = 0; k < 3; k++) {
    probar(A4, A5, "SDA (A4)"); probar(A5, A4, "SCL (A5)");
    pinMode(A4, INPUT); pinMode(A5, INPUT);
    Serial.print("Reposo: SDA="); Serial.print(digitalRead(A4)); Serial.print(" SCL="); Serial.println(digitalRead(A5));
    Serial.println("--"); delay(500);
  }
}
void loop() {}

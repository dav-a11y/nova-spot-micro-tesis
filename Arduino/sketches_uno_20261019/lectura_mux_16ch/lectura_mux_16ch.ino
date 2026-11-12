/*
  Diagnostico de un CD74HC4067 / multiplexor analogico de 16 canales.

  Cableado segun el diagrama actual:
    SIG -> A0
    S3  -> D4
    S2  -> D5
    S1  -> D6
    S0  -> D7
    EN  -> GND (siempre habilitado)
    VCC -> 5 V
    GND -> GND

  Este programa SOLO LEE y transmite por USB. No controla servos ni PWM.
*/

const byte PIN_SIG = A0;
const byte PIN_S0 = 7;
const byte PIN_S1 = 6;
const byte PIN_S2 = 5;
const byte PIN_S3 = 4;

const unsigned long PERIODO_MS = 200;

void seleccionarCanal(byte canal) {
  digitalWrite(PIN_S0, bitRead(canal, 0));
  digitalWrite(PIN_S1, bitRead(canal, 1));
  digitalWrite(PIN_S2, bitRead(canal, 2));
  digitalWrite(PIN_S3, bitRead(canal, 3));
}

int leerCanal(byte canal) {
  seleccionarCanal(canal);
  delayMicroseconds(20);       // tiempo de asentamiento del multiplexor
  analogRead(PIN_SIG);         // descarta una conversion tras cambiar de canal
  return analogRead(PIN_SIG);  // 0..1023, referencia analogica por defecto: 5 V
}

void setup() {
  pinMode(PIN_S0, OUTPUT);
  pinMode(PIN_S1, OUTPUT);
  pinMode(PIN_S2, OUTPUT);
  pinMode(PIN_S3, OUTPUT);
  seleccionarCanal(0);

  Serial.begin(115200);
  delay(300);
  Serial.println(F("MUX_16CH_INICIADO"));
  Serial.println(F("Formato: CH0=valor ... CH15=valor"));
}

void loop() {
  for (byte canal = 0; canal < 16; ++canal) {
    Serial.print(F("CH"));
    Serial.print(canal);
    Serial.print('=');
    Serial.print(leerCanal(canal));
    if (canal < 15) Serial.print(F("  "));
  }
  Serial.println();
  delay(PERIODO_MS);
}

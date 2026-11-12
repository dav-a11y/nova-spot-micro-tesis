/*
  Prueba de movimiento lento del cuadrupedo suspendido.

  Arduino Uno -> PCA9685 (I2C A4=SDA, A5=SCL), direccion 0x40.
  Son servos POSICIONALES de 180 grados. No son servos de giro continuo.

  Comandos por el monitor serie a 115200:
    m : postura estatica y tres ciclos cortos de prueba.
    p : ir solamente a la postura estatica.
    c : calibracion: mueve un servo a la vez +/-8 grados y transmite ADC.
    a : identificacion de coxas (CH0--CH3).
    f : identificacion de femures (CH4--CH7).
    l : identificacion de tibia 1 (inactiva) y tibia 3 (CH10).
    t : tibia 2 a 90 y luego 25 grados, con vigilancia MUX C9.
    e : prueba aislada de tibia 1 (CH12), +/-2 grados desde su centro.
    z : prueba aislada de tibia 3 (CH10), +/-2 grados desde su centro.
    y : secuencia parcial tipo paso en el aire, solo coxas 2-4 y femures.
    g : tibia 4 hacia 150 y luego 15 grados, con vigilancia MUX C10.
    h : sostener tibia 1 (CH12) en 100 grados, sin barrido.
    j : sostener pata 1 (CH0/CH4/CH12) en sus centros, sin barrido.
    n : prueba de tibia 1 por PCA CH12, con CH0/CH4 sosteniendo la pata.
    o : paso minimo de pata 1 hacia atras: F1=110->112 y mantener, en CH0/CH12.
    x : apagar inmediatamente las doce salidas PWM.

  CH9 (tibia 2) permanece fuera de rutinas generales; solo se mueve con el
  ensayo dedicado, gradual y vigilado por su señal local C9.
*/

#include <Wire.h>

// Controlador minimo del PCA9685: evita depender de una biblioteca externa.
class PCA9685 {
 public:
  explicit PCA9685(byte direccion) : direccion_(direccion) {}

  void begin() {
    Wire.begin();
    Wire.setClock(400000);  // 19-oct: PCA9685, TCA9548A y AS5600 admiten 400 kHz
    // 20-oct: si el bus se bloquea (SDA en 0) Wire no se queda esperando para siempre:
    // a los 3 ms aborta y reinicia el bus; las lecturas fallidas salen como -1.
    Wire.setWireTimeout(3000, true);
    escribirRegistro(0x00, 0x00); // MODE1: oscilador activo, sin auto-incremento
    delay(5);
  }

  void setPWMFreq(float frecuencia) {
    // Prescaler del PCA9685: 25 MHz / (4096 * frecuencia) - 1.
    byte prescaler = (byte)(25000000.0 / (4096.0 * frecuencia) - 1.0 + 0.5);
    byte modoAnterior = leerRegistro(0x00);
    escribirRegistro(0x00, (modoAnterior & 0x7F) | 0x10); // SLEEP
    escribirRegistro(0xFE, prescaler);
    escribirRegistro(0x00, modoAnterior);
    delay(5);
    // 19-oct: sin ALLCALL (bit 0), para no chocar con el TCA9548A en 0x70.
    escribirRegistro(0x00, (modoAnterior | 0xA0) & ~0x01); // RESTART + auto-incremento
  }

  void setPWM(byte canal, int encendido, int apagado) {
    if (canal > 15) return;
    Wire.beginTransmission(direccion_);
    Wire.write((byte)(0x06 + 4 * canal));
    Wire.write((byte)(encendido & 0xFF));
    Wire.write((byte)(encendido >> 8));
    Wire.write((byte)(apagado & 0xFF));
    Wire.write((byte)(apagado >> 8));
    Wire.endTransmission();
  }

 private:
  byte direccion_;

  void escribirRegistro(byte registro, byte valor) {
    Wire.beginTransmission(direccion_);
    Wire.write(registro);
    Wire.write(valor);
    Wire.endTransmission();
  }

  byte leerRegistro(byte registro) {
    Wire.beginTransmission(direccion_);
    Wire.write(registro);
    Wire.endTransmission();
    Wire.requestFrom((int)direccion_, 1);
    return Wire.available() ? Wire.read() : 0;
  }
};

PCA9685 pca(0x40);

const int PULSO_MIN = 102;
const int PULSO_MAX = 512;
const int FRECUENCIA_SERVO = 50;
const byte NUM_SERVOS = 12;
const byte PIN_SIG_MUX = A0;
const byte PIN_S0_MUX = 4;  // 19-oct: selectores en D4-D7, D4 = bit de menor peso (S0)
const byte PIN_S1_MUX = 5;
const byte PIN_S2_MUX = 6;
const byte PIN_S3_MUX = 7;
const unsigned long PERIODO_TELEMETRIA_MS = 100;

struct ServoPrueba {
  const char *nombre;
  byte canal;
  int base;       // posicion estatica confirmada por el operador
  int excursion;  // desplazamiento pequeno de la prueba
  bool activo;
};

ServoPrueba servo[NUM_SERVOS] = {
  {"Coxa 1",  0, 159, -5, false}, // 19-oct: equilibrio nuevo 159 (antes 150) // BLOQUEADA: C0=93, fuera de la calibracion local; no ordenar a ciegas
  {"Coxa 2",  1,  42,  5, true},  // 28-oct: 48 -> 42, ajustada en vivo con el operador (a 48 se veía subida); 27-oct: 45 -> 48, el operador veía la pata 2 caída;  // 16-oct: operador indica que 40 queda muy abajo -> 45
  {"Coxa 3",  2,  64,  5, true},  // 27-oct: 61 -> 64, el operador la veía caída  // 19-oct: 72 y 65 chocaban la pata 3 con la 1; 57 no
  {"Coxa 4",  3,  82, -5, true},  // 19-oct: equilibrio colocado a mano por el operador (C2=379)
  {"Femur 1", 4, 110, -4, true},
  {"Femur 2", 5, 100,  4, true},
  {"Femur 3", 6, 100,  4, true},
  {"Femur 4", 7, 100, -4, true},
  {"Tibia 1",12, 100,  4, true},  // 26-oct: el operador la paso de CH8 a CH12 (CH8 no la movia).
  {"Tibia 2", 9, 166,  0, false}, // 27-oct: apoyo nuevo del operador (antes 80) // 19-oct: el operador la paso a CH9.
  {"Tibia 3",10, 100,  4, true},  // 19-oct: el operador la paso a CH10.
  {"Tibia 4",14, 144, -4, false}, // 27-oct: apoyo nuevo del operador (antes 70) // 19-oct: el operador la tiene en CH14 (CH11 y CH12 vacios).
};

int ordenActual[NUM_SERVOS];
const char *estadoActual = "OFF";
unsigned long ultimaTelemetriaMs = 0;

int limitarAngulo(int angulo) {
  return constrain(angulo, 0, 180);
}

// 16-oct: topes absolutos por canal PCA, a partir de los limites medidos por el
// operador con 10 grados de margen.
// Protegen cualquier orden del firmware. Canales sin articulacion: 0-180.
// 19-oct: CH9 = tibia 2, CH10 = tibia 3, CH14 = tibia 4; CH11 y CH12 vacios. Coxa 4 (CH3) con topes
// provisionales 60-105 hasta medir sus limites tras el reajuste.
// 26-oct: tibia 1 en CH12 con los topes que tenia en CH8 (25-160).
// 27-oct: topes de T2 (CH9) 155-180 y T4 (CH14) 130-175 alrededor del apoyo nuevo (166 y 144).
// 27-oct: tibia 1 (CH12) con tope mínimo 18 (antes 25) para darle más recorrido, a pedido del operador.
const byte TOPE_MIN[16] = {105, 10, 25,  60,  30, 45, 40, 25,  25,155,  11,  0,  18,   0, 130,   0};
// 16-oct (barrido de rango con sensores): F2 y F4 dejan de seguir la orden por
// encima de ~135 y T4 por encima de ~105; se limitan ahi.
const byte TOPE_MAX[16] = {170, 85, 90, 105, 140,135,160,135, 160,180, 160,180, 160, 180, 175, 180};

void escribirServo(byte canal, int angulo) {
  angulo = limitarAngulo(angulo);
  if (canal < 16) angulo = constrain(angulo, TOPE_MIN[canal], TOPE_MAX[canal]);
  int pulso = map(angulo, 0, 180, PULSO_MIN, PULSO_MAX);
  pca.setPWM(canal, 0, pulso);
}

void apagarTodos() {
  for (byte canal = 0; canal < 16; ++canal) {
    pca.setPWM(canal, 0, 4096); // FULL_OFF del PCA9685
  }
  estadoActual = "OFF";
  Serial.println(F("PWM APAGADO: CH0--CH15"));
}

void seleccionarCanalMux(byte canal) {
  digitalWrite(PIN_S0_MUX, bitRead(canal, 0));
  digitalWrite(PIN_S1_MUX, bitRead(canal, 1));
  digitalWrite(PIN_S2_MUX, bitRead(canal, 2));
  digitalWrite(PIN_S3_MUX, bitRead(canal, 3));
}

// 19-oct: el modo @ baja a 4 muestras para cumplir el periodo de 30 ms.
byte muestrasMux = 8;

int leerCanalMux(byte canal) {
  seleccionarCanalMux(canal);
  // El condensador de muestreo del ADC debe cargarse tras cambiar el 4067.
  // Es importante cuando se lee el cursor de un potenciometro a traves del MUX.
  delayMicroseconds(500);
  for (byte descarte = 0; descarte < 3; ++descarte) analogRead(PIN_SIG_MUX);
  long suma = 0;
  for (byte muestra = 0; muestra < muestrasMux; ++muestra) suma += analogRead(PIN_SIG_MUX);
  return suma / muestrasMux;
}

// Formato estable para la base de datos:
// DATA,ms,estado,orden_CH0..orden_CH11,ADC_CH0..ADC_CH15
void enviarTelemetriaSiCorresponde() {
  unsigned long ahora = millis();
  if (ahora - ultimaTelemetriaMs < PERIODO_TELEMETRIA_MS) return;
  ultimaTelemetriaMs = ahora;

  Serial.print(F("DATA,"));
  Serial.print(ahora);
  Serial.print(',');
  Serial.print(estadoActual);
  for (byte i = 0; i < NUM_SERVOS; ++i) {
    Serial.print(',');
    Serial.print(ordenActual[i]);
  }
  for (byte canal = 0; canal < 16; ++canal) {
    Serial.print(',');
    Serial.print(leerCanalMux(canal));
  }
  Serial.println();
}

bool paradaSolicitada() {
  while (Serial.available()) {
    char orden = Serial.read();
    if (orden == 'x' || orden == 'X') {
      apagarTodos();
      return true;
    }
  }
  return false;
}

bool esperarConParada(unsigned long milisegundos) {
  unsigned long inicio = millis();
  while (millis() - inicio < milisegundos) {
    if (paradaSolicitada()) return true;
    enviarTelemetriaSiCorresponde();
    delay(5);
  }
  return false;
}

void posturaBase() {
  Serial.println(F("Postura estatica: moviendo servos habilitados."));
  for (byte i = 0; i < NUM_SERVOS; ++i) {
    ordenActual[i] = servo[i].base;
    if (servo[i].activo) escribirServo(servo[i].canal, ordenActual[i]);
  }
  // CH9 queda sin PWM; no se asume un limite seguro para tibia 2.
  pca.setPWM(9, 0, 4096);
  estadoActual = "STAND";
}

bool moverSuave(const int destino[NUM_SERVOS]) {
  bool faltaMover = true;
  while (faltaMover) {
    faltaMover = false;
    for (byte i = 0; i < NUM_SERVOS; ++i) {
      if (!servo[i].activo) continue;
      if (ordenActual[i] < destino[i]) {
        ++ordenActual[i];
        faltaMover = true;
      } else if (ordenActual[i] > destino[i]) {
        --ordenActual[i];
        faltaMover = true;
      }
      escribirServo(servo[i].canal, ordenActual[i]);
    }
    if (paradaSolicitada()) return false;
    enviarTelemetriaSiCorresponde();
    delay(45); // cambio de 1 grado por paso: prueba lenta y visible
  }
  return true;
}

bool moverUnServoSuave(byte indice, int destino) {
  destino = limitarAngulo(destino);
  while (ordenActual[indice] != destino) {
    if (ordenActual[indice] < destino) {
      ++ordenActual[indice];
    } else {
      --ordenActual[indice];
    }
    escribirServo(servo[indice].canal, ordenActual[indice]);
    if (paradaSolicitada()) return false;
    enviarTelemetriaSiCorresponde();
    delay(45);
  }
  return true;
}

// Identifica el canal MUX de cada servo sin alcanzar topes mecanicos.
bool ejecutarCalibracionRango(byte primerIndice, byte ultimoIndice) {
  // Ocho grados siguen lejos de los topes declarados de los once servos activos.
  const int EXCURSION_CALIBRACION = 8;
  // Centra solo el grupo solicitado. No mueve los otros grupos al iniciar.
  for (byte i = primerIndice; i <= ultimoIndice; ++i) {
    if (!servo[i].activo) continue;
    ordenActual[i] = servo[i].base;
    escribirServo(servo[i].canal, servo[i].base);
  }
  estadoActual = "CAL";
  if (esperarConParada(2000)) return false;

  for (byte i = primerIndice; i <= ultimoIndice; ++i) {
    if (!servo[i].activo) continue;
    Serial.print(F("CALIBRANDO "));
    Serial.println(servo[i].nombre);
    if (!moverUnServoSuave(i, servo[i].base + EXCURSION_CALIBRACION)) return false;
    if (esperarConParada(1200)) return false;
    if (!moverUnServoSuave(i, servo[i].base - EXCURSION_CALIBRACION)) return false;
    if (esperarConParada(1200)) return false;
    if (!moverUnServoSuave(i, servo[i].base)) return false;
    if (esperarConParada(600)) return false;
  }
  estadoActual = "STAND";
  Serial.println(F("CALIBRACION INDIVIDUAL TERMINADA"));
  return true;
}

bool ejecutarCalibracionIndividual() {
  return ejecutarCalibracionRango(0, NUM_SERVOS - 1);
}

bool probarTibia2HastaLimitesProximos();

// Prueba aislada: CH9 (tibia 2), con vigilancia de C9.
bool ejecutarPruebaTibias() {
  return probarTibia2HastaLimitesProximos();
}

// Prueba local conservadora tras confirmacion visual de que la articulacion
// fue colocada en su centro. No cambia el PWM ni la orden de las otras patas.
bool ejecutarPruebaTibiaCorta(byte indice, int centro, const char *nombre,
                              const char *estadoSostener) {
  ordenActual[indice] = centro;
  escribirServo(servo[indice].canal, centro);
  estadoActual = "TIBIA_CENTER";
  Serial.print(F("Prueba aislada +/-2 grados: "));
  Serial.println(nombre);
  if (esperarConParada(1500)) return false;

  estadoActual = "TIBIA_TEST";
  if (!moverUnServoSuave(indice, centro + 2) || esperarConParada(1200)) return false;
  if (!moverUnServoSuave(indice, centro) || esperarConParada(800)) return false;
  if (!moverUnServoSuave(indice, centro - 2) || esperarConParada(1200)) return false;
  if (!moverUnServoSuave(indice, centro) || esperarConParada(800)) return false;

  estadoActual = estadoSostener;
  Serial.print(F("Prueba terminada; centro sostenido: "));
  Serial.println(nombre);
  return true;
}

// Avanza una tibia en tramos de hasta 2 grados. Su señal MUX debe cambiar en
// el sentido medido localmente; si no responde, se corta ese canal PCA.
bool moverTibiaVigilada(byte indice, byte canalMux, int objetivo,
                        int minimoCambio, const char *estadoParada,
                        const char *etiqueta) {
  while (ordenActual[indice] != objetivo) {
    int anterior = ordenActual[indice];
    int diferencia = objetivo - anterior;
    int paso = (abs(diferencia) >= 2) ? 2 : 1;
    int siguiente = anterior + ((diferencia > 0) ? paso : -paso);
    int adcAntes = leerCanalMux(canalMux);

    if (!moverUnServoSuave(indice, siguiente) || esperarConParada(120)) {
      return false;
    }

    int adcDespues = leerCanalMux(canalMux);
    int avanceSensor = (siguiente > anterior)
                         ? adcAntes - adcDespues
                         : adcDespues - adcAntes;
    int umbral = (abs(siguiente - anterior) == 1)
                   ? max(1, minimoCambio / 2) : minimoCambio;

    Serial.print(etiqueta);
    Serial.print(',');
    Serial.print(siguiente);
    Serial.print(',');
    Serial.print(adcDespues);
    Serial.print(',');
    Serial.println(avanceSensor);

    if (avanceSensor < umbral) {
      pca.setPWM(servo[indice].canal, 0, 4096);
      estadoActual = estadoParada;
      Serial.println(F("PARADA SEGURA: senal MUX no confirma movimiento; canal apagado."));
      return false;
    }
  }
  return true;
}

bool probarTibia2HastaLimitesProximos() {
  const byte indice = 9;
  const int centro = 80;

  apagarTodos();
  ordenActual[indice] = centro;
  escribirServo(servo[indice].canal, centro);
  estadoActual = "TIBIA2_CENTER";
  Serial.println(F("Tibia 2: C9 vigilado, objetivo 90 y despues 25 grados."));
  if (esperarConParada(1000)) return false;

  estadoActual = "TIBIA2_TO_90";
  if (!moverTibiaVigilada(indice, 9, 90, 3,
                          "TIBIA2_FEEDBACK_STOP", "T2_GUARD")) return false;
  estadoActual = "TIBIA2_AT_90";
  if (esperarConParada(600)) return false;

  estadoActual = "TIBIA2_TO_25";
  if (!moverTibiaVigilada(indice, 9, 25, 3,
                          "TIBIA2_FEEDBACK_STOP", "T2_GUARD")) return false;
  estadoActual = "TIBIA2_AT_25";
  if (esperarConParada(600)) return false;

  apagarTodos();
  Serial.println(F("Tibia 2 alcanzo ambos objetivos; todas las salidas OFF."));
  return true;
}

bool probarTibia4HastaExtremosProximos() {
  const byte indice = 11;
  const int centro = 70;

  apagarTodos();
  ordenActual[indice] = centro;
  escribirServo(servo[indice].canal, centro);
  estadoActual = "TIBIA4_CENTER";
  Serial.println(F("Tibia 4: C10 vigilado, objetivo 150 y despues 15 grados."));
  if (esperarConParada(1000)) return false;

  estadoActual = "TIBIA4_TO_150";
  if (!moverTibiaVigilada(indice, 10, 150, 3,
                          "TIBIA4_FEEDBACK_STOP", "T4_GUARD")) return false;
  estadoActual = "TIBIA4_AT_150";
  if (esperarConParada(600)) return false;

  estadoActual = "TIBIA4_TO_15";
  if (!moverTibiaVigilada(indice, 10, 15, 3,
                          "TIBIA4_FEEDBACK_STOP", "T4_GUARD")) return false;
  estadoActual = "TIBIA4_AT_15";
  if (esperarConParada(600)) return false;

  apagarTodos();
  Serial.println(F("Tibia 4 alcanzo ambos objetivos; todas las salidas OFF."));
  return true;
}

void sostenerTibia1EnCentro() {
  ordenActual[8] = 100;
  escribirServo(servo[8].canal, 100);
  estadoActual = "HOLD_TIBIA1";
  Serial.println(F("Tibia 1 CH12 sostenida en 100 grados; sin barrido."));
}

bool sostenerPata1EnCentros() {
  // La coxa y el femur estabilizan la cadena para distinguir balanceo pasivo
  // de la pata de una oscilacion propia de la tibia 1.
  apagarTodos();
  ordenActual[0] = 150;
  escribirServo(0, 150);
  estadoActual = "PATA1_COXA";
  if (esperarConParada(1200)) return false;

  ordenActual[4] = 110;
  escribirServo(4, 110);
  estadoActual = "PATA1_FEMUR";
  if (esperarConParada(1200)) return false;

  ordenActual[8] = 100;
  escribirServo(servo[8].canal, 100);
  estadoActual = "HOLD_PATA1";
  Serial.println(F("Pata 1 sostenida: CH0=150, CH4=110, tibia1 CH12=100; sin barrido."));
  return true;
}

bool moverIndicePorCanal(byte indice, byte canalPca, int destino) {
  destino = limitarAngulo(destino);
  while (ordenActual[indice] != destino) {
    if (ordenActual[indice] < destino) ++ordenActual[indice];
    else --ordenActual[indice];
    escribirServo(canalPca, ordenActual[indice]);
    if (paradaSolicitada()) return false;
    enviarTelemetriaSiCorresponde();
    delay(45);
  }
  return true;
}

bool probarTibia1EnCanal12() {
  const byte CANAL_TIBIA1 = servo[8].canal;
  apagarTodos();

  ordenActual[0] = 150;
  escribirServo(0, 150);
  estadoActual = "PATA1_COXA";
  if (esperarConParada(1200)) return false;

  ordenActual[4] = 110;
  escribirServo(4, 110);
  estadoActual = "PATA1_FEMUR";
  if (esperarConParada(1200)) return false;

  ordenActual[8] = 100;
  escribirServo(CANAL_TIBIA1, 100);
  estadoActual = "TIBIA1_CH12_CENTER";
  if (esperarConParada(1500)) return false;

  estadoActual = "TIBIA1_CH12_TEST";
  if (!moverIndicePorCanal(8, CANAL_TIBIA1, 102) ||
      esperarConParada(1200)) return false;
  if (!moverIndicePorCanal(8, CANAL_TIBIA1, 100) ||
      esperarConParada(800)) return false;
  if (!moverIndicePorCanal(8, CANAL_TIBIA1, 98) ||
      esperarConParada(1200)) return false;
  if (!moverIndicePorCanal(8, CANAL_TIBIA1, 100) ||
      esperarConParada(800)) return false;

  estadoActual = "HOLD_PATA1_CH12";
  Serial.println(F("Fin CH12: CH0=150, CH4=110, tibia1 CH12=100."));
  return true;
}

bool llevarPata1AtrasYVolver() {
  const byte CANAL_TIBIA1 = servo[8].canal;
  apagarTodos();

  ordenActual[0] = 150;
  escribirServo(0, 150);
  estadoActual = "PATA1_COXA";
  if (esperarConParada(1200)) return false;

  ordenActual[4] = 110;
  escribirServo(4, 110);
  estadoActual = "PATA1_FEMUR_CENTER";
  if (esperarConParada(1200)) return false;

  ordenActual[8] = 100;
  escribirServo(CANAL_TIBIA1, 100);
  estadoActual = "PATA1_TIBIA_CENTER";
  if (esperarConParada(1200)) return false;

  estadoActual = "PATA1_BACKWARD_SMALL_STEP";
  if (!moverIndicePorCanal(4, 4, 112) || esperarConParada(300)) return false;

  estadoActual = "HOLD_PATA1_BACKWARD_112";
  Serial.println(F("Paso minimo: CH4=112; mantener, sin retorno automatico."));
  return true;
}

bool ejecutarPrueba() {
  posturaBase();
  estadoActual = "TEST";
  if (esperarConParada(2500)) return false;

  for (byte ciclo = 0; ciclo < 3; ++ciclo) {
    int objetivo[NUM_SERVOS];
    for (byte i = 0; i < NUM_SERVOS; ++i) {
      objetivo[i] = servo[i].base + servo[i].excursion;
    }
    Serial.print(F("Ciclo "));
    Serial.print(ciclo + 1);
    Serial.println(F("/3: desplazamiento pequeno."));
    if (!moverSuave(objetivo) || esperarConParada(700)) return false;

    for (byte i = 0; i < NUM_SERVOS; ++i) {
      objetivo[i] = servo[i].base - servo[i].excursion;
    }
    if (!moverSuave(objetivo) || esperarConParada(700)) return false;

    for (byte i = 0; i < NUM_SERVOS; ++i) objetivo[i] = servo[i].base;
    if (!moverSuave(objetivo) || esperarConParada(700)) return false;
  }

  Serial.println(F("Prueba terminada. Plataforma en postura estatica."));
  return true;
}

// Prueba mas controlada: servo por servo y agrupada por pata, +/-2 grados.
// Tibia 2 y tibia 4 permanecen excluidas mientras no se habiliten expresamente.
bool ejecutarPruebaSecuencialControlada() {
  const byte ordenPorPata[] = {0, 4, 8, 1, 5, 9, 2, 6, 10, 3, 7, 11};
  const int excursion = 2;

  posturaBase();
  estadoActual = "SEQ";
  if (esperarConParada(1500)) return false;

  for (byte posicion = 0; posicion < NUM_SERVOS; ++posicion) {
    byte indice = ordenPorPata[posicion];
    if (!servo[indice].activo) continue;

    Serial.print(F("Movimiento controlado: "));
    Serial.println(servo[indice].nombre);
    if (!moverUnServoSuave(indice, servo[indice].base + excursion)) return false;
    if (esperarConParada(600)) return false;
    if (!moverUnServoSuave(indice, servo[indice].base - excursion)) return false;
    if (esperarConParada(600)) return false;
    if (!moverUnServoSuave(indice, servo[indice].base)) return false;
    if (esperarConParada(500)) return false;
  }

  estadoActual = "STAND";
  Serial.println(F("Prueba secuencial terminada; articulaciones en centro."));
  return true;
}

// Prueba exclusiva de coxas 2 y 3: coxa 1 se omite porque su ADC C0 no
// concuerda con la calibracion local. No se llama posturaBase(), que moveria
// otras articulaciones. Coxa 4 queda fuera mientras se verifica su caida por
// gravedad. Rampa por escalones de 2 grados hasta +/-16 grados.
bool ejecutarPruebaCoxasPequena() {
  const byte indices[] = {1, 2};
  const int excursionMaxima = 16;
  apagarTodos();
  estadoActual = "COXA";

  for (byte k = 0; k < 2; ++k) {
    byte i = indices[k];
    ordenActual[i] = servo[i].base;
    escribirServo(servo[i].canal, servo[i].base);
    Serial.print(F("COXA centrada: "));
    Serial.println(servo[i].nombre);
    if (esperarConParada(1000)) return false;
  }

  for (byte k = 0; k < 2; ++k) {
    byte i = indices[k];
    Serial.print(F("Rampa coxa en pasos de 2 grados hasta +/-16: "));
    Serial.println(servo[i].nombre);
    for (int excursion = 2; excursion <= excursionMaxima; excursion += 2) {
      if (!moverUnServoSuave(i, servo[i].base + excursion)) return false;
      if (esperarConParada(1200)) return false;
    }
    if (!moverUnServoSuave(i, servo[i].base)) return false;
    if (esperarConParada(800)) return false;
    for (int excursion = 2; excursion <= excursionMaxima; excursion += 2) {
      if (!moverUnServoSuave(i, servo[i].base - excursion)) return false;
      if (esperarConParada(1200)) return false;
    }
    if (!moverUnServoSuave(i, servo[i].base)) return false;
    if (esperarConParada(800)) return false;
  }

  // Conserva el PWM de CH1/CH2 para sostener la carga contra la gravedad.
  // Coxas 1 y 4, y las demas articulaciones, permanecen sin PWM.
  estadoActual = "HOLD_COXA";
  Serial.println(F("Prueba terminada; coxas 2 y 3 en centro y con PWM de sostén. Coxas 1 y 4 sin mover."));
  return true;
}

// Recuperacion prudente de coxa 4 (PCA CH3, MUX C2) tras desplazarse por
// gravedad al cortar PWM. ADC~198 corresponde localmente a 147 grados; una
// lectura menor estima una posicion mayor. La estimacion solo sirve para
// acercarse: se valida la respuesta del potenciometro en pasos de 1 grado.
bool recuperarCoxa4HaciaCentro() {
  const byte indice = 3;
  const byte muxCoxa4 = 2;
  const int adcCentroLocal = 198;
  const float cuentasPorGrado = 2.35f;
  const int adcInicial = leerCanalMux(muxCoxa4);

  Serial.print(F("COXA4 ADC inicial C2="));
  Serial.println(adcInicial);
  if (adcInicial < 30 || adcInicial > 900 || adcInicial >= adcCentroLocal) {
    Serial.println(F("COXA4 sin movimiento: la lectura no coincide con la caida esperada."));
    return false;
  }

  int anguloEstimado = servo[indice].base + (int)((adcCentroLocal - adcInicial) / cuentasPorGrado + 0.5f);
  anguloEstimado = constrain(anguloEstimado, servo[indice].base, 176);
  ordenActual[indice] = anguloEstimado;
  escribirServo(servo[indice].canal, anguloEstimado);
  estadoActual = "COXA4_INICIO";
  Serial.print(F("COXA4 punto inicial aproximado="));
  Serial.println(anguloEstimado);
  if (esperarConParada(1000)) return false;

  int adcPrevio = leerCanalMux(muxCoxa4);
  if (abs(adcPrevio - adcInicial) > 18) {
    estadoActual = "COXA4_HOLD_CHECK";
    Serial.print(F("COXA4 detenida para revisar: cambio inicial ADC="));
    Serial.println(adcPrevio - adcInicial);
    return false; // deja CH3 energizado, no libera la articulacion
  }

  byte pasosSinRespuesta = 0;
  while (ordenActual[indice] > servo[indice].base) {
    int siguiente = max(servo[indice].base, ordenActual[indice] - 1);
    if (!moverUnServoSuave(indice, siguiente)) return false;
    if (esperarConParada(350)) return false;
    int adcActual = leerCanalMux(muxCoxa4);
    int delta = adcActual - adcPrevio; // al bajar el angulo, C2 debe subir
    Serial.print(F("COXA4 paso="));
    Serial.print(ordenActual[indice]);
    Serial.print(F(" ADC="));
    Serial.print(adcActual);
    Serial.print(F(" delta="));
    Serial.println(delta);
    if (delta < -1 || delta > 10) {
      estadoActual = "COXA4_HOLD_CHECK";
      Serial.println(F("COXA4 detenida: respuesta ADC inesperada; CH3 queda sosteniendo."));
      return false;
    }
    if (delta <= 0) {
      ++pasosSinRespuesta;
      if (pasosSinRespuesta >= 3) {
        estadoActual = "COXA4_HOLD_CHECK";
        Serial.println(F("COXA4 detenida: ADC sin respuesta durante 3 pasos; CH3 queda sosteniendo."));
        return false;
      }
    } else {
      pasosSinRespuesta = 0;
    }
    adcPrevio = adcActual;
  }

  if (abs(adcPrevio - adcCentroLocal) > 20) {
    estadoActual = "COXA4_HOLD_CHECK";
    Serial.println(F("COXA4 en pausa cerca del centro, pero ADC fuera de tolerancia; CH3 sostiene."));
    return false;
  }
  estadoActual = "HOLD_COXA4";
  Serial.println(F("COXA4 centrada y sostenida por PWM; otras salidas apagadas."));
  return true;
}

// Caracteriza coxa 4 en un intervalo local creciente. Si la señal
// deja de responder o cambia al sentido incorrecto, detiene el barrido y
// mantiene CH3 energizado en la posición alcanzada.
bool ejecutarBarridoCoxa4() {
  if (!recuperarCoxa4HaciaCentro()) return false;
  const byte indice = 3;
  const byte muxCoxa4 = 2;
  const int excursionMaxima = 20;
  int adcPrevio = leerCanalMux(muxCoxa4);
  byte pasosSinRespuesta = 0;
  estadoActual = "COXA4_TEST";

  for (int direccion = 1; direccion >= -1; direccion -= 2) {
    for (int excursion = 2; excursion <= excursionMaxima; excursion += 2) {
      int objetivo = servo[indice].base + direccion * excursion;
      if (!moverUnServoSuave(indice, objetivo)) return false;
      if (esperarConParada(1200)) return false;
      int adcActual = leerCanalMux(muxCoxa4);
      int delta = direccion > 0 ? adcPrevio - adcActual : adcActual - adcPrevio;
      Serial.print(F("COXA4 barrido angulo="));
      Serial.print(objetivo);
      Serial.print(F(" ADC="));
      Serial.print(adcActual);
      Serial.print(F(" respuesta="));
      Serial.println(delta);
      if (delta < -1 || delta > 18) {
        estadoActual = "COXA4_HOLD_CHECK";
        Serial.println(F("Barrido coxa4 detenido por respuesta inesperada; CH3 sostiene."));
        return false;
      }
      if (delta <= 0) {
        if (++pasosSinRespuesta >= 2) {
          estadoActual = "COXA4_HOLD_CHECK";
          Serial.println(F("Barrido coxa4 detenido por falta de respuesta; CH3 sostiene."));
          return false;
        }
      } else {
        pasosSinRespuesta = 0;
      }
      adcPrevio = adcActual;
    }
    if (!moverUnServoSuave(indice, servo[indice].base)) return false;
    if (esperarConParada(800)) return false;
    adcPrevio = leerCanalMux(muxCoxa4);
    pasosSinRespuesta = 0;
    if (abs(adcPrevio - 198) > 20) {
      estadoActual = "COXA4_HOLD_CHECK";
      Serial.println(F("Barrido coxa4 detenido: retorno fuera de tolerancia; CH3 sostiene."));
      return false;
    }
  }
  estadoActual = "HOLD_COXA4";
  Serial.println(F("Barrido coxa4 +/-8 terminado; CH3 sostiene el centro."));
  return true;
}

// Primera identificacion segura de los cuatro femures: pulsos de ±2°,
// individuales y con pausas para asociar la respuesta ADC de cada MUX.
bool ejecutarPruebaFemuresPequena() {
  const byte indices[] = {4, 5, 6, 7};
  apagarTodos();
  estadoActual = "FEMUR_CENTER";
  for (byte k = 0; k < 4; ++k) {
    byte i = indices[k];
    ordenActual[i] = servo[i].base;
    escribirServo(servo[i].canal, servo[i].base);
    Serial.print(F("FEMUR centro: "));
    Serial.println(servo[i].nombre);
    if (esperarConParada(900)) return false;
  }

  estadoActual = "FEMUR_TEST";
  for (byte k = 0; k < 4; ++k) {
    byte i = indices[k];
    Serial.print(F("FEMUR pulso +/-2: "));
    Serial.println(servo[i].nombre);
    if (!moverUnServoSuave(i, servo[i].base + 2)) return false;
    if (esperarConParada(1000)) return false;
    if (!moverUnServoSuave(i, servo[i].base - 2)) return false;
    if (esperarConParada(1000)) return false;
    if (!moverUnServoSuave(i, servo[i].base)) return false;
    if (esperarConParada(1000)) return false;
  }

  estadoActual = "HOLD_FEMURES";
  Serial.println(F("Prueba inicial de femures terminada; CH4-CH7 sostienen el centro."));
  return true;
}

// Ampliacion gradual de la identificacion femoral: ±2, ±4, ±6, ±8°,
// articulacion por articulacion, retornando al centro entre sentidos.
bool ejecutarBarridoFemures() {
  const byte indices[] = {4, 5, 6, 7};
  const int excursionMaxima = 8;
  apagarTodos();
  estadoActual = "FEMUR_CENTER";
  for (byte k = 0; k < 4; ++k) {
    byte i = indices[k];
    ordenActual[i] = servo[i].base;
    escribirServo(servo[i].canal, servo[i].base);
    Serial.print(F("FEMUR centro: "));
    Serial.println(servo[i].nombre);
    if (esperarConParada(900)) return false;
  }

  for (byte k = 0; k < 4; ++k) {
    byte i = indices[k];
    Serial.print(F("FEMUR barrido +/-8: "));
    Serial.println(servo[i].nombre);
    estadoActual = "FEMUR_TEST";
    for (int direccion = 1; direccion >= -1; direccion -= 2) {
      for (int excursion = 2; excursion <= excursionMaxima; excursion += 2) {
        int objetivo = servo[i].base + direccion * excursion;
        if (!moverUnServoSuave(i, objetivo)) return false;
        if (esperarConParada(800)) return false;
      }
      if (!moverUnServoSuave(i, servo[i].base)) return false;
      if (esperarConParada(700)) return false;
    }
  }

  estadoActual = "HOLD_FEMURES";
  Serial.println(F("Barrido de femures terminado; CH4-CH7 sostienen el centro."));
  return true;
}

// Solo los femures 1 y 3 carecen de canal MUX identificado. Se amplian hasta
// ±16° en pasos de 2°, manteniendo los cuatro femures centrados al terminar.
bool ejecutarPruebaFemuresSinMapa() {
  const byte todos[] = {4, 5, 6, 7};
  const byte sinMapa[] = {4, 6};
  const int excursionMaxima = 16;
  apagarTodos();
  estadoActual = "FEMUR_CENTER";
  for (byte k = 0; k < 4; ++k) {
    byte i = todos[k];
    ordenActual[i] = servo[i].base;
    escribirServo(servo[i].canal, servo[i].base);
    Serial.print(F("FEMUR centro: "));
    Serial.println(servo[i].nombre);
    if (esperarConParada(900)) return false;
  }

  for (byte k = 0; k < 2; ++k) {
    byte i = sinMapa[k];
    Serial.print(F("FEMUR sin mapa, barrido hasta +/-16: "));
    Serial.println(servo[i].nombre);
    estadoActual = "FEMUR_TEST";
    for (int direccion = 1; direccion >= -1; direccion -= 2) {
      for (int excursion = 2; excursion <= excursionMaxima; excursion += 2) {
        int objetivo = servo[i].base + direccion * excursion;
        if (!moverUnServoSuave(i, objetivo)) return false;
        if (esperarConParada(800)) return false;
      }
      if (!moverUnServoSuave(i, servo[i].base)) return false;
      if (esperarConParada(800)) return false;
    }
  }

  estadoActual = "HOLD_FEMURES";
  Serial.println(F("Barrido F1/F3 terminado; CH4-CH7 sostienen el centro."));
  return true;
}

// Ensayo visual de coordinacion tipo paso con el robot suspendido. Las tibias
// quedan siempre sin PWM y coxa 1 se omite por su lectura C0 no validada.
// No es una marcha apoyada ni reproduce una politica PPO.
bool ejecutarPasoParcialEnAire() {
  const byte participantes[] = {1, 2, 3, 4, 5, 6, 7}; // C2-C4 y F1-F4
  apagarTodos();
  for (byte k = 0; k < sizeof(participantes); ++k) {
    byte i = participantes[k];
    ordenActual[i] = servo[i].base;
    escribirServo(servo[i].canal, servo[i].base);
  }
  // Refuerza explicitamente que ninguna tibia ni coxa 1 reciba PWM.
  for (byte canal = 8; canal <= 11; ++canal) pca.setPWM(canal, 0, 4096);
  pca.setPWM(12, 0, 4096);
  estadoActual = "PASO_PARCIAL_CENTRO";
  Serial.println(F("Paso parcial en aire: solo C2-C4 y F1-F4; tibias y C1 apagadas."));
  if (esperarConParada(1000)) return false;

  for (byte ciclo = 0; ciclo < 2; ++ciclo) {
    for (int signo = 1; signo >= -1; signo -= 2) {
      int destino[NUM_SERVOS];
      for (byte i = 0; i < NUM_SERVOS; ++i) destino[i] = servo[i].base;
      // Alternancia diagonal de amplitud minima alrededor de las referencias.
      destino[3] = servo[3].base + signo * 2; // coxa 4
      destino[1] = servo[1].base - signo * 2; // coxa 2
      destino[2] = servo[2].base - signo * 2; // coxa 3
      destino[4] = servo[4].base + signo * 2; // femur 1
      destino[7] = servo[7].base + signo * 2; // femur 4
      destino[5] = servo[5].base - signo * 2; // femur 2
      destino[6] = servo[6].base - signo * 2; // femur 3
      estadoActual = (signo > 0) ? "PASO_PARCIAL_DIAGONAL_A" : "PASO_PARCIAL_DIAGONAL_B";
      for (byte k = 0; k < sizeof(participantes); ++k) {
        byte i = participantes[k];
        if (!moverUnServoSuave(i, destino[i])) return false;
      }
      if (esperarConParada(500)) return false;
    }
  }

  for (byte k = 0; k < sizeof(participantes); ++k) {
    byte i = participantes[k];
    if (!moverUnServoSuave(i, servo[i].base)) return false;
  }
  apagarTodos();
  Serial.println(F("Secuencia parcial terminada; PWM apagado."));
  return true;
}

// Gateo demostrativo EN EL AIRE (robot suspendido), lazo abierto.
// Orden FL(2) -> RR(3) -> FR(1) -> RL(4). Femures +/-6 grados; tibias +/-2..3
// dentro de lo ya probado. Las cuatro coxas sostienen su punto de equilibrio.
// No es una marcha apoyada ni esta validada para el suelo.

// 16-oct: sosten realimentado de coxas 2-4 durante la caminata. Si el
// potenciometro se aleja de su lectura de equilibrio, corrige la orden 1 grado
// (ADC sube cuando el angulo baja, ~-2.4 cuentas/grado), con limite +/-6.
const byte COXA_IDX[3] = {1, 2, 3};
const byte COXA_MUX[3] = {1, 3, 2};
// 27-oct: en el modo '+' la caída por peso de las coxas 2-4 se sigue corrigiendo: corrCoxa[k] se ajusta
// con el potenciómetro solo mientras la coxa está en su base (pata apoyada, cuando carga el peso) y se suma
// siempre a la orden de la marcha (la coxa 2 se caía en el galope sin esta corrección).
int corrCoxa[3] = {0, 0, 0};
int pedidoCoxa[4] = {0, 0, 0, 0};
int coxaRefAdc[3];
float coxaFiltro[3];
unsigned long ultimaCorreccionCoxasMs = 0;
// 19-oct: los potenciometros se desplazan juntos (hasta 30 cuentas) con la corriente
// de los servos. La coxa 1 (C0) no se corrige y solo ve ese desplazamiento: se resta.
int refComunC0 = 0;
void capturarReferenciaCoxas() {
  long sumC0 = 0;
  for (byte n = 0; n < 4; ++n) sumC0 += leerCanalMux(0);
  refComunC0 = sumC0 / 4;
  for (byte k = 0; k < 3; ++k) {
    long sum = 0;
    for (byte n = 0; n < 4; ++n) sum += leerCanalMux(COXA_MUX[k]);
    coxaRefAdc[k] = sum / 4;
    coxaFiltro[k] = coxaRefAdc[k];
  }
}
// Corrige solo la deriva lenta (caida por peso). Las caidas breves del paso se
// atenuan con un promedio movil; las lecturas que saltan > 40 cuentas se ignoran.
void corregirCoxas() {
  int comun = leerCanalMux(0) - refComunC0;
  if (abs(comun) > 80) comun = 0;  // lectura de C0 anomala: sin compensar
  for (byte k = 0; k < 3; ++k) {
    int adc = leerCanalMux(COXA_MUX[k]);
    if (adc < 30 || adc > 950) continue;
    adc -= comun;
    if (abs(adc - coxaFiltro[k]) > 40) continue;
    coxaFiltro[k] = 0.85f * coxaFiltro[k] + 0.15f * adc;
  }
  if (millis() - ultimaCorreccionCoxasMs < 200) return;
  ultimaCorreccionCoxasMs = millis();
  for (byte k = 0; k < 3; ++k) {
    byte i = COXA_IDX[k];
    if (coxaRefAdc[k] < 30 || coxaRefAdc[k] > 950) continue;
    float err = coxaFiltro[k] - coxaRefAdc[k];
    int nuevo = ordenActual[i];
    if (err > 4) nuevo += 1;
    else if (err < -4) nuevo -= 1;
    nuevo = constrain(nuevo, servo[i].base - 6, servo[i].base + 6);
    if (nuevo != ordenActual[i]) {
      ordenActual[i] = nuevo;
      escribirServo(servo[i].canal, nuevo);
    }
  }
}
void corregirCoxasLibres() {
  int comun = leerCanalMux(0) - refComunC0;
  if (abs(comun) > 80) comun = 0;
  for (byte k = 0; k < 3; ++k) {
    int adc = leerCanalMux(COXA_MUX[k]);
    if (adc < 30 || adc > 950) continue;
    adc -= comun;
    if (abs(adc - coxaFiltro[k]) > 40) continue;
    coxaFiltro[k] = 0.85f * coxaFiltro[k] + 0.15f * adc;
  }
  if (millis() - ultimaCorreccionCoxasMs < 200) return;
  ultimaCorreccionCoxasMs = millis();
  for (byte k = 0; k < 3; ++k) {
    byte i = COXA_IDX[k];
    if (coxaRefAdc[k] < 30 || coxaRefAdc[k] > 950) continue;
    if (pedidoCoxa[i] != servo[i].base) continue;      // solo con la pata apoyada
    float err = coxaFiltro[k] - coxaRefAdc[k];
    if (err > 4) corrCoxa[k] += 1;
    else if (err < -4) corrCoxa[k] -= 1;
    corrCoxa[k] = constrain(corrCoxa[k], -6, 6);
  }
}
// 16-oct: 40 ms (0,8 s/fase) -> 25 ms (0,5 s/fase) tras medir seguimiento de F2/F4.
const int PAUSA_PASO_CAMINATA_MS = 25;
bool ejecutarCaminataEnAire() {
  const int A = 15;                                  // amplitud femur (16-oct: 6->10->15)
  const int signoFemur[5] = {0, -1, 1, -1, 1};       // sentido "adelante" por pata
  const int signoTibia[5] = {0, -1, -1, -1, -1};  // 16-oct: T4 invertida (70->56), tramo donde si respondio
  const int ampTibia[5]   = {0, 14, 14, 14, 14};
  const byte ordenPatas[4] = {2, 3, 1, 4};
  // 16-oct: las cuatro coxas se sostienen fijas en sus puntos de equilibrio
  // (C1=159, C2=45, C3=61, C4=82), incluida la coxa 1 (CH0).
  // 16-oct: tibia 1 (indice 8, CH8) fuera de la caminata: su potenciometro
  // interno tiene un tramo danado y produce tirones. Queda sin PWM.
  const byte arranque[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}; // indices servo (19-oct: tibia 1 reparada)
  float offset[5];
  int base[NUM_SERVOS];
  for (byte i = 0; i < NUM_SERVOS; ++i) base[i] = servo[i].base;

  apagarTodos();
  estadoActual = "CAMINATA_ARRANQUE";
  Serial.println(F("Caminata en aire: energizando articulaciones una por una."));
  for (byte k = 0; k < sizeof(arranque); ++k) {
    byte i = arranque[k];
    ordenActual[i] = base[i];
    escribirServo(servo[i].canal, base[i]);
    if (esperarConParada(300)) return false;
  }

  if (esperarConParada(500)) return false;
  capturarReferenciaCoxas();
  // Desfase inicial de cada pata dentro del ciclo de cuatro fases.
  for (byte k = 0; k < 4; ++k) offset[ordenPatas[k]] = -A + k * (2.0f * A / 3.0f);

  // Rampa desde el centro hasta el desfase inicial.
  const byte PASOS = 20;
  for (byte s = 1; s <= PASOS; ++s) {
    for (byte pata = 1; pata <= 4; ++pata) {
      byte f = 3 + pata;
      ordenActual[f] = base[f] + (int)round(signoFemur[pata] * offset[pata] * s / PASOS);
      escribirServo(servo[f].canal, ordenActual[f]);
    }
    if (esperarConParada(40)) return false;
  }

  for (byte ciclo = 0; ciclo < 10; ++ciclo) {  // 16-oct: 4 -> 10 ciclos
    Serial.print(F("Caminata ciclo ")); Serial.println(ciclo + 1);
    for (byte fase = 0; fase < 4; ++fase) {
      byte vuela = ordenPatas[fase];
      estadoActual = "CAMINATA_FASE";
      float inicio[5];
      for (byte pata = 1; pata <= 4; ++pata) inicio[pata] = offset[pata];
      for (byte s = 1; s <= PASOS; ++s) {
        float t = (float)s / PASOS;
        for (byte pata = 1; pata <= 4; ++pata) {
          float o;
          int tib = 0;
          if (pata == vuela) {
            o = inicio[pata] + (2.0f * A) * t;                 // -A -> +A
            tib = (int)round(signoTibia[pata] * ampTibia[pata] * sin(PI * t));
          } else {
            o = inicio[pata] - (2.0f * A / 3.0f) * t;          // empuje hacia atras
          }
          offset[pata] = o;
          byte f = 3 + pata, ti = 7 + pata;
          ordenActual[f] = base[f] + (int)round(signoFemur[pata] * o);
          escribirServo(servo[f].canal, ordenActual[f]);
          ordenActual[ti] = base[ti] + tib;
          escribirServo(servo[ti].canal, ordenActual[ti]);
        }
        corregirCoxas();
        if (esperarConParada(PAUSA_PASO_CAMINATA_MS)) return false;
      }
      if (esperarConParada(150)) return false;
    }
  }

  // Regreso al centro y apagado.
  for (byte s = 1; s <= PASOS; ++s) {
    for (byte pata = 1; pata <= 4; ++pata) {
      byte f = 3 + pata;
      ordenActual[f] = base[f] + (int)round(signoFemur[pata] * offset[pata] * (PASOS - s) / PASOS);
      escribirServo(servo[f].canal, ordenActual[f]);
    }
    if (esperarConParada(40)) return false;
  }
  if (esperarConParada(800)) return false;
  // 16-oct: no soltar las coxas (la coxa 2 cae por su peso). Se apagan solo
  // femures y tibias; las cuatro coxas quedan sostenidas en equilibrio.
  for (byte i = 4; i < NUM_SERVOS; ++i) pca.setPWM(servo[i].canal, 0, 4096);
  estadoActual = "HOLD_EQUILIBRIO";
  Serial.println(F("Caminata terminada; coxas sostenidas en equilibrio, femures y tibias sin PWM."));
  return true;
}

// Identificacion de tibias: recorre PCA CH9..CH15 uno por uno. Cada canal va a
// 90 grados y oscila +/-8 grados (CH9 1 vez, CH10 2 veces, ... CH15 7 veces) para
// que el operador lo reconozca. Apaga cada canal antes de pasar al siguiente.
int ordenIdent = 0;
bool moverCanalSuave(byte canal, int desde, int hasta) {
  int paso = (hasta > desde) ? 1 : -1;
  for (int a = desde; a != hasta; a += paso) {
    ordenIdent = a + paso;
    escribirServo(canal, ordenIdent);
    if (esperarConParada(45)) return false;
  }
  return true;
}
bool identificarCanalesTibias() {
  apagarTodos();
  static char estado[12];
  for (byte canal = 9; canal <= 15; ++canal) {
    byte veces = canal - 8;
    snprintf(estado, sizeof(estado), "IDENT_CH%d", canal);
    estadoActual = estado;
    Serial.print(F("IDENTIFICANDO CH")); Serial.print(canal);
    Serial.print(F(" oscilaciones=")); Serial.println(veces);
    ordenIdent = 90;
    escribirServo(canal, 90);
    if (esperarConParada(1000)) return false;
    for (byte v = 0; v < veces; ++v) {
      if (!moverCanalSuave(canal, 90, 98)) return false;
      if (!moverCanalSuave(canal, 98, 82)) return false;
      if (!moverCanalSuave(canal, 82, 90)) return false;
      if (esperarConParada(250)) return false;
    }
    pca.setPWM(canal, 0, 4096);
    estadoActual = "IDENT_PAUSA";
    if (esperarConParada(2000)) return false;
  }
  apagarTodos();
  Serial.println(F("Identificacion CH9-CH15 terminada; PWM apagado."));
  return true;
}

// Prueba de un solo canal PCA para identificacion visual por el operador.
bool probarUnCanal(byte canal) {
  apagarTodos();
  static char estado[14];
  snprintf(estado, sizeof(estado), "UNO_CH%d", canal);
  estadoActual = estado;
  Serial.print(F("PROBANDO SOLO CH")); Serial.println(canal);
  // 16-oct: amplitud ampliada a +/-20 grados alrededor de 70 (50-90), dentro de
  // los limites declarados de las cuatro tibias.
  ordenIdent = 70;
  escribirServo(canal, 70);
  if (esperarConParada(1000)) return false;
  for (byte v = 0; v < 3; ++v) {
    if (!moverCanalSuave(canal, 70, 90)) return false;
    if (!moverCanalSuave(canal, 90, 50)) return false;
    if (!moverCanalSuave(canal, 50, 70)) return false;
    if (esperarConParada(300)) return false;
  }
  apagarTodos();
  return true;
}

// Prueba amplia de un canal (16-oct): centro y amplitud configurables.
bool probarCanalAmplio(byte canal, int centro, int amp) {
  apagarTodos();
  static char estado[16];
  snprintf(estado, sizeof(estado), "AMPLIO_CH%d", canal);
  estadoActual = estado;
  Serial.print(F("PRUEBA AMPLIA CH")); Serial.println(canal);
  ordenIdent = centro;
  escribirServo(canal, centro);
  if (esperarConParada(1000)) return false;
  for (byte v = 0; v < 3; ++v) {
    if (!moverCanalSuave(canal, centro, centro + amp)) return false;
    if (!moverCanalSuave(canal, centro + amp, centro - amp)) return false;
    if (!moverCanalSuave(canal, centro - amp, centro)) return false;
    if (esperarConParada(300)) return false;
  }
  apagarTodos();
  return true;
}

// Sostiene solo las cuatro coxas en sus puntos de equilibrio, sin caminar.
void sostenerCoxasEquilibrio() {
  apagarTodos();
  for (byte i = 0; i < 4; ++i) {
    ordenActual[i] = servo[i].base;
    escribirServo(servo[i].canal, servo[i].base);
    if (esperarConParada(300)) return;
  }
  estadoActual = "HOLD_EQUILIBRIO";
  Serial.println(F("Coxas sostenidas en equilibrio."));
}

// 16-oct: modo de ejecucion desde el PC (politica PPO). El PC envia lineas
//   S,a0,...,a11\n  (grados de servo por indice; coxas y tibia 1 se ignoran)
// y el Uno responde R,ms,C5,C6,C9,C1,C3,C2,C10,C11 tras aplicar cada linea.
// Seguridad: limites de +/-45 alrededor de la base y topes absolutos por canal, cambio
// maximo 3 grados por linea, coxas fijas con su correccion, tibia 1 sin PWM.
// Si no llega una linea en 300 ms, o llega 'X', sostiene coxas y apaga el resto.

// 19-oct: lectura del AS5600 detras de un TCA9548A (crudo 0-4095, -1 si falla).
// 26-oct: escaneo I2C detras de cada canal de los TCA9548A (orden '^'). Por canal lista las
// direcciones que responden (ACK por SDn/SCn); si hay un AS5600 (0x36) da STATUS (MD iman
// detectado, ML debil, MH fuerte), AGC, MAGNITUDE y RAW ANGLE.
int leerRegistro16(byte dir, byte reg) {
  Wire.beginTransmission(dir); Wire.write(reg);
  if (Wire.endTransmission(false) != 0 || Wire.requestFrom(dir, (uint8_t)2) != 2) return -1;
  return ((Wire.read() << 8) | Wire.read());
}
void escanearI2C() {
  const byte tcas[2] = {0x70, 0x71};
  for (byte t = 0; t < 2; ++t) {
    for (byte c = 0; c < 8; ++c) {
      Wire.beginTransmission(tcas[t]); Wire.write(1 << c);
      byte e = Wire.endTransmission();
      Serial.print(F("I2C,0x")); Serial.print(tcas[t], HEX); Serial.print(','); Serial.print(c);
      if (e != 0) { Serial.println(F(",TCA_SIN_RESPUESTA")); continue; }
      for (byte a = 1; a < 127; ++a) {
        if (a == 0x70 || a == 0x71) continue;
        Wire.beginTransmission(a);
        if (Wire.endTransmission() == 0) { Serial.print(F(",0x")); Serial.print(a, HEX); }
      }
      Wire.beginTransmission(0x36);
      if (Wire.endTransmission() == 0) {
        int st = leerRegistro16(0x36, 0x0B) >> 8;
        Wire.beginTransmission(0x36); Wire.write(0x1A); Wire.endTransmission(false);
        Wire.requestFrom((uint8_t)0x36, (uint8_t)1); int agc = Wire.available() ? Wire.read() : -1;
        Serial.print(F(",MD=")); Serial.print((st >> 5) & 1);
        Serial.print(F(",ML=")); Serial.print((st >> 4) & 1);
        Serial.print(F(",MH=")); Serial.print((st >> 3) & 1);
        Serial.print(F(",AGC=")); Serial.print(agc);
        Serial.print(F(",MAG=")); Serial.print(leerRegistro16(0x36, 0x1B) & 0x0FFF);
        Serial.print(F(",RAW=")); Serial.print(leerRegistro16(0x36, 0x0C) & 0x0FFF);
      }
      Serial.println();
    }
    Wire.beginTransmission(tcas[t]); Wire.write(0); Wire.endTransmission();
  }
  Serial.println(F("FIN_I2C"));
}

int leerAS5600(byte tca, byte canal) {
  Wire.beginTransmission(tca); Wire.write(1 << canal);
  if (Wire.endTransmission() != 0) return -1;
  int raw = -1;
  Wire.beginTransmission(0x36); Wire.write(0x0C);
  if (Wire.endTransmission(false) == 0 && Wire.requestFrom((uint8_t)0x36, (uint8_t)2) == 2) {
    raw = ((Wire.read() << 8) | Wire.read()) & 0x0FFF;
  }
  Wire.beginTransmission(tca); Wire.write(0); Wire.endTransmission();
  return raw;
}
// 26-oct: diagnostico completo (orden '$'): ademas de los campos normales, la respuesta R

// 27-oct: IMU BNO055 (0x28, bus I2C principal). Si responde se pone en modo NDOF (fusion de
// acelerometro, giroscopo y magnetometro) y la respuesta R agrega, tras ENC_F4:
// guinada, roll y pitch en 1/16 de grado, aceleracion lineal x, y, z en cm/s2 y el estado de
// calibracion (CALIB_STAT). Sin IMU los 7 campos valen -1.
const byte BNO = 0x28;
bool hayIMU = false;
bool escribirBNO(byte reg, byte v) {
  Wire.beginTransmission(BNO); Wire.write(reg); Wire.write(v);
  return Wire.endTransmission() == 0;
}
void iniciarIMU() {
  Wire.beginTransmission(BNO);
  hayIMU = Wire.endTransmission() == 0;
  if (!hayIMU) return;
  escribirBNO(0x3D, 0x00); delay(25);      // OPR_MODE = CONFIG
  escribirBNO(0x3E, 0x00); delay(10);      // PWR_MODE = normal
  escribirBNO(0x3B, 0x00);                 // UNIT_SEL: m/s2, grados
  escribirBNO(0x3D, 0x0C); delay(25);      // OPR_MODE = NDOF
}
void imprimirIMU() {
  int v[6] = {-1, -1, -1, -1, -1, -1};
  int cal = -1;
  if (hayIMU) {
    Wire.beginTransmission(BNO); Wire.write(0x1A);
    if (Wire.endTransmission(false) == 0 && Wire.requestFrom(BNO, (uint8_t)6) == 6)
      for (byte k = 0; k < 3; ++k) { byte lo = Wire.read(); v[k] = (int16_t)((Wire.read() << 8) | lo); }
    Wire.beginTransmission(BNO); Wire.write(0x28);
    if (Wire.endTransmission(false) == 0 && Wire.requestFrom(BNO, (uint8_t)6) == 6)
      for (byte k = 3; k < 6; ++k) { byte lo = Wire.read(); v[k] = (int16_t)((Wire.read() << 8) | lo); }
    Wire.beginTransmission(BNO); Wire.write(0x35);
    if (Wire.endTransmission(false) == 0 && Wire.requestFrom(BNO, (uint8_t)1) == 1) cal = Wire.read();
  }
  for (byte k = 0; k < 6; ++k) { Serial.print(','); Serial.print(v[k]); }
  Serial.print(','); Serial.print(cal);
}

// agrega los 16 canales del MUX de potenciometros y los 16 encoders posibles (TCA 0x70/0-7 y 0x71/0-7).
bool diagCompleto = false;
// 27-oct: con la orden '+' el modo de caminata también aplica las órdenes de las coxas (galope) y no las
// fija con corregirCoxas(); los topes absolutos de escribirServo() siguen protegiéndolas.
bool coxasLibres = false;
void terminarStreaming(const __FlashStringHelper *motivo) {
  diagCompleto = false;
  coxasLibres = false;
  for (byte k = 0; k < 3; ++k) corrCoxa[k] = 0;
  for (byte i = 4; i < NUM_SERVOS; ++i) pca.setPWM(servo[i].canal, 0, 4096);
  estadoActual = "HOLD_EQUILIBRIO";
  muestrasMux = 8;
  Serial.print(F("FIN_STREAM ")); Serial.println(motivo);
}
void modoStreaming() {
  apagarTodos();
  const byte arranque[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11};
  for (byte k = 0; k < sizeof(arranque); ++k) {
    byte i = arranque[k];
    ordenActual[i] = servo[i].base;
    escribirServo(servo[i].canal, servo[i].base);
    delay(300);
  }
  delay(500);
  capturarReferenciaCoxas();
  iniciarIMU();
  estadoActual = "STREAM";
  muestrasMux = 4;
  Serial.println(F("STREAM_LISTO"));
  char linea[96];
  unsigned long ultimo = millis();
  while (true) {
    if (!Serial.available()) {
      if (millis() - ultimo > 300) { terminarStreaming(F("timeout")); return; }
      continue;
    }
    size_t n = Serial.readBytesUntil('\n', linea, sizeof(linea) - 1);
    linea[n] = 0;
    if (n == 0) continue;
    if (linea[0] == 'X' || linea[0] == 'x') { terminarStreaming(F("orden")); return; }
    if (linea[0] != 'S') continue;
    int valores[NUM_SERVOS]; byte cuenta = 0;
    char *tok = strtok(linea + 1, ",");
    while (tok && cuenta < NUM_SERVOS) { valores[cuenta++] = atoi(tok); tok = strtok(NULL, ","); }
    if (cuenta != NUM_SERVOS) continue;
    ultimo = millis();
    for (byte i = coxasLibres ? 0 : 4; i < NUM_SERVOS; ++i) {
      int lim = 45;  // 16-oct: los topes absolutos de escribirServo() protegen el rango
      int pedido = valores[i];
      if (i < 4) {
        pedidoCoxa[i] = valores[i];
        for (byte k = 0; k < 3; ++k) if (COXA_IDX[k] == i) pedido += corrCoxa[k];
      }
      int obj = constrain(pedido, servo[i].base - lim, servo[i].base + lim);
      obj = constrain(obj, ordenActual[i] - 3, ordenActual[i] + 3);
      ordenActual[i] = obj;
      escribirServo(servo[i].canal, obj);
    }
    if (coxasLibres) corregirCoxasLibres(); else corregirCoxas();
    Serial.print(F("R,")); Serial.print(millis());
    // 16-oct: se anaden C10 y C11 al final de la respuesta.
    const byte canales[8] = {5, 6, 9, 1, 3, 2, 10, 11};
    for (byte k = 0; k < 8; ++k) { Serial.print(','); Serial.print(leerCanalMux(canales[k])); }
    // 19-oct: angulo crudo (0-4095) del AS5600 de la tibia 2 (TCA 0x70, canal 3); -1 si falla.
    Serial.print(','); Serial.print(leerAS5600(0x70, 3));
    // 19-oct (v6): C0 (coxa 1), C8 (femur 1) y AS5600 de tibia 1 (0x70/0),
    // al final para no mover los campos anteriores.
    Serial.print(','); Serial.print(leerCanalMux(0));
    Serial.print(','); Serial.print(leerCanalMux(8));
    // 26-oct: el campo ENC_T1 lee ahora el encoder del fémur 2, conectado por el operador en 0x70/4.
    Serial.print(','); Serial.print(leerAS5600(0x70, 4));
    // 19-oct: encoders de respaldo de femur 1 (0x70/1) y femur 4 (0x71/5).
    Serial.print(','); Serial.print(leerAS5600(0x70, 1));
    Serial.print(','); Serial.print(leerAS5600(0x71, 5));
    imprimirIMU();
    if (diagCompleto) {
      for (byte c = 0; c < 16; ++c) { Serial.print(','); Serial.print(leerCanalMux(c)); }
      for (byte c = 0; c < 16; ++c) { Serial.print(','); Serial.print(leerAS5600(c < 8 ? 0x70 : 0x71, c % 8)); }
    }
    Serial.println();
  }
}

// 19-oct: identificacion completa del mapa servo -> sensor. Mueve cada
// articulacion sola +/-10 grados alrededor de su base (2 oscilaciones) y deja
// la telemetria DATA con los 16 canales del MUX. Tibia 1 excluida (servo danado).
bool identificarMapaCompleto() {
  const byte orden[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11};
  apagarTodos();
  static char estado[16];
  for (byte k = 0; k < sizeof(orden); ++k) {
    byte i = orden[k];
    snprintf(estado, sizeof(estado), "MAPA_I%d", i);
    estadoActual = estado;
    ordenActual[i] = servo[i].base;
    escribirServo(servo[i].canal, servo[i].base);
    if (esperarConParada(700)) return false;
    for (byte v = 0; v < 2; ++v) {
      if (!moverUnServoSuave(i, servo[i].base + 10) || esperarConParada(300)) return false;
      if (!moverUnServoSuave(i, servo[i].base - 10) || esperarConParada(300)) return false;
    }
    if (!moverUnServoSuave(i, servo[i].base) || esperarConParada(300)) return false;
    if (i >= 4) pca.setPWM(servo[i].canal, 0, 4096);  // suelta femur/tibia; coxas quedan sostenidas
  }
  for (byte i = 4; i < NUM_SERVOS; ++i) pca.setPWM(servo[i].canal, 0, 4096);
  estadoActual = "HOLD_EQUILIBRIO";
  Serial.println(F("Mapa completo terminado; coxas sostenidas."));
  return true;
}

// 19-oct: reposo sostenido. Lleva cada articulacion a su base, una por una
// (coxas primero), y la deja sostenida con PWM.
void reposoSostenido() {
  apagarTodos();
  const byte orden[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11};
  for (byte k = 0; k < sizeof(orden); ++k) {
    byte i = orden[k];
    ordenActual[i] = servo[i].base;
    escribirServo(servo[i].canal, servo[i].base);
    delay(300);
  }
  estadoActual = "HOLD_REPOSO";
  Serial.println(F("Reposo sostenido: las 12 articulaciones en su base."));
}

// 19-oct: identifica el sensor de UNA articulacion. Orden '!' seguida de un
// caracter '0'..'9','a','b' (indice del servo). Mueve solo esa articulacion
// +/-10 grados alrededor de su base (2 oscilaciones) con telemetria DATA.
void identificarUna(byte i) {
  apagarTodos();
  static char estado[12];
  snprintf(estado, sizeof(estado), "UNA_I%d", i);
  ordenActual[i] = servo[i].base;
  escribirServo(servo[i].canal, servo[i].base);
  estadoActual = estado;
  if (esperarConParada(800)) return;
  for (byte v = 0; v < 2; ++v) {
    if (!moverUnServoSuave(i, servo[i].base + 10) || esperarConParada(400)) return;
    if (!moverUnServoSuave(i, servo[i].base - 10) || esperarConParada(400)) return;
  }
  if (!moverUnServoSuave(i, servo[i].base) || esperarConParada(400)) return;
  apagarTodos();
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_S0_MUX, OUTPUT);
  pinMode(PIN_S1_MUX, OUTPUT);
  pinMode(PIN_S2_MUX, OUTPUT);
  pinMode(PIN_S3_MUX, OUTPUT);
  seleccionarCanalMux(0);
  for (byte i = 0; i < NUM_SERVOS; ++i) ordenActual[i] = servo[i].base;
  pca.begin();
  pca.setPWMFreq(FRECUENCIA_SERVO);
  delay(10);
  apagarTodos();
  Serial.println(F("LISTO. k=F1/F3 hasta +/-16, v=femures hasta +/-8, u=femures +/-2, w=coxa4 hasta +/-12, r=recuperar coxa4, q=coxas2-3, m=movimiento, s=secuencial, p=postura, c=todo, a=coxas, f=femures +/-8, l=tibias, t=tibia2 a 90 y 25 con C9 vigilado, e=tibia1 CH12 +/-2, z=tibia3 CH10 +/-2, y=paso parcial en aire C2-C4/F1-F4 con tibias/C1 apagadas, g=tibia4 a 150 y luego 15 con C10 vigilado, h=tibia1 CH12 sostener 100, j=pata1 sostener centros CH12, n=tibia1 CH12 +/-2, o=pata1 atras paso de 2 grados, x=apagar."));
}

void loop() {
  enviarTelemetriaSiCorresponde();
  if (!Serial.available()) return;

  char orden = Serial.read();
  if (orden == 'k' || orden == 'K') {
    ejecutarPruebaFemuresSinMapa();
  } else if (orden == 'v' || orden == 'V') {
    ejecutarBarridoFemures();
  } else if (orden == 'u' || orden == 'U') {
    ejecutarPruebaFemuresPequena();
  } else if (orden == 'w' || orden == 'W') {
    ejecutarBarridoCoxa4();
  } else if (orden == 'r' || orden == 'R') {
    recuperarCoxa4HaciaCentro();
  } else if (orden == 'q' || orden == 'Q') {
    ejecutarPruebaCoxasPequena();
  } else if (orden == 'm' || orden == 'M') {
    ejecutarPrueba();
  } else if (orden == 's' || orden == 'S') {
    ejecutarPruebaSecuencialControlada();
  } else if (orden == 'p' || orden == 'P') {
    posturaBase();
    Serial.println(F("Postura estatica aplicada."));
  } else if (orden == 'c' || orden == 'C') {
    ejecutarCalibracionIndividual();
  } else if (orden == 'a' || orden == 'A') {
    ejecutarCalibracionRango(0, 3);
  } else if (orden == 'f' || orden == 'F') {
    ejecutarCalibracionRango(4, 7);
  } else if (orden == 'l' || orden == 'L') {
    ejecutarCalibracionRango(8, 10);
  } else if (orden == 't' || orden == 'T') {
    ejecutarPruebaTibias();
  } else if (orden == 'e' || orden == 'E') {
    ejecutarPruebaTibiaCorta(8, 100, "Tibia 1 CH12", "HOLD_TIBIA1");
  } else if (orden == 'z' || orden == 'Z') {
    ejecutarPruebaTibiaCorta(10, 100, "Tibia 3 CH10", "HOLD_TIBIA3");
  } else if (orden == 'y' || orden == 'Y') {
    ejecutarPasoParcialEnAire();
  } else if (orden == 'g' || orden == 'G') {
    probarTibia4HastaExtremosProximos();
  } else if (orden == 'h' || orden == 'H') {
    sostenerTibia1EnCentro();
  } else if (orden == 'j' || orden == 'J') {
    sostenerPata1EnCentros();
  } else if (orden == 'n' || orden == 'N') {
    probarTibia1EnCanal12();
  } else if (orden == 'o' || orden == 'O') {
    llevarPata1AtrasYVolver();
  } else if (orden >= '0' && orden <= '5') {
    probarUnCanal(10 + (orden - '0'));
  } else if (orden == '!') {
    unsigned long t0 = millis();
    while (!Serial.available() && millis() - t0 < 2000) {}
    char c = Serial.read();
    int i = (c >= '0' && c <= '9') ? c - '0' : (c == 'a' ? 10 : (c == 'b' ? 11 : -1));
    if (i >= 0) identificarUna(i);
  } else if (orden == '&') {
    reposoSostenido();
  } else if (orden == '%') {
    identificarMapaCompleto();
  } else if (orden == '@') {
    modoStreaming();
  } else if (orden == '^') {
    escanearI2C();
  } else if (orden == '+') {
    coxasLibres = true;
    modoStreaming();
  } else if (orden == '$') {
    diagCompleto = true;
    modoStreaming();
  } else if (orden == '#') {
    sostenerCoxasEquilibrio();
  } else if (orden == 'd' || orden == 'D') {
    probarCanalAmplio(0, 150, 20);  // CH0 coxa 1, 130-170 grados
  } else if (orden == '6') {
    probarCanalAmplio(1, 40, 20);  // CH1 coxa 2, 20-60 grados
  } else if (orden == '7') {
    probarCanalAmplio(8, 80, 40);
  } else if (orden == '8') {
    probarUnCanal(8);
  } else if (orden == '9') {
    probarUnCanal(9);
  } else if (orden == 'i' || orden == 'I') {
    identificarCanalesTibias();
  } else if (orden == 'b' || orden == 'B') {
    ejecutarCaminataEnAire();
  } else if (orden == 'x' || orden == 'X') {
    apagarTodos();
  }
}

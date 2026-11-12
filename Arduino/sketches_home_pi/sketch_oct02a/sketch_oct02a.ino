// PRUEBA 12 AS5600 CON 2 MULTIPLEXORES TCA9548A
// TCA 0x70 y TCA 0x71
//
// TOMA 500 MUESTRAS DE CADA ARTICULACION
// Y AL FINAL MUESTRA:
// - MINIMO
// - MAXIMO
// - PROMEDIO
// - VARIACION TOTAL
// - ESTADO DE ESTABILIDAD

#include <Wire.h>

#define TCA1 0x70
#define TCA2 0x71

#define AS5600 0x36
#define RAW_ANGLE 0x0C

#define NUM_SENSORES 12
#define NUM_MUESTRAS 100


// ==================================================
// NOMBRES DE LOS SENSORES
// ==================================================

const char* nombres[NUM_SENSORES] = {
  "COXA 1",
  "COXA 2",
  "COXA 3",
  "COXA 4",

  "FEMUR 1",
  "FEMUR 2",
  "FEMUR 3",
  "FEMUR 4",

  "TIBIA 1",
  "TIBIA 2",
  "TIBIA 3",
  "TIBIA 4"
};


// ==================================================
// VARIABLES PARA EL ANALISIS
// ==================================================

float minimo[NUM_SENSORES];
float maximo[NUM_SENSORES];

double suma[NUM_SENSORES];

unsigned long contador[NUM_SENSORES];

bool pruebaTerminada = false;


// ==================================================
// Seleccionar canal del TCA9548A
// ==================================================

bool seleccionarCanal(byte direccionTCA, byte canal) {

  Wire.beginTransmission(direccionTCA);
  Wire.write(1 << canal);

  byte error = Wire.endTransmission();

  if (error != 0) {

    Serial.print("ERROR TCA 0x");
    Serial.print(direccionTCA, HEX);

    Serial.print(" canal ");
    Serial.print(canal);

    Serial.print(" codigo = ");
    Serial.println(error);

    return false;
  }

  delay(2);

  return true;
}


// ==================================================
// Apagar todos los canales del TCA
// ==================================================

void apagarTCA(byte direccionTCA) {

  Wire.beginTransmission(direccionTCA);
  Wire.write(0);
  Wire.endTransmission();
}


// ==================================================
// Leer un AS5600
// ==================================================

float leerAS5600(byte direccionTCA, byte canal) {

  // Apagar ambos multiplexores antes de seleccionar
  apagarTCA(TCA1);
  apagarTCA(TCA2);

  if (!seleccionarCanal(direccionTCA, canal)) {
    return -1;
  }


  // Comprobar que el AS5600 responde
  Wire.beginTransmission(AS5600);

  byte error = Wire.endTransmission();

  if (error != 0) {

    apagarTCA(direccionTCA);

    return -1;
  }


  // Seleccionar registro RAW ANGLE
  Wire.beginTransmission(AS5600);

  Wire.write(RAW_ANGLE);

  error = Wire.endTransmission(false);

  if (error != 0) {

    apagarTCA(direccionTCA);

    return -1;
  }


  // Leer 2 bytes
  byte cantidad = Wire.requestFrom(AS5600, (byte)2);

  if (cantidad != 2) {

    apagarTCA(direccionTCA);

    return -1;
  }


  byte alto = Wire.read();
  byte bajo = Wire.read();


  // Unir los 2 bytes
  uint16_t raw = ((uint16_t)alto << 8) | bajo;

  raw &= 0x0FFF;


  // Apagar canal despues de leer
  apagarTCA(direccionTCA);


  // Convertir a grados
  float angulo = raw * 360.0 / 4096.0;

  return angulo;
}


// ==================================================
// Guardar datos para cada sensor
// ==================================================

void guardarValor(byte sensor, float angulo) {

  if (angulo < 0) {
    return;
  }


  // Primera lectura
  if (contador[sensor] == 0) {

    minimo[sensor] = angulo;
    maximo[sensor] = angulo;

  } else {

    if (angulo < minimo[sensor]) {
      minimo[sensor] = angulo;
    }

    if (angulo > maximo[sensor]) {
      maximo[sensor] = angulo;
    }
  }


  suma[sensor] += angulo;

  contador[sensor]++;
}


// ==================================================
// Mostrar sensor
// ==================================================

void mostrarSensor(
  byte numeroSensor,
  const char* nombre,
  byte direccionTCA,
  byte canal
) {

  float angulo = leerAS5600(direccionTCA, canal);

  Serial.print(nombre);

  Serial.print("  |  TCA 0x");
  Serial.print(direccionTCA, HEX);

  Serial.print("  Canal ");
  Serial.print(canal);

  Serial.print("  |  ");

  if (angulo >= 0) {

    Serial.print(angulo, 2);
    Serial.println(" grados");


    if (contador[numeroSensor] < NUM_MUESTRAS) {

      guardarValor(numeroSensor, angulo);
    }

  } else {

    Serial.println("SIN SENSOR / ERROR");
  }

  delay(5);
}


// ==================================================
// Verificar si todos llegaron a 500 muestras
// ==================================================

bool muestrasCompletas() {

  for (byte i = 0; i < NUM_SENSORES; i++) {

    if (contador[i] < NUM_MUESTRAS) {

      return false;
    }
  }

  return true;
}


// ==================================================
// Mostrar resultados finales
// ==================================================

void mostrarResultados() {

  Serial.println();
  Serial.println();
  Serial.println("===============================================");
  Serial.println("        RESULTADOS DE 500 MUESTRAS");
  Serial.println("===============================================");
  Serial.println();


  for (byte i = 0; i < NUM_SENSORES; i++) {

    float promedio = suma[i] / contador[i];

    float variacion = maximo[i] - minimo[i];


    Serial.println("-----------------------------------------------");

    Serial.print("SENSOR: ");
    Serial.println(nombres[i]);


    Serial.print("Muestras: ");
    Serial.println(contador[i]);


    Serial.print("Minimo: ");
    Serial.print(minimo[i], 3);
    Serial.println(" grados");


    Serial.print("Maximo: ");
    Serial.print(maximo[i], 3);
    Serial.println(" grados");


    Serial.print("Promedio: ");
    Serial.print(promedio, 3);
    Serial.println(" grados");


    Serial.print("Variacion total: ");
    Serial.print(variacion, 3);
    Serial.println(" grados");


    Serial.print("ESTADO: ");


    if (variacion <= 0.30) {

      Serial.println("SE MANTIENE MUY ESTABLE");

    }

    else if (variacion <= 0.70) {

      Serial.println("SE MANTIENE ESTABLE");

    }

    else if (variacion <= 1.50) {

      Serial.println("EL VALOR VARIA MODERADAMENTE");

    }

    else {

      Serial.println("EL VALOR ESTA VARIANDO MUCHO");
    }
  }


  Serial.println();
  Serial.println("===============================================");
  Serial.println("              FIN DE LA PRUEBA");
  Serial.println("===============================================");
}


// ==================================================
// SETUP
// ==================================================

void setup() {

  Serial.begin(115200);

  Wire.begin();

  Wire.setWireTimeout(10000, true);


  Serial.println();
  Serial.println("======================================");
  Serial.println("       SPOT MICRO - 12 AS5600");
  Serial.println("       2 x TCA9548A");
  Serial.println("======================================");


  apagarTCA(TCA1);
  apagarTCA(TCA2);


  for (byte i = 0; i < NUM_SENSORES; i++) {

    minimo[i] = 0;
    maximo[i] = 0;

    suma[i] = 0;

    contador[i] = 0;
  }


  delay(100);
}


// ==================================================
// LOOP
// ==================================================

void loop() {

  if (pruebaTerminada) {

    delay(1000);

    return;
  }


  Serial.println();
  Serial.println("========== NUEVA LECTURA ==========");


  // ==================================================
  // COXAS
  // ==================================================

  mostrarSensor(0, "COXA 1 ", TCA2, 3);

  mostrarSensor(1, "COXA 2 ", TCA2, 5);

  mostrarSensor(2, "COXA 3 ", TCA1, 5);

  mostrarSensor(3, "COXA 4 ", TCA1, 2);


  // ==================================================
  // FEMURES
  // ==================================================

  mostrarSensor(4, "FEMUR 1", TCA2, 1);

  mostrarSensor(5, "FEMUR 2", TCA2, 6);

  mostrarSensor(6, "FEMUR 3", TCA1, 4);

  mostrarSensor(7, "FEMUR 4", TCA1, 1);


  // ==================================================
  // TIBIAS
  // ==================================================

  mostrarSensor(8, "TIBIA 1", TCA2, 0);

  mostrarSensor(9, "TIBIA 2", TCA2, 4);

  mostrarSensor(10, "TIBIA 3", TCA1, 3);

  mostrarSensor(11, "TIBIA 4", TCA1, 0);


  Serial.println("--------------------------------------");


  Serial.print("Muestras tomadas: ");
  Serial.print(contador[0]);

  Serial.print(" / ");
  Serial.println(NUM_MUESTRAS);


  if (muestrasCompletas()) {

    pruebaTerminada = true;

    mostrarResultados();

    return;
  }


  delay(500);
}

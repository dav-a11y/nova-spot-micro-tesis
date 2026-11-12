// ============================================================
// PRUEBA 3 SERVOS + TCA9548A
//
// COXA 1:
// Servo  -> PCA9685 CH0
// Sensor -> TCA9548A CH3
//
// FEMUR 1:
// Servo  -> PCA9685 CH4
// Sensor -> TCA9548A CH1
//
// TIBIA 1:
// Servo  -> PCA9685 CH8
// Sensor -> TCA9548A CH0
//
// Los 3 servos giran a la MISMA VELOCIDAD.
// La velocidad aumenta progresivamente.
// ============================================================

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>


// ============================================================
// PCA9685
// ============================================================

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);

#define SERVO_FREQ 50

#define COXA_SERVO   0
#define FEMUR_SERVO  4
#define TIBIA_SERVO  8


// ============================================================
// TCA9548A
// ============================================================

#define TCA_ADDR 0x71

#define COXA_SENSOR_CH   3
#define FEMUR_SENSOR_CH  1
#define TIBIA_SENSOR_CH  0


// ============================================================
// VELOCIDAD DE LOS SERVOS CONTINUOS
//
// 7.5 = aproximadamente STOP
//
// Menor que 7.5 -> un sentido
// Mayor que 7.5 -> otro sentido
// ============================================================

#define STOP 7.5


// Velocidad inicial
#define VELOCIDAD_INICIAL 7.5

// Velocidad máxima
#define VELOCIDAD_MAXIMA 6.0

// Incremento de velocidad
#define PASO_VELOCIDAD 0.1

// Tiempo entre incrementos
#define TIEMPO_INCREMENTO 200


// ============================================================
// Seleccionar canal del TCA9548A
// ============================================================

void seleccionarTCA(uint8_t canal)
{
  if (canal > 7)
    return;

  Wire.beginTransmission(TCA_ADDR);

  Wire.write(1 << canal);

  Wire.endTransmission();
}


// ============================================================
// ENVIAR PWM A LOS 3 SERVOS
//
// Los tres reciben exactamente el mismo porcentaje.
// Por lo tanto, los tres aumentan/disminuyen su
// velocidad simultáneamente.
// ============================================================

void enviarCiclo(float porcentaje)
{
  int valorPWM = (porcentaje / 100.0) * 4096.0;

  pwm.setPWM(COXA_SERVO,  0, valorPWM);
  pwm.setPWM(FEMUR_SERVO, 0, valorPWM);
  pwm.setPWM(TIBIA_SERVO, 0, valorPWM);

  // Apagar los demás canales
  int off = 4096;

  pwm.setPWM(1,  0, off);
  pwm.setPWM(2,  0, off);
  pwm.setPWM(3,  0, off);
  pwm.setPWM(5,  0, off);
  pwm.setPWM(6,  0, off);
  pwm.setPWM(7,  0, off);
  pwm.setPWM(9,  0, off);
  pwm.setPWM(10, 0, off);
  pwm.setPWM(11, 0, off);
}


// ============================================================
// DETENER LOS 3 SERVOS
// ============================================================

void detenerServos()
{
  enviarCiclo(STOP);
}


// ============================================================
// LEER SENSOR COXA
// TCA CH3
// ============================================================

void leerSensorCoxa()
{
  seleccionarTCA(COXA_SENSOR_CH);

  Serial.print("COXA sensor: ");

  // AQUÍ irá la lectura específica del sensor
  Serial.println("seleccionado");
}


// ============================================================
// LEER SENSOR FEMUR
// TCA CH1
// ============================================================

void leerSensorFemur()
{
  seleccionarTCA(FEMUR_SENSOR_CH);

  Serial.print("FEMUR sensor: ");

  // AQUÍ irá la lectura específica del sensor
  Serial.println("seleccionado");
}


// ============================================================
// LEER SENSOR TIBIA
// TCA CH0
// ============================================================

void leerSensorTibia()
{
  seleccionarTCA(TIBIA_SENSOR_CH);

  Serial.print("TIBIA sensor: ");

  // AQUÍ irá la lectura específica del sensor
  Serial.println("seleccionado");
}


// ============================================================
// LEER LOS 3 SENSORES
// ============================================================

void leerTodosLosSensores()
{
  leerSensorCoxa();
  leerSensorFemur();
  leerSensorTibia();
}


// ============================================================
// ACELERAR LOS 3 SERVOS
//
// Empieza lento y aumenta progresivamente.
//
// Los tres reciben exactamente el mismo valor,
// por lo que la velocidad se incrementa de manera
// simultánea.
// ============================================================

void acelerarTodos()
{
  Serial.println("Acelerando...");

  float velocidad = VELOCIDAD_INICIAL;

  while (velocidad >= VELOCIDAD_MAXIMA)
  {
    enviarCiclo(velocidad);

    // Leer sensores durante el movimiento
    leerTodosLosSensores();

    velocidad -= PASO_VELOCIDAD;

    delay(TIEMPO_INCREMENTO);
  }
}


// ============================================================
// FRENAR PROGRESIVAMENTE
// ============================================================

void desacelerarTodos()
{
  Serial.println("Desacelerando...");

  float velocidad = VELOCIDAD_MAXIMA;

  while (velocidad <= STOP)
  {
    enviarCiclo(velocidad);

    leerTodosLosSensores();

    velocidad += PASO_VELOCIDAD;

    delay(TIEMPO_INCREMENTO);
  }

  detenerServos();
}


// ============================================================
// SETUP
// ============================================================

void setup()
{
  Serial.begin(115200);

  Wire.begin();

  // PCA9685
  pwm.begin();

  pwm.setOscillatorFrequency(27000000);

  pwm.setPWMFreq(SERVO_FREQ);

  delay(500);

  // Inicialmente detener
  detenerServos();

  Serial.println("Sistema iniciado.");
}


// ============================================================
// LOOP
// ============================================================

void loop()
{
  // ----------------------------------------
  // 1. Acelerar en un sentido
  // ----------------------------------------

  Serial.println();
  Serial.println(">>> SENTIDO 1");

  acelerarTodos();

  delay(1000);


  // ----------------------------------------
  // 2. Detener
  // ----------------------------------------

  detenerServos();

  delay(1000);


  // ----------------------------------------
  // 3. Acelerar en sentido contrario
  // ----------------------------------------

  Serial.println();
  Serial.println(">>> SENTIDO 2");

  float velocidad = 7.5;

  while (velocidad <= 9.0)
  {
    enviarCiclo(velocidad);

    leerTodosLosSensores();

    velocidad += 0.1;

    delay(TIEMPO_INCREMENTO);
  }


  // ----------------------------------------
  // 4. Mantener un momento
  // ----------------------------------------

  delay(1000);


  // ----------------------------------------
  // 5. Detener
  // ----------------------------------------

  detenerServos();

  delay(2000);
}

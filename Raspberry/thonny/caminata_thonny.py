"""Programa para abrir en Thonny en la Raspberry Pi y mover el cuadrúpedo.

Antes de ejecutar:
- PCA9685 conectado a la Pi: VCC -> pin 1 (3,3 V), SDA -> pin 3, SCL -> pin 5,
  GND -> pin 6, OE -> pin 11 (GPIO17). Comprobar con `i2cdetect -y 1` que
  aparece 0x40.
- Fuente de servos en V+ del PCA9685, con GND común.
- Robot suspendido y alguien junto al corte de la fuente.

Escribe en la consola de Thonny la opción del menú. Ctrl+C detiene la
caminata y deja las coxas sostenidas.
"""
from robot_nova import RobotNova

MENU = """
  1  Coxas al equilibrio (150, 45, 55, 150) y sostenerlas
  2  Postura base completa
  3  Caminata base (fémur 15°, tibia 10°, 0,5 s por fase), 4 ciclos
  4  Caminata base, 10 ciclos
  s  Soltar fémures y tibias (coxas sostenidas)
  x  Apagar todo y salir
"""


def main():
    if input("Robot suspendido y despejado. Escribe MOVER para habilitar el PCA9685: ").strip() != "MOVER":
        print("Cancelado; no se habilitó el PWM.")
        return
    robot = RobotNova()
    robot.armar()
    try:
        robot.sostener_coxas()
        while True:
            op = input(MENU + "Opción: ").strip().lower()
            if op == "1":
                robot.sostener_coxas()
            elif op == "2":
                robot.postura_base()
            elif op in ("3", "4"):
                robot.postura_base()
                robot.caminar(ciclos=4 if op == "3" else 10)
                robot.soltar_patas()
                print("Caminata terminada; coxas sostenidas.")
            elif op == "s":
                robot.soltar_patas()
            elif op == "x":
                break
    except KeyboardInterrupt:
        robot.soltar_patas()
        print("Detenido: fémures y tibias sin PWM, coxas sostenidas.")
        input("Pulsa Enter para apagar también las coxas y salir...")
    finally:
        robot.cerrar()
        print("PWM apagado (OE en alto).")


if __name__ == "__main__":
    main()

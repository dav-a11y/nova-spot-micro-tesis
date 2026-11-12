#!/usr/bin/env python3
"""Visor 3D local para revisar la postura inicial de una pata.

No conecta con ROS, SSH ni PWM. Los angulos son la referencia nominal del
modelo y no sustituyen la calibracion de los sensores AS5600.
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, Slider


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "nova_gait_controller"))
from nova_gait_controller.kinematics import (  # noqa: E402
    BODY_LENGTH,
    BODY_WIDTH,
    COXA_LENGTH,
    FEMUR_LENGTH,
    HIP_SPACING_X,
    HIP_SPACING_Y,
    TIBIA_LENGTH,
)


STAND = np.array([0.10, 0.42, -0.84], dtype=float)
HIP_X = HIP_SPACING_X / 2.0
HIP_Y = HIP_SPACING_Y / 2.0
COLORS = {1: "#d95f02", 2: "#2ca25f", 3: "#3b5bdb", 4: "#de4b63"}
NAMES = {
    1: "Pata 1 - delantera derecha",
    2: "Pata 2 - delantera izquierda",
    3: "Pata 3 - trasera derecha",
    4: "Pata 4 - trasera izquierda",
}


def leg_points(q, leg):
    """Return hip, coxa, knee and foot points in the body frame."""
    front = leg in (1, 2)
    left = leg in (2, 4)
    hip = np.array([HIP_X if front else -HIP_X,
                    HIP_Y if left else -HIP_Y, 0.0])
    side = 1.0 if left else -1.0
    q_coxa, q_femur, q_tibia = q
    angle = side * q_coxa

    def rotate_planar(x, planar_z):
        return np.array([
            hip[0] + x,
            hip[1] + np.cos(angle) * side * COXA_LENGTH
            - np.sin(angle) * planar_z,
            hip[2] + np.sin(angle) * side * COXA_LENGTH
            + np.cos(angle) * planar_z,
        ])

    coxa = rotate_planar(0.0, 0.0)
    knee = rotate_planar(-FEMUR_LENGTH * np.sin(q_femur),
                         -FEMUR_LENGTH * np.cos(q_femur))
    foot = rotate_planar(
        -FEMUR_LENGTH * np.sin(q_femur)
        - TIBIA_LENGTH * np.sin(q_femur + q_tibia),
        -FEMUR_LENGTH * np.cos(q_femur)
        - TIBIA_LENGTH * np.cos(q_femur + q_tibia),
    )
    return np.vstack((hip, coxa, knee, foot))


def draw_body(ax):
    corners = np.array([
        [HIP_X, HIP_Y, 0], [HIP_X, -HIP_Y, 0],
        [-HIP_X, -HIP_Y, 0], [-HIP_X, HIP_Y, 0], [HIP_X, HIP_Y, 0],
    ])
    ax.plot(corners[:, 0], corners[:, 1], corners[:, 2], color="#20252b", lw=4)


def make_figure(selected_leg, initial_q=None):
    fig = plt.figure(figsize=(11, 8))
    ax = fig.add_axes([0.06, 0.24, 0.68, 0.70], projection="3d")
    initial_q = STAND.copy() if initial_q is None else np.asarray(initial_q, dtype=float)
    selected = [selected_leg]
    poses = {leg: STAND.copy() for leg in range(1, 5)}
    poses[selected_leg] = initial_q.copy()
    leg_lines = {}
    foot_points = {}
    for leg in range(1, 5):
        points = leg_points(poses[leg], leg)
        color = COLORS[leg]
        alpha = 1.0 if leg == selected_leg else 0.45
        line, = ax.plot(points[:, 0], points[:, 1], points[:, 2],
                        "o-", lw=5 if leg == selected_leg else 2.5,
                        ms=7, color=color, alpha=alpha,
                        label=NAMES[leg])
        leg_lines[leg] = line
        foot_points[leg] = ax.scatter(*points[-1], s=55 if leg == selected_leg else 25,
                                      color=color, alpha=alpha)

    draw_body(ax)
    ax.set_title(f"Postura inicial 3D - {NAMES[selected[0]]}")
    ax.set_xlabel("X longitudinal (m)")
    ax.set_ylabel("Y lateral (m)")
    ax.set_zlabel("Z vertical (m)")
    ax.set_xlim(-max(0.30, BODY_LENGTH), max(0.30, BODY_LENGTH))
    ax.set_ylim(-max(0.30, BODY_WIDTH), max(0.30, BODY_WIDTH))
    ax.set_zlim(-0.32, 0.10)
    ax.invert_yaxis()
    ax.set_box_aspect((1.3, 1.0, 0.85))
    # Vista frontal: desde el frente del robot, su derecha queda a la derecha
    # de la figura y su izquierda a la izquierda.
    ax.view_init(elev=24, azim=122)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=8)
    fig.text(
        0.06,
        0.215,
        "Geometria medida: coxa 1.50 in | femur 4.25 in | tibia 5.35 in",
        fontsize=9,
        color="#343a40",
    )

    axes = []
    sliders = []
    labels = ("Coxa", "Femur", "Tibia")
    # Los rangos ampliados de coxa y tibia son exploratorios y solo afectan
    # este visor 3D. No son límites físicos ni autorizan comandos a servos.
    limits = ((-3.00, 3.00), (-1.20, 1.20), (-3.00, 1.00))
    for index, (label, (low, high)) in enumerate(zip(labels, limits)):
        slider_ax = fig.add_axes([0.10, 0.16 - index * 0.045, 0.54, 0.025])
        slider = Slider(slider_ax, label, low, high, valinit=poses[selected_leg][index], valstep=0.01)
        sliders.append(slider)

    def refresh():
        for leg in range(1, 5):
            points = leg_points(poses[leg], leg)
            leg_lines[leg].set_data(points[:, 0], points[:, 1])
            leg_lines[leg].set_3d_properties(points[:, 2])
            foot_points[leg]._offsets3d = ([points[-1, 0]], [points[-1, 1]], [points[-1, 2]])
            active = leg == selected[0]
            leg_lines[leg].set_alpha(1.0 if active else 0.45)
            leg_lines[leg].set_linewidth(5 if active else 2.5)
            foot_points[leg].set_alpha(1.0 if active else 0.45)
        ax.set_title(f"Postura inicial 3D - {NAMES[selected[0]]}")
        fig.canvas.draw_idle()

    def update(_value=None):
        values = np.array([slider.val for slider in sliders])
        poses[selected[0]] = values
        refresh()

    for slider in sliders:
        slider.on_changed(update)

    reset_ax = fig.add_axes([0.70, 0.08, 0.12, 0.045])
    save_ax = fig.add_axes([0.84, 0.08, 0.12, 0.045])
    reset_button = Button(reset_ax, "Reiniciar")
    save_button = Button(save_ax, "Guardar PNG + CSV")

    leg_buttons = {}
    for index, leg in enumerate(range(1, 5)):
        button_ax = fig.add_axes([0.78, 0.42 - index * 0.06, 0.18, 0.045])
        button = Button(button_ax, f"Pata {leg}", color=COLORS[leg], hovercolor="#dddddd")
        leg_buttons[leg] = button

    def reset(_event):
        for slider, value in zip(sliders, STAND):
            slider.set_val(value)
        poses[selected[0]] = STAND.copy()
        refresh()

    def select_leg(leg):
        poses[selected[0]] = np.array([slider.val for slider in sliders])
        selected[0] = leg
        for slider, value in zip(sliders, poses[leg]):
            slider.set_val(value)
        refresh()

    def save(_event):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = ROOT / "Experimentos" / f"pose_3d_{stamp}.png"
        positions = ROOT / "Experimentos" / f"pose_3d_{stamp}.csv"
        fig.savefig(output, dpi=180, bbox_inches="tight")
        with positions.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(("pata", "descripcion", "coxa_rad", "femur_rad",
                             "tibia_rad", "fuente"))
            for leg in range(1, 5):
                writer.writerow((leg, NAMES[leg], *poses[leg],
                                 "ajuste_visual_manual_no_calibrado"))
        print(f"Captura guardada en: {output}")
        print(f"Posiciones guardadas en: {positions}")

    reset_button.on_clicked(reset)
    save_button.on_clicked(save)
    for leg, button in leg_buttons.items():
        button.on_clicked(lambda _event, value=leg: select_leg(value))
    # Mantener referencias para que Matplotlib no recoja los controles y sus
    # callbacks después de retornar desde esta función.
    fig._pose_controls = (reset_button, save_button, *sliders, *leg_buttons.values())
    return fig


def main():
    parser = argparse.ArgumentParser(description="Visor 3D de postura inicial")
    parser.add_argument("--pata", type=int, choices=(1, 2, 3, 4), default=1)
    parser.add_argument("--coxa", type=float, default=None)
    parser.add_argument("--femur", type=float, default=None)
    parser.add_argument("--tibia", type=float, default=None)
    args = parser.parse_args()
    values = (args.coxa, args.femur, args.tibia)
    initial_q = None if all(value is None for value in values) else values
    if initial_q is not None and any(value is None for value in values):
        parser.error("--coxa, --femur y --tibia deben usarse juntos")
    make_figure(args.pata, initial_q)
    plt.show()


if __name__ == "__main__":
    main()

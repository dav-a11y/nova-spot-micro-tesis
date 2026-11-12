#!/usr/bin/env python3
"""Simulación quieta en la postura base (cuerpo fijo en el aire, como el robot colgado)."""
import time
import mujoco
import mujoco.viewer
import entrenar_ppo_real as E

m = mujoco.MjModel.from_xml_path(str(E.MODEL))
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
d.qpos[2] = 0.5
mujoco.mj_forward(m, d)
with mujoco.viewer.launch_passive(m, d) as v:
    v.cam.distance, v.cam.elevation, v.cam.azimuth = 0.8, -5, 90
    v.cam.lookat[:] = d.xpos[1]
    while v.is_running():
        mujoco.mj_forward(m, d)          # sin integrar: postura fija
        v.sync()
        time.sleep(0.05)

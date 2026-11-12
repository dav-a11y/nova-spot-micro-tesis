#!/usr/bin/env python3
"""Exporta la red de acción de una política PPO (Stable-Baselines3, MlpPolicy)
a un .npz para ejecutarla en la Raspberry solo con NumPy (sin PyTorch).
Se ejecuta en el PC con el entorno .venv-mujoco."""
import json, sys
from pathlib import Path
import numpy as np
from stable_baselines3 import PPO

origen = Path(sys.argv[1]); destino = Path(sys.argv[2])
m = PPO.load(origen, device="cpu")
capas = [l for l in m.policy.mlp_extractor.policy_net if hasattr(l, "weight")]
pesos = {f"W{i}": l.weight.detach().numpy() for i, l in enumerate(capas)}
pesos.update({f"b{i}": l.bias.detach().numpy() for i, l in enumerate(capas)})
pesos["Wa"] = m.policy.action_net.weight.detach().numpy()
pesos["ba"] = m.policy.action_net.bias.detach().numpy()
meta = json.loads(origen.with_name("metadata.json").read_text()) if origen.with_name("metadata.json").exists() else {}
np.savez(destino, **pesos, metadata=json.dumps(meta))
# Comprobación: misma acción determinista que SB3.
rng = np.random.default_rng(0)
def adelante(o):
    h = o
    for i in range(len(capas)):
        h = np.tanh(h @ pesos[f"W{i}"].T + pesos[f"b{i}"])
    return np.clip(h @ pesos["Wa"].T + pesos["ba"], -1, 1)
err = max(np.abs(adelante(o) - m.predict(o, deterministic=True)[0]).max()
          for o in rng.normal(size=(200, m.observation_space.shape[0])).astype(np.float32))
print(f"Exportado {destino} | capas ocultas {[pesos[f'W{i}'].shape for i in range(len(capas))]} | error máximo frente a SB3: {err:.2e}")

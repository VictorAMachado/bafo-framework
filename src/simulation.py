import numpy as np


def simulate_trajectory(P, estado_inicial, deg_inicial, n_steps, impacto, beta):
    estados = [estado_inicial]
    deg = [deg_inicial]

    base = impacto[2]
    impacto_rel = {k: v - base for k, v in impacto.items()}

    for _ in range(n_steps):
        estado_atual = estados[-1]
        estado_next = np.random.choice(len(P), p=P[estado_atual])

        deg_next = (1 - beta) * deg[-1] + impacto_rel[estado_next]
        deg_next = max(0, deg_next)

        estados.append(estado_next)
        deg.append(deg_next)

    return np.array(estados), np.array(deg)
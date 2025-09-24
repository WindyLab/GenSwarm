# benchmark_orca_vs_official.py
# -*- coding: utf-8 -*-
import time
import math
import numpy as np
import rvo2

from orca  import (
    AgentState,
    compute_velocity_orca,
    compute_velocity_vr_orca,
)

# ---------- 公共配置 ----------
CONFIG = {
    'SEED': 42,
    'N_AGENTS': 10,
    'ARENA_SIDE': 40.0,
    'CIRCLE_RADIUS': 12.0,
    'MAX_SPEED': 1.0,

    # 时间参数（两者等价，库里用 TIME_STEP，这里仿真里也用 DT）
    'TIME_STEP': 0.1,
    'GOAL_TOL': 0.5,

    'AGENT_RADIUS': 0.35,
    'NEIGHBOR_RANGE': 6.0,
    'TIME_HORIZON': 5.0,
    'MAX_STEPS': 2000,

    # ---- VR-ORCA ----
    'GAMMA': 100.0,
    'ALPHA_INIT': 0.5,
    'ALPHA_MIN': 0.0,
    'ALPHA_MAX': 1.0,
    'GRAD_STEPS': 5,
    'FD_EPS': 1e-4,
    'ALPHA_LR': 0.2,
}
# 兼容老字段名
CONFIG['DT'] = CONFIG['TIME_STEP']

np.random.seed(CONFIG['SEED'])

# ---------- 生成一致的初始场景 ----------
def make_circle(N, side, r):
    center = side / 2.0
    pos, goal = [], []
    for i in range(N):
        th = 2 * math.pi * i / N
        p = np.array([center + r * math.cos(th), center + r * math.sin(th)], float)
        g = np.array([center - r * math.cos(th), center - r * math.sin(th)], float)
        pos.append(p); goal.append(g)
    return np.stack(pos), np.stack(goal)

def make_random(N, side):
    pos = np.random.uniform(1.0, side - 1.0, size=(N, 2)).astype(float)
    goal = np.random.uniform(1.0, side - 1.0, size=(N, 2)).astype(float)
    return pos, goal

# ---------- 指标计算 ----------
def compute_metrics(history, goals, cfg):
    H = np.stack(history, axis=0)          # (T, N, 2)
    T, N, _ = H.shape

    disp = np.diff(H, axis=0)              # (T-1, N, 2)
    total_traveled = np.linalg.norm(disp, axis=2).sum()

    total_straight = np.linalg.norm(H[0] - goals, axis=1).sum()
    distance_ratio = total_traveled / (total_straight + 1e-9)

    time_to_finish = (T - 1) * cfg['DT']
    avg_straight_dist = total_straight / N
    time_ideal = avg_straight_dist / cfg['MAX_SPEED']
    time_ratio = time_to_finish / (time_ideal + 1e-9)

    # 最大穿透比（>0 代表重叠）
    max_pen_ratio = 0.0
    for t in range(T):
        pos = H[t]
        for i in range(N):
            for j in range(i + 1, N):
                d = np.linalg.norm(pos[i] - pos[j])
                pen = max(0.0, (2 * cfg['AGENT_RADIUS'] - d) / cfg['AGENT_RADIUS'])
                max_pen_ratio = max(max_pen_ratio, pen)

    return {
        'time_s': time_to_finish,
        'steps': T - 1,
        'time_ratio': time_ratio,
        'distance_ratio': distance_ratio,
        'max_penetration_ratio': max_pen_ratio,
    }

# ---------- 官方 ORCA（PyRVO2）基线 ----------
def run_official_orca(initial_pos, goals, cfg):
    N = initial_pos.shape[0]
    sim = rvo2.PyRVOSimulator(
        cfg['DT'],                 # timeStep
        cfg['NEIGHBOR_RANGE'],     # neighborDist
        200,                       # maxNeighbors
        cfg['TIME_HORIZON'],       # timeHorizon
        cfg['TIME_HORIZON'],       # timeHorizonObst
        cfg['AGENT_RADIUS'],       # radius
        cfg['MAX_SPEED']           # maxSpeed
    )

    ids = []
    for i in range(N):
        aid = sim.addAgent(
            tuple(initial_pos[i]),
            cfg['NEIGHBOR_RANGE'],
            200,
            cfg['TIME_HORIZON'],
            cfg['TIME_HORIZON'],
            cfg['AGENT_RADIUS'],
            cfg['MAX_SPEED'],
            (0.0, 0.0),
        )
        ids.append(aid)

    history = [initial_pos.copy()]
    t0 = time.time()
    for _ in range(cfg['MAX_STEPS']):
        for i, aid in enumerate(ids):
            p = np.array(sim.getAgentPosition(aid))
            d = goals[i] - p
            n = np.linalg.norm(d)
            v_pref = (d / n * min(cfg['MAX_SPEED'], n)) if n > 1e-9 else np.zeros(2)
            sim.setAgentPrefVelocity(aid, tuple(v_pref))
        sim.doStep()
        cur = np.array([sim.getAgentPosition(aid) for aid in ids])
        history.append(cur)

        if np.all(np.linalg.norm(cur - goals, axis=1) < cfg['GOAL_TOL']):
            break
    dt_wall = time.time() - t0
    return compute_metrics(history, goals, cfg) | {'wall_time_s': dt_wall}, history

# ---------- 你的 ORCA/VR-ORCA 实现 ----------
def _neighbors(i, positions, cfg):
    N = positions.shape[0]
    idxs = []
    rng2 = cfg['NEIGHBOR_RANGE'] * cfg['NEIGHBOR_RANGE']
    pi = positions[i]
    for j in range(N):
        if j == i:
            continue
        if np.sum((pi - positions[j])**2) <= rng2:
            idxs.append(j)
    return idxs

def run_custom(initial_pos, goals, cfg, mode='ORCA'):
    N = initial_pos.shape[0]
    positions = initial_pos.copy()
    velocities = np.zeros_like(positions)
    history = [positions.copy()]

    algo = compute_velocity_orca if mode == 'ORCA' else compute_velocity_vr_orca

    t0 = time.time()
    for _ in range(cfg['MAX_STEPS']):
        new_v = np.zeros_like(velocities)
        for i in range(N):
            me = AgentState(
                id=i,
                position=positions[i],
                velocity=velocities[i],
                goal=goals[i],
                radius=cfg['AGENT_RADIUS'],
                max_speed=cfg['MAX_SPEED'],
            )
            neigh = []
            for j in _neighbors(i, positions, cfg):
                neigh.append(AgentState(
                    id=j,
                    position=positions[j],
                    velocity=velocities[j],
                    goal=goals[j],
                    radius=cfg['AGENT_RADIUS'],
                    max_speed=cfg['MAX_SPEED'],
                ))
            new_v[i] = algo(me, neigh, cfg)
        velocities = new_v
        positions = positions + velocities * cfg['DT']
        history.append(positions.copy())

        if np.all(np.linalg.norm(positions - goals, axis=1) < cfg['GOAL_TOL']):
            break
    dt_wall = time.time() - t0
    return compute_metrics(history, goals, cfg) | {'wall_time_s': dt_wall}, history

# ---------- 统一跑两种场景并打印对比 ----------
def run_suite():
    scenarios = {
        'circle': make_circle(CONFIG['N_AGENTS'], CONFIG['ARENA_SIDE'], CONFIG['CIRCLE_RADIUS']),
        'random': make_random(CONFIG['N_AGENTS'], CONFIG['ARENA_SIDE']),
    }
    for name, (pos, goal) in scenarios.items():
        print(f"\n=== Scenario: {name} ===")
        res_off, _ = run_official_orca(pos, goal, CONFIG)
        res_my_orca, _ = run_custom(pos, goal, CONFIG, 'ORCA')
        res_my_vr, _ = run_custom(pos, goal, CONFIG, 'VR-ORCA')

        def fmt(r):
            return (f"steps={r['steps']:4d}  sim_time={r['time_s']:6.2f}s  wall={r['wall_time_s']:6.2f}s  "
                    f"time_ratio={r['time_ratio']:.3f}  dist_ratio={r['distance_ratio']:.3f}  "
                    f"max_pen={r['max_penetration_ratio']:.4f}")

        print("Official ORCA:    ", fmt(res_off))
        print("Your ORCA:        ", fmt(res_my_orca))
        print("Your VR-ORCA:     ", fmt(res_my_vr))

if __name__ == "__main__":
    run_suite()

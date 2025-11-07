#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import shutil
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams["legend.fontsize"] = 18   # 图注
plt.rcParams["axes.titlesize"] = 20    # 标题
plt.rcParams["axes.labelsize"] = 18    # 坐标轴 label
plt.rcParams["xtick.labelsize"] = 18   # x 轴刻度字体
plt.rcParams["ytick.labelsize"] = 18 # y 轴刻度字体

from itertools import permutations

# 如果安装了 scipy，就会使用匈牙利算法加速，否则走暴力枚举
try:
    from scipy.optimize import linear_sum_assignment, minimize
    USE_SCIPY = True
except ImportError:
    USE_SCIPY = False

# ====== 用户需要修改的部分 ======
LOG_DIR = "/home/yons/Desktop/genswarm_VIDEO/genswarn_logs"
OUTPUT_PARENT = "/home/yons/Desktop/genswarm_VIDEO/genswarn_logs/pics"
THRESHOLD_SECONDS = 50.0   # 仅保留从起点算起的前 50 秒数据
# ===============================

def read_log_with_forward_fill(filepath):
    data = []
    prev_prey_obs = None
    prev_robot_obs = {}
    prev_self_pos = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line.strip())
            timestamp = float(entry["timestamp"])

            self_pos = np.array((entry["self_position"][0], entry["self_position"][1]), dtype=float)
            observed_prey_field = np.array(entry["prey_position"], dtype=float)

            actual_list = [
                (obs["position"]["x"], obs["position"]["y"])
                for obs in entry["observations"] if obs["type"] == "Prey"
            ]
            if actual_list:
                actual_prey_obs = np.array(actual_list[0], dtype=float)
            else:
                if prev_prey_obs is None:
                    actual_prey_obs = observed_prey_field.copy()
                else:
                    actual_prey_obs = prev_prey_obs.copy()
            prev_prey_obs = actual_prey_obs

            current_robot_obs = {}
            for obs in entry["observations"]:
                if obs["type"] == "Robot":
                    rid = obs["id"]
                    current_robot_obs[rid] = np.array((obs["position"]["x"], obs["position"]["y"]), dtype=float)
            for rid, prev_pos in prev_robot_obs.items():
                if rid not in current_robot_obs:
                    current_robot_obs[rid] = prev_pos.copy()
            prev_robot_obs = {rid: pos.copy() for rid, pos in current_robot_obs.items()}

            if self_pos is None and prev_self_pos is not None:
                self_pos = prev_self_pos.copy()
            prev_self_pos = self_pos

            data.append({
                "timestamp": timestamp,
                "self_position": self_pos,
                "observed_prey_field": observed_prey_field,
                "actual_prey_obs": actual_prey_obs,
                "observed_robots": current_robot_obs
            })
    return data

def minimal_matching_and_distances(robot_positions, ideal_positions):
    N = robot_positions.shape[0]
    cost_matrix = np.linalg.norm(
        robot_positions[:, None, :] - ideal_positions[None, :, :], axis=2
    )
    if USE_SCIPY:
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
    else:
        best = np.inf
        best_perm = None
        for perm in permutations(range(N)):
            cost = cost_matrix[np.arange(N), perm].sum()
            if cost < best:
                best = cost
                best_perm = perm
        row_ind = np.arange(N)
        col_ind = np.array(best_perm)
    distances = cost_matrix[row_ind, col_ind]
    avg = distances.mean()
    return avg, distances

def estimate_noise_params(distances, errors_xy):
    def neg_log_likelihood(params):
        sigma0, alpha = params
        if sigma0 <= 0 or alpha < 0:
            return np.inf
        sigma_i = sigma0 * (1 + alpha * distances)
        sq_err = errors_xy[:,0]**2 + errors_xy[:,1]**2
        nll = np.sum(2 * np.log(sigma_i) + sq_err / (2 * sigma_i**2))
        return nll

    init = np.array([0.1, 1.0])
    bounds = [(1e-8, None), (0, None)]
    res = minimize(neg_log_likelihood, init, bounds=bounds)
    if res.success:
        return res.x
    else:
        return None

def process_single_log(log_path, output_dir):
    data_all = read_log_with_forward_fill(log_path)
    if not data_all:
        return

    ts_all = np.array([d["timestamp"] for d in data_all], dtype=float)
    t0 = ts_all[0]
    rel_times_all = ts_all - t0
    mask = rel_times_all <= THRESHOLD_SECONDS
    if not np.any(mask):
        return

    data = [data_all[i] for i in range(len(data_all)) if mask[i]]
    times = rel_times_all[mask]

    robot_ids = sorted(data[0]["observed_robots"].keys())
    N = len(robot_ids)

    obs_field_positions = np.vstack([d["observed_prey_field"] for d in data])
    actual_obs_positions = np.vstack([d["actual_prey_obs"] for d in data])
    errors_xy = obs_field_positions - actual_obs_positions
    prey_field_errors = np.linalg.norm(errors_xy, axis=1)

    distances = np.array([np.linalg.norm(d["self_position"] - d["actual_prey_obs"]) for d in data])
    if USE_SCIPY:
        params = estimate_noise_params(distances, errors_xy)
        if params is not None:
            sigma0_est, alpha_est = params
        else:
            sigma0_est, alpha_est = np.nan, np.nan
    else:
        sigma0_est, alpha_est = np.nan, np.nan

    first_center_act = data[0]["actual_prey_obs"]
    first_robot_positions = np.vstack([data[0]["observed_robots"][rid] for rid in robot_ids])
    rel_act = first_robot_positions - first_center_act
    R_act = np.linalg.norm(rel_act, axis=1).mean()
    angles = np.deg2rad(np.arange(0, 360, 360/N))
    ideal_offsets_act = np.column_stack((R_act * np.cos(angles), R_act * np.sin(angles)))

    avg_errors_act = []
    per_robot_errors = []
    for d in data:
        center = d["actual_prey_obs"]
        robot_pos = np.vstack([d["observed_robots"][rid] for rid in robot_ids])
        ideal_pos = center + ideal_offsets_act
        avg_err, dists = minimal_matching_and_distances(robot_pos, ideal_pos)
        avg_errors_act.append(avg_err)
        per_robot_errors.append(dists)
    per_robot_errors = np.array(per_robot_errors)

    # 计算各时间的平均(平均曲线本身）和整体平均
    mean_over_time = np.mean(per_robot_errors, axis=1)
    overall_mean = mean_over_time.mean()

    fig, axs = plt.subplots(2, 1, sharex=True, figsize=(10, 8))
    fig.patch.set_facecolor('white')

    mu = prey_field_errors.mean()
    sigma = prey_field_errors.std(ddof=0)
    axs[0].plot(times, prey_field_errors,
                marker='o', linestyle='-', color='Thistle',
                linewidth=1.5, markersize=4, label="Error(t)")
    axs[0].axhline(mu, color='DarkMagenta', linestyle='--', linewidth=1, label="Mean Error")
    axs[0].fill_between(times, mu - sigma, mu + sigma,
                        color='LightGray', alpha=0.4, label="Std Dev")
    axs[0].set_ylim(0, 2)
    axs[0].set_ylabel("Error (m)")
    axs[0].set_title("Actual Prey Position vs Robot Observation")
    axs[0].grid(True)
    axs[0].legend(loc="upper right")

    arr = np.array(avg_errors_act)
    ymin = 0
    ymax = 1.8  # 固定 y 轴范围为 0–4 米
    axs[1].plot(times, avg_errors_act,
                linestyle='-', color='LightGreen',
                linewidth=1.5, label="Average Error")
    min_err = per_robot_errors.min(axis=1)
    max_err = per_robot_errors.max(axis=1)
    axs[1].fill_between(times, min_err, max_err, color='LightGreen', alpha=0.2, label="Min-Max Range")
    axs[1].axhline(overall_mean, color='DarkGreen', linestyle='--', linewidth=1, label="Overall Mean")
    axs[1].set_ylim(ymin, ymax)
    axs[1].set_xlabel("Time (s)")
    axs[1].set_ylabel("Error (m)")
    axs[1].set_title("Robot Encirclement Error")
    axs[1].grid(True)
    axs[1].legend(loc="upper right")

    plt.tight_layout()
    if USE_SCIPY:
        fname = f"sigma0_{sigma0_est:.3f}_alpha_{alpha_est:.3f}.png"
    else:
        fname = "combined_errors.png"
    combined_path = os.path.join(output_dir, fname)
    plt.savefig(combined_path, dpi=300)
    plt.close(fig)

    shutil.copy(log_path, os.path.join(output_dir, os.path.basename(log_path)))
    print(f"[SAVED] {combined_path}")

def main():
    if not os.path.isdir(LOG_DIR):
        raise FileNotFoundError(f"日志目录不存在：{LOG_DIR}")
    if not os.path.isdir(OUTPUT_PARENT):
        os.makedirs(OUTPUT_PARENT, exist_ok=True)

    for fname in os.listdir(LOG_DIR):
        if not fname.lower().endswith(".txt"):
            continue
        fullpath = os.path.join(LOG_DIR, fname)
        base_name, _ = os.path.splitext(fname)
        output_dir = os.path.join(OUTPUT_PARENT, base_name)
        os.makedirs(output_dir, exist_ok=True)
        print(f"[PROCESSING] {fname} → {output_dir}")
        try:
            process_single_log(fullpath, output_dir)
        except Exception as e:
            print(f"[ERROR] 处理 {fname} 时出错: {e}")

    print("所有日志处理完成。")

if __name__ == "__main__":
    main()
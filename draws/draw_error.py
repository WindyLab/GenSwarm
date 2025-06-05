import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from matplotlib.font_manager import FontProperties

# ------------------------------------------------------------
# 配色与参数（与示例中尽量保持一致）
# ------------------------------------------------------------
# 轨迹彩虹色列表——红、橙、黄、绿、蓝、靛、紫
colors_traj = [
    (1.0, 0.0, 0.0),    # red
    (1.0, 0.65, 0.0),   # orange
    (1.0, 1.0, 0.0),    # yellow
    (0.0, 1.0, 0.0),    # green
    (0.0, 0.0, 1.0),    # blue
    (0.29, 0.0, 0.51),  # indigo
    (0.93, 0.51, 0.93)  # violet
]

# 用于速度映射的色图（与示例接近，这里选 'jet'，你可以改成 'turbo' 或 'viridis'）
speed_cmap = cm.get_cmap('jet')

# 每隔多少步绘制一个箭头
batch_time_points = 5

# 字体统一为 Times New Roman
font_prop = FontProperties(family='Times New Roman', size=10)

# ------------------------------------------------------------
# 主函数：绘制机器人轨迹 + 猎物对比
# ------------------------------------------------------------
def visualize_swarm(log_filename):
    # ——— 1. 读取 log.txt ——
    with open(log_filename, 'r') as f:
        lines = f.readlines()

    # 存放各机器人观测到的位置与速度
    robot_obs = {}   # {robot_id: {"x": [...], "y": [...], "vx": [...], "vy": [...]}}
    # 猎物真值 (x_true, y_true) 以及观测点 (x_obs, y_obs)
    prey_true = {"x": [], "y": []}
    prey_obs  = {"x": [], "y": []}

    for line in lines:
        entry = json.loads(line)
        # — 真值 Prey —
        prey_true["x"].append(entry["prey_position"][0])
        prey_true["y"].append(entry["prey_position"][1])

        # — 观测列表 —
        for obs in entry["observations"]:
            if obs["type"] == "Robot":
                rid = obs["id"]
                if rid not in robot_obs:
                    robot_obs[rid] = {"x": [], "y": [], "vx": [], "vy": []}
                robot_obs[rid]["x"].append(obs["position"]["x"])
                robot_obs[rid]["y"].append(obs["position"]["y"])
                robot_obs[rid]["vx"].append(obs["velocity"]["x"])
                robot_obs[rid]["vy"].append(obs["velocity"]["y"])
            elif obs["type"] == "Prey":
                prey_obs["x"].append(obs["position"]["x"])
                prey_obs["y"].append(obs["position"]["y"])

    # ——— 2. 计算所有机器人速度范围（用于后续颜色映射） ——
    all_speeds = []
    for data in robot_obs.values():
        vx_arr = np.array(data["vx"])
        vy_arr = np.array(data["vy"])
        spd   = np.sqrt(vx_arr**2 + vy_arr**2)
        all_speeds.append(spd)
    if all_speeds:
        all_speeds = np.concatenate(all_speeds)
        vmin, vmax = all_speeds.min(), all_speeds.max()
    else:
        # 万一没有机器人数据
        vmin, vmax = 0.0, 1.0

    norm = Normalize(vmin=vmin, vmax=vmax)  # 用于速度到颜色的归一化

    # ——— 3. 绘制机器人轨迹（Line + Quiver 箭头） ——
    fig1, ax1 = plt.subplots(figsize=(8, 8))

    for idx, (rid, data) in enumerate(robot_obs.items()):
        xs  = np.array(data["x"])   # 机器人当前位置 x 列表
        ys  = np.array(data["y"])   # 机器人当前位置 y 列表
        vx  = np.array(data["vx"])  # 机器人速度 vx 列表
        vy  = np.array(data["vy"])  # 机器人速度 vy 列表

        if len(xs) < 2:
            # 少于两个点则无法画线段
            continue

        # 速度模长
        spd = np.sqrt(vx**2 + vy**2)

        # 轨迹主色（取 colors_traj 列表循环）
        traj_color = colors_traj[idx % len(colors_traj)]

        # 绘制轨迹轮廓线（透明度 0.3）—— 只连一次整条线，方便辨识整体走向
        # 注意交换坐标：横轴为 Y，纵轴为 X
        ax1.plot(ys, xs, color=traj_color, linewidth=1.0, alpha=0.3)

        # 分段绘制 + 箭头
        N = len(xs)
        for j in range(0, N - 1, batch_time_points):
            # 计算这一小段起点 j 和终点 j+batch_time_points (取不超过 N-1)
            j_end = min(j + batch_time_points, N - 1)
            seg_x = xs[j : j_end + 1]
            seg_y = ys[j : j_end + 1]
            # 取起点速度用于给这段线着色
            seg_speed = spd[j]
            # 将速度映射到 [0,1] 之间，再取色板的 RGBA
            color_seg = speed_cmap(norm(seg_speed))

            # 动态透明度：从 0 到 0.5 线性增加
            alpha_seg = 0.5 * (j / (N - 1)) if N > 1 else 0.5

            # 绘制这一段线
            ax1.plot(seg_y, seg_x, color=color_seg, linewidth=0.8, alpha=alpha_seg)

            # 绘制一个箭头：起点 (y[j], x[j])，方向由归一化速度 (vx[j], vy[j]) 决定
            vel_norm = np.linalg.norm([vx[j], vy[j]])
            if vel_norm > 1e-8:
                dx = vx[j] / vel_norm
                dy = vy[j] / vel_norm
                # 注意 quiver 默认输入顺序也是 (x,y) 但结合我们横纵轴交换后要用 dx,dy 对应【经度→横：dy，纬度→纵：dx】？
                # 实际观察，我们把第一个坐标给 quiver 当作“横轴”（对应 y[j]），第二个当作“纵轴”（对应 x[j]），
                # 于是这里把 (dx, dy) 传入的顺序与 (vy, vx) 对应：
                ax1.quiver(
                    ys[j], xs[j],    # 起点坐标 (横=y, 纵=x)
                    dy, dx,         # 速度向量的方向 (横向分量→dy, 纵向分量→dx)
                    angles='xy',
                    scale_units='xy',
                    scale=20,        # 缩放箭头长度，可根据需要调整
                    color=color_seg,
                    alpha=alpha_seg,
                    headwidth=3,
                    headlength=4,
                    linewidth=0.3
                )

        # 在轨迹起点处打一个小圆点来标记当前机器人 ID（可选）
        ax1.scatter(
            ys[0], xs[0],
            s=20,
            color=traj_color,
            edgecolors='k',
            linewidth=0.5,
            label=f"Robot {rid}",
            zorder=5
        )

    # 添加 colorbar，说明箭头/线段的“速度大小”对应颜色映射
    sm = cm.ScalarMappable(cmap=speed_cmap, norm=norm)
    sm.set_array([])  # 仅用于 colorbar
    cbar = fig1.colorbar(sm, ax=ax1, fraction=0.046, pad=0.04)
    cbar.set_label("Speed magnitude", fontproperties=font_prop)

    # 轴样式统一
    ax1.set_title("Robots 2D Trajectories (Colored by Speed)", fontproperties=font_prop)
    ax1.set_xlabel("Y position", fontproperties=font_prop)
    ax1.set_ylabel("X position", fontproperties=font_prop)
    ax1.grid(True, linewidth=0.5, linestyle='--', alpha=0.4)
    ax1.legend(prop=font_prop, fontsize=9)
    ax1.set_aspect('equal', 'box')
    # 将坐标刻度也设为 Times New Roman
    ax1.tick_params(axis='both', labelsize=9)
    for label in ax1.get_xticklabels() + ax1.get_yticklabels():
        label.set_fontproperties(font_prop)

    plt.tight_layout()
    plt.savefig("robot_2d_colored_arrows.png", dpi=300)
    plt.close(fig1)


    # ——— 4. 绘制 猎物真值 vs 观测（Y vs X，绿色实线/红色虚线） ——
    fig2, ax2 = plt.subplots(figsize=(8, 8))

    # 真值轨迹：绿色实线
    xt = np.array(prey_true["x"])
    yt = np.array(prey_true["y"])
    if len(xt) > 1:
        ax2.plot(yt, xt, '-', color='green', linewidth=1.5, alpha=0.7, label="Prey True")

    # 观测轨迹：红色虚线 + “×” 标记
    xo = np.array(prey_obs["x"])
    yo = np.array(prey_obs["y"])
    if len(xo) > 1:
        ax2.plot(yo, xo, '--', color='red', linewidth=1.5, alpha=0.7, label="Prey Observed")
        ax2.scatter(yo, xo, marker='x', color='red', s=30)

    ax2.set_title("Prey 2D Trajectories (True vs Observed)", fontproperties=font_prop)
    ax2.set_xlabel("Y position", fontproperties=font_prop)
    ax2.set_ylabel("X position", fontproperties=font_prop)
    ax2.grid(True, linewidth=0.5, linestyle='--', alpha=0.4)
    ax2.legend(prop=font_prop, fontsize=9)
    ax2.set_aspect('equal', 'box')
    ax2.tick_params(axis='both', labelsize=9)
    for label in ax2.get_xticklabels() + ax2.get_yticklabels():
        label.set_fontproperties(font_prop)

    plt.tight_layout()
    plt.savefig("prey_2d_simple.png", dpi=300)
    plt.close(fig2)


# ——— 示例调用 ———
if __name__ == "__main__":
    visualize_swarm("log.txt")

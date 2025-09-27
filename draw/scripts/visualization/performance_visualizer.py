import json

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple

from matplotlib.patches import Rectangle
from scipy.stats import gaussian_kde
from matplotlib.colors import LinearSegmentedColormap

plt.rcParams.update({'font.size': 16})  # 全局字体大小

# ------------------ 颜色配置 ------------------
# 1) Figure 1：10 个任务各自颜色（示例给出 10 个 RGB 颜色）
TASK_COLORS = np.array([
    (213, 105, 93),
    (245, 176, 65),
    (246, 218, 101),
    (82, 190, 128),
    (145, 223, 208),
    (93, 173, 226),
    (164, 105, 189),
    (138, 112, 103),
    (255, 188, 167),
    (72, 79, 152),
]) / 255


#
def color_rgb_to_hex(color: Tuple[int, int, int]) -> str:
    """将 RGB 颜色转换为 Matplotlib 可用的十六进制格式"""
    return "#{:02x}{:02x}{:02x}".format(*color)


# 2) Figure 2 / 3：4 种方法各自颜色
METHOD_COLORS = {
    "gpt4o": color_rgb_to_hex((140, 205, 191)),
    "o1-mini": color_rgb_to_hex((205, 224, 165)),
    "claude-3.7-sonnet": color_rgb_to_hex((239, 132, 118)),
    "deepseek-v3": color_rgb_to_hex((197, 168, 206)),
    # "llm2swarm": color_rgb_to_hex((143, 188, 232))
}
GRAY_DASH = (0.5, 0.5, 0.5)  # 灰色，用于分割线
# ------------------ 渐变色配置 ------------------
# 渐变色的起始和结束颜色 (RGB)
COLOR_START = np.array([127, 171, 135]) / 255  # 浅绿色 (#7fab87)
COLOR_END = np.array([228, 233, 227]) / 255  # 浅灰色 (#e4e9e3)


def generate_gradient_color(index: int, total: int) -> Tuple[float, float, float]:
    """根据任务索引生成渐变色"""
    ratio = index / max(1, total - 1)
    return tuple((1 - ratio) * COLOR_START + ratio * COLOR_END)


# ------------------ 渐变色配置 ------------------
# 渐变色的颜色停靠点
GRADIENT_COLORS = ["#ee9ca7", "#ffdde1"]
# GRADIENT_COLORS = ["#ffa751","#ffe259"]
# GRADIENT_COLORS = ["#fceabb","#f8b500"]
# GRADIENT_COLORS = ["#ffdde1","#ee9ca7"]
custom_cmap = LinearSegmentedColormap.from_list("custom_gradient", GRADIENT_COLORS)


def plot_horizontal_bar_with_gradient(
        ax: plt.Axes,
        data: np.ndarray,
        y_position: float,
        gradient_cmap: LinearSegmentedColormap,
        bar_height: float = 0.7,
):
    """
    绘制带有从左到右渐变效果的水平柱状图

    参数:
        ax: Matplotlib Axes 对象
        data: 数据，形状为 (N, )
        y_position: 该任务在 y 轴上的位置
        gradient_cmap: 渐变色的 colormap
        bar_height: 柱子的高度
    """
    mean_val = np.mean(data)
    min_val = np.min(data)
    max_val = np.max(data)

    # 创建渐变矩形
    gradient = np.linspace(0, 1, 500).reshape(1, -1)
    ax.imshow(
        gradient,
        extent=[0, mean_val, y_position - bar_height / 2, y_position + bar_height / 2],
        aspect="auto",
        cmap=gradient_cmap,
        alpha=0.95
    )
    rect = Rectangle(
        (0, y_position - bar_height / 2),
        mean_val,
        bar_height,
        edgecolor="black",
        facecolor="none",
        linewidth=0.5
    )
    ax.add_patch(rect)
    # 绘制边框颜色与渐变相似
    border_color = 'gray'
    ax.vlines(
        x=min_val,
        ymin=y_position - bar_height / 4,
        ymax=y_position + bar_height / 4,
        color=border_color,
        linestyles="-",
        linewidth=1.5
    )
    ax.vlines(
        x=max_val,
        ymin=y_position - bar_height / 4,
        ymax=y_position + bar_height / 4,
        color=border_color,
        linestyles="-",
        linewidth=1.5
    )
    ax.hlines(
        y=y_position,
        xmin=min_val,
        xmax=max_val,
        color=border_color,
        linestyles="-",
        linewidth=1.5
    )

    # 散点
    N = len(data)
    y_jitter = np.random.uniform(low=y_position - 0.1, high=y_position + 0.1, size=N)
    ax.scatter(data, y_jitter, color=GRADIENT_COLORS[0], alpha=1.0, s=30, edgecolors='black', linewidths=0.3)


def plot_figure1(tasks_fig1: List[str], data_fig1: Dict[str, List[float]]):
    """
    绘制 Figure 1 并保存，使用从左到右的渐变色。

    参数：
        tasks_fig1 (List[str]): 任务名称列表。
        data_fig1 (Dict[str, List[float]]): 每个任务的成功率数据。
    """
    fig, ax = plt.subplots(figsize=(6, 10))  # 根据需要调整大小

    # 在 y=0..9 处依次绘制 10 个任务
    for i, t in enumerate(tasks_fig1):
        if t not in data_fig1:
            continue

        data_t = np.array(data_fig1[t])
        plot_horizontal_bar_with_gradient(
            ax=ax,
            data=data_t,
            y_position=i,
            gradient_cmap=custom_cmap,
            bar_height=0.7
        )

    # 美化坐标
    ax.set_ylim(-1, len(tasks_fig1))
    ax.set_yticks(range(len(tasks_fig1)))
    ax.set_yticklabels(tasks_fig1)
    ax.set_xlabel("Success rates (%)")

    plt.tight_layout()
    plt.savefig("figure1.svg", format="svg")
    plt.close(fig)  # 关闭当前图以释放内存


def plot_vertical_bar_dist_scatter(
        ax: plt.Axes,
        data: np.ndarray,
        x_position: float,
        color: Tuple[float, float, float],
        bar_width: float = 0.6,
        dist_width: float = 0.3,
        use_kde: bool = True
):
    """
    Figure 2 / 3 用的单任务-方法可视化:
      - 竖直柱状图( bar )：显示 data 的平均值
      - 分布图(可用正态, 也可用KDE)；此处默认 use_kde=False => 用正态分布
      - 散点
    """
    mean_val = np.mean(data)
    # (1) 竖直柱状图
    ax.bar(
        x=x_position,
        height=mean_val,
        width=bar_width,
        color=color,
        alpha=0.8,
        edgecolor="black",
        linewidth=0.5  # 取消边框线宽
    )
    # (2) 分布：根据 use_kde 判断画KDE还是正态
    data_std = np.std(data, ddof=1)
    if data_std > 1e-9:
        y_min, y_max = data.min(), data.max()
        y_vals = np.linspace(y_min, y_max, 200)
        kde = gaussian_kde(data)
        pdf_vals = kde(y_vals)
        pdf_max = pdf_vals.max()
        if pdf_max > 0:
            pdf_vals = pdf_vals / pdf_max * dist_width

        dist_center = x_position
        ax.fill_betweenx(
            y_vals,
            dist_center,
            dist_center + pdf_vals,
            color=color,
            alpha=0.3
        )
        ax.plot(dist_center + pdf_vals, y_vals, color=color, lw=2, alpha=0.8)

    # (3) 散点
    # 让散点 y 就是 data，x 在 [x_position+0.2, x_position+0.4] 中随机抖动
    N = len(data)
    x_jitter = np.random.uniform(
        low=x_position + bar_width * 0.3,
        high=x_position + bar_width * 0.7,
        size=N,
    )
    ax.scatter(x_jitter, data, color=color, alpha=1.0, s=30, edgecolors='black', linewidths=0.3)


def generate_data():
    """
    数据生成函数，返回所有需要的数据结构。
    """
    # =========== 1) 模拟数据 ===========
    # Figure 1 : 10 个任务, 每任务 10 个数据
    tasks_fig1 = [f"Task{i + 1}" for i in range(10)]
    data_fig1: Dict[str, np.ndarray] = {}
    np.random.seed(42)
    for i, t in enumerate(tasks_fig1):
        data_fig1[t] = 30 + 60 * np.random.rand(10)

    # Figure 2 / 3: 6 个任务, 每个任务4种方法, 每组 10 个数据
    tasks_2_3 = [f"T{i + 1}" for i in range(6)]
    methods_2_3 = list(METHOD_COLORS.keys())  # ["full","wo/vlm","cap","metagpt"]
    data_2_3: Dict[str, Dict[str, np.ndarray]] = {}
    np.random.seed(2023)
    for t in tasks_2_3:
        data_2_3[t] = {}
        for m in methods_2_3:
            # 这里只是演示: 不同方法数据范围略有差别
            if m == "full":
                arr = 50 + 40 * np.random.rand(10)
            elif m == "wo/vlm":
                arr = 40 + 30 * np.random.rand(10)
            elif m == "cap":
                arr = 20 + 30 * np.random.rand(10)
            else:  # "metagpt"
                arr = 60 + 30 * np.random.rand(10)
            data_2_3[t][m] = arr

    return tasks_fig1, data_fig1, tasks_2_3, methods_2_3, data_2_3


def plot_figure2(tasks_top3: List[str], methods: List[str], data_2_3: Dict[str, Dict[str, np.ndarray]], group_gap=1,
                 method_gap=0.7):
    """
    绘制 Figure 2 并保存，支持调节组间和组内距离。

    Parameters:
        tasks_top3 (List[str]): Top 3 tasks.
        methods (List[str]): Methods to compare.
        data_2_3 (Dict[str, Dict[str, np.ndarray]]): Data for each task and method.
        group_gap (float): Gap between task groups.
        method_gap (float): Gap between methods within a group.
    """
    fig, ax = plt.subplots(figsize=(15, 5.0))  # 根据需要调整大小

    x_pos = 0
    x_tick_positions = []
    x_tick_labels = []

    # 图例设置
    method_handles = []
    for m in methods:
        method_patch = plt.Rectangle(
            (0, 0), 1, 1,
            fc=METHOD_COLORS[m],
            edgecolor="black",
            alpha=0.6,
            label=m
        )
        method_handles.append(method_patch)

    for t in tasks_top3:
        group_start_pos = x_pos
        for m in methods:
            color_m = METHOD_COLORS[m]
            data_tm = data_2_3[t][m]

            plot_vertical_bar_dist_scatter(
                ax=ax,
                data=data_tm,
                x_position=x_pos,
                color=color_m,
                bar_width=0.6,
                dist_width=0.3,
                use_kde=False
            )
            x_pos += method_gap

        # 记录组中心位置，用于添加任务名称
        x_tick_positions.append((group_start_pos + x_pos - method_gap) / 2)
        x_tick_labels.append(t)

        # 组间留空隙
        x_pos += group_gap

    # 设置任务名称作为横坐标
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels(x_tick_labels, rotation=0)
    ax.set_ylabel("Success rates (%)")
    ax.set_ylim(0, 100)

    # 添加方法图例
    ax.legend(handles=method_handles, loc="upper right")

    plt.tight_layout()
    plt.savefig("model_figure2.svg", format="svg")
    plt.close(fig)


def plot_figure3(tasks_bot3: List[str], methods: List[str], data_2_3: Dict[str, Dict[str, np.ndarray]], group_gap=1,
                 method_gap=0.7):
    """
    绘制 Figure 3 并保存。
    """
    fig, ax = plt.subplots(figsize=(15, 5.0))  # 根据需要调整大小

    x_pos = 0
    x_tick_positions = []
    x_tick_labels = []

    # 图例设置
    method_handles = []
    for m in methods:
        method_patch = plt.Rectangle(
            (0, 0), 1, 1,
            fc=METHOD_COLORS[m],
            edgecolor="black",
            alpha=0.6,
            label=m
        )
        method_handles.append(method_patch)

    for t in tasks_bot3:
        group_start_pos = x_pos
        for m in methods:
            color_m = METHOD_COLORS[m]
            data_tm = data_2_3[t][m]

            plot_vertical_bar_dist_scatter(
                ax=ax,
                data=data_tm,
                x_position=x_pos,
                color=color_m,
                bar_width=0.6,
                dist_width=0.3,
                use_kde=False
            )
            x_pos += method_gap

        # 记录组中心位置，用于添加任务名称
        x_tick_positions.append((group_start_pos + x_pos - method_gap) / 2)
        x_tick_labels.append(t)

        # 组间留空隙
        x_pos += group_gap

    # 设置任务名称作为横坐标
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels(x_tick_labels, rotation=0)
    ax.set_ylabel("Success rates (%)")
    ax.set_ylim(0, 100)

    # 添加方法图例
    ax.legend(handles=method_handles, loc="upper right")
    plt.tight_layout()
    plt.savefig("model_figure3.svg", format="svg")
    plt.close(fig)


def load_success_rates(file_path: str) -> Dict[str, List[float]]:
    """
    从 JSON 文件加载任务成功率数据。

    参数：
        file_path (str): JSON 文件路径。

    返回：
        Dict[str, List[float]]: 任务成功率数据。
    """
    with open(file_path, "r") as f:
        return json.load(f)


def main():
    # 数据生成
    # success_rate_file = "o1_mini_success_rates.json"  # 替换为实际路径
    # success_rate_data = load_success_rates(success_rate_file)
    # task_names = list(success_rate_data.keys())
    # task_names = ["aggregation", "flocking", "shaping", "encircling", "crossing", "covering", "exploration", "pursuing",
    #               "bridging", "clustering"]
    # # 任务名称顺序前后调换
    # task_names = task_names[::-1]

    # 绘制 Figure 1
    # plot_figure1(task_names, success_rate_data)

    # 从 JSON 文件加载数据
    file_path = "model_combined_success_rates.json"  # 文件路径
    success_rate_data = load_success_rates(file_path)

    # 根据 JSON 数据解析任务名称和方法
    task_names = ["aggregation", "flocking", "crossing", "shaping", "encircling", "covering"]
    tasks_top3 = ["aggregation", "flocking", "crossing"]
    tasks_bot3 = ["shaping", "encircling", "covering"]
    methods = ["gpt4o", "o1-mini", "deepseek-v3", "claude-3.7-sonnet"]

    # 将数据转换为所需格式
    data_2_3 = {
        task: {method: np.array(success_rate_data[method][task]) for method in methods}
        for task in task_names
    }

    # 绘制 Figure 2 (Top 3 tasks × 4 methods)
    plot_figure2(tasks_top3, methods, data_2_3)

    # 绘制 Figure 3 (Bottom 3 tasks × 4 methods)
    plot_figure3(tasks_bot3, methods, data_2_3)

    print("Figures 2 and 3 have been successfully saved as SVG files.")


if __name__ == "__main__":
    main()

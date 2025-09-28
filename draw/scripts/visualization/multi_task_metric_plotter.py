import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import gaussian_kde
from matplotlib.patches import Rectangle
from typing import Dict, List, Tuple
import math


# --- 1. 全局配置 ---

def color_rgb_to_hex(color: Tuple[int, int, int]) -> str:
    """Helper function to convert RGB to Hex."""
    return "#{:02x}{:02x}{:02x}".format(*color)


# 采纳用户指定的专业配色方案
METHOD_COLORS = {
    "ours": color_rgb_to_hex((205, 224, 165)),
    "human": color_rgb_to_hex((246, 204, 96)),
    "cap": color_rgb_to_hex((239, 132, 118)),
    "meta": color_rgb_to_hex((197, 168, 206)),
    "llm2swarm": color_rgb_to_hex((143, 188, 232))
}

# 指标名称的完整形式，用于图表标题
METRIC_FULL_NAMES = {
    'max_min_distance': 'Max-Min Distance',
    'average_distance_ratio': 'Target Miss Ratio',
    'mean_distance_error': 'Mean Distance Error',
    'area_ratio': 'Uncovered Area Ratio',
    'variance_nearest_neighbor_distance': 'Nearest Neighbor Distance Variance',
    'procrustes_distance': 'Procrustes Distance',
    'spatial_variance': 'Spatial Variance',
    'mean_dtw_distance': 'Mean DTW Distance'
}


# --- 2. 可视化核心函数 ---

def plot_vertical_bar_dist_scatter(
        ax: plt.Axes,
        data: np.ndarray,
        x_position: float,
        color: str,
        bar_width: float = 0.6,
        dist_width: float = 0.3
):
    """
    绘制包含均值、数据分布和散点的“雨云图”
    """
    if data.size == 0:
        return

    mean_val = np.mean(data)
    # (1) 均值柱状图
    ax.bar(
        x=x_position, height=mean_val, width=bar_width,
        color=color, alpha=0.7, edgecolor="black", linewidth=0.5
    )
    # (2) 数据分布 (KDE)
    if np.std(data) > 1e-9:
        y_vals = np.linspace(data.min(), data.max(), 100)
        kde = gaussian_kde(data)
        pdf_vals = kde(y_vals)
        pdf_vals = pdf_vals / pdf_vals.max() * dist_width

        dist_center = x_position + bar_width / 2
        ax.fill_betweenx(y_vals, dist_center, dist_center + pdf_vals, color=color, alpha=0.3)
        ax.plot(dist_center + pdf_vals, y_vals, color=color, lw=1.5, alpha=0.8)

    # (3) 抖动散点
    x_jitter = np.random.uniform(
        low=x_position - bar_width * 0.4, high=x_position - bar_width * 0.1, size=len(data)
    )
    ax.scatter(x_jitter, data, color=color, alpha=0.9, s=20, edgecolors='black', linewidths=0.3)


# --- 3. 数据处理与主绘图逻辑 ---

def analyze_and_plot(root_dir, task_metrics_map, higher_is_better_metrics):
    """
    使用原始数据绘图，将“越大越好”指标转换为“成本”，并按任务组织图表。
    """
    # --- 数据加载 ---
    all_data = []
    print(f"Starting analysis on directory: {root_dir}")
    if not os.path.isdir(root_dir):
        print(f"Error: Directory not found: {root_dir}");
        return

    for dirpath, _, filenames in os.walk(root_dir):
        target_json = 'wo_vlm.json' if 'wo_vlm.json' in filenames else next(
            (f for f in filenames if f.endswith('.json')), None)
        if not target_json: continue

        parts = dirpath.split(os.sep)
        if len(parts) < 3: continue

        task, method = parts[-2], parts[-3]
        if task not in task_metrics_map: continue

        try:
            filepath = os.path.join(dirpath, target_json)
            with open(filepath, 'r') as f:
                data = json.load(f)
            analysis_data = data.get('analysis', {})
            for metric in task_metrics_map[task]:
                if metric in analysis_data:
                    all_data.append(
                        {'method': method, 'task': task, 'metric': metric, 'value': float(analysis_data[metric])})
        except Exception as e:
            print(f"Warning: Could not process {filepath}. Error: {e}")

    if not all_data:
        print("Error: No data extracted.");
        return

    df = pd.DataFrame(all_data)

    # 方法名称映射
    method_mapping = {"4o_genswarm": "ours", "metagpt": "meta", "Human expert": "human"}
    df['method'] = df['method'].replace(method_mapping)

    # 统一指标为“成本”值 (越小越好)
    df['cost_value'] = np.where(
        df['metric'].isin(higher_is_better_metrics),
        1 - df['value'],
        df['value']
    )

    df.to_csv('../../results/data/comparison_metric.csv', index=False, encoding='utf-8')
    print(f"Processed data with cost values saved to comparison_metric.csv")

    # --- MODIFICATION: Average Rank Calculation ---
    # Calculate mean cost for each method and metric to ensure a fair comparison
    mean_cost_df = df.groupby(['metric', 'method'])['cost_value'].mean().reset_index()

    # Rank methods within each metric (lower cost is better, so rank 1 is best)
    mean_cost_df['rank'] = mean_cost_df.groupby('metric')['cost_value'].rank(method='average')

    # Calculate average rank for each method across all metrics
    average_ranks = mean_cost_df.groupby('method')['rank'].mean().sort_values()

    print("\n--- Average Method Ranks (Lower is Better) ---")
    print(average_ranks)
    print("---------------------------------------------\n")
    # --- END MODIFICATION ---

    # --- Advanced Visualization ---
    plt.rcParams.update({'font.size': 10, 'font.family': 'sans-serif'})

    # 自定义方法排序
    custom_order = ['ours', 'meta', 'cap', 'llm2swarm', 'human']
    methods_in_data = df['method'].unique()
    methods = [m for m in custom_order if m in methods_in_data]
    palette = {m: METHOD_COLORS.get(m, "#808080") for m in methods}

    # 按任务组织指标顺序
    metrics_to_plot = []
    for task in sorted(task_metrics_map.keys()):
        for metric in task_metrics_map[task]:
            if metric in df['metric'].unique():
                metrics_to_plot.append((metric, task))

    num_metrics = len(metrics_to_plot)
    ncols = 4
    nrows = math.ceil(num_metrics / ncols)
    # 增加一点 bottom margin 为图例腾出空间
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 3.5, nrows * 3), squeeze=False,
                             constrained_layout=True)
    axes = axes.flatten()

    for i, (metric_name, task_name) in enumerate(metrics_to_plot):
        ax = axes[i]
        metric_df = df[df['metric'] == metric_name]

        x_positions = np.arange(len(methods))
        for j, method in enumerate(methods):
            data_points = metric_df[metric_df['method'] == method]['cost_value'].values
            plot_vertical_bar_dist_scatter(ax=ax, data=data_points, x_position=x_positions[j], color=palette[method],
                                           bar_width=0.6, dist_width=0.3)

        # 在最后一行的子图上显示X轴标签
        if i >= num_metrics - ncols:
            ax.set_xticks(x_positions)
            ax.set_xticklabels(methods, rotation=45, ha='right')
        else:
            ax.set_xticks(x_positions)
            ax.set_xticklabels([])

        # --- 子图美化 ---
        title = f"{METRIC_FULL_NAMES.get(metric_name, metric_name)}\n(Task: {task_name})"
        ax.set_title(title, fontsize=11, weight='normal')
        ax.tick_params(axis='x', length=0)
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        ax.set_ylabel("")

        # 动态设置Y轴范围
        if metric_name in higher_is_better_metrics or metric_name == 'average_distance_ratio':
            ax.set_ylim(0, 1)
        else:
            if not metric_df.empty:
                all_cost_values = metric_df['cost_value']
                mean_val = all_cost_values.mean()
                upper_limit = mean_val * 3 if mean_val > 0 else 1  # Avoid upper_limit of 0
                lower_limit = 0
                ax.set_ylim(lower_limit, upper_limit)

        for spine in ax.spines.values(): spine.set_linewidth(0.5)

    # 隐藏多余的子图
    for i in range(num_metrics, len(axes)):
        axes[i].set_visible(False)

    # --- 全局图例 ---
    METHOD_LABELS = {
        "ours": "ours",
        "meta": "metagpt",
        "cap": "cap",
        "llm2swarm": "llm2swarm",
        "human": "human"
    }

    legend_handles = [
        Rectangle((0, 0), 1, 1, color=palette[m], label=METHOD_LABELS.get(m, m))
        for m in methods
    ]

    # --- MODIFICATION START ---
    # 将图例移到X轴标签下方
    # 我们不再在每个子图上单独设置标签，而是在图例中显示它们
    for ax in axes:
        ax.set_xticklabels([])  # 清除所有子图的X轴标签，因为它们现在在图例中

    fig.legend(
        handles=legend_handles,
        loc='lower center',  # 将图例框的底部中心作为锚点
        bbox_to_anchor=(0.5, -0.05),  # 将锚点放置在图表下方，并增加一点间距
        ncol=len(methods),  # 设置为多列（水平排列）
        fontsize=11,
        frameon=False,
        title=''
    )
    # --- MODIFICATION END ---

    # 由于 constrained_layout=True，它会自动调整布局。
    # 如果图例或标签仍然重叠，可以手动调整布局：
    # fig.tight_layout(rect=[0, 0.05, 1, 1]) # rect=[left, bottom, right, top]

    # Change the filename extension to .svg
    output_filename = '../../results/charts/comparison_metric.svg'

    # Save the figure as an SVG file. The dpi argument is not needed for vector formats.
    plt.savefig(output_filename, format='svg', bbox_inches='tight')

    print(f"\nAnalysis complete. Final plot saved as '{output_filename}'")
    plt.show()


if __name__ == '__main__':
    # 请确保将此路径更改为您系统上的实际路径
    ROOT_DIRECTORY = '/home/yons/GenSwarm/workspace/comparative'
    TASK_METRICS_MAP = {
        'aggregation': ['max_min_distance'],
        'crossing': ['average_distance_ratio'],
        'encircling': ['mean_distance_error'],
        'covering': ['area_ratio', 'variance_nearest_neighbor_distance'],
        'shaping': ['procrustes_distance'],
        'flocking': ['spatial_variance', 'mean_dtw_distance']
    }
    # 用于识别需要进行 1-value 转换的指标
    HIGHER_IS_BETTER_METRICS = {'area_ratio'}

    analyze_and_plot(ROOT_DIRECTORY, TASK_METRICS_MAP, HIGHER_IS_BETTER_METRICS)

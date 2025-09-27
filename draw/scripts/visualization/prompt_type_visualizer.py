import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# ======== 数据与标签设置 ========
prompt_rename = {
    'default': 'Plain-Basic',
    'simple': 'Plain-Concise',
    'simple_strategy': 'Plain-Strategy',
    'narrative': 'Plain-Narrative',
    'structured_default': 'Structured-Concise',
    'structured_strategy': 'Structured-Strategy'
}

prompt_types = list(prompt_rename.keys())
prompt_labels = [prompt_rename[p] for p in prompt_types]
tasks = ['covering', 'encircling', 'shaping']
models = ['gpt-4o', 'o1-mini', 'DeepSeek-V3']

data = {
    'gpt-4o': {
        'default': [0.659091, 0.7, 0.72],
        'narrative': [0.444444, 0.357143, 0.6875],
        'simple': [0.340909, 0.326087, 0.6875],
        'simple_strategy': [0.818182, 0.511111, 0.72093],
        'structured_default': [0.4, 0.36, 0.727273],
        'structured_strategy': [0.58, 0.6, 0.644444]
    },
    'o1-mini': {
        'default': [0.86, 0.82, 0.66],
        'narrative': [0.48, 0.36, 0.52],
        'simple': [0.46, 0.54, 0.76],
        'simple_strategy': [0.78, 0.6, 0.7],
        'structured_default': [0.48, 0.46, 0.74],
        'structured_strategy': [0.76, 0.7, 0.64]
    },
    'DeepSeek-V3': {
        'default': [0.782609, 0.678571, 0.82],
        'narrative': [0.690476, 0.714286, 0.866667],
        'simple': [0.520833, 0.511628, 0.914894],
        'simple_strategy': [0.931818, 0.738095, 0.880952],
        'structured_default': [0.56, 0.52, 0.913043],
        'structured_strategy': [0.94, 0.8125, 0.928571]
    }
}

# ======== 图布局设置 ========
sns.set(style="whitegrid")
fig = plt.figure(figsize=(14, 6))
gs = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 0.05], wspace=0.03)

vmin, vmax = 30, 100  # 百分比范围
heatmap_cmap = "YlGnBu"
mappable = None

# ======== 绘制热图 ========
for idx, model in enumerate(models):
    ax_hm = fig.add_subplot(gs[0, idx])
    mat = np.array([data[model][pt] for pt in prompt_types]) * 100
    df_hm = pd.DataFrame(mat, index=prompt_labels, columns=tasks)
    hm = sns.heatmap(
        df_hm, ax=ax_hm, cmap=heatmap_cmap,
        vmin=vmin, vmax=vmax, annot=True, fmt=".0f",
        annot_kws={"size": 7}, cbar=False, square=True,
        linewidths=0.3, linecolor='white'
    )
    if mappable is None:
        mappable = hm
    ax_hm.set_title(model, fontsize=11)
    if idx == 0:
        ax_hm.set_ylabel("Prompt Type", fontsize=11)
    else:
        ax_hm.set_ylabel("")
        ax_hm.set_yticklabels([])

# ======== Colorbar ========
cax = fig.add_subplot(gs[0, 3])
fig.colorbar(mappable.collections[0], cax=cax)
cax.set_ylabel("Success Rate (%)", fontsize=9)
# ======== 图标题与显示 ========
fig.suptitle("Heatmaps of instruction impact", fontsize=14)
fig.tight_layout()
plt.savefig("heatmaps.svg", format="svg")

# ======== 在最后一张热图右侧添加平均值文字 ========
row_means = []
for p in prompt_types:
    vals = []
    for m in models:
        vals.extend(data[m][p])
    row_means.append(np.mean(vals) * 100)

final_ax = fig.axes[2]
final_ax.set_xlim(0, len(tasks) + 1.5)  # 加宽坐标轴范围


for i, mean_val in enumerate(row_means):
    print(i, mean_val)
    final_ax.text(len(tasks) + 0.5, i + 0.5, f"{mean_val:.1f}%",
                  va='center', ha='left', fontsize=8, color='black')

final_ax.text(len(tasks) + 0.5, -0.5, "Global Avg",
              ha='left', fontsize=9,)

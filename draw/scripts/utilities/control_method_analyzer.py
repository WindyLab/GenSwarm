import os
import re
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Define the folder path
base_path = "/home/yons/GenSwarm/workspace/4o_genswarm"

# Data structures for results
folder_summary = {}

# Traverse all subfolders
if os.path.exists(base_path):
    for folder_name in sorted(os.listdir(base_path)):
        folder_path = os.path.join(base_path, folder_name)
        if os.path.isdir(folder_path):
            global_count = 0
            local_count = 0
            classification = {}
            for subfolder_name in sorted(os.listdir(folder_path)):
                subfolder_path = os.path.join(folder_path, subfolder_name)
                if os.path.isdir(subfolder_path):
                    global_skills_path = os.path.join(subfolder_path, "global_skill.py")
                    if os.path.exists(global_skills_path):
                        with open(global_skills_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            has_only_import = (
                                re.search(r'^from\s+global_apis\s+import\s+.+$', content, re.M) is not None and
                                re.search(r'^\s*def\s+', content, re.M) is None
                            )
                            if has_only_import:
                                classification[subfolder_name] = 'local'
                                local_count += 1
                            else:
                                classification[subfolder_name] = 'global'
                                global_count += 1
            if global_count + local_count > 0:
                folder_summary[folder_name] = {
                    'global': global_count,
                    'local': local_count,
                    'classification': classification
                }

# ======= Plotting like the screenshot =======
color_map = {
    'global': '#66c2a5',  # greenish
    'local': '#fc8d62',   # orangish
}

labels = list(folder_summary.keys())
n = len(labels)

fig, ax = plt.subplots(figsize=(10, 0.6 * n))

for i, folder in enumerate(labels):
    class_map = folder_summary[folder]['classification']
    total = len(class_map)
    start = 0.0
    for sub_name, label in sorted(class_map.items()):
        width = 1.0 / total
        color = color_map[label]
        ax.barh(i, width, left=start, height=0.6, color=color, edgecolor='white')
        start += width

# Axes formatting
ax.set_yticks(np.arange(n))
ax.set_yticklabels(labels, fontsize=9)
ax.set_xlim(0, 1)
ax.set_xlabel("Frequency of Subfolders", fontsize=10)
ax.set_title("Global vs Local Skill Classification per Folder", fontsize=14)
ax.invert_yaxis()
ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
ax.grid(axis='x', linestyle='--', alpha=0.4)

# Legend
handles = [mpatches.Patch(color=color_map[k], label=k.capitalize()) for k in color_map]
ax.legend(handles=handles, title="Type", bbox_to_anchor=(1.02, 1), loc='upper left')

plt.tight_layout()
plt.show()

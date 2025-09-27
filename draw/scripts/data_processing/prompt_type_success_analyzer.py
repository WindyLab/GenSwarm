import os
import pandas as pd
import re


# 模拟文件系统遍历结构，实际运行时请替换为真实根路径
# root_dir = '../workspace/comparative/llm2swarm/DMXAPI-HuoShan-DeepSeek-V3'  # 根目录
model_name = 'o1-mini'
# model_name= 'gpt-4o-2024-11-20'
# model_name = 'DMXAPI-HuoShan-DeepSeek-V3'
root_dir = f'../workspace/{model_name}'  # 根目录
summary_data = []

# 遍历模拟目录结构
for prompt_type in os.listdir(root_dir):
    prompt_path = os.path.join(root_dir, prompt_type)
    if not os.path.isdir(prompt_path):
        continue
    for task_name in os.listdir(prompt_path):
        task_path = os.path.join(prompt_path, task_name)
        if task_name == 'exploration':
            continue
        if not os.path.isdir(task_path):
            continue
        pic_dir = os.path.join(task_path, 'pic')
        if not os.path.exists(pic_dir):
            continue
        for filename in os.listdir(pic_dir):
            if filename.endswith('wo_vlm.json.txt') and filename.startswith('summary_metrics_'):
                file_path = os.path.join(pic_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    match = re.search(r'success:\s*([0-9.]+)', content)
                    if match:
                        success_value = float(match.group(1))
                        summary_data.append({
                            "PromptType": prompt_type,
                            "Task": task_name,
                            "Success": success_value
                        })

# 转换为 DataFrame
df = pd.DataFrame(summary_data)

# 保存结果为 CSV - 统一保存到results/data目录
results_dir = "../../results/data"
os.makedirs(results_dir, exist_ok=True)
output_path = os.path.join(results_dir, f"{model_name}_summary_success_table.csv")
df.to_csv(output_path, index=False)
print(df)
# 按用户要求将数据透视为 PromptType 为列，Task 为行的 Markdown 表格
if not df.empty:
    pivot_df = df.pivot_table(index='PromptType', columns='Task', values='Success')
    markdown_table = pivot_df.to_markdown()

    # 保存为 markdown 文件
    markdown_path = os.path.join(results_dir, f"{model_name}_success_summary.md")
    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write(f"# {model_name}\n\n")
        f.write(markdown_table)
else:
    markdown_table = "没有可用的数据生成 Markdown 表格。"

import os
import json
import random
from typing import Dict, List, Tuple


def process_experiment_data(root_dir: str):
    """
    遍历目录以处理任务实验数据。

    参数：
        root_dir (str): 根目录路径，每个子目录代表一个任务。

    返回：
        Tuple[Dict[str, List[float]], Dict[str, List[float]]]: 包含每个任务的10组成功率和完全wo_vlm数据。
    """
    task_success_rates = {}
    wo_vlm_success_rates = {}
    debug_success_rates = {}
    # 遍历任务目录
    for task_name in os.listdir(root_dir):

        task_path = os.path.join(root_dir, task_name)
        if not os.path.isdir(task_path):
            continue

        success_rates = []
        debug_rates = []
        wo_vlm_rates = []

        # 遍历实验目录
        experiment_dirs = sorted(
            [os.path.join(task_path, exp) for exp in os.listdir(task_path) if
             os.path.isdir(os.path.join(task_path, exp)) and exp != 'pic']
        )

        for experiment_dir in experiment_dirs:

            debug_json_path = os.path.join(experiment_dir, "debug.json")
            cap_json_path = os.path.join(experiment_dir, "cap.json")
            llm2swarm_json_path = os.path.join(experiment_dir, 'llm2swarm.json')
            meta_json_path = os.path.join(experiment_dir, "meta.json")
            wo_vlm_json_path = os.path.join(experiment_dir, "wo_vlm.json")
            improve_json_path = os.path.join(experiment_dir, "improve.json")
            # 最优先使用improve.json数据
            improve_success_rate = False
            wo_vlm_success_rate = False
            debug_success_rate = False
            mode = None
            if os.path.exists(cap_json_path):
                mode = 'cap'
            elif os.path.exists(meta_json_path):
                mode = 'meta'
            elif os.path.exists(llm2swarm_json_path):
                mode = 'llm2swarm'
            if mode is not None:
                with open(os.path.join(experiment_dir, f"{mode}.json"), "r") as f:
                    data = json.load(f)
                    success_rate = data.get('analysis').get('success', False)
            else:
                if os.path.exists(improve_json_path):
                    with open(improve_json_path, "r") as f:
                        data = json.load(f)
                        improve_success_rate = data.get('analysis').get('success', False)
                if os.path.exists(wo_vlm_json_path):
                    with open(wo_vlm_json_path, "r") as f:
                        data = json.load(f)
                        try:
                            wo_vlm_success_rate = data.get('analysis').get('success', False)
                        except Exception as e:
                            print(wo_vlm_json_path)
                if os.path.exists(debug_json_path):
                    with open(debug_json_path, "r") as f:
                        data = json.load(f)
                        debug_success_rate = data.get('analysis').get('success', False)
                success_rate = improve_success_rate or wo_vlm_success_rate or debug_success_rate
            success_rates.append(success_rate)
            debug_rates.append(wo_vlm_success_rate or debug_success_rate)
            wo_vlm_rates.append(wo_vlm_success_rate)

        def grouped_average(rates, group_size=10):
            """
            This function calculates the average of a list of rates, grouped by the specified group size.
            It returns the percentage average for each group.

            Parameters:
            rates (list): The list of rates to be averaged.
            group_size (int): The number of items in each group (default is 10).

            Returns:
            list: A list of percentage averages for each group.
            """
            grouped_averages = []
            print(rates)
            print(len(rates))
            # Iterate over the rates in chunks of `group_size`
            for i in range(0, len(rates), group_size):
                group = rates[i:i + group_size]
                group_average = sum(group) / len(
                    group) * 100  # Calculate average for the group and convert to percentage
                grouped_averages.append(group_average)  # Append result to the list

            return grouped_averages

        grouped_success_rates = grouped_average(success_rates)
        grouped_wo_vlm_rates = grouped_average(wo_vlm_rates)
        grouped_debug_rates = grouped_average(debug_rates)

        task_success_rates[task_name] = grouped_success_rates
        wo_vlm_success_rates[task_name] = grouped_wo_vlm_rates
        debug_success_rates[task_name] = grouped_debug_rates

    return task_success_rates, debug_success_rates, wo_vlm_success_rates


def save_success_rates_to_file(data: Dict[str, List[float]], file_path: str):
    """
    将成功率数据保存到JSON文件。

    参数：
        data (Dict[str, List[float]]): 成功率数据。
        file_path (str): 保存的文件路径。
    """
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


# 主程序
if __name__ == "__main__":
    root_directory_4o = "../workspace/4o_genswarm"  # 修改为实际路径
    root_directory_o1_mini = "../workspace/genswarm_o1mini"  # 修改为实际路径
    root_directory_deepseek = "../workspace/different_model/deepseek_v3"
    root_directory_claude = "../workspace/different_model/claude-3.7"

    output_file_4o = "4o_success_rates.json"  # 保存结果的文件路径
    output_wo_vlm_file = "wo_vlm_4o_success_rates.json"  # 保存结果的文件路径
    output_file_o1_mini = "o1_mini_success_rates.json"  # 保存结果的文件路径

    output_combined_file = "model_combined_success_rates.json"  # 保存最终合并数据的文件路径

    task_data_4o, wo_vlm_data, _ = process_experiment_data(root_directory_4o)
    o1_mini_data, o1_mini_wo_data, _ = process_experiment_data(root_directory_o1_mini)
    deepseek_data, _, _ = process_experiment_data(root_directory_deepseek)
    claude_data, _, _ = process_experiment_data(root_directory_claude)

    save_success_rates_to_file(task_data_4o, output_file_4o)
    save_success_rates_to_file(wo_vlm_data, output_wo_vlm_file)
    save_success_rates_to_file(o1_mini_data, output_file_o1_mini)
    # 统计每一个任务的平均成功率
    task_averages_4o = {
        task: sum(rates) / len(rates)
        for task, rates in task_data_4o.items()
    }
    wo_vlm_averages = {
        task: sum(rates) / len(rates)
        for task, rates in wo_vlm_data.items()
    }
    o1_mini_wo_vlm_averages = {
        task: sum(rates) / len(rates)
        for task, rates in o1_mini_wo_data.items()
    }
    claude_averages = {
        task: sum(rates) / len(rates)
        for task, rates in claude_data.items()
    }
    o1_mini_averages = {
        task: sum(rates) / len(rates)
        for task, rates in o1_mini_data.items()
    }
    deepseek_averages = {task: sum(rates) / len(rates) for task, rates in deepseek_data.items()}  # ✅ 新增平均值

    print(
        f"4o 平均成功率: {task_averages_4o}\n"
        f"wo_vlm 平均成功率: {wo_vlm_averages}\n"
        f"o1-mini_wo_vlm 平均成功率: {o1_mini_wo_vlm_averages}\n"
        f"claude 平均成功率: {claude_averages}\n"
        f"o1_mini 平均成功率: {o1_mini_averages}\n"
        f"deepseek 平均成功率: {deepseek_averages}"

    )
    # 确保从列表中提取数值进行求和
    task_averages_4o = sum(task_averages_4o.values()) / len(task_averages_4o)
    wo_vlm_averages = sum(wo_vlm_averages.values()) / len(wo_vlm_averages)
    o1_mini_wo_vlm_averages = sum(o1_mini_wo_vlm_averages.values()) / len(o1_mini_wo_vlm_averages)
    claude_averages = sum(claude_averages.values()) / len(claude_averages)
    o1_mini_averages = sum(o1_mini_averages.values()) / len(o1_mini_averages)
    deepseek_averages = sum(deepseek_averages.values()) / len(deepseek_averages)

    print(
        f"4o 平均成功率: {task_averages_4o}\n"
        f"wo_vlm 平均成功率: {wo_vlm_averages}\n"
        f"o1_mini_wo_vlm_averages 平均成功率: {o1_mini_wo_vlm_averages}\n"
        f"claude_averages 平均成功率: {claude_averages}\n"
        f"o1_mini 平均成功率: {o1_mini_averages}\n"
        f"deepseek_averages 平均成功率: {deepseek_averages}\n"
    )

    # 合并所有数据
    combined_data = {
        "gpt4o": wo_vlm_data,
        "claude-3.7-sonnet":claude_data,
        "o1-mini": o1_mini_wo_data,
        "deepseek-v3": deepseek_data  # ✅ 合并数据

    }

    save_success_rates_to_file(combined_data, output_combined_file)
    print(f"合并数据已保存到 {output_combined_file}")

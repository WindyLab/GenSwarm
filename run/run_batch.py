"""
Copyright (c) 2024 WindyLab of Westlake University, China
All rights reserved.

This software is provided "as is" without warranty of any kind, either
express or implied, including but not limited to the warranties of
merchantability, fitness for a particular purpose, or non-infringement.
In no event shall the authors or copyright holders be liable for any
claim, damages, or other liability, whether in an action of contract,
tort, or otherwise, arising from, out of, or in connection with the
software or the use or other dealings in the software.
"""
import os
import subprocess
import time

from run.auto_runner import *
import argparse


def task_mapping(task_name: str) -> type(AutoRunnerBase):
    task_dict = {
        "exploration": AutoRunnerExplore,
        "crossing": AutoRunnerCross,
        "flocking": AutoRunnerFlocking,
        "shaping": AutoRunnerShaping,
        "bridging": AutoRunnerBridging,
        "aggregation": AutoRunnerAggregation,
        "encircling": AutoRunnerEncircling,
        "covering": AutoRunnerCovering,
        "clustering": AutoRunnerClustering,
        "pursuing": AutoRunnerPursuing,
    }
    return task_dict[task_name]


def config_mapping(task_name: str) -> str:
    return task_name + "_config.json"


def restart_roscore():
    # 终止所有正在运行的 roscore
    subprocess.run(["killall", "roscore"])
    print("Restarting roscore...")
    time.sleep(1)  # 确保 roscore 被完全关闭
    # 启动新的 roscore 进程
    subprocess.Popen(["roscore"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)  # 等待 roscore 启动完成


def main():
    # 创建解析器
    parser = argparse.ArgumentParser(description="Run the robot experiment.")
    # 添加 exp_batch 参
    parser.add_argument(
        "--exp_batch",
        type=int,
        default=1,
        help="The number of experiment batches to run",
    )
    parser.add_argument(
        "--task_name",
        type=str,
        default="flocking",
        help="The name of the task to run",
    )
    parser.add_argument(
        "--test_mode",
        type=str,
        default="wo_vlm",
        help="The mode of the test",
    )
    parser.add_argument(
        "--run_mode",
        type=str,
        default="analyze",
        help="The mode of the run",
    )
    # 解析参数
    args = parser.parse_args()
    task_name = args.task_name

    # workspace_path = 'ablation/constraint_pool/' + task_name
    runner_class = task_mapping(task_name)
    config_file = config_mapping(task_name)
    # test_mode = 'improve'
    test_mode = args.test_mode
    # workspace_path = 'encircling'
    if test_mode in ['cap', 'meta', 'llm2swarm']:
        workspace_path = 'comparative/' + test_mode + "/" + task_name
    else:
        workspace_path = 'different_model/claude-3.7/' + task_name

    if test_mode == 'real':
        env_config_path = f"config/real_env/{config_file}"
        experiment_duration = 50
    else:
        env_config_path = f"config/env/{config_file}"
        experiment_duration = 15
    runner = runner_class(
        env_config_path=env_config_path,
        workspace_path=workspace_path,
        experiment_duration=experiment_duration,
        exp_batch=args.exp_batch,
        run_mode=args.run_mode,
        test_mode=test_mode,
        max_speed=4.5,
        tolerance=0.15,
    )

    # 人工复核，哪些任务需要重新跑，写在下面

    # exp_list = ['2024-10-28_01-49-03', '2024-10-28_01-49-05', '2024-10-28_01-49-09', '2024-10-28_01-49-15',
    #             '2024-10-28_01-49-19', '2024-10-28_01-49-27', '2024-10-28_01-51-49']

    exp_list = None
    # exp_list = [
    #     # '2024-10-29_16-15-35',
    #     '2025-01-14_23-43-31', '2025-01-14_23-41-27',
    #
    # ]
    # exp_list = ['shaping_20250116_143843_984_3533656']

    runner.run(exp_list=exp_list)


if __name__ == "__main__":
    main()

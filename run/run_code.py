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

from run.auto_runner import *
import argparse


def task_mapping(task_name: str) -> type(AutoRunnerBase):
    task_dict = {
        "exploration": AutoRunnerExplore,
        "crossing": AutoRunnerCross,
        "flocking": AutoRunnerFlocking,
        "shaping": AutoRunnerShaping,
        "bridging": AutoRunnerBridging,
        "circling": AutoRunnerCircling,
        "encircling": AutoRunnerEncircling,
        "covering": AutoRunnerCovering,
        "clustering": AutoRunnerClustering,
        "pursuing": AutoRunnerPursuing,
    }
    return task_dict[task_name]


def config_mapping(task_name: str) -> str:
    return task_name + "_config.json"


def main():
    # 创建解析器
    parser = argparse.ArgumentParser(description="Run the robot experiment.")
    # 添加 exp_batch 参数
    parser.add_argument(
        "--exp_batch",
        type=int,
        default=1,
        help="The number of experiment batches to run",
    )
    parser.add_argument(
        "--task_name",
        type=str,
        default="exploration",
        help="The name of the task to run",
    )

    # 解析参数
    args = parser.parse_args()
    task_name = args.task_name

    # workspace_path = 'comparative/cap/' + task_name
    workspace_path = task_name
    runner_class = task_mapping(task_name)
    config_file = config_mapping(task_name)
    # test_mode = 'improve'
    test_mode = 'real'
    if test_mode == 'real':
        env_config_path = f"../config/real_env/{config_file}"
        experiment_duration = 100
    else:
        env_config_path = f"../config/env/{config_file}"
        experiment_duration = 10
    runner = runner_class(
        env_config_path=env_config_path,
        workspace_path=workspace_path,
        experiment_duration=experiment_duration,
        exp_batch=args.exp_batch,
        run_mode="rerun",
        test_mode=test_mode,
        max_speed=4.5,
        tolerance=0.15,
    )

    # 人工复核，哪些任务需要重新跑，写在下面

    # exp_list = ['2024-10-28_01-49-03', '2024-10-28_01-49-05', '2024-10-28_01-49-09', '2024-10-28_01-49-15',
    #             '2024-10-28_01-49-19', '2024-10-28_01-49-27', '2024-10-28_01-51-49']
    exp_list = None
    # exp_list = ['2024-10-28_01-24-56']
    exp_list = ['2024-10-28_01-19-35']

    runner.run(exp_list=exp_list)


if __name__ == "__main__":
    main()

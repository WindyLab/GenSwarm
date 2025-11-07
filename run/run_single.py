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

import asyncio
import argparse

import rospy

from modules.file import logger
from modules.framework.workflow import Workflow
from modules.prompt import get_user_commands
from modules.utils.rich_print import rich_input, rich_print
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


async def run_task(task: str, args: argparse.Namespace):
    workflow = Workflow(task, args=args)
    await workflow.run()


if __name__ == "__main__":
    from modules.utils import root_manager
    from run.parser import ParameterService

    # 手动添加 prompt_type 和 llm_name 参数
    import sys
    sys_args = sys.argv[1:]  # 提前保留 CLI 参数用于 parse_arguments()

    parameter_service = ParameterService()
    config_file = "experiment_config.yaml"
    parameter_service.add_arguments_from_yaml(f"./config/{config_file}")

    parameter_service.add_argument('--prompt_type', type=str, default='default', help='Prompt template category')
    parameter_service.add_argument('--llm_name', type=str, default='gpt-4o', help='Name of the LLM used')
    parameter_service.add_argument('--task_name', type=str, default='flocking', help='Name of the task')
    args = parameter_service.parse_arguments(sys_args)
    parameter_service.args = args  # 更新保存的 args

    # ✅ 如果传入 task_name，就覆盖 YAML 中的 run_experiment_name
    if args.task_name:
        experiment_name = args.task_name
        args.run_experiment_name = [experiment_name]  # 确保是列表，兼容原逻辑
    else:
        experiment_name = args.run_experiment_name[0]

    task = get_user_commands(experiment_name,format_type=args.prompt_type)[0]
    env_config_file = config_mapping(experiment_name)
    root_manager.update_root(args=args)

    logger.log(f"\n{parameter_service.format_arguments_as_table(args)}", "warning")

    asyncio.run(run_task(task, args))
    rich_print(title="Code Generation", content="All code has been generated, ready to be deployed.")
    
    # 从workspace_root提取刚生成的实验目录名（最后一级目录）
    file_name = root_manager.workspace_root.name  # 例如: "2025-11-07_08-59-35_015288"

    workspace_relative_path = root_manager.workspace_root.relative_to(
        root_manager.project_root / "workspace"
    ).parent
    
    print(f"file_name: {file_name}")
    print(f"workspace_path: {workspace_relative_path}")
    
    test_mode = "full_version"
    if test_mode == "real":
        env_config_path = f"./config/real_env/{env_config_file}"
        experiment_duration = 60
    else:
        env_config_path = f"./config/env/{env_config_file}"
        experiment_duration = 10
    runner_class = task_mapping(experiment_name)
    runner = runner_class(
        env_config_path=env_config_path,
        workspace_path=str(workspace_relative_path),  # 使用完整的相对路径
        experiment_duration=experiment_duration,
        exp_batch=0,
        run_mode="rerun",
        test_mode=test_mode,
        max_speed=4.5,
        tolerance=0.15,
    )
    runner.run(exp_list=[file_name])
    #
    # test_mode = "real"
    # if test_mode == "real":
    #     env_config_path = f"./config/real_env/{env_config_file}"
    #     experiment_duration = 50
    # else:
    #     env_config_path = f"./config/env/{env_config_file}"
    #     experiment_duration = 10
    # runner_class = task_mapping(experiment_name)
    # runner = runner_class(
    #     env_config_path=env_config_path,
    #     workspace_path=experiment_name,
    #     experiment_duration=experiment_duration,
    #     exp_batch=0,
    #     run_mode="rerun",
    #     test_mode=test_mode,
    #     max_speed=4.5,
    #     tolerance=0.15,
    # )
    # runner.run(exp_list=[file_name])

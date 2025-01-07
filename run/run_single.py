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

    user_instruction = """

"""

    parameter_service = ParameterService()
    config_file = "experiment_config.yaml"
    parameter_service.add_arguments_from_yaml(f"./config/{config_file}")
    experiment_name = parameter_service.args.run_experiment_name[0]
    # task = get_user_commands(experiment_name)[0]
    env_config_file = config_mapping(experiment_name)
    args = parameter_service.args
    file_name = root_manager.update_root(args=args)
    logger.log(f"\n{parameter_service.format_arguments_as_table(args)}", "warning")

    asyncio.run(run_task(user_instruction, parameter_service.args))

    rich_print(title="Code Generation", content="All code has been generated, ready to be deployed.")
    # experiment_name = "encircling"
    # file_name = "2024-12-17_11-56-41"
    test_mode = "full_version"
    rospy.set_param('pub_mqtt', False)
    if test_mode == "real":
        env_config_path = f"./config/real_env/{env_config_file}"
        experiment_duration = 60
    else:
        env_config_path = f"./config/env/{env_config_file}"
        experiment_duration = 10
    runner_class = task_mapping(experiment_name)
    runner = runner_class(
        env_config_path=env_config_path,
        workspace_path=experiment_name,
        experiment_duration=experiment_duration,
        exp_batch=0,
        run_mode="rerun",
        test_mode=test_mode,
        max_speed=4.5,
        tolerance=0.15,
    )
    runner.run(exp_list=[file_name])

    test_mode = "real"
    if test_mode == "real":
        env_config_path = f"./config/real_env/{env_config_file}"
        experiment_duration = 50
    else:
        env_config_path = f"./config/env/{env_config_file}"
        experiment_duration = 10
    runner_class = task_mapping(experiment_name)
    runner = runner_class(
        env_config_path=env_config_path,
        workspace_path=experiment_name,
        experiment_duration=experiment_duration,
        exp_batch=0,
        run_mode="rerun",
        test_mode=test_mode,
        max_speed=4.5,
        tolerance=0.15,
    )
    runner.run(exp_list=[file_name])

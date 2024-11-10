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

from modules.file import logger
from modules.framework.workflow import Workflow
from modules.prompt import get_user_commands


async def run_task(task: str, args: argparse.Namespace):
    workflow = Workflow(task, args=args)
    await workflow.run()


if __name__ == "__main__":
    from modules.utils import root_manager
    from parser import ParameterService

    parameter_service = ParameterService()
    config_file = "experiment_config.yaml"
    parameter_service.add_arguments_from_yaml(f"../config/{config_file}")

    experiment_name = parameter_service.args.run_experiment_name[0]
    task = get_user_commands(experiment_name)[0]

    args = parameter_service.args
    root_manager.update_root(args=args, ablation_path='ablation')
    logger.log(f"\n{parameter_service.format_arguments_as_table(args)}", "warning")

    asyncio.run(run_task(task, parameter_service.args))

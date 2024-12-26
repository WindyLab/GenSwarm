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

import json

from modules.file import logger
from modules.framework.action import ActionNode
from modules.llm import GPT
from modules.prompt import (
    ANALYZE_CONSTRAINT_PROMPT_TEMPLATE,
    CONSTRAIN_TEMPLATE,
    GLOBAL_ROBOT_API,
    LOCAL_ROBOT_API,
    ALLOCATOR_TEMPLATE,
    ENV_DES,
    TASK_DES,
)
from modules.framework.constraint import ConstraintPool
from modules.framework.parser import *
from modules.prompt.user_requirements import get_user_commands
from modules.utils import root_manager, rich_print


class AnalyzeConstraints(ActionNode):
    def __init__(self, next_text, node_name=""):
        super().__init__(next_text, node_name)
        self._interaction_mode = False
        if (
                hasattr(self.context.args, "interaction_mode")
                and self.context.args.interaction_mode is True
        ):
            self.__llm = GPT(memorize=True)
            self._interaction_mode = True
        else:
            self.__llm = GPT()
        self._constraint_pool: ConstraintPool = ConstraintPool()

    def _build_prompt(self):
        # constraints predefined
        user_constraints = {"constraints": self._constraint_pool.constraint_list}
        self.prompt = self.prompt.format(
            task_des=TASK_DES,
            instruction=self.context.command,
            global_api=GLOBAL_ROBOT_API,
            local_api=LOCAL_ROBOT_API
                      + ALLOCATOR_TEMPLATE.format(template="Temporarily unknown"),
            env_des=ENV_DES,
            output_template=CONSTRAIN_TEMPLATE,
            user_constraints=json.dumps(user_constraints, indent=4),
        )
        self.set_logging_text(f"Analyzing constraints")

    async def _process_response(self, response: str) -> str:
        content = parse_text(response, "json")
        self._constraint_pool.init_constraints(content)

        logger.log(f"Analyze Constraints Success", "success")

    def _display(self):
        constraint_names = self._constraint_pool.get_constraint_names()
        constraints = [self._constraint_pool[name] for name in constraint_names]
        content = ""
        for index, constraint in enumerate(constraints):
            content += f"[bold yellow]{index + 1}. {constraint.name}[/bold yellow]\n"
            content += f"[white]{constraint.description}[/white]\n"

        rich_print("Step 1: Analyze Constraints", content)


if __name__ == "__main__":
    import asyncio
    from modules.framework.context import WorkflowContext
    import argparse

    root_manager.update_root("../../../workspace/test")

    parser = argparse.ArgumentParser(
        description="Run simulation with custom parameters."
    )

    parser.add_argument(
        "--interaction_mode",
        type=bool,
        default=False,
        help="Whether to run in interaction mode in analyze constraints.",
    )
    context = WorkflowContext()
    task = get_user_commands("covering")[0]

    context.command = task
    args = parser.parse_args()
    context.args = args
    constraint_analyser = AnalyzeConstraints("analyze constraints")

    asyncio.run(constraint_analyser.run())
    context.save_to_file("../../../workspace/test/constraint.pkl")

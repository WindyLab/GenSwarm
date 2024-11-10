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

from modules.file import logger
from modules.framework.action import ActionNode
from modules.framework.code import FunctionTree
from modules.framework.parser import *
from modules.prompt import (
    ANALYZE_SKILL_PROMPT_TEMPLATE,
    FUNCTION_TEMPLATE,
    GLOBAL_ROBOT_API,
    LOCAL_ROBOT_API,
    ALLOCATOR_TEMPLATE,
    ENV_DES,
    TASK_DES,
)
from modules.utils import root_manager


class AnalyzeSkills(ActionNode):
    def __init__(self, next_text, node_name=""):
        super().__init__(next_text, node_name)

    def _build_prompt(self):
        self.prompt = self.prompt.format(
            task_des=TASK_DES,
            instruction=self.context.command,
            local_api=LOCAL_ROBOT_API
            + ALLOCATOR_TEMPLATE.format(template="Temporarily unknown"),
            global_api=GLOBAL_ROBOT_API,
            env_des=ENV_DES,
            output_template=FUNCTION_TEMPLATE,
        )

    async def _process_response(self, response: str) -> str:
        content = parse_text(response, "json")
        functions = eval(content)["functions"]
        global_functions = []
        local_functions = []
        for function in functions:
            if function["scope"] == "global":
                global_functions.append(function)
            else:
                local_functions.append(function)
        self.context.global_skill_tree.init_functions(global_functions)
        self.context.local_skill_tree.init_functions(local_functions)
        if len(global_functions) == 0:
            logger.log("No global functions detected,generate local skills", "warning")
            self.context.scoop = "local"
            from modules.framework.actions import GenerateFunctions

            self._next = GenerateFunctions()

        logger.log(f"Analyze Functions Success", "success")
        return response


if __name__ == "__main__":
    import asyncio

    function_analyser = AnalyzeSkills("analyze constraints")
    path = "../../../workspace/test"
    root_manager.update_root("../../../workspace/test")

    # function_analyser.context.load_from_file(f"{path}/constraint.pkl")
    asyncio.run(function_analyser.run())
    function_analyser.context.save_to_file(f"{path}/analyze_functions.pkl")

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
from modules.framework.action import ActionNode, AsyncNode
from modules.framework.code import FunctionNode, FunctionTree, State
from modules.framework.parser import SingleFunctionParser, parse_text
from modules.prompt import (
    TASK_DES,
    ENV_DES,
    GLOBAL_ROBOT_API,
    LOCAL_ROBOT_API,
    ALLOCATOR_TEMPLATE,
)


class WriteFunction(ActionNode):
    def __init__(self, skill_tree, next_text: str = "", node_name: str = ""):
        super().__init__(next_text, node_name)
        self._function = None
        self._other_functions_str = ""
        self._skill_tree = skill_tree

    def setup(self, function,  other_functions_str):
        self._function: FunctionNode = function
        self._other_functions_str = other_functions_str

    def _build_prompt(self):
        if len(self.context.global_skill_tree.layers) == 0:
            local_api_prompt = LOCAL_ROBOT_API
        else:
            local_api_prompt = LOCAL_ROBOT_API + ALLOCATOR_TEMPLATE.format(
                template=self.context.global_skill_tree.output_template
            )
        robot_api = (
            GLOBAL_ROBOT_API if self.context.scoop == "global" else local_api_prompt
        )

        self.prompt = self.prompt.format(
            task_des=TASK_DES,
            env_des=ENV_DES,
            robot_api=robot_api,
            instruction=self.context.command,
            function_content=self._function.definition,
            other_functions=self._other_functions_str,
        )

    async def _process_response(self, response: str) -> str:
        desired_function_name = self._function.name
        code = parse_text(text=response)
        parser = SingleFunctionParser()
        parser.parse_code(code)
        parser.check_function_name(desired_function_name)
        self._skill_tree.update_from_parser(parser.imports, parser.function_dict)
        return code


class WriteFunctionsAsync(AsyncNode):
    def __init__(
        self,
        skill_tree,
        run_mode="layer",
        start_state=State.DESIGNED,
        end_state=State.WRITTEN,
    ):
        super().__init__(skill_tree, run_mode, start_state, end_state)

    def _build_prompt(self):
        pass

    async def operate(self, function):
        logger.log(f"Function: {function.name}", "warning")
        other_functions = self.skill_tree.filtered_functions(function)
        other_functions_str = "\n\n".join([f.body for f in other_functions])

        action = WriteFunction(skill_tree=self.skill_tree)
        action.setup(
            function=function,
            other_functions_str=other_functions_str,
        )
        return await action.run()


if __name__ == "__main__":
    import asyncio
    from modules.framework.context import WorkflowContext
    import argparse

    context = WorkflowContext()
    path = "../../../workspace/test"
    context.load_from_file(f"{path}/designed_function.pkl")
    function_writer = WriteFunctionsAsync(
        context.global_skill_tree,
        "layer",
        start_state=State.DESIGNED,
        end_state=State.WRITTEN,
    )
    asyncio.run(function_writer.run())
    context.save_to_file("../../../workspace/test/written_function.pkl")

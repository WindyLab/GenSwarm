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

# from sympy.codegen.ast import continue_

from modules.file import logger
from modules.framework.action import ActionNode, AsyncNode
from modules.framework.code import FunctionNode, FunctionTree, State
from modules.framework.error import CodeParseError
from modules.framework.parser import SingleFunctionParser, parse_text
from modules.prompt import (
    GLOBAL_ROBOT_API,
    LOCAL_ROBOT_API,
    ALLOCATOR_TEMPLATE,
    ENV_DES,
    TASK_DES,
)
from modules.utils import root_manager


class CodeReview(ActionNode):
    def __init__(self, skill_tree, next_text="", node_name=""):
        super().__init__()
        self._function: FunctionNode = None
        self._skill_tree = skill_tree

    def _build_prompt(self):

        other_functions: list[FunctionNode] = self._skill_tree.filtered_functions(
            self._function
        )
        other_functions_str = "\n\n".join([f.function_body for f in other_functions])
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
            instruction=self.context.command,
            robot_api=robot_api,
            env_des=ENV_DES,
            function_name=self._function.name,

            other_functions=other_functions_str,
            function_content=self._function.content,
        )

    def setup(self, function: FunctionNode):
        self._function = function
        logger.log(f"Reviewing function: {self._function.name}", "warning")

    async def _process_response(self, response: str) -> str:
        desired_function_name = self._function.name

        try:
            codes = parse_text(text=response, all_matches=True)
            if not codes:
                logger.log("No code snippets were found in the response.", "warning")
                return response
        except ValueError as e:
            logger.log(f"No function detected in the response: {e}", "warning")
            return response

        for i, code in enumerate(codes):
            try:
                parser = SingleFunctionParser()
                parser.parse_code(code)
                parser.check_function_name(desired_function_name)
                self._skill_tree.update_from_parser(
                    parser.imports, parser.function_dict
                )
                self._skill_tree.save_code([desired_function_name])
                return code
            except Exception as e:
                logger.log(
                    f"Error processing code at index {i}: {e}. Code: {code}",
                    level="warning",
                )
                continue

        logger.log("All code snippets failed to parse.", level="warning")
        raise Exception("All code snippets failed to parse")


class CodeReviewAsync(AsyncNode):
    def __init__(
        self,
        skill_tree,
        run_mode="layer",
        start_state=State.WRITTEN,
        end_state=State.REVIEWED,
    ):
        super().__init__(skill_tree, run_mode, start_state, end_state)

    def _build_prompt(self):
        pass

    async def operate(self, function):
        action = CodeReview(self.skill_tree)
        action.setup(function)
        return await action.run()


if __name__ == "__main__":
    import asyncio
    from modules.framework.context import WorkflowContext
    import argparse

    context = WorkflowContext()
    path = "../../../workspace/test"
    context.load_from_file(f"{path}/written_function.pkl")
    root_manager.update_root("../../../workspace/test")

    code_reviewer = CodeReviewAsync(context.global_skill_tree, "sequential")
    asyncio.run(code_reviewer.run())
    context.save_to_file("../../../workspace/test/reviewed_function.pkl")

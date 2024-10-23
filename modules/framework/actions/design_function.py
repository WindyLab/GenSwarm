from modules.file import logger
from modules.framework.action import ActionNode, AsyncNode
from modules.framework.code import FunctionNode, FunctionTree, State
from modules.framework.constraint import ConstraintPool
from modules.framework.parser import SingleFunctionParser, parse_text
from modules.prompt import (
    GLOBAL_ROBOT_API,
    LOCAL_ROBOT_API,
    ALLOCATOR_TEMPLATE,
    ENV_DES,
    TASK_DES,
)
from modules.utils import root_manager


class DesignFunction(ActionNode):
    def __init__(self, skill_tree):
        super().__init__()
        self._function = None
        self.skill_tree: FunctionTree = skill_tree

    def setup(self, function: FunctionNode):
        self._function = function

    def _build_prompt(self):
        if self._function is None:
            logger.log("Function is not set", "error")
            raise SystemExit

        logger.log(f"Function: {self._function.name}", "warning")

        constraint_pool: ConstraintPool = ConstraintPool()
        other_functions: list[FunctionNode] = self.skill_tree.filtered_functions(
            self._function
        )
        other_functions_str = "\n".join(
            [f.brief if not f.body else f.body for f in other_functions]
        )
        if len(self.context.global_skill_tree.layers) == 0:
            local_api_prompt = LOCAL_ROBOT_API
        else:
            local_api_prompt = LOCAL_ROBOT_API + ALLOCATOR_TEMPLATE.format(
                template=self.context.global_skill_tree.output_template)
        robot_api = GLOBAL_ROBOT_API if self.context.scoop == "global" else local_api_prompt

        self.prompt = self.prompt.format(
            task_des=TASK_DES,
            robot_api=robot_api,
            env_des=ENV_DES,
            function_name=self._function.name,
            function_des=self._function.description,
            constraints=constraint_pool.filtered_constraints(
                related_constraints=self._function.connections
            ),
            other_functions=other_functions_str,
        )

    async def _process_response(self, response: str) -> str:
        desired_function_name = self._function.name
        code = parse_text(text=response)
        parser = SingleFunctionParser()
        parser.parse_code(code)
        parser.check_function_name(desired_function_name)
        new_definition = parser.function_definition
        function_name = parser.function_name
        self.skill_tree.set_definition(function_name, new_definition)
        return str(code)

    async def operate_on_node(self, function_node: FunctionNode):
        self._function = function_node
        return await self.run()


class DesignFunctionAsync(AsyncNode):
    def __init__(
            self, skill_tree, run_mode="layer", start_state=State.NOT_STARTED, end_state=State.DESIGNED,
    ):
        super().__init__(skill_tree, run_mode, start_state, end_state)

    def _build_prompt(self):
        pass

    async def operate(self, function):
        action = DesignFunction(skill_tree=self.skill_tree)
        action.setup(function)
        return await action.run()


if __name__ == "__main__":
    import asyncio
    from modules.framework.context import WorkflowContext
    import argparse

    context = WorkflowContext()
    path = "../../../workspace/test"
    root_manager.update_root('../../../workspace/test')

    context.load_from_file(f"{path}/analyze_functions.pkl")
    function_designer = DesignFunctionAsync(context.global_skill_tree)
    # function_designer = DesignFunctionAsync(context.local_skill_tree)

    asyncio.run(function_designer.run())
    context.save_to_file("../../../workspace/test/designed_function.pkl")

import asyncio
import time

from modules.framework.action import ActionNode
from modules.framework.response.code_parser import SingleFunctionParser
from modules.framework.code.function_node import FunctionNode, State
from modules.framework.response.text_parser import parse_text
from modules.prompt.design_stage_prompt import DesignFunction_PROMPT_TEMPLATE
from modules.prompt.robot_api_prompt import ROBOT_API
from modules.prompt.env_description_prompt import ENV_DES
from modules.prompt.task_description import TASK_DES
from modules.file.log_file import logger
from modules.framework.context.contraint_info import ConstraintPool
from modules.framework.code.function_tree import FunctionTree


class DesignFunction(ActionNode):
    def __init__(self, next_text: str, node_name: str = ""):
        super().__init__(next_text, node_name)
        self._function: FunctionNode = None
        self._function_pool = FunctionTree()

    def setup(self, function):
        self._function = function

    def _build_prompt(self):
        if self._function is None:
            logger.log("Function is not set", "error")
            raise SystemExit

        logger.log(f"Function: {self._function._name}", "warning")

        constraint_pool: ConstraintPool = ConstraintPool()
        other_functions: list[FunctionNode] = self._function_pool.filtered_functions(
            self._function
        )
        other_functions_str = "\n".join(
            [f.brief if not f.body else f.body for f in other_functions]
        )

        self.prompt = DesignFunction_PROMPT_TEMPLATE.format(
            task_des=TASK_DES,
            robot_api=ROBOT_API,
            env_des=ENV_DES,
            function_name=self._function.name,
            function_des=self._function.description,
            other_functions=other_functions_str,
        )

    async def _process_response(self, response: str) -> str:
        desired_function_name = self._function._name
        code = parse_text(text=response)
        parser = SingleFunctionParser()
        parser.parse_code(code)
        parser.check_function_name(desired_function_name)
        new_definition = parser.function_definition
        function_name = parser.function_name
        self._function_pool.set_definition(function_name, new_definition)
        return str(code)

    async def operate_on_node(self, function_node: FunctionNode):
        self._function = function_node
        return await self.run()


class DesignFunctionAsync(ActionNode):
    def _build_prompt(self):
        pass

    async def _run(self):
        function_pool = FunctionTree()

        async def operation(function: FunctionNode):
            action = DesignFunction("design single function")
            action.setup(function)
            return await action.run()

        # operation_type and state is defined in the FunctionNode class, 1 means design, 2 means write ,3 means review
        layer_index = function_pool.get_min_layer_index_by_state(State.NOT_STARTED)
        if layer_index == -1:
            logger.log("No functions in NOT_STARTED state", "error")
            raise SystemExit

        if not all(
            function_node.state == State.NOT_STARTED
            for function_node in function_pool._layers[layer_index].functions
        ):
            logger.log(
                "All functions in the layer are not in NOT_STARTED state", "error"
            )
            # TODO: 解决当出现生成的函数跑到前面层的问题。跑到后面层是通过重置State来解决的，但是跑到前面层的问题还没有解决
            time.sleep(1)
            raise SystemExit

        await function_pool.process_function_layer(
            operation, operation_type=State.DESIGNED, start_layer_index=layer_index
        )

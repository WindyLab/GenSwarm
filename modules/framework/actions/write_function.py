import asyncio
import time

from modules.framework.action import ActionNode
from modules.framework.actions import WriteRun
from modules.framework.response.code_parser import SingleFunctionParser
from modules.framework.code.function_node import FunctionNode, State
from modules.framework.response.text_parser import parse_text
from modules.prompt.coding_stage_prompt import WRITE_FUNCTION_PROMPT_TEMPLATE
from modules.prompt.robot_api_prompt import robot_api
from modules.prompt.task_description import TASK_DES
from modules.prompt.env_description_prompt import ENV_DES
from modules.file.log_file import logger
from modules.framework.context.contraint_info import ConstraintPool
from modules.framework.code.function_tree import FunctionTree


class WriteFunction(ActionNode):
    def __init__(self, next_text: str = "", node_name: str = ""):
        super().__init__(next_text, node_name)
        self._function = None
        self._constraint_text = ""
        self._other_functions_str = ""
        self._function_pool = FunctionTree()
        self._constraint_pool: ConstraintPool = ConstraintPool()

    def _build_prompt(self):
        self.prompt = WRITE_FUNCTION_PROMPT_TEMPLATE.format(
            task_des=TASK_DES,
            env_des=ENV_DES,
            robot_api=robot_api.get_prompt(),
            function_content=self._function._definition,
            other_functions=self._other_functions_str,
        )

    async def _process_response(self, response: str) -> str:
        desired_function_name = self._function.name
        code = parse_text(text=response)
        parser = SingleFunctionParser()
        parser.parse_code(code)
        parser.check_function_name(desired_function_name)
        self._function_pool.update_from_parser(parser.imports, parser.function_dict)
        return code

    async def operate_on_node(self, function_node: FunctionNode):
        logger.log(f"Function: {function_node.name}", "warning")
        other_functions = self._function_pool.filtered_functions(function)
        other_functions_str = "\n\n".join([f.body for f in other_functions])

        self._function = function_node
        self._constraint_text = self._constraint_pool.filtered_constraints(
            function_node.connections
        )
        self._other_functions_str = other_functions_str
        return await self.run()


class WriteFunctionsAsync(ActionNode):
    def __init__(self, next_text: str, node_name: str = ""):
        super().__init__(next_text, node_name)
        self._function_pool = FunctionTree()

    def _build_prompt(self):
        return super()._build_prompt()

    async def _run(self):
        constraint_pool: ConstraintPool = ConstraintPool()
        function_pool: FunctionTree = FunctionTree()

        async def operation(function: FunctionNode):
            logger.log(f"Function: {function.name}", "warning")
            other_functions = self._function_pool.filtered_functions(function)
            other_functions_str = "\n\n".join([f.body for f in other_functions])

            action = WriteFunction()
            action.setup(
                function=function,
                other_functions_str=other_functions_str,
                constraint_text=constraint_pool.filtered_constraints(
                    function.connections
                ),
            )
            return await action.run()

        layer_index = function_pool.get_min_layer_index_by_state(State.DESIGNED)
        # if layer_index == len(function_pool._layers) - 1:
        #     print(layer_index, len(function_pool._layers) - 1)
        #     write_run = WriteRun()
        #     return await write_run.run()

        if not all(
            function_node.state == State.DESIGNED
            for function_node in function_pool._layers[layer_index].functions
        ):
            logger.log("All functions in the layer are not in DESIGNED state", "error")
            # TODO: 解决当出现生成的函数跑到前面层的问题。跑到后面层是通过重置State来解决的，但是跑到前面层的问题还没有解决
            time.sleep(1)
            raise SystemExit
        await function_pool.process_function_layer(
            operation, operation_type=State.WRITTEN, start_layer_index=layer_index
        )

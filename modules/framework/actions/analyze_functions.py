from modules.framework.action import ActionNode
from modules.prompt.analyze_stage_prompt import (
    ANALYZE_FUNCTION_PROMPT_TEMPLATE,
    FUNCTION_TEMPLATE,
)
from modules.prompt.robot_api_prompt import ROBOT_API
from modules.prompt.env_description_prompt import ENV_DES
from modules.prompt.task_description import TASK_DES
from modules.framework.context.contraint_info import ConstraintPool
from modules.framework.code.function_tree import FunctionTree
from modules.file.log_file import logger
from modules.framework.response import *


class AnalyzeFunctions(ActionNode):
    def __init__(self, next_text, node_name=""):
        super().__init__(next_text, node_name)
        self._constraint_pool: ConstraintPool = ConstraintPool()
        self._function_pool = FunctionTree()

    def _build_prompt(self):
        self.prompt = ANALYZE_FUNCTION_PROMPT_TEMPLATE.format(
            task_des=TASK_DES,
            instruction=self.context.command,
            robot_api=ROBOT_API,
            env_des=ENV_DES,
            output_template=FUNCTION_TEMPLATE,
        )

    async def _process_response(self, response: str) -> str:
        content = parse_text(response, "json")
        self._function_pool.init_functions(content)
        logger.log(f"Analyze Functions Success", "success")
        return response


if __name__ == "__main__":
    import asyncio
    from modules.framework.context.workflow_context import WorkflowContext

    context = WorkflowContext()
    context.command = "Integrate into a flock, adhering to cohesion by staying connected, alignment by moving together, and separation by maintaining at least 0.5 meters between robots."
    function_analyser = AnalyzeFunctions("analyze constraints")
    function_analyser.context = context
    path = "../../../workspace/test"
    asyncio.run(function_analyser.run())
    function_analyser.context.save_to_file(f"{path}/analyze_functions.pkl")

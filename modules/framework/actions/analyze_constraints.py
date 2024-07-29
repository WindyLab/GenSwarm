import json

from modules.framework.action import ActionNode
from modules.llm.gpt import GPT
from modules.prompt.analyze_stage_prompt import (
    ANALYZE_CONSTRAINT_PROMPT_TEMPLATE,
    CONSTRAIN_TEMPLATE,
    CONTINUE_ANALYZE_CONSTRAINT_PROMPT_TEMPLATE,
    MODIFY_CONSTRAIN_TEMPLATE,
)
from modules.prompt.robot_api_prompt import ROBOT_API
from modules.prompt.env_description_prompt import ENV_DES
from modules.prompt.task_description import TASK_DES
from modules.framework.response.text_parser import parse_text
from modules.file.log_file import logger
from modules.framework.context.contraint_info import ConstraintPool
from modules.framework.response import *


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
        self.prompt = ANALYZE_CONSTRAINT_PROMPT_TEMPLATE.format(
            task_des=TASK_DES,
            instruction=self.context.command,
            robot_api=ROBOT_API,
            env_des=ENV_DES,
            output_template=CONSTRAIN_TEMPLATE,
            user_constraints=json.dumps(user_constraints, indent=4),
        )

    async def _process_response(self, response: str) -> str:
        content = parse_text(response, "json")
        self._constraint_pool.init_constraints(content)
        if self._interaction_mode:
            satisfied = input("Are you satisfied with the constraints? (y/n)")
            if satisfied != "y":
                await self.interaction_with_user()

        logger.log(f"Analyze Constraints Success", "success")

    async def interaction_with_user(self):
        feedback = input("Please provide feedback:")
        self.prompt = CONTINUE_ANALYZE_CONSTRAINT_PROMPT_TEMPLATE.format(
            feedback=feedback,
            output_template=MODIFY_CONSTRAIN_TEMPLATE,
        )
        await self._run()


if __name__ == "__main__":
    import asyncio
    from modules.framework.context.workflow_context import WorkflowContext
    import argparse

    parser = argparse.ArgumentParser(
        description="Run simulation with custom parameters."
    )

    parser.add_argument(
        "--interaction_mode",
        type=bool,
        default=True,
        help="Whether to run in interaction mode in analyze constraints.",
    )
    context = WorkflowContext()
    context.command = "Integrate into a flock, adhering to cohesion by staying connected, alignment by moving together, and separation by maintaining at least 0.5 meters between robots."
    constraint_analyser = AnalyzeConstraints("analyze constraints")

    asyncio.run(constraint_analyser.run())
    context.save_to_file("../../../workspace/test/constraint.pkl")

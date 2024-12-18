import json
import os

from modules.framework.action import ActionNode
from modules.framework.code import FunctionTree
from modules.framework.parser import CodeParser, parse_text
from modules.llm import GPT
from modules.prompt import (
    FEEDBACK_PROMPT_TEMPLATE,
    CONTINUE_FEEDBACK_PROMPT_TEMPLATE,
    LOCAL_ROBOT_API,
    GLOBAL_ROBOT_API,
    ENV_DES,
    TASK_DES,
    ALLOCATOR_TEMPLATE,
)
from modules.utils import root_manager, rich_code_print


class CodeImprove(ActionNode):
    def __init__(self, next_text: str = "", node_name: str = ""):
        super().__init__(next_text, node_name)
        self.feedback = None
        self._call_times = 0
        self.set_logging_text(f"Improve code via feedback")
        self.code = None

    def _build_prompt(self):
        # if self._call_times == 0:
        if len(self.context.global_skill_tree.layers) == 0:
            local_api_prompt = LOCAL_ROBOT_API
        else:
            local_api_prompt = LOCAL_ROBOT_API + ALLOCATOR_TEMPLATE.format(
                template=self.context.global_skill_tree.output_template
            )
        if self.feedback is None:
            vlm_file = os.path.join(root_manager.workspace_root, "vlm.json")
            if os.path.exists(vlm_file):
                with open(vlm_file, "r") as f:
                    result = json.load(f)
                    if result.get("success", ""):
                        self._next = None
                        raise SystemExit("Success, exit!")
                    self.feedback = result.get("feedback", "")

        self.prompt = FEEDBACK_PROMPT_TEMPLATE.format(
            task_des=TASK_DES,
            global_api=GLOBAL_ROBOT_API,
            local_api=local_api_prompt,
            instruction=self.context.command,
            env_des=ENV_DES,
            global_functions="\n\n\n".join(
                self.context.global_skill_tree.functions_body
            ),
            local_functions="\n\n\n".join(self.context.local_skill_tree.functions_body),
            feedback=self.feedback,
        )

        # else:
        #     self.prompt = CONTINUE_FEEDBACK_PROMPT_TEMPLATE.format(
        #         feedback=self.feedback,
        #
        #     )
        #     self._call_times += 1

    def setup(self, feedback: str):
        self.feedback = feedback
        self.set_logging_text(f"Improving Code")

    async def _process_response(self, response: str, **kwargs) -> str:
        code = parse_text(text=response)
        parser = CodeParser()
        parser.parse_code(code)
        function_list = parser.function_names

        # 判断每个函数属于哪个 skill tree
        for func_name, func_body in parser.function_dict.items():
            if func_name in self.context.global_skill_tree.names:
                # 更新 global_skill_tree
                self.context.global_skill_tree.update_from_parser(
                    parser.imports, {func_name: func_body}
                )
            elif func_name in self.context.local_skill_tree.names:
                # 更新 local_skill_tree
                self.context.local_skill_tree.update_from_parser(
                    parser.imports, {func_name: func_body}
                )

        # 保存函数到文件
        self.context.global_skill_tree.save_functions_to_file()
        self.context.local_skill_tree.save_functions_to_file()
        self.code = code
        return str(code)

    def _display(self):
        rich_code_print("Improve Code", self.code, f"New Code")


if __name__ == "__main__":
    critic = Criticize("constraints")
    import asyncio

    path = "../../../workspace/test"
    root_manager.update_root(path)
    critic.context.load_from_file(path + "/run_code.pkl")
    asyncio.run(critic.run())
    critic.context.save_to_file(f"{path}/analyze_constraints.pkl")

from modules.framework.action import ActionNode
from modules.framework.code.parser import AstParser
from modules.prompt.run_code_prompt import HUMAN_FEEDBACK_PROMPT_TEMPLATE
from modules.prompt.robot_api_prompt import ROBOT_API
from modules.prompt.env_description_prompt import ENV_DES
from modules.prompt.task_description import TASK_DES
from modules.framework.code.parser import parse_text
from modules.framework.context.function_info import FunctionPool

class GrammarFeedback(ActionNode):
    def __init__(self, next_text: str = '', node_name: str = ''):
        super().__init__(next_text, node_name)
        self.feedback = None
        self._function_pool = FunctionPool()

    def _build_prompt(self):

        self.prompt = HUMAN_FEEDBACK_PROMPT_TEMPLATE.format(
            task_des=TASK_DES,
            robot_api=ROBOT_API,
            env_des=ENV_DES,
            #!warn: exclude functions with empty content
            functions=self._function_pool.function_valid_content,
            feedback=self.feedback,
        )

    def setup(self, feedback: str):
        self.feedback = feedback

    def _process_response(self, response: str, **kwargs) -> str:
        code = parse_text(text=response)
        code_obj = AstParser(code)
        code_obj.parse_code(code)
        function_list = code_obj.function_names
        code_obj.save_to_pool()

        self._function_pool.save_and_check_functions(function_list)

        return str(code)

if __name__ == '__main__':
    critic = GrammarFeedback("constraints")
    from modules.utils import root_manager
    import asyncio

    path = '../../../workspace/test'
    root_manager.update_root(path)
    critic.context.load_from_file(path + "/run_code.pkl")
    asyncio.run(critic.run())
    critic.context.save_to_file(f'{path}/analyze_constraints.pkl')

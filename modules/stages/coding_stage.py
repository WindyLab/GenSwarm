import asyncio

from modules.prompt.robot_api_prompt import ROBOT_API
from modules.prompt.env_description_prompt import ENV_DES
from modules.stages.stage import Stage, StageResult
from modules.actions import WriteCode
from modules.utils import CodeMode, extract_top_level_function_names
from modules.prompt.coding_stage_prompt import WRITE_FUNCTION_PROMPT_TEMPLATE, WRITE_RUN_PROMPT_TEMPLATE
from modules.framework.workflow_context import FileStatus
from modules.utils import combine_unique_imports


class CodingStage(Stage):
    def __init__(self, action: WriteCode = None):
        super().__init__()
        self._action = action

    async def _write_run(self):
        sequence_diagram = self._context.sequence_diagram.message
        function_content_list = [f['content'] for f in self._context.function_list]
        function_list_str = "\n".join(function_content_list)
        result = await self._action.run(
            prompt=WRITE_RUN_PROMPT_TEMPLATE.format(sequence_diagram=sequence_diagram, env_des=ENV_DES,
                                                    robot_api=ROBOT_API, function_list=function_list_str),
            filename=f"run.py"
        )
        return result

    async def _write_function(self, function: str, index: int, other_functions: list[str], function_name: str):
        result = await self._action.run(
            prompt=WRITE_FUNCTION_PROMPT_TEMPLATE.format(
                env_des=ENV_DES,
                robot_api=ROBOT_API,
                function=function,
                other_functions="\n".join(other_functions)
            ),
            filename=f"functions.py",
            function_name=function_name
        )
        # add the function code to the functions.py file
        new_message = (self._context.code_files['functions.py'].message
                       + f'\n\n{eval(result)["code"][0]}')
        self._context.code_files['functions.py'].message = new_message

        # update the function list with the new function code
        self._context.function_list[index]['content'] = eval(result)['code'][0]
        return eval(result)

    async def _write_functions(self):

        function_list = self._context.function_list
        tasks = []
        import_list = []
        for index, function in enumerate(function_list):
            other_functions = [f['content'] for f in function_list if f != function]
            task = asyncio.create_task(self._write_function(
                function=function['content'],
                index=index,
                other_functions=other_functions,
                function_name=function['name'])
            )
            tasks.append(task)
        result_list = await asyncio.gather(*tasks)

        # combine the import lists from all the functions
        for result in result_list:
            import_list.extend(result['import'])
        combined_import_str = combine_unique_imports(import_list) + '\n'
        # add the import list to the functions.py file
        new_message = combined_import_str + self._context.code_files['functions.py'].message
        self._context.code_files['functions.py'].message = new_message

    async def _run(self) -> StageResult:
        code_files = self._context.code_files
        if code_files['functions.py'].status == FileStatus.NOT_WRITTEN:
            await self._write_functions()
            code_files['functions.py'].version += 1
            return StageResult(keys=[CodeMode.WRITE_FUNCTION])

        elif code_files['run.py'].status == FileStatus.NOT_WRITTEN:
            await self._write_run()
            code_files['run.py'].version += 1
            return StageResult(keys=[CodeMode.WRITE_RUN])

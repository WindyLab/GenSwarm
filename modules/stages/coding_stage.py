import asyncio

from modules.prompt.design_stage_prompt import DesignFunction_PROMPT_TEMPLATE
from modules.prompt.robot_api_prompt import ROBOT_API, robot_api
from modules.prompt.env_description_prompt import ENV_DES
from modules.prompt.task_description import TASK_DES
from modules.stages.stage import Stage, StageResult
from modules.actions import WriteCode, DesignFunction
from modules.utils import CodeMode, extract_top_level_function_names
from modules.prompt.coding_stage_prompt import WRITE_FUNCTION_PROMPT_TEMPLATE, WRITE_RUN_PROMPT_TEMPLATE
from modules.framework.workflow_context import FileStatus, WorkflowContext


class CodingStage(Stage):
    def __init__(self, action: WriteCode = None):
        super().__init__()
        self._action = action

    async def _design_function(self, prompt: str, function_name: str):
        self._action = DesignFunction()
        await self._action.run(prompt=prompt, function_name=function_name)

    async def _design_functions(self):
        function_layers = self._context.function_pool.function_layer
        for i, layer in enumerate(function_layers):
            tasks = []
            self._context.log.format_message(f"Layer: {i}", "warning")
            for function in layer:
                self._context.log.format_message(f"Function: {function.name}", "warning")
                constraint_text = ''
                for constraint in function.satisfying_constraints:
                    if constraint not in self._context.constraint_pool.constraints:
                        print(f"Constraint {constraint} is not in the constraint pool")
                        raise SystemExit
                    constraint_text += self._context.constraint_pool.constraints[constraint].text + '\n'

                function_list = [f.text if f.content is None else f.content for f in
                                 self._context.function_pool.functions.values() if f.name != function.name]

                prompt = DesignFunction_PROMPT_TEMPLATE.format(
                    task_des=TASK_DES,
                    robot_api=robot_api.get_prompt(),
                    env_des=ENV_DES,
                    function_name=function.name,
                    function_des=function.description,
                    constraints=constraint_text,
                    other_functions='\n'.join(function_list)

                )
                task = asyncio.create_task(self._design_function(prompt, function.name))
                tasks.append(task)
            await asyncio.gather(*tasks)

    async def _write_function(self, prompt: str, function_name: str):
        self._action = WriteCode()
        await self._action.run(prompt=prompt, function_name=function_name)

    async def _write_functions(self):
        function_layers = self._context.function_pool.function_layer
        for i, layer in enumerate(function_layers):
            self._context.log.format_message(f"Layer: {i}", "warning")
            tasks = []
            for function in layer:
                self._context.log.format_message(f"Function: {function.name}", "warning")
                constraint_text = ''
                for constraint in function.satisfying_constraints:
                    if constraint not in self._context.constraint_pool.constraints:
                        print(f"Constraint {constraint} is not in the constraint pool")
                        raise SystemExit
                    constraint_text += self._context.constraint_pool.constraints[constraint].text + '\n'

                function_list = [f.text if f.content is None else f.content for f in
                                 self._context.function_pool.functions.values() if f.name != function.name]

                api_list = [name for name in function.calls if name in robot_api.apis.keys()]
                prompt = WRITE_FUNCTION_PROMPT_TEMPLATE.format(
                    task_des=TASK_DES,
                    robot_api=robot_api.get_prompt(),
                    env_des=ENV_DES,
                    function_content=function.content,
                    constraints=constraint_text,
                    other_functions='\n\n'.join(function_list)

                )
                task = asyncio.create_task(self._write_function(prompt, function_name=function.name))
                tasks.append(task)
            await asyncio.gather(*tasks)

    async def _write_run(self):
        self._action = WriteCode()
        functions = '\n\n'.join(
            [f.content for f in self._context.function_pool.functions.values() if f.content is not None])
        prompt = WRITE_RUN_PROMPT_TEMPLATE.format(
            task_des=TASK_DES,
            robot_api=ROBOT_API,
            functions=functions,
        )
        await self._action.run(prompt=prompt, function_name='run_loop')

    async def _run(self) -> StageResult:
        await self._design_functions()
        await self._write_functions()
        await self._write_run()
        return StageResult()


if __name__ == '__main__':
    from modules.utils import root_manager
    import os
    import pickle

    path = '/home/derrick/catkin_ws/src/code_llm/workspace/test'
    # pkl_path = f'{path}/design_stage.pkl'
    # pkl_path = f'{path}/analyze_functions_stage.pkl'
    # pkl_path = f'{path}/coding_stage.pkl'
    # pkl_path = f'{path}/design_functions_stage.pkl'
    pkl_path = f'{path}/write_run_stage.pkl'
    programmer = CodingStage(WriteCode())
    programmer.context.load_from_file(pkl_path)
    root_manager.update_root(path, set_data_path=False)

    programmer.context.function_pool.update_message()

    asyncio.run(programmer.run())
    # # programmer.context.save_to_file(f'{path}/coding_stage.pkl')
    # # programmer.context.save_to_file(f'{path}/write_functions_stage.pkl')
    # # programmer.context.save_to_file(f'{path}/design_functions_stage.pkl')
    programmer.context.save_to_file(f'{path}/write_run_stage.pkl')

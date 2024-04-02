import argparse
import asyncio
from os import listdir

from modules.actions import RunCode, Debug
from modules.stages.stage import Stage, StageResult
from modules.utils import get_param, call_reset_environment
from modules.prompt.run_code_prompt import DEBUG_PROMPT
from modules.prompt.env_description_prompt import ENV_DES
from modules.prompt.robot_api_prompt import ROBOT_API
from modules.prompt.task_description import TASK_DES
from modules.utils import TestResult


class RunningStage(Stage):
    def __init__(self, action: RunCode = None):
        super().__init__()
        self._action = action
        self._error_message = ""

    async def _run_code(self, robot_id: int) -> str:
        code_info = {
            'command': ["python", "run.py", str(robot_id)]
        }
        result = await self._action.run(
            code_info=code_info,
            mode='script',
        )
        return result

    async def _run_codes(self):
        robot_num = get_param('robots_num')
        tasks = []
        self._action = RunCode()

        try:
            print(f"call reset environment: start")
            call_reset_environment(True)
            for robot_id in range(robot_num):
                task = asyncio.create_task(self._run_code(robot_id))
                tasks.append(task)
            result_list = list(set(await asyncio.gather(*tasks)))
        finally:
            print(f"call reset environment: end")
            call_reset_environment(True)
            from modules.utils import generate_video_from_frames, root_manager
            data_root = root_manager.data_root
            number = len(listdir(f"{data_root}/frames")) - 1
            generate_video_from_frames(
                frames_folder=f"{data_root}/frames/frame{number}",
                video_path=f"{data_root}/output{number}.mp4",
            )
            print(f"synthesize frame{number} ---> output{number}.mp4")
            print("############END############")

        return result_list

    async def _debug(self, error_message: str):
        mentioned_function = ""
        for function in self.context.function_pool.functions.values():
            if function.name in error_message:
                mentioned_function += "\n\n" + function.content
        self._action = Debug()
        prompt = DEBUG_PROMPT.format(
            task_des=TASK_DES,
            robot_api=ROBOT_API,
            env_des=ENV_DES,
            mentioned_functions=mentioned_function,
            error_message=error_message

        )
        await self._action.run(prompt=prompt)

    async def _run(self) -> StageResult:
        result = await self._run_codes()
        if 'NONE' in result and len(result) == 1:
            self._error_message = "No result received"
            return StageResult(keys=[TestResult.ALL_PASS])
        elif 'Timeout' in result and len(result) == 1:
            return StageResult(keys=[TestResult.ALL_PASS])

        result_content = '\n'.join(result)
        await self._debug(result_content)
        return StageResult(keys=[TestResult.NOT_PASS])


if __name__ == '__main__':
    run_test = RunningStage(RunCode())
    from modules.utils import root_manager

    parser = argparse.ArgumentParser(description="Run simulation with custom parameters.")
    parser.add_argument("--timeout", type=int, default=30, help="Total time for the simulation")
    args = parser.parse_args()
    path = '/home/lufengxu/distributedArchitecture/src/code_llm/workspace/2024-04-02_15-55-41'
    # run_test.context.load_from_file(f'{path}/write_run_stage.pkl')
    run_test.context.args = args
    root_manager.update_root(path, set_data_path=False)
    asyncio.run(run_test.run())
    # run_test.context.save_to_file(f'{path}/running_stage.pkl')

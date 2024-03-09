import asyncio
from os import listdir

from modules.actions import RunCode
from modules.stages.stage import Stage, StageResult
from modules.utils import get_param, call_reset_environment


class RunningStage(Stage):
    def __init__(self, action: RunCode = None):
        super().__init__()
        self._action = action

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

        try:
            call_reset_environment(True)
            for robot_id in range(robot_num):
                task = asyncio.create_task(self._run_code(robot_id))
                tasks.append(task)
            result_list = await asyncio.gather(*tasks)
        except Exception as e:
            self._logger.error(f"An error occurred while running the command: {e}")
            result_list = [f"An error occurred while running the command: {e}"]
        finally:
            call_reset_environment(True)
            from modules.utils import generate_video_from_frames, root_manager
            data_root = root_manager.data_root
            generate_video_from_frames(
                frames_folder=f"{data_root}/frames",
                video_path=f"{data_root}/output{len(listdir(data_root))}.mp4",
            )
        return '\n'.join(result_list)

    async def _run(self) -> StageResult:
        result = await self._run_codes()
        self._context.run_result.message = result
        return StageResult(keys=[])


if __name__ == '__main__':
    run_test = RunningStage(RunCode())
    from modules.utils import root_manager

    path = '/home/ubuntu/Desktop/CodeLLM/workspace/2024-03-09_10-38-59'
    root_manager.update_root(path)
    asyncio.run(run_test.run())

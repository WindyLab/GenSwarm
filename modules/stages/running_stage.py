from modules.actions import RunCode
from modules.stages.stage import Stage, StageResult
from modules.utils import get_param, call_reset_environment
import asyncio


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

        call_reset_environment(True)
        for robot_id in range(robot_num):
            task = asyncio.create_task(self._run_code(robot_id))
            tasks.append(task)
        result_list = await asyncio.gather(*tasks)
        call_reset_environment(True)

        return '\n'.join(result_list)

    async def _run(self) -> StageResult:
        result = await self._run_codes()
        self._context.run_result.message = result
        return StageResult(keys=[])


if __name__ == '__main__':
    run_test = RunningStage(RunCode())
    from modules.const import set_workspace_root

    set_workspace_root('/home/derrick/catkin_ws/src/code_llm/workspace/2024-03-05_15-05-15')
    asyncio.run(run_test.run())

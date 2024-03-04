from modules.stages.stage import Stage, StageResult
from modules.actions import AnalyzeReqs
from modules.prompt.const import ROBOT_API, ENV_DES
from modules.prompt.analyze_prompt import ANALYZE_PROMPT_TEMPLATE


class AnalyzeStage(Stage):
    def __init__(self, action: AnalyzeReqs):
        super(AnalyzeStage, self).__init__()
        self._user_command = ""
        self._action = action

    async def _run(self) -> StageResult:
        prompt = ANALYZE_PROMPT_TEMPLATE.format(instruction=self._context.user_command.message, api=ROBOT_API, env_des=ENV_DES)
        await self._action.run(prompt=prompt)
        return StageResult(keys=[])


if __name__ == "__main__":
    stage = AnalyzeStage(AnalyzeReqs())
    res = stage.run()
    print(res)

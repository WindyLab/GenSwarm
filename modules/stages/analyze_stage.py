from modules.stages.stage import Stage, StageResult
from modules.actions import AnalyzeReqs
from modules.prompt.robot_api_prompt import ROBOT_API
from modules.prompt.env_description_prompt import ENV_DES
from modules.prompt.analyze_stage_prompt import ANALYZE_PROMPT_TEMPLATE


class AnalyzeStage(Stage):
    def __init__(self, action: AnalyzeReqs):
        super(AnalyzeStage, self).__init__()
        self._user_command = ""
        self._action = action

    async def _run(self) -> StageResult:
        prompt = ANALYZE_PROMPT_TEMPLATE.format(
            instruction=self._context.user_command.message,
            robot_api=ROBOT_API,
            env_des=ENV_DES
        )
        await self._action.run(prompt=prompt)
        return StageResult(keys=[])


if __name__ == "__main__":
    stage = AnalyzeStage(AnalyzeReqs())
    res = stage.run()
    print(res)

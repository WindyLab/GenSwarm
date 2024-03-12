from modules.framework.workflow_context import FileStatus
from modules.stages.stage import Stage, StageResult
from modules.actions import DesignFunction, WriteSeqDiagram
from modules.prompt.robot_api_prompt import ROBOT_API
from modules.prompt.env_description_prompt import ENV_DES
from modules.utils import DesignPattern
from modules.prompt.design_stage_prompt import DesignFunction_PROMPT_TEMPLATE,WriteSeqDiagram_PROMPT_TEMPLATE


class DesignStage(Stage):
    def __init__(self, action: DesignFunction | WriteSeqDiagram = None):
        super().__init__()
        self._action = action

    async def _design_function(self):
        self._action = DesignFunction()
        prompt = DesignFunction_PROMPT_TEMPLATE.format(
            analysis=self._context.analysis.message,
            code=ROBOT_API,
            env_des=ENV_DES
        )
        await self._action.run(prompt=prompt)

    async def _design_sequence_diagram(self):
        self._action = WriteSeqDiagram()
        analysis = self._context.analysis.message
        function_content_list = [f['content'] for f in self._context.function_list]
        function_list_str = "\n".join(function_content_list)
        prompt = WriteSeqDiagram_PROMPT_TEMPLATE.format(
            analysis=analysis,
            robot_api=ROBOT_API,
            function_list=function_list_str,
            env_des=ENV_DES
        )
        await self._action.run(prompt=prompt)

    async def _run(self) -> StageResult:
        # if no function list, design function
        if not self._context.function_list:
            await self._design_function()
            return StageResult(keys=[DesignPattern.FUNCTION])

        # if no sequence diagram and function list exists, design sequence diagram
        elif self._context.sequence_diagram.status == FileStatus.NOT_WRITTEN:
            await self._design_sequence_diagram()
            return StageResult(keys=[DesignPattern.SEQ_DIAGRAM])

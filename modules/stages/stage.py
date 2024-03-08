from enum import Enum
from typing import List, Union, final
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from modules.utils.logger import setup_logger, LoggerLevel
from modules.utils.common import TestResult, BugSource, DesignPattern, CodeMode
from modules.framework.workflow_context import WorkflowContext


class StageResult(BaseModel):
    keys: List[Union[TestResult, BugSource, DesignPattern, CodeMode]] = Field(default=[])


class StageType(Enum):
    AnalyzeStage = 1
    DesignStage = 2
    CodingStage = 3
    TestingStage = 4
    RunningStage = 5
    FinalStage = 6


class Stage(ABC, BaseModel):
    def __init__(self):
        super(Stage, self).__init__()
        self._logger = setup_logger(self.__class__.__name__, LoggerLevel.DEBUG)
        self._context = WorkflowContext()

    def __str__(self) -> str:
        return self.__class__.__name__

    @final
    async def run(self) -> StageResult:
        # self._logger.info(f"Current stage: {self}")
        self._context.log.format_message(str(self), "stage")
        return await self._run()

    async def _run(self) -> StageResult:
        return StageResult()


if __name__ == "__main__":
    stage = Stage()
    print(stage.test())

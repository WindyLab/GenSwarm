from enum import Enum

from pydantic import BaseModel, Field

from modules.utils import read_file, write_file, append_file
from modules.const import WORKSPACE_ROOT


class FileStatus(Enum):
    NOT_WRITTEN = 0
    NOT_TESTED = 1
    TESTED_FAIL = 2
    TESTED_PASS = 3


class RunResult(Enum):
    WITH_ERROR = 1
    WITHOUT_ERROR = 2


class FileInfo(BaseModel):
    name: str = Field(default='')
    status: FileStatus = Field(default=FileStatus.NOT_WRITTEN)
    version: int = Field(default=0)

    def __init__(self, name: str = '', message: str = ''):
        super().__init__()
        self.name = name
        self._message = message

    @property
    def message(self):
        if not self._message:
            self._message = read_file(WORKSPACE_ROOT, self.name)
        return self._message

    @message.setter
    def message(self, content: str):
        self._message = content
        if self.status == FileStatus.NOT_WRITTEN:
            self.status = FileStatus.NOT_TESTED
        write_file(WORKSPACE_ROOT, self.name, content)

class FileLog(BaseModel):
    name: str = Field(default='')
    # status: FileStatus = Field(default=FileStatus.NOT_WRITTEN)
    version: int = Field(default=0)

    def __init__(self, name: str = '', message: str = ''):
        super().__init__()
        self.name = name
        self._message = message

    @property
    def message(self):
        self._message = read_file(WORKSPACE_ROOT, self.name)
        return self._message

    @message.setter
    def message(self, content: str):
        append_file(WORKSPACE_ROOT, self.name, content)

class WorkflowContext():
    _instance = None
    user_command: FileInfo = FileInfo(name='command.md')
    analysis: FileInfo = FileInfo(name='analysis.md')
    function_list: list[str] = []
    code_files: dict[str, FileInfo] = {
        'functions.py': FileInfo(name='functions.py'),
        'test.py': FileInfo(name='test.py'),
        'run.py': FileInfo(name='run.py'),
    }
    sequence_diagram: FileInfo = FileInfo(name='sequence_diagram.md')
    run_result: FileInfo = FileInfo(name='run_result.md')
    log: FileLog = FileLog(name='log.md')

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance


if __name__ == "__main__":
    context = WorkflowContext()
    context.user_command = "this is a test"
    tt = context.code_files
    tt["test"] = "dd"
    print(context.code_files)

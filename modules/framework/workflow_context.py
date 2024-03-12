import argparse
from enum import Enum

from pydantic import BaseModel, Field
from modules.utils import read_file, write_file
from modules.utils import setup_logger, LoggerLevel, format_log_message


class FileStatus(Enum):
    NOT_WRITTEN = 0
    NOT_TESTED = 1
    TESTED_FAIL = 2
    TESTED_PASS = 3


class RunResult(Enum):
    WITH_ERROR = 1
    WITHOUT_ERROR = 2


class FileInfo(BaseModel):
    root: str = Field(default='')
    name: str = Field(default='')
    status: FileStatus = Field(default=FileStatus.NOT_WRITTEN)
    version: int = Field(default=0)

    def __init__(self, name: str = '', message: str = '', root: str = ''):
        super().__init__()
        self.name = name
        self._message = message
        self.root = root

    @property
    def message(self):
        if not self._message:
            from modules.utils import root_manager
            self.root = root_manager.workspace_root
            self._message = read_file(self.root, self.name)
        return self._message

    @message.setter
    def message(self, content: str):
        self._message = content
        if self.status == FileStatus.NOT_WRITTEN:
            self.status = FileStatus.NOT_TESTED
        from modules.utils import root_manager
        self.root = root_manager.workspace_root
        write_file(self.root, self.name, content)


class FileLog(FileInfo):
    def __init__(self, name: str = '', message: str = '', root: str = ''):
        super().__init__(name, message, root)
        self._logger = setup_logger(self.__class__.__name__, LoggerLevel.DEBUG)

    @property
    def message(self):
        return super().message

    @message.setter
    def message(self, content: str):
        from modules.utils import root_manager
        self.root = root_manager.workspace_root
        write_file(self.root, self.name, content, mode='a')

    def format_message(self, content: str, style: str):
        """
        Formats a message based on the provided style and logs the content.

        :param content: The message content to be formatted and logged.
        :param style: The style to format the message. Supported styles: stage, action,
                      prompt, response, success, error, warning.
        """
        color_mapping = {
            'stage': '***\n# <span style="color: blue;">Current Stage: *{}*</span>\n',
            'action': '## <span style="color: purple;">Current Action: *{}*</span>\n',
            'prompt': '### <span style="color: grey ;">Prompt: </span>\n{}\n',
            'response': '### <span style="color: black;">Response: </span>\n{}\n',
            'success': '#### <span style="color: gold;">Success: {}</span>\n',
            'error': '#### <span style="color: red;">Error: </span>\n{}\n',
            'warning': '#### <span style="color: orange;">Warning: </span>\n{}\n',
        }

        # Verify style is supported
        if style not in color_mapping:
            self._logger.error(f"Style {style} is not supported")
        log_action = {
            'stage': self._logger.info,
            'action': self._logger.debug,
            'prompt': self._logger.debug,
            'response': self._logger.info,
            'success': self._logger.info,
            'error': self._logger.error,
            'warning': self._logger.warning,
        }.get(style, self._logger.info)

        log_action(content)

        self.message = color_mapping[style].format(content)


class WorkflowContext:
    _instance = None
    user_command: FileInfo = FileInfo(name='command.md')
    analysis: FileInfo = FileInfo(name='analysis.md')
    function_list: list[dict[str, str]] = []
    code_files: dict[str, FileInfo] = {
        'functions.py': FileInfo(name='functions.py'),
        'test.py': FileInfo(name='test.py'),
        'run.py': FileInfo(name='run.py'),
    }
    sequence_diagram: FileInfo = FileInfo(name='sequence_diagram.md')
    run_result: FileInfo = FileInfo(name='run_result.md')
    log: FileLog = FileLog(name='log.md')
    args: argparse.Namespace = argparse.Namespace()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance


if __name__ == "__main__":
    # context = WorkflowContext()
    # context.log.message = ('Hello World!', 'prompt')
    log = FileLog(name='log.md')
    log.format_message('a', 'prompt')

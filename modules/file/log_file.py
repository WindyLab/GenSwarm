"""
Copyright (c) 2024 WindyLab of Westlake University, China
All rights reserved.

This software is provided "as is" without warranty of any kind, either
express or implied, including but not limited to the warranties of
merchantability, fitness for a particular purpose, or non-infringement.
In no event shall the authors or copyright holders be liable for any
claim, damages, or other liability, whether in an action of contract,
tort, or otherwise, arising from, out of, or in connection with the
software or the use or other dealings in the software.
"""
from datetime import datetime

from modules.utils import setup_logger, LoggerLevel
from .base_file import BaseFile


class _Logger:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._logger = setup_logger(cls.__class__.__name__, LoggerLevel.DEBUG)
            cls._file: BaseFile = None
            cls._color_mapping = {
                "stage": '***\n# <span style="color: blue;">Current Stage: *{}*</span>\n',
                "action": '## <span style="color: purple;">Current Action: *{}*</span>\n',
                "prompt": '### <span style="color: grey ;">Prompt: </span>\n{}\n',
                "response": '### <span style="color: black;">Response: </span>\n{}\n',
                "success": '#### <span style="color: gold;">Success: {}</span>\n',
                "error": '#### <span style="color: red;">Error: </span>\n{}\n',
                "warning": '#### <span style="color: orange;">Warning: </span>\n{}\n',
                "info": '#### <span style="color: black;">info: </span>\n{}\n',
                "debug": '#### <span style="color: black;">debug: </span>\n{}\n',
            }
            cls._log_action_dict = {
                "stage": cls._logger.info,
                "action": cls._logger.debug,
                "prompt": cls._logger.debug,
                "response": cls._logger.info,
                "success": cls._logger.info,
                "error": cls._logger.error,
                "warning": cls._logger.warning,
                "info": cls._logger.info,
                "debug": cls._logger.debug,
            }
        return cls._instance

    def set_file(self, file: BaseFile):
        self._file = file

    def is_file_exists(self):
        return self._file is not None

    def log(self, content: str, level: str = "info", print_to_terminal: bool = True):
        """
        Formats a message based on the provided style and logs the content.

        :param content: The message content to be formatted and logged.
        :param level: The style to format the message. Supported styles: stage, action,
                      prompt, response, success, error, warning.
        """
        # Get current time as a timestamp
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S:%f]")

        # Verify level is supported
        if level not in self._color_mapping:
            self._logger.error(f"Level {level} is not supported")
        log_action = self._log_action_dict.get(level, self._logger.info)

        # Format content with timestamp
        content_with_timestamp = f"{timestamp}:{content}"

        if print_to_terminal:
            pass
            # log_action(content_with_timestamp)
        if not self._file:
            from modules.file.file import File

            self._file = File("log.md")

        # Write log to file with formatted content
        self._file.write(
            self._color_mapping[level].format(content_with_timestamp), mode="a"
        )


class _MuteLogger(_Logger):
    def log(self, content: str, level: str = "info", print_to_terminal: bool = True):
        super(_MuteLogger, self).log(content, level, print_to_terminal=False)


# logger = _Logger()
logger = _MuteLogger()

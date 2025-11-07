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
        color_mapping = {
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

        # Get current time as a timestamp
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S:%f]")

        # Verify level is supported
        if level not in color_mapping:
            self._logger.error(f"Level {level} is not supported")
        log_action = {
            "stage": self._logger.info,
            "action": self._logger.debug,
            "prompt": self._logger.debug,
            "response": self._logger.info,
            "success": self._logger.info,
            "error": self._logger.error,
            "warning": self._logger.warning,
            "info": self._logger.info,
            "debug": self._logger.debug,
        }.get(level, self._logger.info)

        # Format content with timestamp
        content_with_timestamp = f"{timestamp}:{content}"

        if print_to_terminal:
            log_action(content_with_timestamp)
        if not self._file:
            from modules.file.file import File

            self._file = File("log.md")

        # Write log to file with formatted content
        self._file.write(color_mapping[level].format(content_with_timestamp), mode="a")


logger = _Logger()

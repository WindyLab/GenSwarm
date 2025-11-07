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

import logging
from enum import Enum


# ANSI 转义码
_ANSI_COLOR_CODES = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
    "BLACK": "\033[30m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "WHITE": "\033[37m",
}


class _ColoredFormatter(logging.Formatter):
    def format(self, record):
        # Apply color based on log level
        log_level_color = {
            logging.DEBUG: _ANSI_COLOR_CODES["BLUE"],
            logging.INFO: _ANSI_COLOR_CODES["GREEN"],
            logging.WARNING: _ANSI_COLOR_CODES["YELLOW"],
            logging.ERROR: _ANSI_COLOR_CODES["RED"],
            logging.CRITICAL: _ANSI_COLOR_CODES["MAGENTA"],
        }.get(record.levelno, _ANSI_COLOR_CODES["RESET"])

        # Customize log record message with color
        record.msg = f"{log_level_color}{record.msg}{_ANSI_COLOR_CODES['RESET']}"

        # Apply color to other parts of the log record
        record.levelname = (
            f"{log_level_color}[{record.levelname}]{_ANSI_COLOR_CODES['RESET']}"
        )
        record.name = f"{log_level_color}[{record.name}]{_ANSI_COLOR_CODES['RESET']}"
        # ✅ 不修改 record.created，因为 logging 系统需要它保持 float 类型
        # 如果需要颜色，应该在格式化后的字符串上添加

        return super(_ColoredFormatter, self).format(record)


class LoggerLevel(Enum):
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING


def setup_logger(name, level=LoggerLevel.INFO):
    """
    Set up a logger and return it.

    Args:
        name (str): The logger name.
        level (str): The logging level as a string ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').

    Returns:
        logging.Logger: The configured logger.
    """
    # Convert the level string to the corresponding integer value
    # level = getattr(logging, level.upper(), logging.INFO)
    logger = logging.getLogger(name)
    logger.setLevel(level.value)
    # Create a console handler
    ch = logging.StreamHandler()
    # Use the custom colored formatter
    formatter = _ColoredFormatter("%(created)s%(name)s%(levelname)s %(message)s")
    ch.setFormatter(formatter)
    # Add the console handler to the logger
    logger.addHandler(ch)

    return logger


if __name__ == "__main__":
    pass

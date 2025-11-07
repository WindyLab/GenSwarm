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

from .logger import setup_logger, LoggerLevel
from .media import generate_video_from_frames, process_video, create_video_from_frames
from .root import get_project_root, root_manager
from .run_scripts import run_script
from .save_json import save_dict_to_json

__all__ = [
    "setup_logger",
    "LoggerLevel",
    "generate_video_from_frames",
    "process_video",
    "create_video_from_frames",
    "get_project_root",
    "root_manager",
    "run_script",
    'save_dict_to_json'
]

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

import argparse
import datetime
from pathlib import Path


def get_project_root():
    """Search upwards to find the project root directory."""
    current_path = Path.cwd()
    while True:
        if (
                (current_path / ".git").exists()
                or (current_path / ".project_root").exists()
                or (current_path / ".gitignore").exists()
        ):
            # use metagpt with git clone will land here
            return current_path
        parent_path = current_path.parent
        if parent_path == current_path:
            # use metagpt with pip install will land here
            cwd = Path.cwd()
            return cwd
        current_path = parent_path


class _RootManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls.project_root = None
            cls.workspace_root = None
            cls.data_root = None
            cls._instance.update_root()
        return cls._instance

    def update_root(
            self, workspace_root: str = None, args: argparse.Namespace = None, ablation_path='',
    ) -> None:
        if workspace_root is None or args is not None:
            self.project_root = get_project_root()
            current_datetime = datetime.datetime.now()
            formatted_date = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
            generate_mode = ""
            task_name = ""
            if args is not None:
                if hasattr(args, "generate_mode"):
                    generate_mode = args.generate_mode
                if hasattr(args, "run_experiment_name"):
                    task_name = "_".join(args.run_experiment_name)
            self.workspace_root = (
                    self.project_root
                    / f"workspace/{generate_mode}/{ablation_path}/{task_name}/{formatted_date}"
            )
        else:
            self.workspace_root = Path(workspace_root)
        self.data_root = self.workspace_root / "data"


root_manager = _RootManager()

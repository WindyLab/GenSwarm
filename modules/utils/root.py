import datetime
import os
from pathlib import Path

from modules.utils import read_file, write_file, set_param


class RootManager:
    def __init__(self):
        self.project_root = None
        self.workspace_root = None
        self.data_root = None

    def update_root(self, workspace_root: str = None):
        if workspace_root is None:
            self.project_root = self.get_project_root()
            current_datetime = datetime.datetime.now()
            formatted_date = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
            self.workspace_root = self.project_root / f"workspace/{formatted_date}"
        else:
            self.workspace_root = Path(workspace_root)
        self.data_root = self.workspace_root / "data"
        set_param('data_path', str(self.data_root))  # this is important

    @staticmethod
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

    def init_workspace(self):
        if not os.path.exists(self.workspace_root):
            os.makedirs(self.workspace_root)
            os.makedirs(os.path.join(self.workspace_root, 'data/frames'))
            utils = read_file(os.path.join(self.project_root, 'modules/env'), 'functions.py')
            write_file(self.workspace_root, 'functions.py', utils)
            set_param('data_path', str(self.data_root))
            print(f"Workspace initialized at {self.workspace_root}")


root_manager = RootManager()

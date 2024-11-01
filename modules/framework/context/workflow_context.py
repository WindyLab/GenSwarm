import argparse
import pickle

from transformers import SEWDModel

from modules.file import File
from modules.framework.code import FunctionTree
from modules.framework.constraint import ConstraintPool

from .context import Context
from modules.prompt import global_import_list, local_import_list


class WorkflowContext(Context):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()

        return cls._instance

    def _initialize(self):
        self.user_command = File(name="command.md")
        self.feedbacks = []
        self.run_code = File(name="run.py")
        self.args = argparse.Namespace()
        self._constraint_pool = ConstraintPool()
        # TODO:所有的命名统一化，比如这里的global skill tree和local skill tree (@Jiwenkang 10-4)

        self._global_skill_tree = FunctionTree(
            name="global_skill",
            init_import_list={
                f"from global_apis import {','.join(global_import_list)}"
            }
        )
        self._local_skill_tree = FunctionTree(
            name="local_skill",
            init_import_list={
                f"from apis import initialize_ros_node, {','.join(local_import_list)}"
            }
        )
        self.global_run_result = File(name="allocate_result.pkl")
        self.scoop = "global"
        self.vlm = False

    def save_to_file(self, file_path):
        with open(file_path, "wb") as file:
            pickle.dump(self._instance, file)

    def load_from_file(self, file_path):
        with open(file_path, "rb") as file:
            self._instance = pickle.load(file)

    def set_root_for_files(self, root_value):
        for file_attr in vars(self).values():
            if isinstance(file_attr, File):
                file_attr.root = root_value
            if isinstance(file_attr, FunctionTree):
                file_attr.file.root = root_value

    @property
    def command(self):
        return self._instance.user_command.message

    @command.setter
    def command(self, value):
        self._instance.user_command.message = value

    @property
    def global_skill_tree(self) -> FunctionTree:
        return self._instance._global_skill_tree

    @property
    def local_skill_tree(self) -> FunctionTree:
        return self._instance._local_skill_tree

    @property
    def constraint_pool(self) -> ConstraintPool:
        return self._instance._constraint_pool

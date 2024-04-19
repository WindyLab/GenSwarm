import argparse
import pickle
from abc import ABC, abstractmethod

from modules.file.file import File
from modules.framework.context.function_info import FunctionPool

class Context(ABC):
    @abstractmethod
    def save_to_file(self, filename):
        pass
    
    @abstractmethod
    def load_from_file(self, filename):
        pass
    
    @property
    def command():
        raise NotImplementedError

class WorkflowContext(Context):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()

        return cls._instance

    def _initialize(self):
        self.user_command = File(name='command.md')
        self.function_pool = FunctionPool()
        self.design_result = File(name='design_result.py')
        self.function_list = []
        self.parameters = File(name="parameters.md")
        self.run_code = File(name='run.py', message="""import sys
from functions import run_loop
robot_id = sys.argv[1]
if __name__ == '__main__':
    run_loop()
""")
        # self.sequence_diagram = FileInfo(name='sequence_diagram.md')
        self.run_result = File(name='run_result.md')
        self.args = argparse.Namespace()

    def save_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            pickle.dump(self._instance, file)

    def load_from_file(self, file_path):
        with open(file_path, 'rb') as file:
            self._instance = pickle.load(file)

    @property
    def command(self):
        return self._instance.user_command.message
    
    @command.setter
    def command(self, value):
        self._instance.user_command.message = value

    @property
    def parameters(self):
        return self._instance.parameters.message
    
    @parameters.setter
    def parameters(self, value):
        self._instance.parameters.message = value

if __name__ == '__main__':
    context = WorkflowContext()

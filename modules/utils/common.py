import os
import re
import ast
import shutil
import rospy
from typing import Any
from enum import Enum
from std_srvs.srv import SetBool
import datetime
import threading
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


current_datetime = datetime.datetime.now()
formatted_date = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
PROJECT_ROOT = get_project_root()
WORKSPACE_ROOT = PROJECT_ROOT / f"workspace/{formatted_date}"
DATA_PATH = WORKSPACE_ROOT / "data"
ENV_PATH = WORKSPACE_ROOT / "env"

GLOBAL_LOCK = threading.Lock()


class TestResult(Enum):
    HALF_PASS = 1
    ALL_PASS = 2
    NOT_PASS = 3


class BugSource(Enum):
    CODE = 1
    TEST_CODE = 2


class DesignPattern(Enum):
    FUNCTION = 1
    SEQ_DIAGRAM = 2


class CodeMode(Enum):
    WRITE_FUNCTION = 1
    WRITE_RUN = 2


def get_class_name(cls) -> str:
    """Return class name"""
    return f"{cls.__name__}"


def any_to_str(val: Any) -> str:
    """Return the class name or the class name of the object, or 'val' if it's a string type."""
    if isinstance(val, str):
        return val
    elif not callable(val):
        return get_class_name(type(val))
    else:
        return get_class_name(val)


def check_file_exists(directory, filename):
    file_path = os.path.join(directory, filename)
    return os.path.exists(file_path)


def write_file(directory, filename, content, mode='w'):
    file_path = os.path.join(directory, filename)
    try:
        with open(file_path, mode) as file:
            file.write(content)
    except Exception as e:
        print("Exception: ", e)
    operation = "written" if mode == 'w' else "appended"
    print(f"File {operation}: {file_path}")
    return file_path


def copy_folder(source_folder, destination_folder):
    try:
        # Copy the entire folder and its contents
        shutil.copytree(source_folder, destination_folder)
    except Exception as e:
        raise Exception(f"Error copying folder: {e}")


def init_workspace():
    global WORKSPACE_ROOT, PROJECT_ROOT
    if not os.path.exists(WORKSPACE_ROOT):
        os.makedirs(WORKSPACE_ROOT)
        os.makedirs(os.path.join(WORKSPACE_ROOT, 'data/frames'))
        utils = read_file(os.path.join(PROJECT_ROOT, 'modules/env'), 'functions.py')
        write_file(WORKSPACE_ROOT, 'functions.py', utils)
        set_param('data_path', str(DATA_PATH))
    print(f"Workspace initialized at {WORKSPACE_ROOT}")


def read_file(directory, filename):
    file_path = os.path.join(directory, filename)
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
        return file_content
    except FileNotFoundError:
        return f"File not found: {file_path}"


def parse_code(text: str, lang: str = "python") -> str:
    pattern = rf"```{lang}.*?\s+(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        code = match.group(1)
    else:
        raise Exception
    return code


def extract_function_definitions(source_code):
    parsed_ast = ast.parse(source_code)

    def reconstruct_function_definition(function_node):
        func_header = f"def {function_node.name}({', '.join(ast.unparse(arg) for arg in function_node.args.args)}):"
        docstring = ast.get_docstring(function_node)
        docstring_part = ''
        if docstring:
            indented_docstring = '\n'.join('    ' + line for line in docstring.split('\n'))
            docstring_part = f'    """\n{indented_docstring}\n    """\n'
        body_part = ''
        return f"{func_header}\n{docstring_part}{body_part}"

    function_definitions = [reconstruct_function_definition(node) for node in ast.walk(parsed_ast) if
                            isinstance(node, ast.FunctionDef)]

    return function_definitions


def extract_imports_and_functions(source_code):
    parsed_ast = ast.parse(source_code)

    imports = []
    functions = []

    for node in parsed_ast.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ''
                imports.append(f"from {module} import {', '.join(alias.name for alias in node.names)}")
        elif isinstance(node, ast.FunctionDef):
            func_def = ast.unparse(node).strip()
            if func_def:
                functions.append(func_def)

    return imports, functions


def combine_unique_imports(import_list):
    unique_imports = set()

    for import_str in import_list:
        import_lines = import_str.splitlines()
        for import_line in import_lines:
            unique_imports.add(import_line.strip())

    combined_imports = "\n".join(sorted(unique_imports))

    return combined_imports


def call_reset_environment(data: bool):
    """

    Args:
        data (bool): Whether to render the environment
    """
    if not rospy.core.is_initialized():
        rospy.init_node('reset_environment_client', anonymous=True)

    rospy.wait_for_service('/reset_environment')
    try:
        reset_environment = rospy.ServiceProxy('/reset_environment', SetBool)
        resp = reset_environment(data)
        return resp.success, resp.message
    except rospy.ServiceException as e:
        print("Service call failed: %s" % e)


def get_param(param_name):
    return rospy.get_param(param_name)


def set_param(param_name, param_value):
    rospy.set_param(param_name, param_value)
    print(f"Setting param {param_name} to {param_value}")


def set_workspace_root(workspace_root: str):
    global WORKSPACE_ROOT, DATA_PATH, ENV_PATH

    # 创建一个PosixPath对象
    WORKSPACE_ROOT = Path(workspace_root)

    # 使用Path对象的操作来设置DATA_PATH和ENV_PATH
    DATA_PATH = WORKSPACE_ROOT / "data"
    ENV_PATH = WORKSPACE_ROOT / "env"

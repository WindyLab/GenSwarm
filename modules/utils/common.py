import os
import re
import ast
import shutil
import rospy
from typing import Any
from enum import Enum
from std_srvs.srv import SetBool


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


def write_file(directory, filename, content):
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w') as file:
        file.write(content)

    print(f"File written: {file_path}")
    return file_path

def append_file(directory, filename, content):
    file_path = os.path.join(directory, filename)
    with open(file_path, 'a') as file:
        file.write(content)
    print(f"Log appended: {file_path}")
    return file_path

def copy_folder(source_folder, destination_folder):
    try:
        # Copy the entire folder and its contents
        shutil.copytree(source_folder, destination_folder)
    except Exception as e:
        raise Exception(f"Error copying folder: {e}")


def init_workspace():
    from modules.prompt.const import WORKSPACE_ROOT, PROJECT_ROOT
    if not os.path.exists(WORKSPACE_ROOT):
        os.makedirs(WORKSPACE_ROOT)
        os.makedirs(os.path.join(WORKSPACE_ROOT, 'data/frames'))
        utils = read_file(os.path.join(PROJECT_ROOT, 'modules/env'), 'functions.py')
        write_file(WORKSPACE_ROOT, 'functions.py', utils)
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

import ast
import re
from modules.framework.context.function_info import FunctionPool
from modules.file.log_file import logger


class AstParser(ast.NodeVisitor):
    def __init__(self, code_str) -> None:
        self._imports = set()
        self._function_dict : dict[str, str] = {}
        self._function_defs = []
        self._code_to_parse = code_str
        self._function_pool = FunctionPool()
        
    @property
    def imports(self):
        return self._imports
    
    @property
    def function_contents(self):
        return self._function_dict.values()
    
    @property
    def function_names(self):
        return self._function_dict.keys()

    @property
    def function_defs(self):
        return self._function_defs

    def parse_code(self, code_str):
        tree = ast.parse(code_str)
        self.visit(tree)

    def save_to_pool(self):
        self._save_imports()
        self._save_function_dict()

    def _save_imports(self):
        self._function_pool.import_list |= self._imports

    def _save_function_dict(self):
        self._function_pool.update_function_tree(self._function_dict)

    # visit_xxx functions are automatically executed in visit()
    # see details in ast.NodeVisitor
    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            import_str = f"import {alias.name}"
            if alias.asname:
                import_str += f" as {alias.asname}"
            self._imports.add(import_str)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ''
        for alias in node.names:
            import_str = f"from {module} import {alias.name}"
            if alias.asname:
                import_str += f" as {alias.asname}"
            self._imports.add(import_str)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        def reconstruct_function_definition(function_node):
            defaults_start_index = len(function_node.args.args) - len(function_node.args.defaults)

            parameters = [
                ast.unparse(arg) + (
                    f'={ast.unparse(function_node.args.defaults[i - defaults_start_index])}' 
                        if i >= defaults_start_index else '')
                for i, arg in enumerate(function_node.args.args)
            ]

            func_header = f"def {function_node.name}({', '.join(parameters)}):"
            docstring = ast.get_docstring(function_node)
            docstring_part = ''
            if docstring:
                indented_docstring = '\n'.join('    ' + line for line in docstring.split('\n'))
                docstring_part = f'    """\n{indented_docstring}\n    """\n'
            body_part = ''
            return f"{func_header}\n{docstring_part}{body_part}"
        
        self._function_dict[node.name] = ast.unparse(node).strip()
        self._function_defs.append(reconstruct_function_definition(node))


def parse_text(text: str, lang: str = "python") -> str:
    pattern = rf"```{lang}.*?\s+(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        code = match.group(1)
    else:
        error_message = f"Error: No '{lang}' code block found in the text."
        raise ValueError(error_message)
    return code



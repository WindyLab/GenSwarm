import ast

# from modules.file.log_file import logger
from modules.framework.error import CodeParseError

class CodeParser(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self._imports = set()
        self._function_dict : dict[str, str] = {}
        self._function_defs : dict[str, str] = {}

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
        def reconstruct_function_definition(function_node: ast.FunctionDef):
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
        self._function_defs[node.name] = reconstruct_function_definition(node)

class SingleFunctionParser(CodeParser):
    def parse_code(self, code_str):
        super().parse_code(code_str)
        self._check_error()

    def _check_error(self):
        if not self._function_dict:
            raise CodeParseError("Failed: No function detected in the response", "error")
            # return ''
        if len(self._function_dict) > 1:
            raise CodeParseError("Failed: More than one function detected in the response")

    def check_function_name(self, desired_function_name):
        function_name = self._function_dict.keys()[0]
        if function_name != desired_function_name:
            raise CodeParseError(f"Function name mismatch: {function_name} != {desired_function_name}")
        if not function_name:
            raise CodeParseError(f"Failed: No function detected in the response")

    # def update_definition(self):
    #     self._function_pool.set_definiton(self._function_dict.keys()[0],
                                        #   self._function_defs[0])
    
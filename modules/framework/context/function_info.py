from collections import defaultdict
from modules.framework.context.file_info import FileInfo, logger

# TODO: function pool and constraint pool should be rewrite totally
class FunctionInfo:
    def __init__(self, description, name):
        self.name = name
        self.description = description
        self.import_list = []
        self.parameters = []
        self.calls = []
        self.satisfying_constraints: list[str] = []
        self.content = None
        self.definition = None
        self.text = f"**{self.name}**: {self.description}"

class FunctionPool(FileInfo):

    def __init__(self, name: str = '', root: str = ''):
        super().__init__(name=name, root=root)
        self.import_list: list[str] = ['from apis import *']
        self.functions: dict[str, FunctionInfo] = {}
        self.parameters: dict = {}
        self.function_layer: list[FunctionInfo] = []

    def init_functions(self, content: str):
        try:
            for function in eval(content)['functions']:
                name = function['name']
                self.functions[name] = FunctionInfo(
                    name=name,
                    description=function['description'],
                )
                self.functions[name].satisfying_constraints = function['constraints']
                self.functions[name].calls = function['calls']

            self.function_layer = self.build_layers_from_bottom()
        except Exception as e:
            logger.log(f'Error in init_functions: {e}', level='error')
            raise Exception

    def add_functions(self, content: str):
        from modules.utils import extract_imports_and_functions, extract_top_level_function_names
        import_list, function_list = extract_imports_and_functions(content)
        self.import_list.extend(import_list)
        for function in function_list:
            function_name = extract_top_level_function_names(function)[0]
            import_content, function_content = extract_imports_and_functions(function)
            self.functions.setdefault(
                function_name,
                FunctionInfo(name=function_name, description='')
            ).content = function_content[0]
            self.functions[function_name].import_list.extend(import_content)
            self.functions[function_name].calls = []
            for other_function in self.functions.values():
                if other_function.name != function_name and other_function.name in function_content[0]:
                    self.functions[function_name].calls.append(other_function.name)
            logger.log(f" function_name: {function_name}, calls: {self.functions[function_name].calls}", level='info')

        self.function_layer = self.build_layers_from_bottom()

    def check_function_grammar(self, function_name: str):
        from modules.utils import check_grammar, find_function_name_from_error
        relative_function = self.extend_calls(function_name)
        logger.log(f"relative_function: {relative_function}", level='warning')
        self.update_message(relative_function)

        errors = check_grammar(str(self.root / self.name))
        if errors:
            for e in errors:
                error_function_name = find_function_name_from_error(file_path=str(self.root / self.name),
                                                                    error_line=e['line'])
                logger.log(f"{error_function_name}: {e['error_message']}", level='error')
            logger.log(f'Grammar check failed for {function_name}', level='error')
        else:
            logger.log(f'Grammar check passed for {function_name}', level='debug')
        return errors

    def extend_calls(self, function_name: str, seen: set = None):
        if seen is None:
            seen = set()

        if function_name not in seen:
            if function_name in self.functions.keys():
                seen.add(function_name)
                calls = self.functions[function_name].calls
                for call in calls:
                    if call not in seen:
                        self.extend_calls(call, seen)
        return list(seen)

    def update_message(self, function_name: str | list[str] = None):
        from modules.utils import combine_unique_imports
        import_str = combine_unique_imports(self.import_list)
        self.message = f"{import_str}\n\n{self.functions_content(function_name)}\n"

    def functions_content(self, function_name: str | list[str] = None):
        if function_name:
            if isinstance(function_name, str):
                function_name = [function_name]
            return '\n\n\n'.join([self.functions[f].content for f in function_name])
        return '\n\n\n'.join([f.content for f in self.functions.values()])

    def build_layers_from_bottom(self):
        bottom_layer_functions = [
            func for func in self.functions.values()
            if all(called_func not in self.functions for called_func in func.calls)
        ]

        function_names = {func.name for func in self.functions.values()
                          if func not in bottom_layer_functions}

        calls_of = defaultdict(list)
        for func in self.functions.values():
            for called_func in func.calls:
                calls_of[func.name].append(called_func)

        layers = [bottom_layer_functions]
        handled_functions = set({func.name for func in bottom_layer_functions})

        while function_names:
            next_layer = []
            for func in function_names:
                flag = True
                for calls_func in calls_of[func]:
                    if calls_func not in handled_functions:
                        flag = False
                        break

                if flag:
                    next_layer.append(self.functions[func])
            if next_layer:
                layers.append(next_layer)
                for func in next_layer:
                    function_names.remove(func.name)
                handled_functions = handled_functions.union(set({func.name for func in next_layer}))
        logger.log(f"layers: {[[f.name for f in layer] for layer in layers]}", level='warning')
        return layers

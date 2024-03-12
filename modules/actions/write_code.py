from modules.actions.action import Action
from modules.utils import parse_code, extract_imports_and_functions, extract_top_level_function_names


class WriteCode(Action):
    name: str = "WriteCode"

    def process_response(self, response: str, **kwargs) -> str:
        code = parse_code(text=response)
        if not kwargs.get('filename'):
            self._context.log.format_message(f"Write Sequence Diagram Failed: No filename provided", "error")
            raise SystemExit  # avoid retry mechanism

        filename = kwargs.get('filename')
        if filename not in self._context.code_files:
            self._context.log.format_message(f"Write Code Failed: No filename found in context", "error")
            raise SystemExit

        elif filename == "functions.py":
            if not kwargs.get('function_name'):
                self._context.log.format_message(f"Write Code Failed: No function name provided", "error")
                raise Exception  # to trigger retry
            function_name = kwargs.get('function_name')
            import_list, function_list = extract_imports_and_functions(code)
            # avoid generating a function without any function
            if not function_list:
                self._context.log.format_message(f"Write Code Failed: No function detected in the response", "error")
                raise Exception
            # avoid generating more than one function
            elif len(function_list) > 1:
                self._context.log.format_message(
                    f"Write Code Failed: More than one function detected in the response: {function_list}", "error")
                raise Exception  # to trigger retry
            # check if the function name matches the provided function name
            # avoid generating a function with a different name

            elif extract_top_level_function_names(function_list[0])[0] != function_name:

                self._context.log.format_message(
                    f"Write Code Failed: Function name:{extract_top_level_function_names(function_list[0])}"
                    f"does not match the provided function name:{function_name}", "error")
                raise Exception
            result = {
                "import": import_list,
                "code": function_list
            }
            return str(result)
        elif filename == "run.py":
            code_prefix = "from functions import * \nimport sys\n\nos.environ['ROBOT_ID'] = sys.argv[1]\n"
            self._context.code_files[filename].message = code_prefix + code
            return code

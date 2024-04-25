import unittest

from modules.framework.response.code_parser import CodeParser
from modules.framework.response.text_parser import parse_text


class TestAstParser(unittest.TestCase):

    def setUp(self):
        self.code_str = """
import math
from collections import deque as d

def add(a, b=0):
    \"\"\"This function adds two numbers.\"\"\"
    return a + b

def subtract(x, y=0):
    \"\"\"This function subtracts two numbers.\"\"\"
    return x - y
        """

        self.parser = CodeParser()
        self.parser.parse_code(self.code_str)

    def test_imports(self):
        expected_imports = {"import math", "from collections import deque as d"}
        self.assertEqual(self.parser._imports, expected_imports)

    def test_function_names(self):
        expected_function_names = {"add", "subtract"}
        self.assertEqual(set(self.parser._function_dict.keys()), expected_function_names)

    def test_function_contents(self):
        expected_function_contents = [
            'def add(a, b=0):\n    """This function adds two numbers."""\n    return a + b',
            'def subtract(x, y=0):\n    """This function subtracts two numbers."""\n    return x - y'
        ]
        self.assertEqual(list(self.parser._function_dict.values()), expected_function_contents)

    def test_function_defs(self):
        expected_function_defs = [
            'def add(a, b=0):\n    """\n    This function adds two numbers.\n    """\n',
            'def subtract(x, y=0):\n    """\n    This function subtracts two numbers.\n    """\n'
        ]
        self.assertEqual(self.parser._function_defs, expected_function_defs)


class TestTextParser(unittest.TestCase):
    def test_parse_code(self):
        text = "```python\nprint('Hello, World!')\n```"
        expected_code = "print('Hello, World!')\n"
        parsed_code = parse_text(text=text)
        self.assertEqual(parsed_code, expected_code)

if __name__ == '__main__':
    unittest.main()

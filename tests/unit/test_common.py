import unittest
import os
# import cv2

from modules.utils.common import *

class TestCommon(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = '/tmp'
        os.makedirs(cls.test_dir, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_dir)

    def test_get_class_name(self):
        class TestClass: pass
        self.assertEqual(get_class_name(TestClass), 'TestClass')

    def test_any_to_str(self):
        self.assertEqual(any_to_str(5), 'int')
        self.assertEqual(any_to_str('test'), 'test')
        self.assertEqual(any_to_str(cv2.imread), 'imread')

    def test_check_file_exists(self):
        self.assertFalse(check_file_exists(self.test_dir, 'test.txt'))
        open(os.path.join(self.test_dir, 'test.txt'), 'a').close()
        self.assertTrue(check_file_exists(self.test_dir, 'test.txt'))

    def test_write_file(self):
        file_path = write_file(self.test_dir, 'test.txt', 'test content')
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, 'r') as file:
            content = file.read()
            self.assertEqual(content, 'test content')

    def test_copy_folder(self):
        source_folder = self.test_dir + "/source_folder"
        os.makedirs(source_folder, exist_ok=True)
        file_path = os.path.join(source_folder, 'test.txt')
        open(file_path, 'a').close()

        destination_folder =  self.test_dir + '/destination_folder'
        copy_folder(source_folder, destination_folder)
        self.assertTrue(os.path.exists(destination_folder))
        self.assertTrue(os.path.exists(os.path.join(destination_folder, 'test.txt')))

    def test_read_file(self):
        file_path = os.path.join(self.test_dir, 'test.txt')
        with open(file_path, 'w') as file:
            file.write('test content')
        content = read_file(self.test_dir, 'test.txt')
        self.assertEqual(content, 'test content')

    def test_parse_code(self):
        text = """
```python
def test_function():
    return "test"
```
        """
        expected_code = "def test_function():\n    return \"test\"\n"
        self.assertEqual(parse_code(text), expected_code)

    def test_extract_function_definitions(self):
        source_code = """
def test_function():
    \"\"\"Test function\"\"\"
    print("hi")
        """
        expected_function_definitions = ["def test_function():\n    \"\"\"\n    Test function\n    \"\"\"\n"]
        self.assertEqual(extract_function_definitions(source_code), expected_function_definitions)

    def test_extract_imports_and_functions(self):
        source_code = """
import os
from math import sqrt

def test_function():
    pass
        """
        expected_imports = ["import os", "from math import sqrt"]
        expected_functions = ["def test_function():\n    pass"]
        imports, functions = extract_imports_and_functions(source_code)
        self.assertEqual(imports, expected_imports)
        self.assertEqual(functions, expected_functions)

    def test_combine_unique_imports(self):
        import_list = ["import os", "import cv2", "from math import sqrt", "import os"]
        expected_combined_imports = "from math import sqrt\nimport cv2\nimport os"
        self.assertEqual(combine_unique_imports(import_list), expected_combined_imports)


if __name__ == '__main__':
    unittest.main()

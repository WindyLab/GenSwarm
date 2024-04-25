import unittest
from unittest.mock import patch, Mock, ANY
from modules.framework.code.function_layer import FunctionLayer
from modules.framework.code.function_node import FunctionNode
from modules.framework.code.function_tree import FunctionTree

class TestFunctionLayer(unittest.TestCase):

    def setUp(self):
        self.function1 = FunctionNode(name="func1", description="Function 1")
        self.function2 = FunctionNode(name="func2", description="Function 2")
        self.function3 = FunctionNode(name="func3", description="Function 3")
        self.function_layer = FunctionLayer({self.function1, self.function2})

    def test_add_function(self):
        self.function_layer.add_function(self.function3)
        self.assertIn(self.function3, self.function_layer._layer)

    def test_functions_property(self):
        self.assertCountEqual(self.function_layer.functions, [self.function1, self.function2])

    def test_next_function(self):
        with self.assertRaises(StopIteration):
            for _ in range(len(self.function_layer) + 1):
                next(self.function_layer)

    def test_empty_layer(self):
        function_layer = FunctionLayer()
        self.assertEqual(len(function_layer), 0)


class TestFunctionTree(unittest.TestCase):

    def assert_logged():
        def decorator(test_method):
            def wrapper(self, *args, **kwargs):
                with patch('modules.file.log_file.logger.log') as mock_logger:
                    test_method(self, *args, **kwargs)
                    mock_logger.assert_called_with(ANY, level="warning")
            return wrapper
        return decorator

    def setUp(self):
        self.function1 = FunctionNode(name="func1", description="Function 1")
        self.function2 = FunctionNode(name="func2", description="Function 2")
        self.function3 = FunctionNode(name="func3", description="Function 3")
        self.function_dict = {
            "func1": self.function1,
            "func2": self.function2,
            "func3": self.function3
        }
        self.function_tree = FunctionTree()

    def connect_functions(self):
        self.function1.add_callee(self.function2)
        self.function1.add_callee(self.function3)

    def test_get_bottom_layer_without_callee(self):
        self.function_tree._function_nodes = self.function_dict
        bottom_layer = self.function_tree._get_bottom_layer()
        self.assertEqual(len(bottom_layer._layer), 3)
        self.assertIn(self.function1, bottom_layer._layer)
        self.assertIn(self.function2, bottom_layer._layer)
        self.assertIn(self.function3, bottom_layer._layer)

    def test_get_bottom_layer_1_caller(self):
        self.function_tree._function_nodes = self.function_dict
        self.connect_functions()
        bottom_layer = self.function_tree._get_bottom_layer()
        self.assertEqual(len(bottom_layer._layer), 2)
        self.assertNotIn(self.function1, bottom_layer._layer)
        self.assertIn(self.function2, bottom_layer._layer)
        self.assertIn(self.function3, bottom_layer._layer)
    
    @assert_logged()
    def test_update_1_layer(self):
        self.function_tree.update(self.function_dict)
        self.assertEqual(len(self.function_tree._layers), 1)
        self.assertIn(self.function1, self.function_tree._layers[0]._layer)
        self.assertIn(self.function2, self.function_tree._layers[0]._layer)
        self.assertIn(self.function3, self.function_tree._layers[0]._layer)

    @assert_logged()
    def test_update_2_layer(self):
        self.connect_functions()
        self.function_tree.update()
        self.assertEqual(len(self.function_tree._layers), 2)
        self.assertIn(self.function1, self.function_tree._layers[1]._layer)
        self.assertIn(self.function2, self.function_tree._layers[0]._layer)
        self.assertIn(self.function3, self.function_tree._layers[0]._layer)

    @assert_logged()
    def test_getitem_with_int(self):
        self.connect_functions()
        self.function_tree.update()

        self.assertEqual(self.function_tree[0], self.function_tree._layers[0])
        self.assertEqual(self.function_tree[-1], self.function_tree._layers[-1])
        with self.assertRaises(IndexError):
            self.function_tree[10]

    @assert_logged()
    def test_getitem_with_slice(self):
        self.connect_functions()
        self.function_tree.update()
        sliced_layers = self.function_tree[0:2]
        self.assertEqual(sliced_layers, [self.function_tree._layers[0], self.function_tree._layers[1]])
        
if __name__ == '__main__':
    unittest.main()

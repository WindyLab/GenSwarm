import unittest
from unittest.mock import patch, ANY, MagicMock, call
from modules.framework.code.function_node import FunctionNode
from modules.framework.code.function_tree import FunctionTree
from modules.file import logger, File


class TestFunctionTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.set_file(File("log.md"))

    def setUp(self):
        self.function1 = FunctionNode(name="func1", description="Function 1")
        self.function2 = FunctionNode(name="func2", description="Function 2")
        self.function3 = FunctionNode(name="func3", description="Function 3")
        self.function_dict = {
            "func1": self.function1,
            "func2": self.function2,
            "func3": self.function3,
        }
        self.function_tree = FunctionTree()
        self.function_tree.reset()

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

    def test_update_1_layer(self):
        self.function_tree._function_nodes = self.function_dict
        self.function_tree.update()
        self.assertEqual(len(self.function_tree._layers), 1)
        self.assertIn(self.function1, self.function_tree._layers[0]._layer)
        self.assertIn(self.function2, self.function_tree._layers[0]._layer)
        self.assertIn(self.function3, self.function_tree._layers[0]._layer)

    def test_update_2_layer(self):
        self.connect_functions()
        self.function_tree._function_nodes = self.function_dict
        self.function_tree.update()
        self.assertEqual(len(self.function_tree._layers), 2)
        self.assertIn(self.function1, self.function_tree._layers[1]._layer)
        self.assertIn(self.function2, self.function_tree._layers[0]._layer)
        self.assertIn(self.function3, self.function_tree._layers[0]._layer)

    def test_nodes_property(self):
        # Test the nodes property
        self.assertEqual(len(self.function_tree.nodes), 0)
        self.function_tree["function_name"] = FunctionNode(
            "function_name", "description"
        )
        self.assertEqual(len(self.function_tree.nodes), 1)

    def test_names_property(self):
        # Test the names property
        self.assertEqual(len(self.function_tree.names), 0)
        self.function_tree["function_name"] = FunctionNode(
            "function_name", "description"
        )
        self.assertIn("function_name", self.function_tree.names)

    def test_keys_set_property(self):
        # Test the keys_set property
        self.assertEqual(len(self.function_tree.keys_set), 0)
        self.function_tree["function_name"] = FunctionNode(
            "function_name", "description"
        )
        self.assertIn("function_name", self.function_tree.keys_set)

    def test_filtered_functions(self):
        # Test the filtered_functions method
        function_node1 = FunctionNode("function1", "description1")
        function_node2 = FunctionNode("function2", "description2")
        self.function_tree["function1"] = function_node1
        self.function_tree["function2"] = function_node2
        result = self.function_tree.filtered_functions(function_node1)
        self.assertNotIn(function_node1, result)
        self.assertIn(function_node2, result)

    def test_related_function_content(self):
        # Test related_function_content method
        function_node1 = FunctionNode("function1", "description1")
        function_node2 = FunctionNode("function2", "description2")
        function_node1.content = "code content for function1"
        self.function_tree["function1"] = function_node1
        self.function_tree["function2"] = function_node2
        error_msg = "errors in function1"
        result = self.function_tree.related_function_content(error_msg)
        self.assertIn(function_node1.content, result)

    def test_update(self):
        function_node1 = FunctionNode("function1", "description1")
        function_node2 = FunctionNode("function2", "description2")
        function_node1.add_callee(function_node2)
        self.function_tree["function1"] = function_node1
        self.function_tree["function2"] = function_node2
        self.function_tree.update()
        self.assertEqual(len(self.function_tree._layers), 2)
        self.assertIn(function_node2, self.function_tree._layers[0])
        self.assertNotIn(function_node1, self.function_tree._layers[0])

    def test_init_functions(self):
        # Test init_functions method
        content = '{"functions": [{"name": "function1", "description": "desc1", "constraints": [], "calls": ["function2"]}, {"name": "function2", "description": "desc2", "constraints": [], "calls": []}]}'
        self.function_tree.init_functions(content)
        self.assertIn("function1", self.function_tree.names)
        self.assertIn("function2", self.function_tree.names)
        self.assertEqual(len(self.function_tree._layers), 2)

    def test_find_all_relative_functions(self):
        # Test _find_all_relative_functions method
        function_node1 = FunctionNode("function1", "description1")
        function_node2 = FunctionNode("function2", "description2")
        function_node3 = FunctionNode("function3", "description3")
        function_node1.add_callee(function_node2)
        function_node2.add_callee(function_node3)
        self.function_tree["function1"] = function_node1
        self.function_tree["function2"] = function_node2
        self.function_tree["function3"] = function_node3
        result = self.function_tree._find_all_relative_functions(function_node1)
        self.assertEqual(len(result), 3)
        self.assertIn(function_node1, result)
        self.assertIn(function_node2, result)
        self.assertIn(function_node3, result)

    def test_cross_layer_calling(self):
        fn_a = FunctionNode(name="A", description="")
        fn_b = FunctionNode(name="B", description="")
        fn_c = FunctionNode(name="C", description="")
        fn_d = FunctionNode(name="D", description="")

        fn_b.add_callee(fn_a)  # B调用A
        fn_c.add_callee(fn_a)  # C调用A
        fn_d.add_callee(fn_b)  # D调用B
        fn_d.add_callee(fn_c)  # D调用C
        fn_d.add_callee(fn_a)  # D也调用A

        # 添加函数节点到FunctionTree
        self.function_tree["A"] = fn_a
        self.function_tree["B"] = fn_b
        self.function_tree["C"] = fn_c
        self.function_tree["D"] = fn_d

        # 更新函数层级
        self.function_tree.update()

        # 打印层级结果
        for layer_index, layer in enumerate(self.function_tree._layers):
            print(f"Layer {layer_index}: {[fn.name for fn in layer]}")

        # 断言检查层级结果
        self.assertEqual(len(self.function_tree._layers), 3)
        self.assertIn(fn_a, self.function_tree._layers[0]._layer)
        self.assertIn(fn_b, self.function_tree._layers[1]._layer)
        self.assertIn(fn_c, self.function_tree._layers[1]._layer)
        self.assertIn(fn_d, self.function_tree._layers[2]._layer)

    def test_obtain_node(self):
        self.function_tree._obtain_node(name="function1", content="a = b + c")
        self.assertEqual(self.function_tree["function1"].content, "a = b + c")
        for body in self.function_tree.functions_body:
            self.assertIsNotNone(body)

    def test_update_function_dict(self):
        function_dict = {"function1": "a = b + c"}
        self.function_tree._update_function_dict(function_dict)
        self.assertEqual(self.function_tree["function1"].content, "a = b + c")

    def test_update_from_parser(self):
        function_dict = {"function1": "a = b + c"}
        self.function_tree.update_from_parser(set(), function_dict)
        self.assertEqual(self.function_tree["function1"].content, "a = b + c")

    def test_get_min_layer_index_by_state(self):
        function_node1 = FunctionNode("function1", "description1")
        function_node2 = FunctionNode("function2", "description2")
        function_node3 = FunctionNode("function3", "description3")
        function_node4 = FunctionNode("function4", "description4")
        function_node5 = FunctionNode("function5", "description5")

        function_node1.state = FunctionNode.State.NOT_STARTED
        function_node2.state = FunctionNode.State.WRITTEN
        function_node3.state = FunctionNode.State.WRITTEN
        function_node4.state = FunctionNode.State.DESIGNED
        function_node5.state = FunctionNode.State.REVIEWED

        function_node1.add_callee(function_node2)
        function_node1.add_callee(function_node3)
        function_node4.add_callee(function_node1)
        function_node5.add_callee(function_node4)

        self.function_tree["function1"] = function_node1
        self.function_tree["function2"] = function_node2
        self.function_tree["function3"] = function_node3
        self.function_tree["function4"] = function_node4
        self.function_tree["function5"] = function_node5

        self.function_tree.update()

        min_layer_index_written = self.function_tree.get_min_layer_index_by_state(
            FunctionNode.State.WRITTEN
        )
        min_layer_index_designed = self.function_tree.get_min_layer_index_by_state(
            FunctionNode.State.DESIGNED
        )
        min_layer_index_not_started = self.function_tree.get_min_layer_index_by_state(
            FunctionNode.State.NOT_STARTED
        )
        min_layer_index_reviewed = self.function_tree.get_min_layer_index_by_state(
            FunctionNode.State.REVIEWED
        )
        min_layer_index_nonexistent = self.function_tree.get_min_layer_index_by_state(5)

        self.assertEqual(min_layer_index_written, 0)
        self.assertEqual(min_layer_index_designed, 2)
        self.assertEqual(min_layer_index_not_started, 1)
        self.assertEqual(min_layer_index_reviewed, 3)
        self.assertEqual(min_layer_index_nonexistent, -1)

        function_node2.state = FunctionNode.State.DESIGNED
        function_node3.state = FunctionNode.State.DESIGNED
        self.function_tree.update()

        min_layer_index_written_after_state_change = (
            self.function_tree.get_min_layer_index_by_state(FunctionNode.State.WRITTEN)
        )
        self.assertEqual(min_layer_index_written_after_state_change, -1)

    def test_functions_brief(self):
        self.function_tree._function_nodes = {
            "func1": FunctionNode(name="func1", description="Function 1"),
            "func2": FunctionNode(name="func2", description="Function 2"),
        }

        # 断言 functions_brief 返回的列表包含了所有函数的简要描述
        self.assertEqual(
            self.function_tree.functions_brief,
            ["**func1**: Function 1", "**func2**: Function 2"],
        )

    def test_function_valid_content(self):
        func1 = FunctionNode(name="func1", description="")
        func1.content = "def func1():\n    pass"
        func2 = FunctionNode(name="func2", description="")
        func2.content = "def func2():\n    pass"

        self.function_tree._function_nodes = {
            "func1": func1,
            "func2": func2,
            "func3": FunctionNode(name="func3", description=""),
        }

        # 断言 function_valid_content 返回的列表包含了所有有效的函数内容
        self.assertEqual(
            self.function_tree.function_valid_content,
            ["def func1():\n    pass", "def func2():\n    pass"],
        )

    def test_save_functions_to_file(self):
        # 设置一些假的数据
        self.function_tree.import_list = {"import os", "import sys"}
        self.function1.content = "def func1():\n    pass"
        self.function2.content = "def func2():\n    pass"
        self.function_tree._function_nodes = {
            "func1": self.function1,
            "func2": self.function2,
        }

        # 设置模拟的 File 对象
        self.function_tree._file = MagicMock()

        # 运行方法
        self.function_tree.save_functions_to_file()

        # 断言文件消息设置正确
        expected_message = "import os\nimport sys\n\ndef func1():\n    pass\n\n\ndef func2():\n    pass\n\n"
        self.function_tree._file._message = expected_message


class TestFunctionTreeAsync(unittest.IsolatedAsyncioTestCase):
    async def test_process_function_layers(self):
        function_tree = FunctionTree()
        function_tree.reset()
        # Test process_function_layers method
        function_node1 = FunctionNode("function1", "description1")
        function_node2 = FunctionNode("function2", "description2")
        output_names = []

        from modules.framework.code.function_layer import FunctionLayer

        layer = FunctionLayer()
        layer.add_function(function_node1)
        layer.add_function(function_node2)

        async def mock_operation(node):
            output_names.append(node.name)

        function_tree._layers = [layer]
        await function_tree.process_function_layer(mock_operation)
        self.assertIn("function1", output_names)
        self.assertIn("function2", output_names)


if __name__ == "__main__":
    unittest.main()

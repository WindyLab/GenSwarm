import unittest
from unittest.mock import patch
import shutil
from pathlib import Path
from modules.utils.root import RootManager

class TestRootManager(unittest.TestCase):
    def setUp(self):
        self.root_manager = RootManager()

    def tearDown(self):
        pass

    def test_update_root_without_workspace_root(self):
        self.root_manager.update_root()
        self.assertIsNotNone(self.root_manager.workspace_root)
        self.assertIsNotNone(self.root_manager.data_root)

    @patch('modules.utils.root.set_param')
    def test_init_workspace(self, mock_set_param):
        mock_set_param.return_value = True

        self.root_manager.update_root()  # Make sure workspace_root is set
        self.root_manager.init_workspace()
        self.assertTrue(self.root_manager.workspace_root.exists())
        self.assertTrue(self.root_manager.data_root.exists())
        self.assertTrue((self.root_manager.workspace_root / "data/frames").exists())
        self.assertTrue((self.root_manager.workspace_root / "functions.py").exists())

if __name__ == '__main__':
    unittest.main()

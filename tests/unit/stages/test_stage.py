import unittest
from modules.stages.stage import Stage, StageResult


class TestStage(unittest.IsolatedAsyncioTestCase):
    async def test_run(self):
        stage = Stage()
        result = await stage.run()
        self.assertIsInstance(result, StageResult)
        self.assertEqual(len(result.keys), 0)  # Assuming no keys are added by default

if __name__ == '__main__':
    unittest.main()

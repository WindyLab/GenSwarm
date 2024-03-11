import unittest
import asyncio
from unittest.mock import AsyncMock
from modules.actions.run_code import RunCode

class TestRunCode(unittest.IsolatedAsyncioTestCase):
    async def test_run(self):
        # Mock the _run_script method
        run_code = RunCode()
        run_code._run_script = AsyncMock(return_value=("stdout content", "stderr content"))
        # Mock the code_info parameter
        code_info = {"command": ["ls", "-l"]}
        # Call the _run method
        response = await run_code._run(code_info)
        # Assert the response
        self.assertEqual(response, "stdout contentstderr content")

if __name__ == '__main__':
    unittest.main()

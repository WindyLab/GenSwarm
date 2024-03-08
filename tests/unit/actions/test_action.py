import unittest
from unittest.mock import MagicMock, AsyncMock
from modules.actions import Action

class TestAction(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        class MockAction(Action):
            def process_response(self, response: str, **kwargs) -> str:
                return response
        self.action = MockAction()

    async def test_run_method_invocations(self):
        # Mocking _run and _ask methods
        self.action._ask = AsyncMock(return_value="mocked_response")
        # Call run method
        response = await self.action.run(prompt="test_prompt")
        # Verify that _ask method is called with correct prompt
        self.action._ask.assert_called_once_with("test_prompt")

    async def test_returned_result(self):
        # Mocking _ask method
        self.action._llm.ask = AsyncMock(return_value="mocked_response")

        # Call run method
        response = await self.action.run(prompt="test_prompt")

        # Verify that the returned result is correct
        self.assertEqual(response, "mocked_response")

    async def test_missing_prompt(self):
        # Call run method without providing prompt
        with self.assertRaises(SystemExit):
            await self.action.run()

if __name__ == '__main__':
    unittest.main()

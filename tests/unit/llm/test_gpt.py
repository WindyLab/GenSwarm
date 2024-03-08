import unittest
from unittest.mock import patch, AsyncMock
from modules.llm.gpt import GPT

class TestGPT(unittest.IsolatedAsyncioTestCase):
    async def test_ask(self):
        # 创建 AsyncMock 以模拟异步方法的行为
        mock_chat = AsyncMock()
        mock_chat.return_value = AsyncMock(choices=[AsyncMock(message=AsyncMock(content="Mock response"))])
        
        # 使用 patch 替换 AsyncOpenAI，并设置其返回模拟对象
        with patch('modules.llm.gpt.AsyncOpenAI') as MockAsyncOpenAI:
            MockAsyncOpenAI.return_value.chat.completions.create = mock_chat

            # 创建被测试的 GPT 对象
            gpt = GPT(model='mock-model')         
            response = await gpt.ask("Mock prompt", temperature=0.5)

            # 断言结果是否符合预期
            mock_chat.assert_awaited_once_with(
                model='mock-model',
                messages=[{"role": "user", "content": "Mock prompt"}],
                temperature=0.5
            )
            self.assertEqual(response, "Mock response")


if __name__ == '__main__':
    unittest.main()

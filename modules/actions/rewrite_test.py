from modules.actions.action import Action
from modules.utils import parse_code

PROMPT_TEMPLATE = """
This is the test file you previously wrote, but there are error messages as follows. 
code:
```python
{test_code}
```
Error message:
{error_message}

The test file is at the same directory level as the source file (filename=core.py).
Use 'from core import ...' and 'from env import env' to import the source file.


You need to rewrite the entire test file to correct the errors. 
Note: output the complete file.


you should correctly import the necessary classes based on these file locations!
Return ```python your_code_here ``` with NO other texts,
your code:
"""


class RewriteUnitTest(Action):
    name: str = "RewriteUnitTest"

    async def write_code(self, prompt):
        code_rsp = await self._ask(prompt)

        try:
            code = parse_code(text=code_rsp)
        except Exception:
            # Handle the exception if needed
            self._logger.error(f"Can't parse the code: {code_rsp}")

            # Return code_rsp in case of an exception, assuming llm just returns code as it is and doesn't wrap it inside ```
            code = code_rsp
        return code

    async def run(self, test_code, error_message):
        prompt = PROMPT_TEMPLATE.format(
                test_code=test_code,
                )
        code = await self.write_code(prompt)
        return code

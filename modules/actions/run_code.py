import os
import subprocess
import traceback
from typing import Tuple
from modules.actions.action import Action
from loguru import logger

PROMPT_TEMPLATE = """
Role: You are a senior development and qa engineer, your role is summarize the code running result.
If the running result does not include an error, you should explicitly approve the result.
On the other hand, if the running result indicates some error, you should point out which part, the development code or the test code, produces the error,
and give specific instructions on fixing the errors. Here is the code info:
{context}
Now you should begin your analysis
---
## instruction:
Please summarize the cause of the errors and give correction instruction
## File To Rewrite: Determine the ONE file to rewrite in order to fix the error, for example, xyz.py, or test_xyz.py
## Status:
Determine if all of the code works fine, if so write PASS, else FAIL,
WRITE ONLY ONE WORD, PASS OR FAIL, IN THIS SECTION
---
You should fill in necessary instruction, status, and finally return all content between the --- segment line.
"""

CONTEXT = """
## Development Code File Name
{code_file_name}
## Development Code
```python
{code}
```
## Test File Name
{test_file_name}
## Test Code
```python
{test_code}
```
## Running Command
{command}
## Running Output
standard output: {outs};
standard errors: {errs};
"""


class RunCode(Action):
    name: str = 'RunCode'

    @classmethod
    async def run_text(cls, code) -> Tuple[str, str]:
        try:
            # We will document_store the result in this dictionary
            namespace = {}
            exec(code, namespace)
            return namespace.get("result", ""), ""
        except Exception:
            # If there is an error in the code, return the error message
            return "", traceback.format_exc()

    @classmethod
    async def run_script(cls, working_directory, command=[]) -> Tuple[str, str]:
        working_directory = str(working_directory)
        # Copy the current environment variables
        env = os.environ.copy()

        # Start the subprocess
        process = subprocess.Popen(
                command, cwd=working_directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
                )

        try:
            # Wait for the process to complete, with a timeout
            stdout, stderr = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            logger.info("The command did not complete within the given timeout.")
            process.kill()  # Kill the process if it times out
            stdout, stderr = process.communicate()
        return stdout.decode("utf-8"), stderr.decode("utf-8")

    async def run(self, code, mode="script", code_file_name="", test_code="", test_file_name="", command=[],
                  **kwargs) -> str:
        logger.info(f"Running {' '.join(command)}")
        if mode == "script":
            outs, errs = await self.run_script(command=command, **kwargs)
        elif mode == "text":
            outs, errs = await self.run_text(code=code)

        logger.info(f"{outs=}")
        logger.info(f"{errs=}")

        context = CONTEXT.format(
                code=code,
                code_file_name=code_file_name,
                test_code=test_code,
                test_file_name=test_file_name,
                command=" ".join(command),
                outs=outs[:500],  # outs might be long but they are not important, truncate them to avoid token overflow
                errs=errs[:10000],  # truncate errors to avoid token overflow
                )

        prompt = PROMPT_TEMPLATE.format(context=context)
        rsp = await self._aask(prompt)

        result = context + rsp

        return result

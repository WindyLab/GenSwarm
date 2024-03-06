import asyncio
import os
import traceback
from typing import Tuple

from modules.actions.action import Action

PROMPT_TEMPLATE = """
Role: You are a senior development and qa engineer, your role is summarize the code running result.
If the running result does not include an error, you should explicitly approve the result.
On the other hand, if the running result indicates some error, you should point out which part, the development code or the test code, produces the error,
and give specific instructions on fixing the errors. Here is the code info:
{context}
Now you should begin your analysis
---
## Instruction:
Please summarize the cause of the errors and give correction instruction
## File To Rewrite: Determine the ONE file to rewrite in order to fix the error, for example, xyz.py, or test_xyz.py
## Status:
Determine if all of the code works fine, if so write PASS, else FAIL,
WRITE ONLY ONE WORD, PASS OR FAIL, IN THIS SECTION
---
---
You should fill in necessary Instruction, status, and finally return all content between the --- segment line.
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
    def _run_text(cls, code) -> Tuple[str, str]:
        try:
            # We will document_store the result in this dictionary
            namespace = {}
            exec(code, namespace)
            return namespace.get("result", ""), ""
        except Exception:
            # If there is an error in the code, return the error message
            return "", traceback.format_exc()

    async def _run_script(self, working_directory, command=[]) -> Tuple[str, str]:
        working_directory = str(working_directory)
        env = os.environ.copy()

        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=working_directory,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
            return stdout.decode("utf-8"), stderr.decode("utf-8")
        except asyncio.TimeoutError:
            self._logger.info("The command did not complete within the given timeout.")
            process.kill()
            await process.wait()
            stdout, stderr = '', 'The command did not complete within the given timeout.'
            return stdout, stderr
        except Exception as e:
            self._logger.error(f"An error occurred while running the command: {e}")
            return '', f"An error occurred while running the command: {e}"

    async def _run(self, code_info, mode="script", **kwargs) -> str:
        command = code_info["command"]
        self._logger.info(f"Running {' '.join(command)}")
        outs, errs = "", ""
        if mode == "script":
            # Note: must call call_reset_environment before and after running the script
            from modules.prompt.const import WORKSPACE_ROOT

            outs, errs = await self._run_script(working_directory=WORKSPACE_ROOT, command=command)

        self._logger.info(f"Outs: {outs}")
        self._logger.error(f"Errs: {errs}")

        return str(outs + errs)

    def process_response(self, response: str, **kwargs) -> str:
        return response

    # def _run(self, code_info, mode="script", **kwargs) -> str:
    #     code_info = eval(code_info)
    #     code_file_name = code_info["file_name"]
    #     code = read_file(directory=WORKSPACE_ROOT, filename=code_file_name)
    #     test_file_name = code_info["test_file_name"]
    #     command = ["python", test_file_name]
    #     test_code = read_file(directory=WORKSPACE_ROOT, filename=test_file_name)
    #
    #     self._logger.info(f"Running {' '.join(command)}")
    #     if mode == "script":
    #         outs, errs = self._run_script(working_directory=WORKSPACE_ROOT, command=command, **kwargs)
    #     elif mode == "text":
    #         outs, errs = self._run_text(code=code)
    #
    #     self._logger.info(f"{outs=}")
    #     self._logger.info(f"{errs=}")
    #
    #     context = CONTEXT.format(
    #         code=code,
    #         code_file_name=code_file_name,
    #         test_code=test_code,
    #         test_file_name=test_file_name,
    #         command=" ".join(command),
    #         outs=outs[:500],  # outs might be long but they are not important, truncate them to avoid token overflow
    #         errs=errs[:10000],  # truncate errors to avoid token overflow
    #     )
    #
    #     prompt = PROMPT_TEMPLATE.format(context=context)
    #     rsp = self._ask(prompt)
    #     self._logger.error("run code analysis: \n%s", rsp)
    #     status = re.search("Status:\s*(.+)", rsp, re.IGNORECASE).group(1)
    #
    #     # send results
    #     if status == "PASS":
    #         return "no error", [TestResult.ALL_PASS
    #                             if test_file_name == "test_run.py"
    #                             else TestResult.HALF_PASS]
    #     else:
    #         instruction = re.search("Instruction:\s*(.+)", rsp, re.IGNORECASE).group(1)
    #         file_name = re.search("File To Rewrite:\s*(.+\\.py)", rsp, re.IGNORECASE).group(1)
    #         if 'test' in file_name:
    #             return instruction, [TestResult.NOT_PASS, BugSource.TEST_CODE]
    #         else:
    #             return instruction, [TestResult.NOT_PASS, BugSource.CODE]

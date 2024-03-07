import asyncio
import os
import sys
import traceback
from typing import Tuple

from modules.actions.action import Action
from modules.prompt.run_code_prompt import PROMPT_TEMPLATE, CONTEXT


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

    async def _run_script(self, working_directory, command=[], print_output=True) -> Tuple[str, str]:
        working_directory = str(working_directory)
        env = os.environ.copy()

        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=working_directory,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )

        stdout_chunks, stderr_chunks = [], []

        # Simplified stream reading with direct print control
        async def read_stream(stream, accumulate, is_stdout=True):
            while True:
                line_bytes = await stream.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode('utf-8')
                accumulate.append(line)
                if print_output:
                    print(line, end='' if is_stdout else '', file=sys.stderr if not is_stdout else None)

        try:
            # Gather stdout and stderr concurrently
            await asyncio.gather(
                read_stream(process.stdout, stdout_chunks, is_stdout=True),
                read_stream(process.stderr, stderr_chunks, is_stdout=False)
            )

            # Wait for process to complete
            await process.wait()

        except asyncio.TimeoutError:
            self._logger.info("The command did not complete within the given timeout.")
            # self._context.log.format_message("The command did not complete within the given timeout.","error")
            process.kill()
            await process.wait()
            return '', 'The command did not complete within the given timeout.'
        except Exception as e:
            self._logger.error(f"An error occurred while running the command: {e}")
            # self._context.log.format_message(f"An error occurred while running the command: {e}","error")
            return '', f"An error occurred while running the command: {e}"

        # Join collected lines into single strings
        stdout = ''.join(stdout_chunks)
        stderr = ''.join(stderr_chunks)
        return stdout, stderr


    async def _run(self, code_info, mode="script", **kwargs) -> str:
        command = code_info["command"]
        self._logger.info(f"Running {' '.join(command)}")

        outs, errs = "", ""
        if mode == "script":
            # Note: must call call_reset_environment before and after running the script
            from modules.utils.common import WORKSPACE_ROOT

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
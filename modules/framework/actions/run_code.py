"""
Copyright (c) 2024 WindyLab of Westlake University, China
All rights reserved.

This software is provided "as is" without warranty of any kind, either
express or implied, including but not limited to the warranties of
merchantability, fitness for a particular purpose, or non-infringement.
In no event shall the authors or copyright holders be liable for any
claim, damages, or other liability, whether in an action of contract,
tort, or otherwise, arising from, out of, or in connection with the
software or the use or other dealings in the software.
"""

import asyncio
import json
import os
import pickle
import sys
import traceback

import rospy

from modules.file import logger
from modules.framework.action import ActionNode
from modules.framework.code_error import Bug
from modules.utils import root_manager, get_project_root


class RunAllocateRun(ActionNode):
    def __init__(self, next_text: str = "", node_name: str = ""):
        super().__init__(next_text, node_name)

    async def _run_script(
        self, working_directory, command=[], print_output=True
    ) -> str:
        working_directory = str(working_directory)
        env = os.environ.copy()

        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=working_directory,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

        stdout_chunks, stderr_chunks = [], []

        async def read_stream(stream, accumulate, is_stdout=True):
            while True:
                line_bytes = await stream.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode("utf-8")
                accumulate.append(line)
                if print_output:
                    print(
                        line,
                        end="" if is_stdout else "",
                        file=sys.stderr if not is_stdout else None,
                    )

        try:
            if hasattr(self.context.args, "timeout"):
                timeout = self.context.args.timeout
            else:
                timeout = 30
            await asyncio.wait_for(
                asyncio.gather(
                    read_stream(process.stdout, stdout_chunks, is_stdout=True),
                    read_stream(process.stderr, stderr_chunks, is_stdout=False),
                ),
                timeout=timeout,
            )

            if (
                "WARNING: cannot load logging configuration file, logging is disabled\n"
                in stderr_chunks
            ):
                stderr_chunks.remove(
                    "WARNING: cannot load logging configuration file, logging is disabled\n"
                )
            if stderr_chunks:
                return "\n".join(stderr_chunks)
            else:
                return "NONE"

        except asyncio.TimeoutError:
            logger.log(content="Timeout", level="error")
            process.kill()
            await process.wait()  # Ensure the process is terminated
            return "Timeout"
        except asyncio.CancelledError:
            logger.log(content="Cancelled", level="error")
            process.kill()
            await process.wait()  # Ensure the process is terminated
            raise
        except Exception as e:
            logger.log(content=f"error in run allocate: {e}", level="error")
            process.kill()
            await process.wait()  # Ensure the process is terminated
            return f"error in run allocate: {e}"
        finally:
            if process.returncode is None:
                process.kill()
                await process.wait()

    async def _run(self):
        command = ["python", "allocate_run.py"]
        result = await self._run_script(
            working_directory=root_manager.workspace_root, command=command
        )
        return self._process_response(result)

    def _process_response(self, result: str):
        if result == "NONE":
            logger.log(content="Run allocate success", level="success")
            return result
        else:
            logger.log(content=f"Run allocate failed, result: {result}", level="error")
            return Bug(error_msg=result, error_function="RunAllocateRun")


class RunCode(ActionNode):
    def __init__(self, next_text: str = "", node_name: str = ""):
        super().__init__(next_text, node_name)
        self.start_id = None
        self.end_id = None
        self.task = None

    def _build_prompt(self):
        pass

    def setup(self, start: int, end: int):
        self.start_id = start
        self.end_id = end

    async def _run_script(
        self, working_directory, command=[], print_output=True
    ) -> str:
        working_directory = str(working_directory)
        env = os.environ.copy()

        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=working_directory,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

        stdout_chunks, stderr_chunks = [], []

        async def read_stream(stream, accumulate, is_stdout=True):
            while True:
                line_bytes = await stream.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode("utf-8")
                accumulate.append(line)
                if print_output:
                    print(
                        line,
                        end="" if is_stdout else "",
                        file=sys.stderr if not is_stdout else None,
                    )

        try:
            # Apply timeout to the gather call using asyncio.wait_for
            if hasattr(self.context.args, "timeout"):
                timeout = self.context.args.timeout
            else:
                timeout = 30
            await asyncio.wait_for(
                asyncio.gather(
                    read_stream(process.stdout, stdout_chunks, is_stdout=True),
                    read_stream(process.stderr, stderr_chunks, is_stdout=False),
                ),
                timeout=timeout,
            )

            if (
                "WARNING: cannot load logging configuration file, logging is disabled\n"
                in stderr_chunks
            ):
                stderr_chunks.remove(
                    "WARNING: cannot load logging configuration file, logging is disabled\n"
                )
            if stderr_chunks:
                return "\n".join(stderr_chunks)
            else:
                return "NONE"

        except asyncio.TimeoutError:
            logger.log(content="Timeout", level="error")
            process.kill()
            await process.wait()  # Ensure the process is terminated
            return "Timeout"
        except asyncio.CancelledError:
            logger.log(content="Cancelled", level="error")
            process.kill()
            await process.wait()  # Ensure the process is terminated
            raise
        except Exception as e:
            logger.log(content=f"error in run code: {e}", level="error")
            process.kill()
            await process.wait()  # Ensure the process is terminated
            return f"error in run code: {e}"
        finally:
            # Ensure the process is terminated in case of any other unexpected errors
            if process.returncode is None:  # Check if process is still running
                process.kill()
                await process.wait()

    async def run(self, auto_next: bool = True) -> str:
        script = self.context.args.script
        command = ["python", script, str(self.start_id), str(self.end_id)]
        # print(f"运行命令: {command}")

        # 运行主脚本，并传递额外的输入参数
        result = await self._run_script(
            working_directory=root_manager.workspace_root, command=command
        )
        return result

    def _process_response(self, response: str) -> str:
        return response


class RunCodeAsync(ActionNode):
    def __init__(self, next_text: str = "", node_name: str = ""):
        super().__init__(next_text, node_name)

    async def _run(self):
        start_idx = rospy.get_param("robot_start_index")
        end_idx = rospy.get_param("robot_end_index")
        total_robots = end_idx - start_idx + 1
        num_processes = min(3, total_robots)  # 并行进程数
        robots_per_process = total_robots // num_processes

        robot_ids = list(range(start_idx, end_idx + 1))
        robot_id_chunks = [
            robot_ids[i : i + robots_per_process]
            for i in range(0, total_robots, robots_per_process)
        ]
        tasks = []
        result_list = []
        try:
            for chunk in robot_id_chunks:
                action = RunCode()
                action.setup(chunk[0], chunk[-1])
                task = asyncio.create_task(action.run())
                tasks.append(task)
            result_list = list(set(await asyncio.gather(*tasks)))
        except Exception as e:
            print("Error in RunCodeAsync: ", e)
            traceback.print_exc()
        finally:
            os.system("pgrep -f run.py | xargs kill -9")
            return self._process_response(result_list)

    def _process_response(self, result: list):
        if ("NONE" in result or "Timeout" in result) and len(result) == 1:
            logger.log(content="Run code success", level="success")
            return "NONE"
        logger.log(content=f"Run code failed, result: {result}", level="error")
        result_content = "\n".join(result)
        return Bug(error_msg=result_content, error_function="", error_code="")


if __name__ == "__main__":
    from modules.framework.handler import BugLevelHandler
    from modules.framework.handler import FeedbackHandler
    from modules.framework.actions import *
    import argparse

    parser = argparse.ArgumentParser(
        description="Run simulation with custom parameters."
    )

    parser.add_argument(
        "--timeout", type=int, default=60, help="Total time for the simulation"
    )
    parser.add_argument(
        "--feedback",
        type=str,
        default="None",
        help="Optional: human, VLM, None,Result feedback",
    )
    parser.add_argument(
        "--data",
        type=str,
        default="encircling/2024-10-14_01-05-45",
        help="Data path for the simulation",
    )
    parser.add_argument(
        "--target_pkl",
        type=str,
        default="WriteRun.pkl",
        help="Data path for the simulation",
    )
    parser.add_argument("--script", type=str, default="run.py", help="Script to run")
    args = parser.parse_args()

    data = args.data
    path = f"{get_project_root()}/workspace/{data}"

    rospy.set_param("path", data)
    root_manager.update_root(path)
    debug_code = DebugError("fixed code")
    human_feedback = Criticize("feedback")
    run_allocate = RunAllocateRun("run allocate")
    run_code = RunCodeAsync("run code")
    video_critic = VideoCriticize("")
    run_allocate._next = run_code
    # initialize error handlers
    bug_handler = BugLevelHandler()
    bug_handler.next_action = debug_code
    debug_code._next = run_code
    hf_handler = FeedbackHandler()
    hf_handler.next_action = human_feedback
    human_feedback._next = run_code

    # link error handlers
    chain_of_handler = bug_handler
    bug_handler.successor = hf_handler

    if args.feedback != "None":
        run_allocate.error_handler = chain_of_handler
        run_code.error_handler = chain_of_handler

        run_code._next = video_critic
        video_critic.error_handler = chain_of_handler
    if args.target_pkl != "None":
        run_code.context.load_from_file(path + "/" + args.target_pkl)
    run_code.context.args = args
    asyncio.run(run_allocate.run())
    run_code.context.save_to_file(f"{path}/run_code.pkl")

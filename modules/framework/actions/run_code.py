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

import argparse
import asyncio
import os
import subprocess
import time
import traceback

import rospy

# import rospy

from modules.file import logger
from modules.framework.action import ActionNode
from modules.framework.code_error import Bug, Feedback
from modules.framework.context import WorkflowContext
from modules.utils import (
    root_manager,
    get_project_root,
    run_script,
    save_dict_to_json,
    rich_print,
)
from modules.utils.rich_print import rich_input


class RunAllocateRun(ActionNode):
    def __init__(self, next_text: str = "", node_name: str = "", env=None):
        self.call_times = 0
        self.env = env
        super().__init__(next_text, node_name)

    async def _run(self):
        try:
            self.context.scoop = "global"
            self.call_times += 1
            if len(self.context.global_skill_tree.layers) == 0:
                logger.log(content="No task to run", level="error")
                result = "No task to run"
            else:
                command = ["python", "allocate_run.py"]
                self.env.start_environment(
                    experiment_path=self.context.args.experiment_path
                )
                result = await run_script(
                    working_directory=root_manager.workspace_root,
                    command=command,
                    print_output=False,
                    timeout=20,
                )
        finally:
            os.system("pgrep -f allocate_run.py | xargs kill -9")
            return self._process_response(result)

    def _process_response(self, result: str):
        dict_result = {
            "run_times": self.call_times,
            "result": result,
            "test_mode": self.context.args.test_mode,
        }
        try:
            self.env.stop_environment(save_result=False)
            if result == "NONE":
                logger.log(content="Run allocate success", level="success")
                return result
            if result == "No task to run":
                return result
            else:
                logger.log(
                    content=f"Run allocate failed, result: {result}", level="error"
                )
                print(f"Run allocate failed, result: {result}")

                if self.call_times >= 3:
                    logger.log(
                        content=f"Run code failed {self.call_times} times, retrying...",
                        level="warning",
                    )

                    return str(dict_result)
                    # self._next = None
                if self.context.args.test_mode in ["debug", "full_version"]:
                    return Bug(
                        error_msg=result,
                        error_code="\n\n".join(
                            self.context.global_skill_tree.functions_body
                        ),
                        error_function="",
                    )

                return str(dict_result)
        except Exception as e:
            logger.log(content=f"Exception occurred: {e}", level="error")
        finally:
            save_dict_to_json(
                dict_result,
                root_manager.workspace_root
                / f"{self.context.args.test_mode}_global_run.json",
            )


class RunCodeReal(ActionNode):
    def __init__(self, env):
        super().__init__()
        self.stage = None
        self.path = None
        self.env = env

    def _build_prompt(self):
        pass

    def setup(self, stage: int, path: str):
        self.stage = f"{stage}"
        colon_index = path.find("workspace/")

        if colon_index != -1:
            substring = path[colon_index + len("workspace/"):]
            self.path = substring
        self.set_logging_text("Running code.py")

    async def _run(self) -> str:
        # 构造 docker-compose.yml 的路径
        compose_file_path = os.path.join(
            root_manager.project_root, "docker/docker-compose.yml"
        )

        config_path = os.path.join(root_manager.project_root, "config/hosts")

        playbook_path = os.path.join(
            root_manager.project_root, "docker/ansible/main.yml"
        )

        # os.environ["DATA_PATH"] = self.path
        # os.environ["STAGE"] = self.stage
        if self.stage == "1":
            self.env.start_environment(
                experiment_path=self.context.args.experiment_path,
                render_mode="human",
            )
        working_directory = os.path.join(root_manager.project_root, "docker")
        # command = ["docker-compose", "up", "deploy"]
        command = [
            "ansible-playbook",
            "-i",
            config_path,  # 指定 hosts 文件
            playbook_path,  # Playbook 文件路径
            "-e",
            f"DATA_PATH={self.path}",  # 传递环境变量 DATA_PATH
            "-e",
            f"STAGE={self.stage}",  # 传递环境变量 STAGE
        ]
        env = os.environ.copy()
        # 调用 docker-compose 命令并显示输出
        result = await run_script(
            working_directory=working_directory,
            print_output=True,
            command=command,
            timeout=70,
            env=env,
        )
        rich_print(content="Code is deployed.", title="Deploy Code")
        if self.stage == "1":
            pub_mqtt = rich_input(
                "Code deployment completed.Robots are ready to run the experiment.Start the experiment? (y/n)")
            if pub_mqtt == "y":
                rospy.set_param("pub_mqtt", True)
            time.sleep(self.context.args.timeout)
            self.env.stop_environment(file_name="real", save_result=True)
            rospy.set_param('pub_mqtt', False)
        logger.log(content=result, level="info")

        # rich_print(content=result, title="Deploy Code")
        return self._process_response(result)

    def _process_response(self, response: str):
        if self.stage == "1":
            # 定义颜色代码
            RED = "\033[31m"
            GREEN = "\033[32m"
            YELLOW = "\033[33m"
            RESET = "\033[0m"

            if_feedback = input(f"{GREEN}If task is done? Press y/n: {RESET}")
            if if_feedback.lower() == "y":
                logger.log("run code: success", "warning")
                return "NONE"
            else:
                rich_print(content="Task is not done.", title="Task Status")
                feedback = input(f"{YELLOW}Please provide feedback: {RESET}")
                rich_print(content=f"Feedback received:{feedback}", title="Feedback")
                self.context.feedbacks.append(feedback)
                return Feedback(feedback)
        return response


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

    async def run(self, auto_next: bool = True) -> str:
        script = self.context.args.script
        command = ["python", script, str(self.start_id), str(self.end_id)]
        result = await run_script(
            working_directory=root_manager.workspace_root,
            command=command,
            timeout=self.context.args.timeout,
        )
        return result

    def _process_response(self, response: str) -> str:
        return response


class RunCodeAsync(ActionNode):
    from run.auto_runner.core import EnvironmentManager

    def __init__(
            self, next_text: str = "", node_name: str = "", env: EnvironmentManager = None
    ):
        self.call_times = 0
        self.env = env
        super().__init__(next_text, node_name)

    async def _run(self):
        self.call_times += 1
        self.context.scoop = "local"
        start_idx = 4
        end_idx = 9
        total_robots = end_idx - start_idx + 1
        num_processes = min(10, total_robots)  # 并行进程数
        robots_per_process = total_robots // num_processes

        robot_ids = list(range(start_idx, end_idx + 1))
        robot_id_chunks = [
            robot_ids[i: i + robots_per_process]
            for i in range(0, total_robots, robots_per_process)
        ]
        tasks = []
        result_list = []
        try:
            if len(self.context.global_skill_tree.layers) == 0:
                keep_entities = False
            else:
                keep_entities = True
            self.env.start_environment(
                experiment_path=root_manager.workspace_root, keep_entities=keep_entities,
                render_mode="human",
            )
            for chunk in robot_id_chunks:
                action = RunCode()
                action.setup(chunk[0], chunk[-1])
                task = asyncio.create_task(action.run())
                tasks.append(task)
            result_list = list(set(await asyncio.gather(*tasks)))
        except Exception as e:
            print("Error in RunCodeAsync: ", e)
        finally:
            os.system(f"pgrep -f run.py | xargs kill -9")
            return self._process_response(result_list)

    def _process_response(self, result: list):
        dict_result = {
            "run_times": self.call_times,
            "result": result,
            "test_mode": self.context.args.test_mode,
        }
        try:
            if self.context.args.test_mode not in ["full_version"]:
                self._next = None
            self.context.save_to_file(
                root_manager.workspace_root / f"{self.context.args.test_mode}.pkl"
            )

            if all(item in ["NONE", "Timeout"] for item in result):
                logger.log(content="Run code success", level="success")
                self.env.stop_environment(file_name=self.context.args.test_mode, save_result=True)
                return "NONE"

            result = [item for item in result if item not in ["NONE", "Timeout"]]
            logger.log(content=f"Run code failed, result: {result}", level="error")
            self.env.stop_environment(file_name=self.context.args.test_mode, save_result=False)

            result_content = result[0]

            if self.call_times >= 3:
                logger.log(
                    content=f"Run code failed {self.call_times} times, retrying...",
                    level="warning",
                )
                return str(dict_result)

            if self.context.args.test_mode in ["debug", "full_version"]:
                return Bug(
                    error_msg=result_content,
                    error_code="\n\n".join(
                        self.context.local_skill_tree.functions_body
                    ),
                    error_function="",
                )

        except Exception as e:
            logger.log(content=f"Exception occurred: {e}", level="error")

        finally:
            save_dict_to_json(
                dict_result,
                root_manager.workspace_root
                / f"{self.context.args.test_mode}_local_run.json",
            )

        # else:
        #     logger.log(content=f"Run code failed 3 times or VLM is enabled_{self.context.vlm},", level="error")
        #     return 'Fail'


def init_workflow(args, env=None) -> ActionNode:
    from modules.framework.handler import BugLevelHandler
    from modules.framework.handler import FeedbackHandler
    from modules.framework.actions import DebugError, CodeImprove, VideoCriticize

    init_result = {
        "target_pkl": None,
        "feedback": None,
        "test_mode": None,
        "first_action": None,
        "error": None,
    }
    try:
        context = WorkflowContext()
        debug_code = DebugError()
        code_improver = CodeImprove("feedback")
        run_allocate = RunAllocateRun("run allocate", env=env)
        run_code = RunCodeAsync("run code", env=env)
        copy_file = RunCodeReal(env=env)
        copy_file.setup(stage=0, path=args.experiment_path)
        run_real = RunCodeReal(env=env)
        run_real.setup(stage=1, path=args.experiment_path)
        stop_docker = RunCodeReal(env=env)
        stop_docker.setup(stage=2, path=args.experiment_path)
        video_critic = VideoCriticize("")
        if args.test_mode == "real":
            run_allocate._next = copy_file
            # stop_docker._next = run_real
            copy_file._next = run_real
            code_improver._next = run_allocate
            # run_real._next = stop_docker
        else:
            run_allocate._next = run_code

        bug_handler = BugLevelHandler()
        bug_handler.next_action = debug_code
        debug_code._next = run_allocate

        hf_handler = FeedbackHandler()
        hf_handler.next_action = code_improver
        # code_improver._next = run_allocate

        # link error handlers
        chain_of_handler = bug_handler
        bug_handler.successor = hf_handler
        run_allocate.error_handler = chain_of_handler
        run_code.error_handler = chain_of_handler
        run_real.error_handler = chain_of_handler
        if args.test_mode == "full_version":
            run_code._next = video_critic
            video_critic.error_handler = chain_of_handler
        target_pkl = None
        if args.test_mode == "improve":
            if os.path.exists(args.experiment_path + "/" + "debug.pkl"):
                target_pkl = "run_code.pkl"
            else:
                target_pkl = "WriteRun.pkl"

        elif args.test_mode in ["wo_vlm", "full_version", "debug", "real"]:
            target_pkl = "WriteRun.pkl"
        if target_pkl:
            context.load_from_file(args.experiment_path + "/" + target_pkl)
            if args.test_mode != "real":
                context.global_skill_tree.save_functions_to_file()
                context.local_skill_tree.save_functions_to_file()
        context.args = args
        init_result["target_pkl"] = args.target_pkl
        init_result["feedback"] = args.feedback
        init_result["test_mode"] = args.test_mode

        if args.test_mode == "meta" or args.test_mode == "cap":
            init_result["first_action"] = "RunCode"
            return run_code
        if args.test_mode == "vlm":
            init_result["first_action"] = "VideoCriticize"
            return video_critic
        init_result["first_action"] = "RunAllocateRun"

        if args.test_mode == "improve":
            return code_improver
        return run_allocate
    except Exception as e:
        print(f"Error in init_workflow: {e}")
        init_result["error"] = traceback.format_exc()

    finally:
        save_dict_to_json(
            init_result, root_manager.workspace_root / f"{args.test_mode}_init_run.json"
        )


def runcode(
        timeout=20,
        feedback="None",
        experiment_path="clustering/2024-10-21_03-04-33",
        target_pkl="WriteRun.pkl",
        script="run.py",
        human_feedback=False,
        env_manager=None,
        debug=False,
        test_mode="wo_vlm",
):
    """
    Run the simulation with custom parameters (synchronously).

    Args:
        timeout (int): Total time for the simulation.
        feedback (str): Optional feedback type ("human", "VLM", "None").
        experiment_path (str): Data path for the simulation.
        target_pkl (str): Path to the target pkl file.
        script (str): Script to run for the simulation.
        human_feedback (bool): Whether to use human feedback.
    """

    parser = argparse.ArgumentParser(
        description="Run simulation with custom parameters."
    )

    parser.add_argument(
        "--timeout", type=int, default=20, help="Total time for the simulation"
    )
    parser.add_argument(
        "--feedback",
        type=str,
        default="None",
        help="Optional: human, VLM, None, Result feedback",
    )
    parser.add_argument(
        "--experiment_path",
        type=str,
        default="clustering/2024-10-21_03-04-33",
        help="Data path for the simulation",
    )
    parser.add_argument(
        "--target_pkl",
        type=str,
        default="WriteRun.pkl",
        help="Data path for the simulation",
    )
    parser.add_argument("--script", type=str, default="run.py", help="Script to run")
    parser.add_argument(
        "--human_feedback",
        type=bool,
        default=False,
        help="Whether to use human feedback",
    )
    parser.add_argument(
        "--debug", type=bool, default=False, help="Whether to use debug mode"
    )
    parser.add_argument(
        "--test_mode",
        type=str,
        default="wo_vlm",
        help="Optional: wo_vlm,full_version,debug,vlm,real",
    )
    args = parser.parse_args(
        args=[
            f"--timeout={timeout}",
            f"--feedback={feedback}",
            f"--experiment_path={experiment_path}",
            f"--target_pkl={target_pkl}",
            f"--script={script}",
            f"--human_feedback={str(human_feedback)}",
            f"--debug={str(debug)}",
            f"--test_mode={str(test_mode)}",
        ]
    )

    path = args.experiment_path

    root_manager.update_root(path)

    first_action = init_workflow(args, env=env_manager)
    if first_action is not None:
        # 使用 asyncio.run() 来运行异步的 first_action.run()
        result = asyncio.run(first_action.run())
        return result
    return None
    # 保存执行结果
    # first_action.context.save_to_file(f"{path}/run_code.pkl")


if __name__ == "__main__":
    runcode()

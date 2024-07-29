import asyncio
import os

from modules.framework.actions import *
from modules.framework.action import *
from modules.framework.actions.generate_functions import GenerateFunctions
from modules.framework.actions.video_criticize import VideoCriticize
from modules.framework.handler import *
from modules.framework.actions.action_on_layer import ActionOnLayer

from modules.utils.logger import setup_logger
from modules.framework.context.workflow_context import WorkflowContext
from modules.file import File, logger
from modules.utils.root import root_manager


class Workflow:
    def __init__(self, user_command: str, args=None):
        self._logger = setup_logger("Workflow")
        self._context = WorkflowContext()
        self._context.args = args
        self._context.command = user_command
        # initialize context for all action nodes
        ActionNode.context = self._context
        self._pipeline = None
        self._chain_of_handler = None

        self.init_workspace()
        self.init_log_file()
        self.build_up()

    @staticmethod
    def init_log_file():
        logger.set_file(File("log.md"))

    @staticmethod
    def init_workspace():
        workspace_root = root_manager.workspace_root
        project_root = root_manager.project_root
        os.makedirs(os.path.join(workspace_root, "data/frames"))

        util_file = File(root=os.path.join(project_root, "modules/env"), name="apis.py")
        util_file.copy(root=workspace_root)

        run_file = File(root=os.path.join(project_root, "modules/env"), name="run.py")
        run_file.copy(root=workspace_root)

    def build_up(self):
        # initialize actions
        # analyze_constraints = AnalyzeConstraints("constraint pool")
        analyze_functions = AnalyzeFunctions("function pool")
        generate_functions = GenerateFunctions("function")
        write_functions = WriteFunctionsAsync("function.py")
        write_run = WriteRun("code")
        code_review = CodeReview("reviewed code")

        run_code = RunCodeAsync("pass")
        debug_code = DebugError("fixed code")
        human_feedback = Criticize("feedback")
        video_critic = VideoCriticize("")
        # initialize error handlers
        bug_handler = BugLevelHandler()
        bug_handler.next_action = debug_code
        debug_code._next = run_code
        # critic_handler = CriticLevelHandler()
        hf_handler = FeedbackHandler()
        hf_handler.next_action = human_feedback
        human_feedback._next = run_code
        # link error handlers
        self._chain_of_handler = bug_handler
        bug_handler.successor = hf_handler
        run_code.error_handler = self._chain_of_handler
        video_critic.error_handler = self._chain_of_handler
        # link actions
        # stage 1
        analysis_stage = ActionLinkedList("Analysis", analyze_constraints)
        analysis_stage.add(analyze_functions)
        # stage 2
        coding_stage = ActionLinkedList("Coding", generate_functions)
        # coding_stage.add(write_functions)
        # coding_stage.add(write_run)
        # stage 3
        # review_stage = ActionLinkedList("Review", code_review)
        # stage 4
        test_stage = ActionLinkedList("Testing", run_code)
        test_stage.add(video_critic)

        # mermaid graph would be incomplete if final action is not linked
        run_code._next = ActionNode(next_text="pass", node_name="END")

        # combine stages
        code_llm = ActionLinkedList("Code-LLM", analysis_stage)

        # code_llm.add(analysis_stage)
        code_llm.add(coding_stage)
        # code_llm.add(review_stage)
        # code_llm.add(test_stage)
        code_llm.add(ActionNode("PASS", "END"))
        self._pipeline = code_llm
        # assign error handlers to actions

    async def run(self):
        text = display_all(self._pipeline, self._chain_of_handler)
        flow = File(name="flow.md")
        flow.message = text
        await self._pipeline.run()


if __name__ == "__main__":
    task_list = [""]
    from modules.utils import root_manager

    workflow = Workflow(task_list[0])
    asyncio.run(workflow.run())

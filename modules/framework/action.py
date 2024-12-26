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

import sys
import asyncio
import traceback

from tenacity import retry, stop_after_attempt, wait_random_exponential

from modules.file import logger
from modules.framework.code import FunctionTree
from modules.framework.code_error import CodeError
from modules.framework.context import WorkflowContext
from modules.framework.constraint import ConstraintPool
from modules.framework.node_renderer import *
from modules.llm import GPT
from modules.prompt import Prompt
from modules.utils import setup_logger, LoggerLevel, root_manager


class BaseNode(ABC):
    def __init__(self):
        self._logger = setup_logger(self.__class__.__name__, LoggerLevel.DEBUG)
        self.__next = None  # next constraints
        self._renderer = None

    def __str__(self):
        return self.__class__.__name__

    @property
    def _next(self):
        # _ means this is protected property
        return self.__next

    @_next.setter
    def _next(self, value):
        # if not isinstance(value, BaseNode):
        #     raise ValueError("Value must be a BaseNode")
        self.__next = value

    @abstractmethod
    async def run(self, auto_next: bool = True) -> str:
        # Abstract method for executing constraints logic
        pass

    def set_renderer(self, renderer):
        self._renderer = renderer
        renderer.set_node(self)

    def flow_content(self, visited):
        return self._renderer.flow_content(visited)

    def graph_struct(self, level):
        return self._renderer.graph_struct(level)


class ActionNode(BaseNode):
    def __init__(self, next_text: str = "", node_name: str = "", llm: GPT = None):
        super().__init__()
        self.__llm = llm if llm else GPT()
        self.prompt = None
        self.resp_template = None
        self._next_text = next_text  # label text rendered in mermaid graph
        self._node_name = node_name  # to distinguish objects of same class type
        self.error_handler = None  # this is a chain of handlers, see handler.py
        self.set_renderer(ActionNodeRenderer())
        self.context: WorkflowContext = WorkflowContext()
        self._logging_text = "Thinking"

    def __str__(self):
        if self._node_name:
            return self._node_name
        else:
            # return class name when node_name is not defined
            return super(ActionNode, ActionNode).__str__(self)

    def _build_prompt(self):
        pass

    def _display(self):
        pass

    def set_logging_text(self, text):
        self._logging_text = text

    async def run(self, auto_next: bool = True) -> str:
        # First create a prompt, then utilize it to query the language model.
        self.prompt = Prompt().get_prompt(
            action=self.__class__.__name__, scope=self.context.scoop
        )
        self._build_prompt()
        logger.log(f"Action: {str(self)}", "info")
        res = await self._run()
        self._display()
        self.context.save_to_file(file_path=root_manager.workspace_root / f"{self}.pkl")
        if isinstance(res, CodeError):
            # If response is CodeError, handle it and move to next action
            #
            if self.error_handler:
                next_action = self.error_handler.handle(res)
                return await next_action.run()
            else:
                logger.log(f"No error handler available to handle request", "warning")
                # raise ValueError("No error handler available to handle request")
        if auto_next and self._next is not None:
            return await self._next.run()

    @retry(
        stop=stop_after_attempt(5), wait=wait_random_exponential(multiplier=1, max=10)
    )
    async def _run(self) -> str:
        async def loading_animation():
            num_dots = 1
            while True:
                # 输出点点动画
                sys.stdout.write(
                    f"\r\033[32m{self._logging_text}" + "." * num_dots + "\033[0m"
                )
                sys.stdout.flush()
                num_dots = (num_dots + 1) % 8  # 点的数量在 0 到 3 之间循环
                await asyncio.sleep(0.5)  # 控制动画速度

        animation_task = asyncio.create_task(loading_animation())

        try:
            if self.prompt is None:
                raise SystemExit("Prompt is required")
            # print('action node prompt:')
            code = await self.__llm.ask(self.prompt)

            print_to_terminal = True
            if hasattr(self.context.args, "print_to_terminal"):
                print_to_terminal = self.context.args.print_to_terminal
            logger.log(
                f"Prompt:\n {self.prompt}", "debug", print_to_terminal=print_to_terminal
            )
            logger.log(
                f"Response:\n {code}", "info", print_to_terminal=print_to_terminal
            )
            code = await self._process_response(code)
            return code
        except Exception as e:
            tb = traceback.format_exc()
            logger.log(f"Error in {str(self)}: {e},\n {tb}", "error")
            raise Exception
        finally:
            animation_task.cancel()
            try:
                await animation_task  # 等待动画任务取消完成
            except asyncio.CancelledError:
                pass
            sys.stdout.write("\r" + " " * 80 + "\r")  # 覆盖 "Thinking" 并清空行
            sys.stdout.flush()

    async def _process_response(self, content: str) -> str:
        return content


class AsyncNode(ActionNode):
    def __init__(
            self,
            skill_tree: FunctionTree,
            run_mode="layer",
            start_state=None,
            end_state=None,
    ):
        super().__init__("")
        self._run_mode = run_mode
        self._start_state = start_state
        self._end_state = end_state
        self.skill_tree = skill_tree
        self.constraint_pool = ConstraintPool()

    def _build_prompt(self):
        pass

    async def operate(self, function):
        raise NotImplementedError("Subclasses should implement this method")

    async def _run(self):
        if self._run_mode == "layer":
            await self._run_layer_mode()
        elif self._run_mode == "sequential":
            await self._run_sequential_mode()
            for function in self.skill_tree.nodes:
                function.state = self._end_state
        elif self._run_mode == "parallel":
            await self._run_parallel_mode()
            for function in self.skill_tree.nodes:
                function.state = self._end_state
        else:
            logger.log("Unknown generate_mode", "error")
            raise SystemExit

    async def _run_layer_mode(self):
        layer_index = self.skill_tree.get_min_layer_index_by_state(self._start_state)
        if layer_index == -1:
            logger.log(f"No functions in {self._start_state} state", "error")
            raise SystemExit

        if not all(
                function_node.state == self._start_state
                for function_node in self.skill_tree.layers[layer_index].functions
        ):
            logger.log(
                "All functions in the layer are not in NOT_STARTED state", "error"
            )
            raise SystemExit

        await self.skill_tree.process_function_layer(
            self.operate, self._end_state, layer_index
        )

    async def _run_sequential_mode(self):
        for function in self.skill_tree.nodes:
            if function.state == self._start_state:
                await self.operate(function)

    async def _run_parallel_mode(self):
        tasks = []
        for function in self.skill_tree.nodes:
            if function.state == self._start_state:
                tasks.append(self.operate(function))
        await asyncio.gather(*tasks)


class ActionLinkedList(BaseNode):
    def __init__(self, name: str, head: BaseNode):
        super().__init__()
        self.head = head  # property is used
        self._name = name  # name of the structure
        self.set_renderer(ActionLinkedListRenderer())

    def __str__(self):
        if self._head:
            return str(self._head)

    @property
    def head(self):
        return self._head

    @head.setter
    def head(self, value):
        if isinstance(value, BaseNode):
            self._head = value
            self._tail = value
        else:
            raise TypeError("head must be a BaseNode")

    @property
    def _next(self):
        return self._tail._next

    @_next.setter
    def _next(self, value):
        self._tail._next = value

    def add(self, action: "BaseNode"):
        if isinstance(action, BaseNode):
            self._tail._next = action
            self._tail = action
        else:
            raise ValueError("Value must be a BaseNode")

    async def run(self, **kwargs):
        return await self._head.run()

    async def run_internal_actions(self, start_node=None):
        current_node = self._head if start_node is None else start_node
        while current_node:
            await current_node.run(auto_next=False)
            current_node = current_node._next


if __name__ == "__main__":
    pass

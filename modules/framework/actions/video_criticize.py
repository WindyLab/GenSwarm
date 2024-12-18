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
import os.path

from click import prompt
from numpy.version import full_version

from modules.file import logger
from modules.framework.action import ActionNode
from modules.framework.code import FunctionTree
from modules.framework.code_error import Feedback
from modules.framework.constraint import ConstraintPool
from modules.framework.parser import parse_text
from modules.llm import GPT
from modules.utils import (
    root_manager,
    process_video,
    create_video_from_frames,
    save_dict_to_json, rich_print,
)
from modules.prompt import (
    VIDEO_PROMPT_TEMPLATE,
    OUTPUT_TEMPLATE,
    TASK_DES,
)


class VideoCriticize(ActionNode):
    def __init__(
            self,
            skill_tree,
            next_text: str = "",
            node_name: str = "",
    ):
        self.result_dict = None
        self.__llm = GPT(memorize=True, model="VLM")

        super().__init__(next_text, node_name, self.__llm)
        self._frames: list
        self._skill_tree = skill_tree
        self._constraint_pool = ConstraintPool()
        self.set_logging_text(f"Providing feedback on the simulation video")

    def _display(self):
        rich_print(title='Feedback', content=self.result_dict["feedback"])

    def _build_prompt(self):
        self.setup()

        self.prompt = [
            {
                "type": "text",
                "text": VIDEO_PROMPT_TEMPLATE.format(
                    task_des=TASK_DES,
                    instruction=self.context.command,
                    command=self.context.command,
                    feedback="/n".join(self.context.feedbacks),
                    constraint=str(self._constraint_pool),
                    out_put=OUTPUT_TEMPLATE,
                ),
            },
            *map(
                lambda x: {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpg;base64,{x}", "detail": "low"},
                },
                self._frames,
            ),
        ]
        pass

    def setup(self):
        from modules.utils import root_manager, process_video, create_video_from_frames

        self.context.vlm = True
        wo_vlm_path = f"{root_manager.workspace_root}/wo_vlm.mp4"
        debug_path = f"{root_manager.workspace_root}/debug.mp4"
        full_version_path = f"{root_manager.workspace_root}/full_version.mp4"
        # 判断是否有wo_vlm.mp4，debug.mp4 两个文件
        if os.path.exists(debug_path):
            video_path = debug_path
        elif os.path.exists(wo_vlm_path):
            video_path = wo_vlm_path
        elif os.path.exists(full_version_path):
            video_path = full_version_path
        else:
            video_path = None
        self.result_dict = {"video_path": video_path, "success": None, "feedback": None}
        if video_path is None:
            save_dict_to_json(
                self.result_dict, f"{root_manager.workspace_root}/vlm.json"
            )
            logger.log("No video file found", "error")
            raise SystemExit("No video file found")

        self._frames = process_video(video_path, start_time=0, seconds_per_frame=1)
        create_video_from_frames(
            self._frames, output_path=f"{root_manager.data_root}/extra.mp4", fps=1
        )

    async def _process_response(self, response: str) -> str | Feedback:
        try:
            response = parse_text(text=response, lang="json")
            result = eval(response)
            self.result_dict["feedback"] = result["feedback"]

            # Process success case
            if result["result"].strip().lower() == "success":
                self.result_dict["success"] = True
                if self.context.args.human_feedback == "True":
                    if_feedback = input("If task is done? Press y/n: ")
                    if if_feedback.lower() == "y":
                        logger.log("run code: success", "warning")
                        return "NONE"
                    else:
                        if self.context.args.feedback == "None":
                            logger.log("run code: fail", "warning")
                            return "NONE"
                        feedback = input("Please provide feedback: ")
                        self.context.feedbacks.append(feedback)
                        return Feedback(feedback)
                else:
                    return result["feedback"]

            # Process fail case
            elif result["result"].strip().lower() == "fail":
                self.result_dict["success"] = False
                return Feedback(result["feedback"])

            # Invalid result case
            else:
                logger.log(f"Invalid result: {result}", "error")
                raise Exception("Invalid result")

        except Exception as e:
            logger.log(f"Exception occurred: {e}", "error")
            raise  # Re-raise the exception after logging

        finally:
            save_dict_to_json(
                self.result_dict, f"{root_manager.workspace_root}/vlm.json"
            )

    # async def _run(self) -> str:
    #     sim = """```json
    #     {
    #     "result": "SUCCESS",
    #     "feedback": "..."
    #     }```
    #     """
    #     res = await self._process_response(response=sim)
    #     return res


if __name__ == "__main__":
    import asyncio

    path = "../../../workspace/encircling/2024-10-21_03-18-15"
    root_manager.update_root(path)
    function_analyser = VideoCriticize("analyze constraints")

    function_analyser.context.load_from_file(f"{path}/RunCodeAsync.pkl")
    asyncio.run(function_analyser.run())
    function_analyser.context.save_to_file(f"{path}/analyze_functions.pkl")

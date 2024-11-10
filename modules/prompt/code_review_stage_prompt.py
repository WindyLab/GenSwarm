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

LOCAL_CODE_REVIEW_PROMPT_TEMPLATE: str = """
## Background:
{task_des}

## Role setting:
- You are a critic, You should now check if there are any bugs in the functions written by other agents or if there have been any incorrect calls.

## These are the User original instructions:
{instruction}

## These are the basic Robot APIs:
These APIs can be directly called by you.
```python
{robot_api}
```

## These are the environment description:
These are the basic descriptions of the environment.
{env_des}

## These are the existing functions that you can directly call:
```python
{other_functions}
```

## These are the functions that need to be checked:
```python
{function_content}
```



## The output TEXT format is as follows:
Reasoning: think step by step, whether the to be checked function has any bugs or incorrect calls.In the reasoning section, you can directly write the code without using ```python```.

Modified function:
```python
import ... (import the necessary modules,if any)
def {function_name}(...):
    # put the modified function body here,please output the complete and correct function, and only modify the parts that are incorrect.
```

## Notes:
Your output should satisfy the following notes:
- Carefully check if there are any bugs or logical inconsistencies in this function.
- Ensure the call to each sub-function is correct.
- Check that all defined variables are used.
- Strictly adhere to the specified format.
- In the Reasoning section, '''python''' is not allowed. You can only use '''python''' in the Modified function section. In the Reasoning section, code should be written directly.
- The modified function section should only appear when the function has bugs or incorrect calls. If the function is correct, this section should not appear.
- If the function needs to be rewritten, ensure that the rewritten function name is {function_name}.
- If you need to rewrite the function, output the complete and correct function, only modifying the incorrect parts.
- Carefully consider and ensure that your revised version is correct.
- Ensure that the velocities of different task objectives are completely superposed in the function without omission.
- If there is an error in the function, provide the erroneous line of code in the Reasoning section, along with suggestions for correction.
- If the function outputs velocity, the velocity must be normalized.
- The current task does not necessarily require a global allocator. If needed, use the corresponding API to obtain the assigned task. If there is no such API, the task does not require a global allocator.
- When using the API to obtain the task assigned to the robot, it only needs to be called once. Repeated calls are unnecessary, as the allocation is based on the robot's initial state and occurs only once at the beginning.
- Preserve the function's docstring, with the option to modify its content.
- The current task does not necessarily require a global allocator. If needed, use the corresponding API to obtain the assigned task. If there is no such API, the task does not require a global allocator.
- Strictly adhere to the specified format.
""".strip()

GLOBAL_CODE_REVIEW_PROMPT_TEMPLATE: str = """
## Background:
{task_des}
## Role setting:
- You are a critic, You should now check if there are any bugs in the functions written by other agents or if there have been any incorrect calls.


## These are the User original instructions:
{instruction}

## These are the basic Robot APIs:
These APIs can be directly called by you.
```python
{robot_api}
```

## These are the environment description:
These are the basic descriptions of the environment.
{env_des}

## These are the existing functions that you can directly call:
```python
{other_functions}
```

## These are the functions that need to be checked:
```python
{function_content}
```


## The output TEXT format is as follows:

Reasoning: think step by step, whether the to be checked function has any bugs or incorrect calls.In the reasoning section, you can directly write the code without using ```python```.

Modified function:
```python
import ... (import the necessary modules,if any)
def {function_name}(...):
    # put the modified function body here,please output the complete and correct function, and only modify the parts that are incorrect.
```

## Notes:
- Carefully check if there are any bugs in this function, or if there are any logical inconsistencies.
- Check if the call to each sub-function is correct.
- Check that all defined variables are used.
- Strictly adhere to the specified format.
- During the Reasoning section, '''python''' is not allowed. You can only use '''python''' in the Modified function section. You can directly write the code in the Reasoning section.
- The modified function section should be filled in only when the function has bugs or incorrect calls. Otherwise, this section should not appear.
- If the function needs to be rewritten, please ensure that the rewritten function name is {function_name}.
- If you need to rewrite a function, please output the complete and correct function, and only modify the parts that are incorrect.
- You should carefully consider and ensure that your revised version is correct.
- If there is an error in this function, please provide the erroneous line of code in the "reasoning" section, along with suggestions for how it could be corrected.
- If the function outputs velocity, then this velocity must be normalized.
- The current task does not necessarily require a global allocator. If needed, please use the corresponding API to obtain the assigned task. If there is no corresponding API, then the current task does not require a global allocator.
- When using the API to obtain the task assigned to the current robot, it only needs to be called once. Repeated calls will not be useful, as the allocation is done only once at the beginning based on the robot's initial state.
- Preserve the function's docstring, with the option to modify its content.
- The task allocation can include various types such as positions, lists of positions, or specific angles, based on the requirements of the task.
- The allocation method for robots should ensure that the total movement distance for each robot is minimized while completing all tasks, and that no task conflicts occur (i.e., each robot is assigned a distinct task, with no overlap between tasks).
- Strictly adhere to the specified format.
""".strip()

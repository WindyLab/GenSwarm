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

DESIGN_LOCAL_FUNCTION_PROMPT_TEMPLATE = """
## Background:
{task_des}
## Role setting:
- Your task is to refine the designed function {function_name} based on the existing descriptions while keeping the function name unchanged.

## These are the environment description:
{env_des}

## These are the User original instructions:
{instruction}

## Existing robot APIs:
```python
{robot_api}
```

## These are the existing functions' descriptions and names:
{other_functions}


## The output TEXT format is as follows:
### Reasoning: (reason step by step about how to design this function)
### Code:
```python
def {function_name}(input1, input2, ...):
    '''
    Description:Refine this description '{function_des}' in detail to guide the generation of the function and put it at here.

    params:
        input1: type, description
        input2: type, description
        ...
    return:
        type, description
    '''
    pass
```

## Notes:
- You need to enhance the existing function descriptions by adding more details.
- Ensure the function name is {function_name}, and set the number of input and output variables as needed.
- All parameters required for the algorithm should be set as input variables with default values.
- The function body content does not need to be provided; simply giving a `pass` is sufficient.
- Take a holistic approach and reuse existing functions as much as possible.
- The current task does not necessarily require a global allocator. If needed, please use the corresponding API to obtain the assigned task. If there is no corresponding API, then the current task does not require a global allocator.
""".strip()

DESIGN_GLOBAL_FUNCTION_PROMPT_TEMPLATE = """
## Background:
{task_des}

## Role setting:
- Your task is to refine the designed function {function_name} based on the existing descriptions while keeping the function name unchanged.

## These are the environment description:
{env_des}

## These are the User original instructions:
{instruction}

## Existing APIs:
```python
{robot_api}
```

## These are the existing functions' descriptions and names:
{other_functions}


## The output TEXT format is as follows:
### Reasoning: (reason step by step about how to design this function)
### Code:
```python
def {function_name}(input1, input2, ...):
    '''
    Description:Refine this description '{function_des}' in detail to guide the generation of the function and put it at here.

    params:
        input1: type, description
        input2: type, description
        ...
    return:
        type, description
    '''
    pass
```

## Notes:
- You need to enhance the existing function descriptions by adding more details.
- Ensure the function name is {function_name}, and set the number of input and output variables as needed.
- All parameters required for the algorithm should be set as input variables with default values.
- The function body content does not need to be provided; simply giving a `pass` is sufficient.
- Take a holistic approach and reuse existing functions as much as possible.
- The allocation method for robots should be optimal, ensuring no conflicts occur between them.
- Task allocation will only occur once at the beginning of the task, so the tasks assigned to each robot should take environmental changes into account and avoid relying on any single changing object.
- The allocation method for robots should ensure that the total movement distance for each robot is minimized while completing all tasks, and that no task conflicts occur (i.e., each robot is assigned a distinct task, with no overlap between tasks).
- The task allocation can include various types such as positions, lists of positions, or specific angles, based on the requirements of the task.
""".strip()

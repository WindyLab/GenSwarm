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

WRITE_GLOBAL_FUNCTION_PROMPT_TEMPLATE = """
## Background:
{task_des}
## Role setting:
- Your task is to complete this predefined function according to the description.

## These are the environment description:
These are the basic descriptions of the environment.
{env_des}

## These are the User original instructions:
{instruction}


## These are GLOBAL APIs:
```python
{robot_api}
```

## These are the functions you can call directly even if they are not implemented now:
```python
{other_functions}
```




## Task
Complete the following function. The output TEXT format is as follows:
### Reasoning: (reason step by step about how to implement this function.)
### Code:
```python
import ...(if necessary)
{function_content}
    ...(function body,you need to complete it)
```
## Notes:
- The global API and existing functions can be called directly without the need for imports.
- Generate bug-free, directly invocable function code according to Google's coding standards.
- Adjustable parameters should be taken as input parameters with default values set for each parameter.
- You can only write functions according to the task's specified format, and cannot generate other helper functions. If necessary, define sub-functions within the specified function.
- Take a holistic approach and reuse **existing functions as much as possible**; this function is just a part of the entire control system.
- Avoid using global variables, and do not use variable names that conflict with global variables within the function.
- Preserve the function's docstring but modify its content if necessary, ensuring the function name remains unchanged.
- Do not use while loops in the function body.
- Do not raising errors or using assertions in the function body.
- Do not assume any part of the code,because the code will be executed directly without any modification and human intervention.
- If the function definition or docstring needs modification, ensure the function name stays the same.
- Import required modules before the function name, not within the function body.
- The robot allocation method should be optimal, avoiding conflicts between robots.
- Task allocation will only occur once at the start of the task. The tasks assigned to each robot should take environmental changes into account and avoid relying on any single changing object.
- The allocation method for robots should ensure that the total movement distance for each robot is minimized while completing all tasks, and that no task conflicts occur (i.e., each robot is assigned a distinct task, with no overlap between tasks).
- The task allocation can include various types such as positions, lists of positions, or specific angles, based on the requirements of the task.
- Strictly follow the specified format.
""".strip()

WRITE_LOCAL_FUNCTION_PROMPT_TEMPLATE = """
## Background:
{task_des}
## Role setting:
- Your task is to complete this predefined function according to the description.

## These are the environment description:
These are the basic descriptions of the environment.
{env_des}

## These are the User original instructions:
{instruction}


## These are the basic Robot APIs:
```python
{robot_api}
```

## These are the functions you can call directly even if they are not implemented now:
```python
{other_functions}
```

## Task
Complete the following function. The output TEXT format is as follows:
### Reasoning: (reason step by step about how to implement this function.)
### Code:
```python
import ...(if necessary)
{function_content}
    ...(function body,you need to complete it)
```
## Notes:
- The Robot API and existing functions can be called directly without the need for imports.
- Generate bug-free, directly invocable function code according to Google's coding standards.
- Adjustable parameters should be set as input parameters, with default values for each parameter.
- You can only complete the functions specified in the task according to the specified format; no other helper functions may be generated. If necessary, sub-functions can be defined within the main function.
- Take a holistic approach and reuse **existing functions as much as possible**; the function is just one part of the entire control system.
- Avoid using global variables and do not use the same variable names as global variables within the function.
- Preserve the function's docstring but modify its content if necessary. Ensure the function name remains unchanged.
- If the function definition or docstring needs to be modified, ensure the function name stays the same.
- Import required modules before the function name, not within the function body.
- If the function outputs velocity, the velocity must be normalized.
- Do not raising errors or using assertions in the function body.
- Do not assume any part of the code,because the code will be executed directly without any modification and human intervention.
- The current task does not necessarily require a global allocator. If needed, use the appropriate API to obtain the assigned task. If no such API exists, the task does not require a global allocator.
""".strip()

WRITE_GLOBAL_RUN_PROMPT_TEMPLATE = """
## Background:
{task_des}

## Role setting:
You need to write an interface function that calls the existing global function to assign appropriate strategies to each robot.
## These are the environment description:
These are the basic descriptions of the environment.
{env_des}

## These are the User original instructions:
{instruction}


## These are the basic global APIs:
```python
{robot_api}
```

## These are the functions generated by other assistants,you can call them directly:
```python
{functions}
```

## Task
Complete the following function. The output TEXT format is as follows:
### Reasoning: (reason step by step about how to implement this function.)
### Code:
```python
import ...(if necessary)
def allocate_run():
    '''
    Description:...

    params:
        None
    return:
        dict: A dictionary containing the robot id and the policy assigned to it.
         - key: int, the robot id.
         - value: any data type, e.g. tuple, list,float etc., decided by the task type.
    '''
    ...(function body,you need to complete it)
```
### Return format:
```json
{template}
```

## Notes:
- The API and existing functions can be called directly without the need imports.
- You need to generate bug-free, directly invocable function code according to Google's coding standards.
- You can only complete the functions specified in Task according to the specified format; you cannot generate other Helper functions. If necessary, you can define functions within this function.
- You can only call these existing functions and global Api, and you cannot define complex logic on your own,just call the existing functions.
- Import the required modules before the function name, and do not import them in the function body.
- Use the existing high-level functions.
- Do not use while loops
- Do not raising errors or using assertions in the function body.
- Do not assume any part of the code,because the code will be executed directly without any modification and human intervention.
- The allocation method for robots should ensure that the total movement distance for each robot is minimized while completing all tasks, and that no task conflicts occur (i.e., each robot is assigned a distinct task, with no overlap between tasks).
- Task allocation will only occur once at the beginning of the task, so the tasks assigned to each robot should take environmental changes into account and avoid relying on any single changing object.
- The task allocation can include various types such as positions, lists of positions, or specific angles, based on the requirements of the task.
- You should populate the output format based on the code you've written, as this output format will impact the code development for the Robots.
- Ensure that this function can be executed to completion and is able to return the expected output.
- Strictly follow the specified format.
"""

GLOBAL_RUN_OUTPUT_TEMPLATE = """
{
    "key":
        {
            "type":"int",
            "description":"the robot id."
        },
    "value":
        {
            "type":"any data type e.g. tuple[float,float],dict[str,tuple[float,float]]], list[tuple[float,float]],float, etc., decided by the task type.",
            "description":"the task assigned to the robot."
        }
}
"""

WRITE_LOCAL_RUN_PROMPT_TEMPLATE = """
## Background:
{task_des}
## Role setting:
- Your task is to create an interface function for users to call, based on existing functions written by other assistants. Users only need to call this function to complete the predetermined task.

## These are the environment description:
These are the basic descriptions of the environment.
{env_des}

## These are the User original instructions:
{instruction}

## These are the basic Robot APIs:
```python
{robot_api}
```

## These are the functions generated by other assistants,you can call them directly:
```python
{functions}
```

## Task
Complete the following function. The output TEXT format is as follows:
### Reasoning: (reason step by step about how to implement this function.)
### Code:
```python
import ...(if necessary)
def run_loop():
    '''
    Description: An interface function for users to call, based on existing functions written by other assistants. Users only need to call this function to complete the predetermined task.

    params:
        None
    return:
        None
    '''
    ...(function body,you need to complete it)
```

## Notes:
- The Robot API and existing functions can be called directly without the need for imports.
- Generate bug-free, directly invocable function code according to Google's coding standards.
- You can only complete the functions specified in the task according to the specified format; no other helper functions may be generated. If necessary, sub-functions can be defined within the main function.
- You can only call existing functions and RobotApi, and cannot define complex logic on your own.
- Import required modules before the function name, not within the function body.
- Use a while loop to wait for the task to complete.
- Determine whether a break is needed based on the specific task. If the current task is continuous, a break is not allowed.
- You need to ensure that the entire system can update observation data in real-time and issue control speeds in real-time based on the observation data. If it is not implemented in other functions, you need to achieve this through a While loop.
- Use existing high-level functions.
- Do not raising errors or using assertions in the function body.
- Do not assume any part of the code,because the code will be executed directly without any modification and human intervention.
- Strictly follow the specified format.
- Use time.sleep to limit the loop frequency, and robot control should be executed at a frequency of 100Hz.
""".strip()

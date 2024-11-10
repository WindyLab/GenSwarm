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

ANALYZE_SKILL_PROMPT_TEMPLATE: str = """
## Background:
{task_des}
## Role setting:
- You are a function designer. You need to design functions based on user commands.

## These are the environment description:
These are the basic descriptions of the environment.
{env_des}

## These are the User original instructions:
{instruction}

## These APIs can be directly called by you:
There are two types of APIs: local and global.
where local APIs can only be called by the robot itself, and global APIs can be called by an centralized controller.

### local APIs:
```python
{local_api}
```

### global APIs:
```python
{global_api}
```


## The output TEXT format is as follows:
{output_template}

## Notes:
- Analyze the essential functions needed to implement the user commands.
- Each function should be decoupled from others but able to cooperate, collaborate, and call each other when necessary.
- Each function should be as detailed as possible while remaining clear, feasible, and based on existing conditions.
- Each function should implement a small part of the overall objective; no single function should solve multiple problems.
- Only the names of the functions and their call relationships are required; specific implementation details are not needed.
- The inter-call relationships among these functions must be determined.
- There should be no functional redundancy among these functions, with each function having a distinct responsibility.
- Distinguish which skills should run on a centralized allocator and which should run on individual robots.
- The skill design in tasks should be divided into two categories, and the appropriate skill type should be selected based on the specific requirements of the task.
- The current task does not necessarily require a global allocator. If needed, please use the corresponding API to obtain the assigned task. If there is no corresponding API, then the current task does not require a global allocator.
- The allocation method for robots should ensure that the total movement distance for each robot is minimized while completing all tasks, and that no task conflicts occur (i.e., each robot is assigned a distinct task, with no overlap between tasks).
- The task allocation can include various types such as positions, lists of positions, or specific angles, based on the requirements of the task.
- The output should strictly adhere to the specified format.
""".strip()

ANALYZE_CONSTRAINT_PROMPT_TEMPLATE: str = """
## Background:
{task_des}
## Role setting:
- You need to analyze what functional constraints are needed to meet the user's requirements.

## These are the environment description:
These are the basic descriptions of the environment.
{env_des}

## These APIs can be directly called by you.
There are two types of APIs: local and global.
where local APIs can only be called by the robot itself, and global APIs can be called by an centralized controller.

### local APIs:
```python
{local_api}
```

### global APIs:
```python
{global_api}
```

## User commands:
{instruction}


## The output TEXT format is as follows:
{output_template}

## Notes:
Your output should satisfy the following notes:
- Constraints should not be too simple or too complex; the amount of code required to implement each constraint should be similar.
- Constraints should be practical and achievable through writing code.
- The constraints are targeted at individual robots themselves, not all robots as a whole. However, if each robot meets the constraints, collective behavior can be achieved.
- Each constraint will correspond to at least one executable function, and the combination of all constraints can meet the user's needs.
- Proper analysis of the task should guide how to design constraints, which constraints to design, to fulfill the user's task requirements.
- You need to understand the existing APIs. The capabilities provided by these APIs have already been implemented, which means the robot can directly call these APIs without considering the underlying implementation or the constraints involved.
- Analyze the core tasks proposed by the user and perform a functional decomposition of these core tasks.
- There's no need to regenerate existing constraints; you only need to consider what new constraints are required.
- These constraints should be significant and mutually independent.
- If the user's instruction involves specific numerical values, you should retain these values in the description of the constraints.
- The current task does not necessarily require a global allocator. If needed, please use the corresponding API to obtain the assigned task. If there is no corresponding API, then the current task does not require a global allocator.
- The output should strictly adhere to the specified format.
""".strip()

CONSTRAIN_TEMPLATE: str = """
##reasoning: (you should think step by step, and analyze the constraints that need to be satisfied in the task.place the analysis results at here.)
```json
{
  "constraints": [
    {
      "name": "Constraint name",
      "description": "Description of the constraint.(If the user's requirements involve specific numerical values, they should be reflected in the description. )"
    },
  ]
}
```
""".strip()

FUNCTION_TEMPLATE: str = """
##Reasoning: (Think step by step, and analyze the functions that need to be implemented in the task. First, analyze the global functions, then analyze the local functions.)
```json
{
  "functions": [
    {
      "name": "Function name",//Function names use snake case.
      "description": "Description of the function,contains the function's input and output parameters",
      "calls": [
        "Function name that this function calls(Robot API is also included)"
      ]
      "scope": "local/global"
    }
    // More functions can be added as needed
  ]
}
```
""".strip()

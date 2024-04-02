ANALYZE_FUNCTION_PROMPT_TEMPLATE: str = """
## Background:
{task_des}
## Role setting:
- You are a function designer. You need to design functions based on user commands and constraint information.
- Your output will guide the generation of control code for the robots. Therefore, the functions you generate should be accurate and feasible, and based on existing conditions.
## These are the basic Robot APIs:
These APIs can be directly called by you.
```python
{robot_api}
```

## Constraints information:
The following are the constraints that the generated functions need to satisfy.
{constraints}
## User commands:
{instruction}
## The output TEXT format is as follows:
```json
{output_template}
```
## Notes:
Your output should satisfy the following notes:
- Analyze what essential functions are needed to implement the user commands.
- Each function should be decoupled from others and closely cooperate, collaborate, and even call each other.
- Each function should be as detailed as possible while also being clear, feasible, and based on existing conditions.
- Each function only needs to implement a small functionality under the overall objective, and one function should not solve multiple problems.
- You need to consider which constraints each function should satisfy or, in other words, implement.
- One function can satisfy multiple constraints, and several functions can also implement a single constraint.
- You only need to provide the names of the functions and their constraint and call relationships. The specific implementation of the functions is not required.
- You need to determine the inter-call relationships among these functions.
- These functions must not have functional redundancy among them, with each function bearing distinct responsibilities.
- You only need to analyze the constraints that the current function itself must meet; the constraints of the functions it calls are beyond the consideration of the current function.
- Each constraint in the Constraints information should be satisfied by one of the functions generated in your function list, without any omissions.
- If the function outputs velocity, then this velocity must be normalized.
- The output should strictly adhere to the specified format.

""".strip()

CLASS_DIAGRAM_PROMPT_TEMPLATE: str = """
## Background:
{task_des}
## Role setting:
- You are a class diagram designer, and your task is to design a class diagram based on the constraint information. 

## These are the basic Robot APIs:
These APIs can be directly called by you.
```python
{robot_api}
```
## These are the environment description:
These are the basic descriptions of the environment.
{env_des}
## Constraints information:
The following are the constraints that the generated functions need to satisfy.
{constraints}
## User commands:
{instruction}
## The output TEXT format is as follows:
```mermaid
... // class diagram code
```
## Notes:
Your output should satisfy the following notes:
- Analyze what essential functions are needed to implement the user commands.
- Each deterministic constraint is defined as a class parameter with its value specified.
- Functional constraint is defined as a method of the class, specifying its input and output parameter names as well as their data structures.
- 
- The output should strictly adhere to the specified format.
""".strip()

ANALYZE_CONSTRAINT_PROMPT_TEMPLATE: str = """
## Background:
{task_des}
## Role setting:
- You need to analyze what functional constraints are needed to meet the user's requirements.

## These APIs can be directly called by you.
```python
{robot_api}
```
## User commands:
{instruction}

## These are the environment description:
These are the basic descriptions of the environment.
{env_des}

## These are the constraints that user defined:
{user_constraints}

## The output TEXT format is as follows:
```json
{output_template}
```

## Constraints:
Your output should satisfy the following constraints:
- Constraints should not be too simple or too complex; the amount of code required to implement each constraint should be similar.
- Constraints should be practical and achievable through writing code.
- Each constraint will correspond to at least one executable function, and the combination of all constraints can meet the user's needs.
- Proper analysis of the task should guide how to design constraints, which constraints to design, to fulfill the user's task requirements.
- You need to understand the existing APIs. The capabilities provided by these APIs have already been implemented, which means the robot can directly call these APIs without considering the underlying implementation or the constraints involved.
- Analyze the core tasks proposed by the user and perform a functional decomposition of these core tasks.
- There's no need to regenerate existing constraints; you only need to consider what new constraints are required.
- These constraints should be significant and mutually independent.
- If the user's instruction involves specific numerical values, you should retain these values in the description of the constraints.
- The output should strictly adhere to the specified format.

""".strip()

CONSTRAIN_TEMPLATE: str = """
{
  "reasoning": "think step by step, and analyze the constraints that need to be satisfied in the task.",
  "constraints": [
    {
      "name": "Constraint name",
      "description": "Description of the constraint.(If the user's requirements involve specific numerical values, they should be reflected in the description. )"
    },
  ]
}
""".strip()

FUNCTION_TEMPLATE: str = """
{
  "reasoning": "think step by step, and analyze the functions that need to be implemented in the task."
  "functions": [
    {
      "name": "Function name",
      "description": "Description of the function,contains the function's input and output parameters",
      "constraints": [
        "Name of the constraint that this function needs to satisfy"
        // More constraints can be added as needed
      ]
      "calls": [
        "Function name that this function calls(Robot API is also included)"
      ]
    }
    // More functions can be added as needed
  ]
}
""".strip()

PARAMETER_PROMPT_TEMPLATE: str = """
## Background:
{task_des}
## Role setting:
- You need to analyze which global parameters are required throughout the code to ensure the consistency of the overall strategy.

## These are the environment description:
{env_des}

## Functions:
{function_des}

## The output TEXT format is as follows
1. Reasoning: Infer all parameters that might be used throughout the entire task process, with as much detail as possible.
2. Parameters: ```python\n parameter_name: parameter_type = default_value\n...```

## Constraints:
Your output should satisfy the following constraints:
- You should further clarify which parameters the entire code will use based on the demand analysis and constraint analysis.
- Consider what parameters may be needed for each function.
- For each function, careful analysis is needed to determine which functions it requires or may potentially require.
- Analyze numerical parameters.
- Consider the parameters that need to be taken into account when using these functions to fulfill user requirements.
- Strictly follow the specified format.
"""

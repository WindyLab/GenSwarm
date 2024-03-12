WRITE_FUNCTION_PROMPT_TEMPLATE = """
## These are the environment description: 
{env_des}

## These are the basic Robot APIs:
```python
{robot_api}
```

## These are existing functions:
```python
{other_functions}
```

## Constraints: 
The functions you generate need to comply with the following constraints.
1. Above functions are in the same py file as yours and can be invoked directly using their function names.
2. Write complete code, your code will not be modified, if you can't write complete code, simplify the function
3. Set default value: If there is any setting, ALWAYS SET A DEFAULT VALUE, ALWAYS USE STRONG TYPE AND EXPLICIT VARIABLE. 
4. Before using a others functions/modules, make sure to import them first.
5. YOU MUST FOLLOW "Data structures and interface definitions". DONT CHANGE ANY DESIGN.
6. You only need to make sure single function has correct input and output. don't need to consider complex conditions.
7. You can only complete this one function; you cannot generate other Helper functions. If necessary, you can define functions within this function.

## Task description:
Please finish the following function, maximizing the reuse of existing functions:
{function}
""".strip()

WRITE_RUN_PROMPT_TEMPLATE = """
## Task description:
You are a robot, you need to translate the sequence diagram into Python code.

## These are the environment description: 
{env_des}

## The list of functions you can call is as follows:
```python
from functions imports *
{robot_api}
{function_list}
```

## This is the Sequence Diagram: 
{sequence_diagram}

## Constrains: 
1. the functions provided are available, you can use them by "from functions import *" 
2. Set default value: If there is any setting, ALWAYS SET A DEFAULT VALUE, ALWAYS USE STRONG TYPE AND EXPLICIT VARIABLE. 
3. Ensure the generated code contains a 'if __name__ == '__main__':' statement and can be executed directly
4. Write complete code, your code will not be modified, and if you can't write complete code, simplify the function.

## The generated result should be in the following fields:
1. explanation: think step by step. How to translate the sequence diagram into Python code.
2. python code: Translate the sequence diagram into corresponding Python code. ```python\n <your response>```

## The output  TEXT format is as follows:
1. explanation: <explanation>
2. python code: <python code>
""".strip()

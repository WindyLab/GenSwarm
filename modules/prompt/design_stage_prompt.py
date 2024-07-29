DesignFunction_PROMPT_TEMPLATE = """
## Background:
{task_des}
## Role setting:
- Your task is to refine the designed function based on the existing descriptions while keeping the function name unchanged.

## Existing robot APIs:
```python
{robot_api}
```

## These are the environment description:
{env_des}

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
- Keep the function names unchanged; the number of input and output variables is set as needed.
- All parameters required for the algorithm should be set as input variables with default values.
- The function does not need to provide the content of the function body; just giving a `pass` is suffice.
- Take a holistic approach and reuse existing functions as much as possible.
- Make sure the function name is {function_name}.
- The output should be in the specified format.
""".strip()

WriteSeqDiagram_PROMPT_TEMPLATE = """
## Task description:
Based on the user requirements document and current functions, you need to design a sequence diagram.

## User requirements:
{analysis}

## These are the environment description:
{env_des}

## These are the basic Robot APIs:
```python
{robot_api}
```

## These are existing functions:
```python
{function_list}
```

## Explanation:
1. The sequence diagram is to call the existing functions to fulfill the user's requirements.
2. The sequence diagram can be directly translated into Python code, which is capable of continuously monitoring the environment and outputting control signals at a certain frequency.
3. The code generated from the sequence diagram should not loop infinitely; it should be able to exit the loop once the task is completed.

## Constraints:
1. You need to use these existing functions to generate a call flow diagram to fulfill the user's requirements.
2. You can't define any new functions.
3. Ensure that the sequence diagram translates directly into executable code that can accomplish the task objectives.

## The generated result should be in the following fields:
1. explanation: think step by step. How do you make the diagram conform to the algorithm?
2. sequence diagram: use Mermaid's sequenceDiagram to write sequence diagram, ```mermaid\nsequenceDiagram\n <your response>```

## The output TEXT format is as follows:
1. explanation: <explanation>
2. sequence diagram: <sequence diagram>
""".strip()

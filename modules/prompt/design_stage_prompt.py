DesignFunction_PROMPT_TEMPLATE = """
In order to assist users in automating specific tasks, you need to design a series of decoupled Python functions based on user functional requirements and constraints.
- These functions should be decoupled from each other. 
- Each function can utilize the existing APIs.
- Each function should have strong reusable and should have well-defined input and output interfaces.
- Each function does not need to provide the content of the function body; just giving a `pass` is suffice.

These are the existing robot APIs, functions should try to reuse them as much as possible and refer to the design of them:
{robot_api}

These are the environment description:
{env_des}

The generated result should be in the following fields:
explanation: think step by step. How do you make the functions conform to the algorithm?
function list: write the function list in the following format, ```python\n<your python code>```
- To avoid complexity, functions only need to provide the function name and docstring; you cannot write out the function body. You only need to design rather than write code.
- Every function should provide a detailed description of its functionality as well as any constraints that may need to be considered.

The output TEXT format is as follows:
explanation: <explanation>
function list: <function list>"

Analysis: {analysis}
""".strip()

WriteSeqDiagram_PROMPT_TEMPLATE = """
Based on the user requirements document and current functions, you need to design a sequence diagram.
These are the environment description:
{env_des}

These are the basic Robot APIs:
{robot_api}

These are existing functions:
{function_list}

Explanation: 
1. The sequence diagram is to call the existing functions to fulfill the user's requirements.
2. The sequence diagram can be directly translated into Python code, which is capable of continuously monitoring the environment and outputting control signals at a certain frequency.
3. The code generated from the sequence diagram should not loop infinitely; it should be able to exit the loop once the task is completed.
constrains: 
1. You need to use these existing functions to generate a call flow diagram to fulfill the user's requirements.
2. You can't define any new functions.
3. Ensure that the sequence diagram translates directly into executable code that can accomplish the task objectives.

The generated result should be in the following fields:
explanation: think step by step. How do you make the diagram conform to the algorithm?
sequence diagram: use Mermaid's sequenceDiagram to write sequence diagram: ```mermaid\nsequenceDiagram\n <your response>```

The output TEXT format is as follows:
explanation: <explanation>
sequence diagram: <sequence diagram>

User requirements: {analysis}
""".strip()

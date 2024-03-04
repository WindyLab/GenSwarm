DesignFunction_PROMPT_TEMPLATE = """
User requirements: {analysis}
In order to assist users in automating specific tasks, you need to design a series of decoupled Python functions based on user functional requirements and constraints.
- These functions should be decoupled from each other. 
- Each function can utilize the existing APIs.
- Each function should have strong reusability and should have a sufficient number of inputs and outputs.
- Each function does not need to provide the content of the function body; just giving a `pass` will suffice.

This is the existing environment API. 
{code}
{env_des}
Functions should try to reuse these APIs as much as possible and refer to the design of these APIs.

Please respond with the following format:
0)explanation: think step by step. How do you make the functions conform to the algorithm?
1)function list: write the function list in the following format, ```python\n<your response>```
Note:
- To avoid complexity, functions only need to provide the function name and docstring; you cannot write out the function body. You only need to design rather than write code.
- Every function should provide a detailed description of its functionality as well as any constraints that may need to be considered.
"""
WriteSeqDiagram_PROMPT_TEMPLATE = """
requirements document: {analysis}
function list: 
{robot_api}
{function_list}
{env_des}
Based on the user requirements document and current functions, you are required to design a sequence diagram.
Explanation: 
1. This sequence diagram is to call these existing functions to fulfill the user's requirements.
2. This sequence diagram can be directly translated into Python code, which is capable of continuously monitoring the environment and outputting control signals at a certain frequency.
3. The code generated from the sequence diagram should not loop infinitely; it should be able to exit the loop once the task is completed.
constrains: 
1. You need to use these existing functions to generate a call flow diagram to fulfill the user's requirements.
2. You can't define any new functions.
3. Ensure that the sequence diagram translates directly into executable code that can accomplish the task objectives.

You should respond to with:
0)explanation: think step by step. How do you make the diagram conform to the algorithm?
1)sequence diagram: use Mermaid's sequenceDiagram to write sequence diagram, ```mermaid\nsequenceDiagram\n <your response>```
You should only respond in the format as described below :
0)explanation:
1)sequence diagram:
"""

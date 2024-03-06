PROMPT_TEMPLATE: str = """
You are a robot with the ability to move and perceive.
You need to understand the user's commands and then analyze these commands. Consider what functions are needed to meet the user's requirements.
{env_des}
user requirements:{instruction}
APIs: {api}
Output the analysis in the following format:

User Requirement Description: Detailed description of the task the user hopes to automate.
Functional Requirements:
List the functions expected to be developed based on user needs and available resources.
For each function, briefly describe its purpose and expected outcome.
These functions should be decoupled from each other.
""".strip()

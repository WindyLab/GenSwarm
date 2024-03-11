ANALYZE_PROMPT_TEMPLATE: str = """
You are a robot with the ability to move and perceive.
These are the basic Robot APIs:
{robot_api}
These are the environment description:
{env_des}

You need to analyze user's command. Consider what functions are needed to meet the user's requirements.

The generated result should be in the following fields:
Keyword: what are the key words in the requirements?
Definition: Professional explanations about the keywords?
User Requirement Description: Detailed description of the task the user hopes to automate.
Functional Requirements: List the functions expected to be developed based on your analysis and available resources. For each function, briefly describe its purpose and expected outcome. These functions should be decoupled from each other.

The output TEXT format is as follows:
Keyword: <Keyword>
Definition: <Definition>
User Requirement: <User Requirement>
Functional Requirements: <Functional Requirements>

User requirements: {instruction}
""".strip()
